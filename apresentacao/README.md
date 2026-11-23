# `apresentacao/` — a defesa do TCC, como página interativa

Apresentação da banca construída sobre o próprio edugraph: mesma
identidade visual da interface (direção editorial científica, família
Source, cores de Okabe & Ito), diagramas animados do método e uma
**demonstração ao vivo** do sistema real, com o tour de boas-vindas e a
turma fictícia de Computação.

Segue a estrutura do artigo e da defesa de TCC: **sumário**, **introdução**
(contextualização, problema de pesquisa, justificativa, objetivo geral e
específicos), **fundamentação teórica**, **metodologia** (caracterização,
bases, critérios e etapas), **desenvolvimento** (com a demonstração),
**resultados e discussão**, **considerações finais** (conclusões,
limitações e trabalhos futuros) e **referências**. Citações no sistema
autor-data da ABNT NBR 10520:2023 — por exemplo (Blondel *et al.*, 2008)
— e referências na NBR 6023:2018. Cada slide mostra no rodapé em que
seção da apresentação ele está.

É uma pasta isolada, em HTML, CSS e JavaScript puros, sem build e sem
dependências; o servidor é só biblioteca padrão do Python. Fora dela, a
única mudança foi visual no tour do próprio sistema (balão, véu e
progresso em `frontend/src/tour/Tour.tsx` e `frontend/src/styles.css`),
sem mudar textos nem lógica — recompile com `python scripts/iniciar.py`.

## Rodar

```bash
python scripts/iniciar.py          # uma vez: instala, testa e compila a interface do sistema
python apresentacao/servir.py      # sobe o sistema (se não estiver no ar) e a apresentação
```

Abre `http://127.0.0.1:8765/index.html`. O sistema fica em
`http://127.0.0.1:8000` e aparece dentro do slide da demonstração.

| Opção de `servir.py` | Para quê |
|---|---|
| `--sem-app` | só a apresentação; o sistema você sobe à parte |
| `--app-url http://127.0.0.1:8001` | sistema em outra porta (vira `?app=` na URL) |
| `--porta 9000` | apresentação em outra porta |
| `--curta` | versão curta: tira os 2 slides marcados `data-opcional` (≈ 1 min a menos) |
| `--sem-navegador` | não abre o navegador |

Sem Python à mão, `index.html` também abre direto do disco (duplo
clique): slides, animações, notas na tela (N) e a demonstração funcionam.
Só o **modo apresentador** precisa do servidor, porque o navegador não
deixa uma página aberta do disco ler as notas da outra.

## No dia

1. Rode `python apresentacao/servir.py` com antecedência.
2. No slide da demonstração (tecla **D**), confira que a barra diz
   **“Ao vivo · sistema conectado”**. Entre (Enter), aperte ▶ uma vez e saia:
   a primeira rodada carrega as bibliotecas; depois é instantâneo.
3. Volte ao início (Home), ponha a janela no projetor e aperte **F**.
4. No notebook, aperte **P** para abrir o modo apresentador e arraste-o
   para a sua tela. As duas janelas ficam sincronizadas.

### Teclado (janela da plateia)

| Tecla | Faz |
|---|---|
| → · espaço · PgDn | avança (passo a passo dentro do slide) |
| ← · PgUp | volta |
| ↑ ↓ | slide anterior / seguinte, sem passos |
| Home · End | início · último slide principal |
| número + Enter | vai ao slide |
| **O** | visão geral (todos os slides) |
| **F** | tela cheia |
| **P** | modo apresentador (segunda janela) |
| **N** | notas na própria tela (tela única) |
| **D** | vai à demonstração; no slide, entra nela |
| Enter · **R** | no slide da demo: entra · reinicia o sistema |
| **A** | apêndice técnico (para as perguntas) |
| **B** ou . | tela preta |
| **K** · **J** · **L** | nas sequências animadas: tocar/pausar · voltar 2 s · avançar 2 s |

O mouse mostra uma barra de controles discreta no pé da tela (some
sozinha); no toque, deslizar para o lado troca de slide.

### Modo apresentador

`apresentador.html` (tecla P): slide atual, o próximo passo ou slide,
as notas em letra grande, cronômetro (alvo em `js/config.js`) e relógio.
As setas dessa janela comandam a plateia; **D** e **Esc** entram e saem
da demonstração na tela do projetor. Se a janela da plateia fechar, ele
avisa e continua andando sozinho, para as notas não se perderem.

## A demonstração ao vivo

