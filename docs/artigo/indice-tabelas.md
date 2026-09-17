# Índice de tabelas

> **Arquivo gerado** a partir de `results/tables/`. Mesma regra do índice
> de figuras: não editar à mão.

Lista planejada, com a spec que produz cada tabela.

| # | Tabela | Spec | Fonte | Onde no artigo |
|---|---|---|---|---|
| 1 | Estatísticas do dataset | A-07 | `metrics/` | seção de dados |
| 2 | Projeção à mão × NetworkX | A-05 | `metrics/projections.csv` | seção de projeção |
| 3 | **Louvain × Girvan-Newman × ponderação** | B-04 | `metrics/communities.csv` | **tabela principal** |
| 4 | Perfil das comunidades | B-05 | `communities/*/profile.csv` | comunidades |
| 5 | Validação: NMI, pureza, desfecho por comunidade | B-06 | — | validação |
| 6 | Disciplinas críticas por métrica | C-03 | `metrics/centrality_top.csv` | disciplinas críticas |
| 7 | Discordância entre métricas | C-03 | — | discussão |
| 8 | Reprovação nas disciplinas críticas × base | C-06 | — | validação |
| 9 | Tamanhos por recorte de escala | A-06 | — | limitações |

## Regras

- `metrics/` é **rascunho de trabalho**, reescrito a cada rodada;
  `results/tables/` é o que foi para o texto, e é versionado. Ter as duas
  coisas separadas é o que permite comparar a tabela do rascunho com a da
  versão final e explicar a diferença.
- Toda tabela carrega as colunas que identificam a configuração
  (`dataset`, `projection_id`, `algorithm`) — senão a linha não é
  reproduzível.
- A tabela 3 traz a coluna `status`: uma execução que estourou o
  orçamento entra na comparação **com o status visível** (ADR-0006).
- Números com o mesmo número de casas decimais dentro de uma coluna.
- Ao reportar o número de comunidades, **dizer quantas são unitárias**.
