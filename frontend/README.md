# `frontend/` — visualização interativa  `[C]`

React + Vite + Cytoscape.js (decisão **D3**, registrada na ADR-0005).
Consome a API somente leitura do FastAPI e é compilado para
`src/edugraph/api/static/`, de onde o próprio FastAPI o serve em `/`.

## Requisitos

**Node.js 18 ou superior** (Vite 5 não roda em versões anteriores).
Confira com `node --version`; se estiver abaixo, instale o LTS atual —
versões anteriores à 18 estão sem suporte de segurança.

## Comandos

```bash
cd frontend
npm install

npm run dev        # servidor de desenvolvimento em :5173, com proxy para :8000
npm run build      # compila para ../src/edugraph/api/static/
npm run typecheck  # tsc sem emitir
```

Em desenvolvimento, suba os dois:

```bash
python -m edugraph api serve --root data/fixtures   # terminal 1
npm run dev                                          # terminal 2
```

O Vite encaminha `/health`, `/datasets` e `/openapi.json` para a API, de
modo que o front usa caminhos relativos nos dois modos e não precisa
saber onde está rodando.

## O que a interface faz (spec C-05)

- **Cor por comunidade**, com a paleta de Okabe & Ito (acessível para
  daltonismo) **e uma forma por comunidade** — em escala de cinza, é a
  forma que separa os grupos (`src/palette.ts`). A maior comunidade fica
  sempre com a primeira cor, então o mesmo grafo sai com as mesmas cores.
- **Tamanho por centralidade** (grau, intermediação ou autovetor). Trocar
  a métrica anima o tamanho dos nós sem recarregar nem refazer o layout.
- **Seletor de partição**, com Q, número de comunidades e legenda.
  Trocar a partição só recolore: o grafo não é redesenhado.
- **Painel do nó**: comunidade, as três métricas com a posição no ranking
  e os vizinhos do mais forte ao mais fraco — clicar num vizinho o
  seleciona. A vizinhança do nó selecionado fica em destaque no grafo.
- **Transição entre projeções**: os nós em comum partem da posição em
  que estavam.
- **Grafos grandes**: a API corta a resposta em 5.000 arestas por padrão
  pelo **esqueleto** (as k ligações mais fortes de cada nó, com o maior
  k que cabe), e a interface diz que cortou. Acima de
  `MAX_EDGES_CONFORTAVEL` (3.000) o desenho é simplificado e há aviso.

Figuras do artigo **não** saem daqui: saem de `reporting/figures.py`.
As capturas da interface são material complementar do capítulo 3.

## Roteiro de verificação manual

Teste de interface com navegador não paga o custo num TCC de três
pessoas (decisão registrada na spec C-05); este roteiro substitui.
Rode a API com o build (`npm run build` antes) e abra
`http://127.0.0.1:8000`:

```bash
python -m edugraph api serve --root data/processed --root data/fixtures
```

1. **Abrir** e escolher o dataset `synthetic_v1` (com `data/processed` na
   raiz, a tela abre no primeiro dataset do OULAD que tiver partição). Ele aparece com a projeção colorida
   pela partição Louvain e a legenda com três comunidades.
2. **Trocar a projeção** para `student_simple`. O grafo é redesenhado;
   a partição acompanha (`louvain__student_simple`, Q ≈ 0,4666).
3. **Trocar a métrica** de Grau para Intermediação. Os nós mudam de
   tamanho com transição, sem recarregar; os que ligam as comunidades
   crescem.
4. **Clicar num nó.** O painel mostra comunidade, grau, intermediação e
   autovetor, com a posição de cada um; clicar num vizinho troca a
   seleção. Clicar no fundo limpa.
5. **Trocar a partição** para "sem cor por comunidade" e voltar. Só as
   cores mudam; as posições ficam.
6. **Grafo grande.** Com o OULAD em `data/processed`, abrir
   `oulad_vle_bbb_2013j` / `student_simple` (1,75 M arestas). A faixa de
   aviso diz que é o esqueleto (k = 2, 3.732 arestas) e que todos os
   1.870 nós estão presentes; a interface continua respondendo.
7. **Escala de cinza.** No console do navegador,
   `document.documentElement.style.filter = "grayscale(1)"`: as
   comunidades continuam distinguíveis pela forma.
8. `npm run typecheck` passa.

## Limite de escala

`MAX_EDGES_CONFORTAVEL` em `GraphView.tsx` é 3.000. Acima disso o
navegador engasga e a figura deixa de comunicar. O corte é
responsabilidade da API (spec C-04, parâmetros `max_edges` e `cut`); o
componente confia no que recebe, mas avisa quando o número passa.