O slide 23 mostra uma janela com o edugraph de verdade (`/?tour`, que
força o tour do laboratório — `frontend/src/tour/estado.ts`). O iframe
fica numa camada fora do palco escalado, na resolução real da tela: ao
entrar, a janela cresce até ocupar a tela inteira, sem recarregar nem
refazer o layout do sistema. Lá dentro o teclado é do sistema (espaço,
← →, F). Para voltar, o botão **“Voltar à apresentação”** no topo, ou
**Esc** na janela do apresentador. O estado do sistema é preservado.

**Se o sistema não responder,** a barra diz “Sistema não respondeu”, e a
janela mostra **capturas reais** com o aviso “não é execução ao vivo”.
Enter abre a galeria de 17 capturas (tour, as quatro etapas do Louvain,
a revelação, o Girvan–Newman e o explorador), gravadas em 16/11/2026
sobre `data/fixtures`. A verificação de saúde roda a cada 5 s: subindo a
API, a janela volta a ser ao vivo sozinha. Nada é simulado.

## Organização

```
apresentacao/
├─ index.html          os 59 slides (33 + 26 de apêndice) e as notas de cada um
├─ apresentador.html   modo apresentador
├─ css/apresentacao.css   tokens, palco, motor, demo, controles
├─ css/slides.css         estilos de cada slide e diagrama
├─ js/config.js        endereço do sistema, alvo de tempo, lista de capturas
├─ js/deck.js          motor: escala 16:9, passos, teclado, visão geral, sincronização
├─ js/demo.js          a janela ao vivo e a reserva de capturas
├─ js/dados.js         dados reais dos diagramas (gerado por gerar_dados.py)
├─ js/contexto-dados.js  os números do Inep, escritos à mão com gráfico e página
├─ js/desenho.js       posições do exemplo dos seis alunos (um lugar só)
├─ js/contexto.js      as animações da Introdução e dos slides novos da Fundamentação
├─ js/diagramas.js     desenha a rede real, o exemplo tiny_v1 e os contadores
├─ js/motion.js        abertura, encerramento e as três sequências animadas
├─ js/apresentador.js  modo apresentador
├─ img/app/            capturas reais do sistema (WebP)
├─ fonts/              Source Serif 4, Source Sans 3, Source Code Pro (SIL OFL 1.1)
├─ servir.py           servidor local (+ sobe o sistema)
├─ gerar_dados.py      gera js/dados.js a partir de data/fixtures
├─ aplicar_enredo.py   leva a fala do ENREDO.md para as notas (e conta o tempo)
├─ gerar_roteiro.py    gera ROTEIRO.md a partir das notas
├─ ROTEIRO.md          o roteiro falado, slide a slide (gerado)
├─ NARRATIVA.md        como contamos o trabalho (fonte das ideias e dos números)
├─ ENREDO.md           o texto falado no dia (fonte das notas)
├─ PLANO-AJUSTE.md     o plano do ajuste "contexto primeiro" e o que foi aplicado
├─ VERIFICACAO.md      o que foi testado e o que não foi
└─ ferramentas/capturar.cjs   regrava as capturas (opcional, Playwright)
```

## Editar

- **Texto, ordem e notas:** cada slide é uma `<section class="slide">` em
  `index.html`; mova a seção para mudar a ordem (a numeração é automática).
  `data-titulo` aparece na visão geral e no apresentador; `data-secao="n"`
  marca a seção no rodapé (os nomes estão em `js/config.js`). As notas
  ficam no `<aside class="notas">` do próprio slide.
- **Passos:** `data-passo="n"` faz o elemento aparecer no n-ésimo avanço;
  `data-sai="n"` o tira; `data-esmaece="n"` o esmaece. `data-entra` entra
  em cascata quando o slide abre. O slide recebe `data-etapa` com o passo
  atual, para o CSS dos diagramas reagir.
- **Versão curta:** marque o slide com `data-opcional` e use `--curta`.
  Hoje: “o aluno que some” e a validação na turma inventada.
- **Apêndice:** um slide com `data-apendice` sai da numeração principal e
  só aparece com a tecla A. Foi para lá o que saiu da fala para caber em
  15–20 minutos (o escore *z*, o Girvan–Newman, a arquitetura, o clique…).
- **Fala:** a fonte é o `ENREDO.md`. Depois de mudá-lo, rode
  `python apresentacao/aplicar_enredo.py` (atualiza as notas; com
  `--contar`, só conta palavras e tempo) e
  `python apresentacao/gerar_roteiro.py`.
- **Capturas:** troque os arquivos de `img/app/` e a lista em `js/config.js`.

## Motion design

As animações são parte da explicação, não enfeite, e funcionam offline
(HTML, CSS, SVG, Canvas e JavaScript, sem bibliotecas externas):

- **Abertura** (capa): a marca do edugraph — círculo, triângulo e quadrado
  — se desfaz nos 98 alunos reais de `synthetic_v1`, cada um saindo da
  forma da sua comunidade; depois entram título, equipe com RA e orientador.
