# Índice de figuras

> **Arquivo gerado.** Regenerar com `python -m edugraph figures --index`
> (disponível quando a spec A-07 fechar). Não editar à mão: três pessoas
> editando o mesmo índice é conflito de merge em todo PR.

Enquanto o gerador não existe, esta é a lista **planejada**, com a spec
que produz cada figura.

| # | Figura | Spec | Arquivo | Onde no artigo |
|---|---|---|---|---|
| 1 | Arquitetura de componentes | — | `results/figures/fig1-arquitetura.svg` | abertura do cap. 3 |
| 2 | Grafo bipartido | A-07 | `fig2-bipartido` | seção de dados |
| 3 | Distribuição de pesos: simples × alocação de recursos | A-05 | `fig3-ponderacoes` | seção de projeção |
| 4 | Comunidades na projeção aluno↔aluno | B-07 | `fig4-comunidades` | seção de comunidades |
| 5 | Distribuição de tamanhos de comunidade | B-07 | `fig5-tamanhos` | seção de comunidades |
| 6 | Q × tempo por algoritmo | B-04/B-07 | `fig6-q-tempo` | comparação de algoritmos |
| 7 | Ranking de disciplinas por intermediação | C-03/C-07 | `fig7-disciplinas` | disciplinas críticas |
| 8 | Desfecho por quartil de centralidade | C-06 | `fig8-validacao` | validação |
| — | Capturas da interface | C-05 | `results/figures/ui-*` | aplicação |

## Regras

- Toda figura sai em **PNG e SVG** (`reporting.figures.save_figure`).
- Estilo comum em `reporting.figures.STYLE`: tamanho no valor final, sem
  reescalar — texto reescalado é a causa número um de legenda ilegível na
  banca.
- Cores precisam distinguir **também em escala de cinza**: o artigo pode
  ser impresso em preto e branco.
- Figura de grafo grande é **agregada ou amostrada**, e a legenda diz o
  que foi feito.
- Rodar duas vezes produz a mesma figura (layout com seed fixa).

A figura 1 é gerada do Mermaid de
[`../arquitetura/diagrama-cap3.md`](../arquitetura/diagrama-cap3.md).
