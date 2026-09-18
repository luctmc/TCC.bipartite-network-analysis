"""Comparação à mão × NetworkX  ``[A]`` — spec A-05.

Produz ``metrics/projections.csv``, uma das tabelas do capítulo 3:
para cada projeção, a discrepância máxima de peso entre as duas
implementações, o tempo de cada uma e o número de arestas.

A comparação é o melhor teste possível da implementação à mão: uma
divergência acima da tolerância aponta bug real, e uma aresta presente
em uma e ausente na outra é diferença **infinita** — nunca silenciada.
"""

from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any

import numpy as np

from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.protocols import ProjectionAlgorithm
from edugraph.contracts.registry import PROJECTIONS
from edugraph.contracts.types import BipartiteBundle, ProjectionBundle, ProjectionSpec

#: Tolerância da comparação numérica. Acima disso, as implementações
#: divergem de verdade e a spec A-05 falha em vez de reportar.
TOLERANCE = 1e-9

#: Colunas de ``metrics/projections.csv`` (ver docs/contratos/metrics.md).
METRICS_COLUMNS: tuple[str, ...] = (
    "dataset",
    "projection_id",
    "n_nodes",
    "n_edges_manual",
    "n_edges_networkx",
    "max_abs_diff",
    "runtime_manual_s",
    "runtime_networkx_s",
    "equal_within_tolerance",
)

#: Chave de idempotência da tabela: rodar de novo atualiza a linha.
METRICS_KEY: tuple[str, ...] = ("dataset", "projection_id")


def _edge_weights(bundle: ProjectionBundle) -> dict[tuple[str, str], float]:
    return {(min(u, v), max(u, v)): float(d["weight"]) for u, v, d in bundle.graph.edges(data=True)}


def compare(
    manual: ProjectionBundle,
    reference: ProjectionBundle,
    *,
    runtime_manual_s: float = math.nan,
    runtime_networkx_s: float = math.nan,
) -> dict[str, Any]:
    """Compara duas projeções do mesmo bipartido e lado.

    Returns
    -------
    dict
        Uma linha no formato de :data:`METRICS_COLUMNS`.

    Raises
    ------
    ContractError
        Se as projeções não forem do mesmo lado ou da mesma fonte — aí
        não há o que comparar, e reportar um número seria enganoso.

    Notes
    -----
    ``max_abs_diff`` é ``inf`` quando o conjunto de nós ou de arestas
    difere. Arestas presentes em uma e ausentes na outra não podem ser
    tratadas como "peso zero": seriam um erro de algoritmo disfarçado de
    diferença numérica pequena.
    """
    if manual.spec.side != reference.spec.side or manual.spec.weighting != reference.spec.weighting:
        raise ContractError(
            f"projeções incomparáveis: {manual.spec.projection_id!r} × "
            f"{reference.spec.projection_id!r}"
        )
    if manual.source.dataset != reference.source.dataset:
        raise ContractError(
            f"projeções de datasets diferentes: {manual.source.dataset!r} × "
            f"{reference.source.dataset!r}"
        )

    wm, wr = _edge_weights(manual), _edge_weights(reference)
    same_nodes = set(manual.graph.nodes) == set(reference.graph.nodes)
    same_edges = wm.keys() == wr.keys()

    if same_nodes and same_edges:
        max_abs_diff = max((abs(wm[e] - wr[e]) for e in wm), default=0.0)
    else:
        max_abs_diff = math.inf

    return {
        "dataset": manual.source.dataset,
        "projection_id": manual.spec.projection_id,
        "n_nodes": manual.graph.number_of_nodes(),
        "n_edges_manual": manual.graph.number_of_edges(),
        "n_edges_networkx": reference.graph.number_of_edges(),
        "max_abs_diff": max_abs_diff,
        "runtime_manual_s": runtime_manual_s,
        "runtime_networkx_s": runtime_networkx_s,
        "equal_within_tolerance": bool(math.isfinite(max_abs_diff) and max_abs_diff < TOLERANCE),
    }


def time_projection(
    algorithm: ProjectionAlgorithm, bipartite: BipartiteBundle, spec: ProjectionSpec
) -> tuple[ProjectionBundle, float]:
    """Projeta e mede o tempo de parede, em segundos."""
    start = time.perf_counter()
    bundle = algorithm.project(bipartite, spec)
    return bundle, time.perf_counter() - start


def compare_implementations(bipartite: BipartiteBundle, spec: ProjectionSpec) -> dict[str, Any]:
    """Roda a implementação à mão e a de referência e devolve a linha da tabela.

    Resolve as duas no registro por ``manual_<weighting>`` e
    ``networkx_<weighting>``; ``spec.implementation`` é ignorada, porque
    aqui as duas rodam por definição.
    """
    from edugraph.data.projection import manual, networkx_ref  # noqa: F401  (registro)

    manual_algo = PROJECTIONS.get(f"manual_{spec.weighting}")
    reference_algo = PROJECTIONS.get(f"networkx_{spec.weighting}")

    m_bundle, m_time = time_projection(manual_algo, bipartite, spec)  # type: ignore[arg-type]
    r_bundle, r_time = time_projection(reference_algo, bipartite, spec)  # type: ignore[arg-type]
    return compare(m_bundle, r_bundle, runtime_manual_s=m_time, runtime_networkx_s=r_time)


def compare_all(bipartite: BipartiteBundle) -> list[dict[str, Any]]:
    """As quatro projeções (dois lados × duas ponderações), uma linha cada."""
    rows = []
    for side in ("student", "discipline"):
        for weighting in ("simple", "resource_allocation"):
            spec = ProjectionSpec(side=side, weighting=weighting)  # type: ignore[arg-type]
            rows.append(compare_implementations(bipartite, spec))
    return rows


def write_metrics(rows: list[dict[str, Any]], out_root: str | Path, dataset: str) -> Path:
    """Grava/atualiza ``metrics/projections.csv`` (idempotente por :data:`METRICS_KEY`)."""
    ordered = [{col: row[col] for col in METRICS_COLUMNS} for row in rows]
    return io.append_metrics_rows(out_root, dataset, "projections", ordered, key=list(METRICS_KEY))


def weight_distribution(bundle: ProjectionBundle, bins: int = 20) -> dict[str, list[float]]:
    """Histograma dos pesos — insumo da figura "simples × ponderada" (A-05).

    Returns
    -------
    dict
        ``bin_edges`` (``bins + 1`` valores) e ``counts`` (``bins``
        valores), com ``sum(counts) == n_edges``.
    """
    weights = np.fromiter(
        (float(d["weight"]) for _, _, d in bundle.graph.edges(data=True)), dtype=float
    )
    if weights.size == 0:
        return {"bin_edges": [0.0, 1.0], "counts": [0.0]}
    counts, edges = np.histogram(weights, bins=bins)
    return {"bin_edges": edges.tolist(), "counts": counts.astype(float).tolist()}
