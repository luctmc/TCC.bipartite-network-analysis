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
| 4 | Comunidades na projeção aluno↔aluno | B-07 | presente | `fig4-comunidades-synthetic_v1-girvan_newman__student_simple.{png,svg}`, `fig4-comunidades-synthetic_v1-louvain__student_simple.{png,svg}` | seção de comunidades |
| 5 | Distribuição de tamanhos de comunidade | B-07 | presente | `fig5-tamanhos-synthetic_v1.{png,svg}` | seção de comunidades |
| 6 | Q × tempo por algoritmo | B-04/B-07 | presente | `fig6-q-tempo-synthetic_v1.{png,svg}` | comparação de algoritmos |
| 7 | Ranking de disciplinas por intermediação | C-03/C-07 | presente | `fig7-disciplinas-oulad_module_presentation-discipline_simple.{png,svg}`, `fig7-disciplinas-oulad_vle_bbb_2013j-discipline_simple.{png,svg}` | disciplinas críticas |
| 8 | Desfecho por quartil de centralidade | C-06 | presente | `fig8-validacao-oulad_vle_bbb_2013j-student_simple-betweenness.{png,svg}`, `fig8-validacao-oulad_vle_bbb_2013j-student_simple-degree.{png,svg}`, `fig8-validacao-oulad_vle_bbb_2013j-student_simple-eigenvector.{png,svg}` | validação |
| 9 | Capturas da interface | C-05 | presente | `ui-1-comunidades-synthetic_v1.{png}`, `ui-2-intermediacao-synthetic_v1.{png}`, `ui-3-disciplinas-criticas-oulad_module_presentation.{png}`, `ui-4-alunos-ava-oulad_vle_bbb_2013j.{png}` | aplicação |

## Legendas geradas

**`fig2-bipartido-oulad_bbb_2013j`** — Grafo bipartido de oulad_bbb_2013j: 1706 alunos, 11 disciplinas e 14180 arestas (critério score_threshold, limiar 40). Para legibilidade, a figura mostra uma amostra determinística de 300 alunos (semente 0) e todas as suas arestas; as estatísticas do texto referem-se ao grafo completo.

**`fig2-bipartido-oulad_module_presentation`** — Grafo bipartido de oulad_module_presentation: 22425 alunos, 22 disciplinas e 24500 arestas (critério score_threshold, limiar 40). Para legibilidade, a figura mostra uma amostra determinística de 300 alunos (semente 0) e todas as suas arestas; as estatísticas do texto referem-se ao grafo completo.

**`fig4-comunidades-synthetic_v1-girvan_newman__student_simple`** — Comunidades na projeção student_simple de synthetic_v1, por girvan_newman (Q = 0.4174, 3 comunidades, status ok). Cores da escala cividis, que se distingue também em escala de cinza; a forma do marcador repete a informação da cor. Layout spring com semente 0.

**`fig4-comunidades-synthetic_v1-louvain__student_simple`** — Comunidades na projeção student_simple de synthetic_v1, por louvain (Q = 0.4666, 3 comunidades, status ok). Cores da escala cividis, que se distingue também em escala de cinza; a forma do marcador repete a informação da cor. Layout spring com semente 0.

**`fig5-tamanhos-synthetic_v1`** — Distribuição de tamanhos das comunidades, um painel por algoritmo, sobre 2 partições de synthetic_v1. Tamanhos em ordem decrescente; 0 comunidades de um nó só no total. Cores da escala cividis.

**`fig6-q-tempo-synthetic_v1`** — Modularidade × tempo de execução em synthetic_v1, 2 execuções. Marcador vazado indica execução que não terminou dentro do orçamento (ADR-0006). O mais lento levou 399× o tempo do mais rápido. Escala logarítmica no tempo.

**`fig7-disciplinas-oulad_module_presentation-discipline_simple`** — Disciplinas de oulad_module_presentation ordenados pela intermediação na projeção discipline_simple (weight_mode = none). Quanto maior a barra, mais caminhos mínimos entre outras disciplinas passam por ela. Spec C-07.

**`fig7-disciplinas-oulad_vle_bbb_2013j-discipline_simple`** — Recursos do ava de oulad_vle_bbb_2013j ordenados pela intermediação na projeção discipline_simple (weight_mode = inverse, estimativa com k = 200). Quanto maior a barra, mais caminhos mínimos entre outras disciplinas passam por ela. Spec C-07.

**`fig8-validacao-oulad_vle_bbb_2013j-student_simple-betweenness`** — Desfecho histórico por faixa de centralidade (intermediação) na projeção student_simple de oulad_vle_bbb_2013j. Faixas por posição no ranking, Q1 = menor centralidade. A linha tracejada marca a fração de concluintes da base (57,3%): quando os aprovados (Distinction + Pass) da faixa ficam abaixo dela, a faixa tem mais não conclusão (Fail + Withdrawn) que a base. Validação a posteriori (spec C-06): o desfecho não entra em nenhum cálculo de centralidade.

**`fig8-validacao-oulad_vle_bbb_2013j-student_simple-degree`** — Desfecho histórico por faixa de centralidade (grau) na projeção student_simple de oulad_vle_bbb_2013j. Faixas por posição no ranking, Q1 = menor centralidade. A linha tracejada marca a fração de concluintes da base (57,3%): quando os aprovados (Distinction + Pass) da faixa ficam abaixo dela, a faixa tem mais não conclusão (Fail + Withdrawn) que a base. Validação a posteriori (spec C-06): o desfecho não entra em nenhum cálculo de centralidade.

**`fig8-validacao-oulad_vle_bbb_2013j-student_simple-eigenvector`** — Desfecho histórico por faixa de centralidade (autovetor) na projeção student_simple de oulad_vle_bbb_2013j. Faixas por posição no ranking, Q1 = menor centralidade. A linha tracejada marca a fração de concluintes da base (57,3%): quando os aprovados (Distinction + Pass) da faixa ficam abaixo dela, a faixa tem mais não conclusão (Fail + Withdrawn) que a base. Validação a posteriori (spec C-06): o desfecho não entra em nenhum cálculo de centralidade.

**`ui-1-comunidades-synthetic_v1`** — Interface do edugraph sobre a base sintética (synthetic_v1, projeção aluno↔aluno): as três comunidades encontradas pelo Louvain (Q = 0,467), cada uma com uma cor e uma forma, correspondem às três áreas plantadas no gerador. Captura da spec C-05.

**`ui-2-intermediacao-synthetic_v1`** — Mesma rede com o tamanho dos nós pela intermediação: os alunos que ligam as comunidades crescem. O painel mostra o nó selecionado com as três métricas e a posição no ranking (1º em grau e em intermediação, 15º em autovetor). Captura da spec C-05.

**`ui-3-disciplinas-criticas-oulad_module_presentation`** — Projeção disciplina↔disciplina do OULAD (22 disciplinas, módulo × apresentação), com o tamanho pela intermediação: as maiores são as disciplinas críticas da spec C-03 (FFF_2014B, DDD_2014J, FFF_2014J). Cores pelas comunidades do Louvain. Captura da spec C-05.

**`ui-4-alunos-ava-oulad_vle_bbb_2013j`** — Os 1.870 alunos da coorte BBB 2013J ligados pelo uso do AVA (1,75 milhão de arestas), desenhados pelo esqueleto da API: as 2 ligações mais fortes de cada aluno, como diz a faixa de aviso. Tamanho pelo autovetor; cores pelo Louvain (Q = 0,039, estrutura fraca). Captura da spec C-05.


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
