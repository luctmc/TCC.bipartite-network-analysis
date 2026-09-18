# Índice de figuras

> **Arquivo gerado** por `python -m edugraph figures --index` a partir de
> `results/figures/`. Não editar à mão: a lista planejada vive em
> `edugraph.reporting.figures.PLANNED_FIGURES`; para acrescentar uma
> figura ao plano, edite lá e regenere.

| # | Figura | Spec | Estado | Arquivos | Onde no artigo |
|---|---|---|---|---|---|
| 1 | Arquitetura de componentes | — | pendente | — | abertura do cap. 3 |
| 2 | Grafo bipartido | A-07 | presente | `fig2-bipartido-oulad_bbb_2013j.{png,svg}`, `fig2-bipartido-oulad_module_presentation.{png,svg}` | seção de dados |
| 3 | Distribuição de pesos: simples × alocação de recursos | A-05 | pendente | — | seção de projeção |
| 4 | Comunidades na projeção aluno↔aluno | B-07 | pendente | — | seção de comunidades |
| 5 | Distribuição de tamanhos de comunidade | B-07 | pendente | — | seção de comunidades |
| 6 | Q × tempo por algoritmo | B-04/B-07 | pendente | — | comparação de algoritmos |
| 7 | Ranking de disciplinas por intermediação | C-03/C-07 | pendente | — | disciplinas críticas |
| 8 | Desfecho por quartil de centralidade | C-06 | pendente | — | validação |
| 9 | Capturas da interface | C-05 | pendente | — | aplicação |

## Legendas geradas

**`fig2-bipartido-oulad_bbb_2013j`** — Grafo bipartido de oulad_bbb_2013j: 1706 alunos, 11 disciplinas e 14180 arestas (critério score_threshold, limiar 40). Para legibilidade, a figura mostra uma amostra determinística de 300 alunos (semente 0) e todas as suas arestas; as estatísticas do texto referem-se ao grafo completo.

**`fig2-bipartido-oulad_module_presentation`** — Grafo bipartido de oulad_module_presentation: 22425 alunos, 22 disciplinas e 24500 arestas (critério score_threshold, limiar 40). Para legibilidade, a figura mostra uma amostra determinística de 300 alunos (semente 0) e todas as suas arestas; as estatísticas do texto referem-se ao grafo completo.


## Regras

- Toda figura sai em **PNG e SVG** (`reporting.figures.save_figure`), sem
  data nos metadados: a mesma figura gerada duas vezes tem os mesmos bytes.
- Estilo comum em `reporting.figures.STYLE`: tamanho no valor final, sem
  reescalar — texto reescalado é a causa número um de legenda ilegível.
- Cores distinguem **também em escala de cinza**: o artigo pode ser
  impresso em preto e branco.
- Figura de grafo grande é **amostrada ou agregada**, e a legenda diz o
  que foi feito (gravada em `<nome>.caption.txt` ao lado da figura).

A figura 1 é exportada do Mermaid de
[`../arquitetura/diagrama-cap3.md`](../arquitetura/diagrama-cap3.md).
