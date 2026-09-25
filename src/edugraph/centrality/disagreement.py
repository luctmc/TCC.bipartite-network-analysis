"""Discordância entre métricas de centralidade  ``[C]`` — spec C-03.

Onde as três métricas discordam é onde há o que discutir: um nó no topo
da intermediação mas não do grau é ponte sem ser popular — exatamente o
perfil de uma disciplina-gargalo que poucos cursam mas que conecta áreas.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import rankdata

from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import CentralityResult

#: As três métricas que a discordância compara.
METRICS: tuple[str, ...] = ("degree", "betweenness", "eigenvector")


def disagreement(results: dict[str, CentralityResult], *, top_n: int = 5) -> dict[str, list[str]]:
    """Os quatro conjuntos de discordância entre as três métricas.

    O top-N de cada métrica usa o mesmo desempate por id do ranking, para
    que os conjuntos batam com a tabela de disciplinas críticas.

    Returns
    -------
    dict
        ``only_degree``, ``only_betweenness``, ``only_eigenvector`` e
        ``all_three`` — nós no top-N de apenas uma métrica, e nós no
        top-N das três. Listas ordenadas, para a tabela ser estável.
    """
    missing = [m for m in METRICS if m not in results]
    if missing:
        raise ContractError(
            f"discordância: faltam as métricas {missing}; ela compara as três "
            "(rode `centrality all` antes)"
        )

    tops = {metric: {node for node, _ in results[metric].top(top_n)} for metric in METRICS}
    out: dict[str, list[str]] = {}
    for metric in METRICS:
        others = set().union(*(tops[m] for m in METRICS if m != metric))
        out[f"only_{metric}"] = sorted(tops[metric] - others)
    out["all_three"] = sorted(set.intersection(*tops.values()))
    return out


def rank_correlation(left: CentralityResult, right: CentralityResult) -> float:
    """Correlação de Spearman entre dois rankings.

    Quantifica em um número o que os conjuntos de discordância mostram
    caso a caso. Estatística descritiva sobre rankings conhecidos — não
    é modelo nem predição.

    Empates recebem o posto médio, e o coeficiente é o de Pearson sobre
    os postos. Se um dos rankings for todo empatado (K₇), a correlação
    não existe e o resultado é ``nan`` — em vez de um número inventado.
    """
    if set(left.scores) != set(right.scores):
        raise ContractError(
            "correlação de postos: os dois resultados não cobrem os mesmos nós "
            f"({left.projection_id}/{left.metric} × {right.projection_id}/{right.metric})"
        )
    nodes = sorted(left.scores)
    x = rankdata([left.scores[n] for n in nodes])
    y = rankdata([right.scores[n] for n in nodes])
    x, y = x - x.mean(), y - y.mean()
    denominator = math.sqrt(float(np.dot(x, x)) * float(np.dot(y, y)))
    if denominator == 0.0:
        return math.nan
    return float(np.dot(x, y)) / denominator


#: Colunas da tabela de discordância (tabela 7 do artigo).
DISAGREEMENT_COLUMNS: tuple[str, ...] = ("dataset", "projection_id", "comparison", "top_n", "value")

#: Os três pares de métricas da correlação de postos.
PAIRS: tuple[tuple[str, str], ...] = (
    ("degree", "betweenness"),
    ("degree", "eigenvector"),
    ("betweenness", "eigenvector"),
)


def disagreement_rows(
    results: dict[str, CentralityResult],
    *,
    top_n: int = 5,
    dataset: str = "",
    labels: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    """Os quatro conjuntos e as três correlações, no formato da tabela.

    Nos conjuntos, ``value`` é a lista de rótulos separada por ``"; "``
    (vazia quando o conjunto é vazio); nas correlações, é o Spearman —
    ``nan`` quando um ranking é todo empatado.
    """
    names = labels or {}
    projection_id = next(iter(results.values())).projection_id
    base = {"dataset": dataset, "projection_id": projection_id, "top_n": top_n}

    rows: list[dict[str, object]] = [
        {**base, "comparison": name, "value": "; ".join(names.get(n, n) for n in nodes)}
        for name, nodes in disagreement(results, top_n=top_n).items()
    ]
    rows.extend(
        {
            **base,
            "comparison": f"spearman_{a}_{b}",
            "value": rank_correlation(results[a], results[b]),
        }
        for a, b in PAIRS
    )
    return [{column: row[column] for column in DISAGREEMENT_COLUMNS} for row in rows]
