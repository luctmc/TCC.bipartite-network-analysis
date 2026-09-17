# `metrics/*.csv` — as tabelas do capítulo 3

**Produz:** todas as frentes · **Consome:** o artigo
**Código:** `edugraph.contracts.io.append_metrics_rows`
**Em disco:** `<root>/<dataset>/metrics/`

O briefing (§9) trata isto como requisito funcional: "todos os números
precisam sair em formato tabelável, porque viram tabelas do capítulo 3".

## As três tabelas

### `communities.csv` — a tabela principal (spec B-04)

Compara Louvain × Girvan-Newman × ponderação.

```
dataset,projection_id,algorithm,modularity,n_communities,
largest_community,runtime_s,status,params
```

Chave: `(dataset, projection_id, algorithm)`.

A coluna `status` é o que torna a comparação honesta: uma linha com
`timeout` não é comparável com uma `ok` em pé de igualdade, e omiti-la
seria esconder o resultado que a seção 8 do briefing manda reportar.

### `centrality_top.csv` — as disciplinas críticas (spec C-03)

```
dataset,projection_id,metric,rank,node_id,label,score
```

Chave: `(dataset, projection_id, metric, rank)`.

As linhas das projeções `discipline_*` são a **saída obrigatória** sobre
gargalos no fluxo curricular (briefing §6.2).

### `projections.csv` — à mão × NetworkX (spec A-05)

```
dataset,projection_id,n_nodes,n_edges_manual,n_edges_networkx,
max_abs_diff,runtime_manual_s,runtime_networkx_s,equal_within_tolerance
```

Chave: `(dataset, projection_id)`.

É a tabela que sustenta a afirmação de domínio do algoritmo (ADR-0010).

## Idempotência por chave

`append_metrics_rows` recebe a lista de colunas que formam a chave.
Rodar a mesma configuração de novo **atualiza** a linha em vez de
duplicá-la, e a saída fica ordenada pela chave.

Consequência: dá para acumular as métricas de várias execuções na mesma
tabela sem que a ordem dependa de quem rodou primeiro — o que importa
quando três pessoas geram linhas da mesma tabela em máquinas diferentes.

Mudar as colunas de uma tabela existente é erro de contrato, não merge
silencioso: a função recusa e manda subir `SCHEMA_VERSION`.

## De `metrics/` para o artigo

`metrics/` fica em `data/`, que é ignorado pelo git (exceto fixtures).
As tabelas **finais** são copiadas para `results/tables/`, que é
versionado, por `edugraph.reporting.tables.write_table`.

A separação é proposital: `metrics/` é rascunho de trabalho, reescrito a
cada rodada; `results/tables/` é o que foi para o texto, e tê-lo
versionado é o que permite comparar a tabela do rascunho com a da versão
final e explicar a diferença.
