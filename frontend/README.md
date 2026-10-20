# `frontend/` — visualização interativa  `[C]`

React + Vite + Cytoscape.js (decisão **D3**, registrada na ADR-0005).
Consome a API somente leitura do FastAPI e é compilado para
`src/edugraph/api/static/`, de onde o próprio FastAPI o serve em `/`.

## Requisitos

**Node.js `^20.19.0 || ^22.13.0 || >=24`.** A faixa vem do ESLint 10, que o
branch `c/pendencias-frente-c` adiciona e declara em `engines` no
`package.json`; o Vite 5 sozinho roda em versões mais antigas, mas o projeto
passa a exigir esta faixa. Confira com `node --version`; se estiver fora dela,
instale o LTS atual.

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

**Direção A · Editorial científico** (REBRAND-02, 20/10/2026): implementação
do protótipo `TCC-design-direcoes/direcao-a-editorial-cientifico.html`
escolhido pelo usuário. A tela funciona como uma página de periódico:
coluna de métodos, figura numerada e nota lateral do nó, separadas por
filetes. O título curto da aplicação e os três autores foram preservados.

- **Claro padrão:** papel `#FBFAF7`, tinta `#1A1915`, folha branca.
  **Escuro:** grafite quente `#161512`, folha `#1C1B18`, tinta `#ECE8DF`.
  O script inline define o tema antes da primeira pintura, usando a escolha
  salva em `localStorage` (`edugraph-tema`) ou o claro padrão. O botão
  continua alternando os temas sem recriar o grafo nem perder a seleção.
- **Fontes locais, aprovadas sob SIL OFL 1.1:** Source Serif 4 (normal e
  itálico variáveis, com tamanho óptico) nos títulos, números e legenda;
  Source Sans 3 variável na interface e nos rótulos do canvas; Source Code
  Pro Regular nos ids. Obtidas dos repositórios oficiais da Adobe:
  [source-serif](https://github.com/adobe-fonts/source-serif),
  [source-sans](https://github.com/adobe-fonts/source-sans) e
  [source-code-pro](https://github.com/adobe-fonts/source-code-pro).
  Os WOFF2 reduzidos, as três licenças OFL e os URLs imutáveis com os commits
  de origem estão em [public/fonts/README.md](public/fonts/README.md).
  O subset latino com português soma 588.068 bytes (42,3% menor), com
  `unicode-range` e eixos variáveis preservados. O script de regeneração usa
  fonttools/Brotli em venv temporário, sem dependências novas no projeto.
  Não há CDN nem requisição externa de fonte em runtime.
- **Métodos em quatro passos:** Dados, Projeção, Comunidades e Centralidade.
  Ids e callbacks continuam iguais; opções de tamanho têm aparência de
  rádios 2×2 e explicação da métrica ativa. A modularidade usa notação
  matemática (*Q* = 0,3715); a legenda das comunidades usa linhas de tabela.
- **Figura 1:** faixa de números no topo do palco; legenda editorial sob
  o grafo ensina forma/cor, tamanho e peso. Nós chapados e rótulos com halo;
  contorno de tinta no claro, recorte de papel no escuro e seleção por
  anel na própria forma. Arestas neutras, sólidas, com largura de 0,75 a
  4,75 px conforme o peso em grafos pequenos. A direção A original usa
  linhas sólidas; não foi adotado o tracejado da direção C. Nenhum vidro,
  gradiente, reflexo SVG ou acento verde da moldura anterior permanece.
  Okabe & Ito e as formas de `palette.ts` continuam intactos.
- **Painel do nó:** nome em serifa, comunidade, scores com quatro casas,
  pontos de posição e texto exato como "3º de 7". Até 15 pontos por métrica;
  em redes maiores as marcas são proporcionais, com a posição exata em
  texto e nome acessível. Vizinhos mantêm ordem por peso, limite de 12,
  clique para selecionar e aviso de truncamento, com barras finas neutras.
- **Seletor:** mantém ARIA, teclado/type-ahead, portal com abertura para cima,
  reconfirmação sem `onChange` e `<select>` nativo oculto do `capture.mjs`.
  O menu usa o mesmo papel e os mesmos filetes dos campos.
- **Responsividade:** três colunas em 1440; métodos e inspetor mais estreitos
  em 1024; em 390, cabeçalho, figura, painel, controles e rodapé nessa ordem.
  Status e raízes da API ficam visíveis também no celular: raízes em 7ch,
  com reticências e caminho completo no `title`. O DOM segue figura/painel
  antes dos métodos, como no celular; o grid mantém métodos | figura | nota
  no desktop. Tab segue a ordem do DOM nos dois tamanhos.
  Zoom permanece por ref (`aproximar`, `afastar`, `centralizar`) e atalhos
  `+`, `−`, `0`; o desenho grande mantém estilo fixo, zoom quantizado e
  cleanup. A câmera inicial e Centralizar usam a mesma folga: 36 px no
  desktop e 28 px quando o canvas tem menos de 600 px, com zoom de
  enquadramento até 3,6 e rótulos incluídos na caixa. Ao redimensionar uma
  figura já aberta, Centralizar refaz o fit. No celular, os botões ocupam
  uma linha própria abaixo do canvas. O menu tem largura mínima de cerca
  de 20rem limitada à viewport; ids ficam em uma linha com reticências e
  texto completo no `title`, enquanto rótulos podem quebrar entre palavras.
- **Estados e acessibilidade:** vazio com filete tracejado, carregamento com
  fio de progresso e erro textual legível; foco visível azul, contraste de
  tinta e papel e cor/forma redundantes. `MotionConfig reducedMotion="user"`
  e CSS de `prefers-reduced-motion` preservados; entradas por opacidade,
  sem deslocamento decorativo. Rodapé em texto com link do repositório.

As capturas da figura 9 anteriores ao REBRAND-02 estão desatualizadas.
Refazê-las com `npm run capture` e regenerar o índice de figuras depois
da integração; as telas OULAD exigem seus artefatos reais.

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


## Contraste dos controles (REBRAND-02)

Bordas indicativas usam `--rule-control`; filetes decorativos mantêm `--rule-2`.
Contrastes calculados pela luminância relativa sRGB (WCAG):

| Tema / borda | Contra papel | Contra folha |
| --- | ---: | ---: |
| Claro `#807A6C` | `#FBFAF7`: **4,091:1** | `#FFFFFF`: **4,270:1** |
| Escuro `#787266` | `#161512`: **3,823:1** | `#1C1B18`: **3,606:1** |

O token identifica gatilhos e menu do Seletor, rádios inativos, botão de tema
e bordas/divisórias do zoom. Todos superam 3:1 nos dois fundos do tema.