- **Encerramento**: o caminho inverso — a rede volta a ser a marca.
- **Sete sequências com tocar, pausar e barra de tempo** (como um vídeo,
  mas vetoriais e geradas dos dados), cada uma começando sozinha ao chegar
  no slide, com legendas que acompanham o tempo:
  - *O aluno que some* (slide 4, linha do tempo **ilustrativa**);
  - *De cada 100 que entraram* (slide 5, os números do Inep);
  - *A lista vira mapa* (slide 6, a planilha dos seis alunos vira o mapa);
  - *Entra a lista, sai o mapa* (slide 10, a solução);
  - *O teste contra o acaso* (slide 24, a rede real se desfaz numa réplica
    nula e o *Q* cai);
  - no apêndice: *Do dado ao resultado* e *O que acontece quando se
    aperta ▶*.
- **Cenas por passos** (`js/contexto.js`), que quem apresenta controla com
  a seta: a ligação e a força da ligação (slide 7), os grupos, a ponte e
  a beirada (slide 8), as três perguntas (slide 9), o que é um grafo (um
  metrô genérico que vira o grafo bipartido dos seis alunos, slide 14) e,
  no apêndice, por que procurar na comunidade, o escore *z* e o
  dicionário. Todas usam **o mesmo desenho dos seis alunos**, nas mesmas
  posições dos slides técnicos (`js/desenho.js`), com a espessura de cada
  ligação igual ao peso real.
- **Transições**: o slide que sai recua e o que entra se aproxima
  (profundidade, ao contrário quando se volta); as aberturas de capítulo
  entram como uma cortina lateral.

Cada sequência é uma função pura do tempo (`render(t)`), por isso dá para
pausar e arrastar sem perder a sincronia. Vídeo renderizado (Remotion, por
exemplo) foi avaliado e descartado: traria arquivos pesados, perderia a
nitidez no projetor e não deixaria parar num quadro para responder a uma
pergunta. Com `prefers-reduced-motion`, tudo abre no quadro final.

## Tempo

Feita para **15 a 20 minutos**: 33 slides principais (seis são aberturas
de capítulo, de poucos segundos). A fala do `ENREDO.md` soma ≈ 1.500
palavras fora a demonstração (≈ 11 min a 140 palavras por minuto); com
os avanços, as animações e ≈ 3 min de demonstração, **≈ 17 min**. Com
`--curta`, ≈ 16 min. A conta por parte e a ordem de corte, se o ensaio
passar de 20 min, estão no fim do `ENREDO.md`. O cronômetro do modo
apresentador usa `duracaoAlvoMin` (20) de `js/config.js`.
O detalhe técnico está no **apêndice** (tecla A), para as perguntas da
banca.

## De onde vêm os números

**Só estas coisas são escolha de desenho, e estão avisadas na tela:** os
nomes e cursos dos seis alunos do exemplo (Ana a Felipe = alunos 1 a 6 de
`tiny_v1`), a linha do tempo do slide 4, as duas turmas (300 × 15) do
slide 7, o metrô genérico do slide 14 e, no apêndice, o desenho do motivo
2 de “por que procurar dentro da comunidade”. Os números do Inep (slide 5) vêm de `js/contexto-dados.js`, escrito à
mão e conferido no relatório. Todo o resto lê `js/dados.js`, gerado por
`python apresentacao/gerar_dados.py` a partir de `data/fixtures`:

- a rede da capa, da modularidade e do encerramento é a projeção
  aluno ↔ aluno de `synthetic_v1` (98 alunos), com o esqueleto de arestas
  que a API serve e as 3 comunidades do Louvain (*Q* = 0,4666);
- o teste contra o acaso usa 5 réplicas nulas reais de `synthetic_v1`
  (`null_replicas`, semente 0), projetadas e passadas pelo Louvain;
- a fundamentação usa a fixture `tiny_v1` (6 alunos, 3 disciplinas), cujos
  valores o grupo derivou no papel: as matrículas, as duas projeções, o
  rastro real do Louvain (4 movimentos) e do Girvan–Newman do laboratório
  (`edugraph.lab.trace`) e as três centralidades;
- os textos de “quem merece atenção” e “quem se destaca” são os que o
  próprio sistema escreve (`run_lab` sobre `tiny_v1` e sobre a turma padrão
  do laboratório, semente 12), lidos de `js/dados.js`.

Só as posições dos nós são escolha de desenho. Os demais números têm a
origem na fonte do slide ou na nota do apresentador; os do OULAD inteiro
vêm dos documentos do grupo, porque `data/processed/` não está no
repositório. Detalhes em [VERIFICACAO.md](VERIFICACAO.md).
