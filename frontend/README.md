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
- **Rótulos**: disciplinas sempre com nome, quando o zoom deixa ler; alunos
  (números de matrícula) só em grafos de até 40 nós. Acima disso, o nome
  aparece sob o mouse, no nó selecionado e nos vizinhos dele quando são até
  15 — com mais, a lista fica no painel.
- **Grafos grandes**: a API corta a resposta em 5.000 arestas por padrão
  pelo **esqueleto** (as k ligações mais fortes de cada nó, com o maior
  k que cabe), e a interface diz que cortou. Acima de
  `MAX_EDGES_CONFORTAVEL` (3.000) o desenho é simplificado e há aviso.

Figuras do artigo **não** saem daqui: saem de `reporting/figures.py`.
As capturas da interface são material complementar do capítulo 3.

## Aparência, tema e acessibilidade

- **Cabeçalho.** Sobrelinha do trabalho (TCC · Grupo 16 · UniAnchieta), o
  título "Análise Topológica e Detecção de Comunidades em Redes Complexas"
  em fonte serifada do sistema, os autores (os mesmos de `pyproject.toml`,
  em `AUTORES` no `App.tsx`), o wordmark *edugraph* com um monograma SVG e,
  à direita, o status da API, as raízes consultadas e o botão de tema. No
  celular ficam só o wordmark, os chips e o título.
- **Modo claro e escuro.** O botão sol/lua (`aria-pressed`) troca o atributo
  `data-theme` do `<html>`. O tema inicial vem de `prefers-color-scheme` e
  é definido por um script em `index.html` **antes da primeira pintura**
  (sem piscar); a escolha fica em `localStorage` (`edugraph-tema`), com
  `try/catch`. Os tokens dos dois temas estão em `styles.css`
  (`:root` e `:root[data-theme="light"]`). O canvas do Cytoscape não entende
  `var(--x)`: ao trocar o tema, o `GraphView` refaz a folha de estilo
  relendo os tokens, sem tocar em dados, posições nem seleção. A paleta das
  comunidades é a mesma nos dois temas; só o anel dos nós se ajusta. A
  transição é curta e não existe com `prefers-reduced-motion`.
- **Barra lateral em quatro passos** (Dados, Projeção, Comunidades,
  Centralidade), com ajuda curta. Projeções e algoritmos aparecem com
  rótulo em português (`ROTULO_PROJECAO` e `ROTULO_ALGORITMO` em `App.tsx`);
  o id técnico, que é o que vai para a API, aparece em fonte monoespaçada.
  O cartão "Como ler o grafo" explica forma, cor, tamanho e espessura e fica
  oculto no celular.
- **Seletor próprio** (`components/Seletor.tsx`). O menu de um `<select>` é o
  popup do sistema, que destoa do tema. O componente segue o padrão WAI-ARIA
  *select-only combobox*: gatilho `role="combobox"` com `aria-expanded` e
  `aria-activedescendant`, painel `role="listbox"`. Teclado: setas,
  Home/End, PageUp/PageDown, Enter ou Espaço, Esc (devolve o foco), digitar
  para buscar (repetir a mesma tecla cicla entre opções com a mesma inicial)
  e clique fora. O painel é desenhado no `<body>` com posição fixa, abre
  para cima quando não cabe embaixo e fecha ao rolar ou redimensionar.
  Escolher de novo a opção **já selecionada** só fecha o menu: o `onChange`
  é o mesmo de um `<select>` e não dispara. Um `<select>` nativo oculto e
  sincronizado continua no DOM — é por ele que `scripts/capture.mjs` escolhe
  as cenas.
- **Painel do nó**: silhueta com o mesmo acabamento dos nós, métricas em um
  bloco ("1º de 7" e barra), vizinhos com a forma da comunidade e barra de
  peso. **Faixa de números** sob o grafo, com Q em destaque e medidor de
  0 a 1; o contador anima até o valor (sem animação com movimento reduzido).
- **Nós** com forma arredondada, gradiente derivado da cor-base e reflexo
  (este só acima de 14 px na tela). O tamanho do rótulo e a largura do anel
  e das arestas acompanham o zoom, em faixas discretas; acima de 400 nós ou
  1.600 arestas o desenho é fixo, sem gradiente nem funções de zoom.
- **Rodapé** fino com o link do repositório do TCC no GitHub
  (`target="_blank"`, `rel="noopener noreferrer"`).
- **Movimento.** `framer-motion` anima a entrada do painel do nó, da faixa
  de números e a troca de projeção; `MotionConfig reducedMotion="user"` e a
  regra global de `prefers-reduced-motion` em `styles.css` tiram o
  deslocamento e deixam só o que ajuda a entender.
- **Limites conhecidos.** O `npm run lint` existe em `package.json`, mas o
  ESLint não é dependência do projeto: o comando falha com
  `eslint: command not found`. O reflexo e os gradientes dos nós não foram
  medidos em grafos acima de 400 nós (nesse caso o desenho fixo os
  desliga).

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

## Capturas para o artigo (figura 9)

`npm run capture` gera as capturas da interface em `results/figures/`
(`ui-*.png`, 3200 × 2000, com a legenda em `ui-*.caption.txt`). O script
(`scripts/capture.mjs`) abre a interface num Edge ou Chrome headless, monta
cada cena pelos próprios controles da tela e fotografa. Não instala nada: usa
o WebSocket nativo do Node 22+.

```bash
python -m edugraph api serve --root data/processed --root data/fixtures   # terminal 1
npm run capture                                                           # terminal 2
python -m edugraph figures --index                                        # atualiza o índice
```

Para apontar outro navegador Chromium (por exemplo o Brave, se não houver
Edge nem Chrome), use `EDUGRAPH_BROWSER`; para fotografar o servidor de
desenvolvimento em vez do build servido pela API, `--url http://127.0.0.1:5173`.
Para não sobrescrever `results/figures`, passe `--out` com outro diretório.

As cenas seguem o roteiro acima: comunidades em `synthetic_v1`, a mesma rede
por intermediação com um nó selecionado, as disciplinas críticas do OULAD e
os alunos do AVA pelo esqueleto. Sem o OULAD em `data/processed`, as duas
últimas são puladas. Refaça as capturas sempre que a interface mudar. Elas
não são reproduzíveis byte a byte (o layout anima), ao contrário das figuras
de `reporting/figures.py`.

## Limite de escala

`MAX_EDGES_CONFORTAVEL` em `GraphView.tsx` é 3.000. Acima disso o
navegador engasga e a figura deixa de comunicar. O corte é
responsabilidade da API (spec C-04, parâmetros `max_edges` e `cut`); o
componente confia no que recebe, mas avisa quando o número passa.
