"""Centralidade de grau  ``[C]`` — spec C-01.

A mais simples das três e a linha de base contra a qual as outras duas
são lidas: um nó pode ter grau alto e intermediação baixa (popular, mas
não ponte), e é dessa discordância que sai a discussão da spec C-03.

Duas variantes, ambas registradas: ``degree`` (contagem de vizinhos,
normalizada por n−1) e a força ponderada, que soma os pesos. A força
normalizada divide pela maior força do grafo — não há um "n−1" natural
para pesos —, e essa escolha fica em ``params.normalization``.
"""

from __future__ import annotations

import time
from typing import Any

import networkx as nx

from edugraph.centrality._params import check_params
from edugraph.contracts.errors import ContractError
from edugraph.contracts.registry import CENTRALITIES
from edugraph.contracts.types import CentralityResult, Meta, ProjectionBundle

#: Id da spec, gravado em ``meta.producer`` de todo artefato daqui.
PRODUCER = "C-01"

ACCEPTED_PARAMS: tuple[str, ...] = ("normalized", "weight")


def _count(graph: nx.Graph[Any], normalized: bool) -> tuple[dict[str, float], str]:
    """Número de vizinhos, opcionalmente dividido por n−1."""
    if normalized:
        # nx.degree_centrality já divide por n−1 (e devolve 1,0 para n=1).
        return {str(n): float(s) for n, s in nx.degree_centrality(graph).items()}, "n_minus_1"
    return {str(n): float(d) for n, d in graph.degree()}, "none"


def _strength(graph: nx.Graph[Any], weight: str, normalized: bool) -> tuple[dict[str, float], str]:
    """Soma dos pesos, opcionalmente dividida pela maior força."""
    strength = {str(n): float(d) for n, d in graph.degree(weight=weight)}
    if not normalized:
        return strength, "none"
    largest = max(strength.values(), default=0.0)
    if largest == 0.0:
        # Só nós isolados: força zero em todos, e dividir por zero não
        # diria nada a mais do que o próprio zero.
        return strength, "max_strength"
    return {n: s / largest for n, s in strength.items()}, "max_strength"


class DegreeCentrality:
    """Satisfaz :class:`~edugraph.contracts.protocols.CentralityMetric`.

    Parameters aceitos em ``compute``:

    ``normalized`` : bool
        Divide por n−1. Padrão ``True`` — o validador de contrato exige
        scores em [0, 1] quando este parâmetro é verdadeiro.
    ``weight`` : str | None
        ``"weight"`` para a força ponderada, ``None`` para a contagem.
    """

    name = "degree"

    def compute(self, projection: ProjectionBundle, **params: Any) -> CentralityResult:
        """Grau (ou força) de cada nó da projeção.

        Raises
        ------
        ContractError
            Se a projeção estiver vazia ou vier parâmetro desconhecido.
        """
        check_params(params, ACCEPTED_PARAMS, "DegreeCentrality.compute")
        normalized = bool(params.get("normalized", True))
        weight = params.get("weight")

        graph = projection.graph
        if graph.number_of_nodes() == 0:
            raise ContractError(
                f"grau: projeção {projection.projection_id!r} não tem nós; não há o que medir"
            )

        start = time.perf_counter()
        if weight is None:
            scores, normalization = _count(graph, normalized)
        else:
            scores, normalization = _strength(graph, str(weight), normalized)
        runtime_s = time.perf_counter() - start

        return CentralityResult(
            projection_id=projection.projection_id,
            metric="degree",
            scores=scores,
            params={
                "normalized": normalized,
                "weight": weight,
                "normalization": normalization,
            },
            runtime_s=runtime_s,
            converged=True,
            meta=Meta(
                producer=PRODUCER,
                stats={
                    "n_nodes": graph.number_of_nodes(),
                    "n_edges": graph.number_of_edges(),
                },
                notes=(
                    "Contagem de vizinhos por nx.degree_centrality."
                    if weight is None
                    else "Força ponderada: soma dos pesos, normalizada pela maior força."
                ),
            ),
        )


CENTRALITIES.register("degree", DegreeCentrality())
