# `Partition` — a partição de comunidades

**Produz:** `[B]` (specs B-01 e B-02) · **Consome:** `[C]` API e front
**Código:** `edugraph.contracts.types.Partition`
**Em disco:** `<root>/<dataset>/communities/<algorithm>__<projection_id>/`

## Tipo

```python
@dataclass
class Partition:
    algorithm: Literal["louvain", "girvan_newman"]
    projection_id: str
    membership: dict[str, int]  # nó → comunidade, ids densos 0..k-1
    modularity: float
    n_communities: int
    runtime_s: float
    params: dict[str, Any]  # seed, resolution, time_budget_s, sample…
    status: Literal["ok", "timeout", "skipped"]
    meta: Meta
```

## `status` não é detalhe

É o campo que transforma "o Girvan-Newman não terminou" de falha de
execução em **resultado do capítulo 3** (ADR-0006).

| `status` | Significa |
|---|---|
| `ok` | rodou até o critério de parada |
| `timeout` | estourou `time_budget_s`; `membership` traz a melhor partição vista até ali |
| `skipped` | nem o primeiro corte coube no orçamento; partição trivial, Q = 0 |

**O contrato proíbe levantar exceção por estouro de orçamento.** Uma
linha com `status="timeout"` entra na tabela comparativa como qualquer
outra — com a coluna `status` ao lado, para que a comparação não pareça
mais limpa do que é.

## `params` é o que o artigo cita

Tudo o que muda o resultado vai para `params`: `seed`, `resolution`,
`time_budget_s`, `sample_nodes`, `implementation`. Sem isso, uma linha da
tabela do capítulo 3 não é reproduzível, e a rastreabilidade exigida pelo
briefing §9 se perde.

## Em disco

`membership.csv`:

```csv
node_id,community
S100001,0
S100002,1
```

`profile.csv` — a caracterização da spec B-05, **saída obrigatória** do
TCC. Descrita em [`characterize`](../specs/frente-b/B-05-caracterizacao.md);
colunas em `PROFILE_COLUMNS`.

`meta.json` traz `algorithm`, `projection_id`, `modularity`,
`n_communities`, `runtime_s`, `status` e `params`.

## Invariantes

`validate_partition` recusa se:

- `membership` estiver vazio;
- os ids de comunidade **não forem densos `0..k-1`** — a biblioteca não
  garante isso, e `modularity.densify` existe para corrigir;
- `n_communities` não bater com o número de comunidades presentes;
- `modularity` estiver fora de `[-0,5, 1]`;
- `runtime_s` for negativo ou não finito.

Quando a projeção é passada junto (é o que os testes de contrato fazem),
recusa também se as chaves de `membership` não forem **exatamente** o
conjunto de nós dela. É esse cruzamento que impede uma partição de uma
projeção ser servida como se fosse de outra.

## Nota sobre comunidades unitárias

O starter kit relata ~25 comunidades em `synthetic_v1`; a fixture tem 3.
A diferença são nós isolados, cada um virando comunidade de tamanho 1 —
que aqui não existem, porque o bipartido já os removeu. Ao reportar `k`
no artigo, vale dizer quantas comunidades são unitárias: um `k` alto
composto de singletons diz algo muito diferente de um `k` alto de grupos
reais.
