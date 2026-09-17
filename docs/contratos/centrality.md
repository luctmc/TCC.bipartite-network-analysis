# `CentralityResult` — uma métrica de centralidade sobre uma projeção

**Produz:** `[C]` (specs C-01 e C-02) · **Consome:** `[C]` API e front
**Código:** `edugraph.contracts.types.CentralityResult`
**Em disco:** `<root>/<dataset>/centrality/<projection_id>/<metric>.csv`

Um artefato por (projeção, métrica). Três métricas: `degree`,
`betweenness`, `eigenvector`.

## Tipo

```python
@dataclass
class CentralityResult:
    projection_id: str
    metric: Literal["degree", "betweenness", "eigenvector"]
    scores: dict[str, float]
    params: dict[str, Any]  # normalized, weight, max_iter, tol, implementation
    runtime_s: float
    converged: bool
    meta: Meta
```

## `converged` e o fallback

A iteração de potência pode não convergir em grafo desconexo — e a
projeção aluno↔aluno do OULAD tende a ser desconexa. O contrato exige
que isso vire `converged=False` no artefato e queda para o cálculo direto
por autovalores, **nunca uma exceção** que derrube o pipeline.

O valor vira nota de rodapé do artigo: um ranking obtido por fallback
merece ser declarado como tal.

## `params` muda o ranking, então entra no artefato

**Cuidado com o peso na intermediação.** Em NetworkX, `weight` num
caminho mínimo é **distância**: peso alto vira caminho longo. Mas nas
projeções peso alto significa *mais* afinidade, ou seja, distância
*menor*. Passar `weight="weight"` direto inverte a semântica.

A spec C-01 precisa decidir e registrar em `params.weight_mode`:

| `weight_mode` | O que faz |
|---|---|
| `none` | ignora o peso; é o que as fixtures usam |
| `inverse` | usa `1/w` como distância — coerente com a semântica de afinidade |
| `raw` | usa `w` como distância; só faz sentido se o peso for mesmo custo |

As fixtures usam `none` de propósito: não antecipam a decisão, apenas
registram a escolha. Qualquer que seja a decisão, ela vira legenda de
tabela, porque muda o ranking.

## Em disco

`<metric>.csv`:

```csv
node_id,score
DAAA,1.0
DBBB,1.0
```

`<metric>.meta.json` traz `projection_id`, `metric`, `params`,
`runtime_s` e `converged`.

## Invariantes

`validate_centrality` recusa se:

- `scores` estiver vazio;
- algum valor não for finito;
- `degree` ou `betweenness` estiverem fora de `[0, 1]` com
  `params.normalized=True` — o sintoma clássico de normalização errada;
- o autovetor tiver componente negativa. Por Perron-Frobenius o autovetor
  principal de um grafo conexo é não negativo; uma componente negativa
  costuma ser sinal trocado na normalização, não resultado.

Com a projeção passada junto, recusa também se as chaves não forem
exatamente o conjunto de nós dela.

## Empates são o caso normal, não a exceção

Na projeção disciplina↔disciplina de `synthetic_v1` — que é o grafo
completo K₇ — **todos** os nós empatam: grau 1,0, intermediação 0,0. Isso
não é bug, é a degeneração da decisão D1.

Consequência prática: `CentralityResult.top()` desempata por `node_id`, e
a spec C-03 precisa fazer o mesmo. Sem desempate determinístico, a tabela
do artigo muda de uma execução para outra sem que nenhum dado tenha
mudado.
