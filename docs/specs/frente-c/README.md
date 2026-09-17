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
