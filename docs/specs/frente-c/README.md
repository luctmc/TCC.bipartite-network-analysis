# Specs da Frente C — Centralidade e Aplicação  `[C]` Lucas

Grau, intermediação, autovetor, disciplinas críticas, API e front-end.

**Produz** `centrality/`, `metrics/centrality_top.csv`, a API e a
interface. **Consome** `projections/`, `communities/` e os próprios
`centrality/`.

| ID | Spec | Consome | Cumpre | Artigo |
|---|---|---|---|---|
| [C-01](C-01-grau-intermediacao.md) | Grau e intermediação | Projection (fixture) | CentralityResult | decisão sobre o peso |
| [C-02](C-02-autovetor.md) | Autovetor por iteração de potência | Projection (fixture) | CentralityResult | **algoritmo implementado à mão** |
| [C-03](C-03-disciplinas-criticas.md) | Disciplinas críticas e discordância | CentralityResult | `metrics/centrality_top.csv` | **saída obrigatória** + tabela |
| [C-04](C-04-api.md) | API somente leitura | todos os bundles (fixture) | API | — |
| [C-05](C-05-frontend.md) | Front-end React + Cytoscape.js | API | visualização | capturas do cap. 3 |
| [C-06](C-06-validacao-centralidade.md) | Validação a posteriori | CentralityResult, Outcomes | — | tabela + figura |
| [C-07](C-07-relatorio-interno.md) | Relatório interno | `metrics/` | `results/` | **saída obrigatória** |

## Ordem sugerida

**Onda 1:** C-01, C-04 · **Onda 2:** C-02, C-03, C-05 · **Onda 3:** C-06
· **Onda 4:** C-07.

## Três coisas para não esquecer

**A projeção disciplina↔disciplina é obrigatória.** A seção 13 do
briefing avisa que é fácil esquecer dela. É ela que responde à parte do
objetivo declarado sobre gargalos no fluxo curricular — centralidade só
sobre alunos não cumpre o que a Introdução prometeu.

**Peso no caminho mínimo é distância, não afinidade.** Em NetworkX,
passar `weight="weight"` na intermediação faz peso alto virar caminho
longo — o inverso da semântica das projeções. A C-01 precisa decidir e
registrar.

**Em `synthetic_v1`, a projeção de disciplinas é o grafo completo K₇.**
Toda intermediação é zero, todo grau é 1,0. É a confirmação empírica da
decisão D1, e nenhum teste deve afirmar que uma disciplina específica
lidera o ranking nessa fixture. Ver
`data/fixtures/synthetic_v1/REFERENCE.md`.

## O que já existe no dia 0

- `/health` e `/datasets` **funcionando** e testados.
- O esqueleto do front conectando na API, com seletores montados a partir
  de `/datasets`.
- As centralidades de referência nas fixtures, para o front ter o que
  mostrar antes de C-01 e C-02.

## O que a Frente A entrega — leia antes de escolher o `--root`

Em `data/processed`, prontos para `--root`. **A escolha do dataset não é
indiferente**, e a razão está na spec A-08:

| dataset | o que é | para quê |
|---|---|---|
| `oulad_vle_bbb_2013j` | coorte BBB 2013J pelo **AVA**: 1.870 alunos × 320 recursos, projeção aluno↔aluno com 1,75 M arestas | **comunidades de alunos** — é o único com sinal |
| `oulad_vle_bbb_2013j_null0..4` | réplicas nulas do anterior | a linha de base da B-06 |
| `oulad_module_presentation` | base inteira por módulo×apresentação, 22.425 alunos, 22 disciplinas | **projeção de disciplina** e disciplinas críticas (C-03) |
| `oulad_module_presentation_null0..2` | réplicas nulas do anterior | linha de base |
| `oulad_bbb_2013j` | coorte por avaliação, 1.706 alunos | comparação Louvain × Girvan-Newman (grafo menor) |

**O aviso que evita concluir o contrário do certo.** Na projeção
aluno↔aluno de `oulad_module_presentation`, o Q real (0,7728) é **menor**
que o das réplicas embaralhadas (0,781): ali não há estrutura de
comunidade, e o Q alto é artefato da esparsidade. Quem quiser comunidades
de alunos usa `oulad_vle_bbb_2013j`, onde o Q real fica 5 vezes acima do
nulo.

Nada muda no código de quem consome: `kind`, `nodes.csv` e o layout são
idênticos nos dois. Muda só o que o nó do lado V significa — recurso do
AVA em vez de disciplina (ADR-0012).
