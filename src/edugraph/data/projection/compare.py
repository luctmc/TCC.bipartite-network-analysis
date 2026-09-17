"""Comparação à mão × NetworkX  ``[A]`` — spec A-05.

Produz ``metrics/projections.csv``, uma das tabelas do capítulo 3:
para cada projeção, a discrepância máxima de peso entre as duas
implementações, o tempo de cada uma e o número de arestas.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.types import ProjectionBundle

#: Tolerância da comparação numérica. Acima disso, as implementações
#: divergem de verdade e a spec A-05 falha em vez de reportar.
TOLERANCE = 1e-9

#: Colunas de ``metrics/projections.csv``.
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


def compare(manual: ProjectionBundle, reference: ProjectionBundle) -> dict[str, Any]:
    """Compara duas projeções do mesmo bipartido e lado.

    Returns
    -------
    dict
        Uma linha no formato de :data:`METRICS_COLUMNS`.

    Notes
    -----
    A implementar em A-05: conferir que o conjunto de nós é idêntico,
    que o conjunto de arestas é idêntico, e calcular a maior diferença
    absoluta de peso. Arestas presentes em uma e não na outra são
    diferença de ``inf`` — não devem ser silenciadas.
    """
    raise NotImplementedError("A-05: ver docs/specs/frente-a/A-05-comparacao-projecao.md")


def weight_distribution(bundle: ProjectionBundle, bins: int = 20) -> dict[str, list[float]]:
    """Histograma dos pesos — insumo da figura "simples × ponderada" (A-05)."""
    raise NotImplementedError("A-05: figura da distribuição de pesos")
