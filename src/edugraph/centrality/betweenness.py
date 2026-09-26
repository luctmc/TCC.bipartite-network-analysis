"""Centralidade de intermediação  ``[C]`` — spec C-01.

Fração dos caminhos mínimos que passam por um nó. É a métrica que o
objetivo declarado na Introdução associa a "gargalos no fluxo
educacional": uma disciplina de alta intermediação liga partes do
currículo que, sem ela, ficariam distantes.

Via ``nx.betweenness_centrality``, que usa Brandes (2001) internamente.
Não é implementada à mão: o custo didático é alto e o retorno baixo
perto das outras duas implementações manuais do projeto (ADR-0010).

**Cuidado com o peso.** Em NetworkX, ``weight`` num caminho mínimo é
*distância*, não afinidade: peso alto vira caminho longo. Como nas
projeções peso alto significa *mais* afinidade, rodar com
``weight="weight"`` inverteria a semântica. Por isso o padrão é
``weight_mode="none"`` (caminho mínimo em saltos), com ``"inverse"``
(distância ``1/w``) disponível para a análise de sensibilidade. A decisão
e o porquê estão em ``docs/artigo/decisoes-metodologicas.md``.
"""

from __future__ import annotations

import time
from typing import Any, Literal

import networkx as nx

from edugraph.centrality._params import check_params
from edugraph.contracts.errors import ContractError
from edugraph.contracts.registry import CENTRALITIES
from edugraph.contracts.types import CentralityResult, Meta, ProjectionBundle

#: Id da spec, gravado em ``meta.producer`` de todo artefato daqui.
PRODUCER = "C-01"

WeightMode = Literal["none", "inverse", "raw"]
WEIGHT_MODES: tuple[str, ...] = ("none", "inverse", "raw")

#: Decisão da C-01: caminho mínimo em saltos (ver o docstring do módulo).
DEFAULT_WEIGHT_MODE: WeightMode = "none"

#: Semente da amostragem de pivôs quando ``k`` vem sem ``seed``.
DEFAULT_SEED = 42

ACCEPTED_PARAMS: tuple[str, ...] = ("normalized", "weight_mode", "k", "seed")

#: Atributo temporário com a distância ``1/w`` no modo ``inverse``.
_DISTANCE = "_distance"


def _distance_graph(graph: nx.Graph[Any], weight_mode: str) -> tuple[nx.Graph[Any], str | None]:
    """Grafo e atributo de distância que o Brandes deve usar.

    No modo ``inverse`` trabalha sobre uma cópia: a projeção recebida não
    pode sair daqui com um atributo a mais.
    """
    if weight_mode == "none":
        return graph, None
    if weight_mode == "raw":
        return graph, "weight"
    copy = graph.copy()
    for _, _, data in copy.edges(data=True):
        data[_DISTANCE] = 1.0 / float(data["weight"])
    return copy, _DISTANCE


class BetweennessCentrality:
    """Satisfaz :class:`~edugraph.contracts.protocols.CentralityMetric`.

    Parameters aceitos em ``compute``:

    ``normalized`` : bool
        Padrão ``True``.
    ``weight_mode`` : {"none", "inverse", "raw"}
        Como tratar o peso da projeção como distância. Vai para
        ``params`` e para a legenda da tabela, porque muda o ranking.
    ``k`` : int | None
        Amostragem de pivôs para grafos grandes; com ``seed``, é
        determinística. Estimativa, e a tabela precisa dizer isso.
    ``seed`` : int
        Semente da amostragem; só é usada (e gravada) quando há ``k``.
    """

    name = "betweenness"

    def compute(self, projection: ProjectionBundle, **params: Any) -> CentralityResult:
        """Intermediação de cada nó da projeção.

        Raises
        ------
        ContractError
            Se a projeção estiver vazia, se ``weight_mode`` não for um dos
            três do contrato, ou se vier parâmetro desconhecido.
        """
        check_params(params, ACCEPTED_PARAMS, "BetweennessCentrality.compute")
        normalized = bool(params.get("normalized", True))
        weight_mode = str(params.get("weight_mode", DEFAULT_WEIGHT_MODE))
        if weight_mode not in WEIGHT_MODES:
            raise ContractError(
                f"intermediação: weight_mode={weight_mode!r} não existe; use um de {WEIGHT_MODES}"
            )

        graph = projection.graph
        n = graph.number_of_nodes()
        if n == 0:
            raise ContractError(
                f"intermediação: projeção {projection.projection_id!r} não tem nós; "
                "não há o que medir"
            )

        # k >= n não é amostra: é o cálculo exato com mais passos. Tratar
        # como exato evita declarar estimativa onde não há.
        k_param = params.get("k")
        if k_param is not None and int(k_param) < 1:
            raise ContractError(f"intermediação: k precisa ser >= 1; recebeu {k_param!r}")
        k = int(k_param) if k_param is not None and int(k_param) < n else None
        seed = int(params.get("seed", DEFAULT_SEED)) if k is not None else None

        work, distance = _distance_graph(graph, weight_mode)
        start = time.perf_counter()
        raw = nx.betweenness_centrality(
            work, k=k, normalized=normalized, weight=distance, seed=seed
        )
        runtime_s = time.perf_counter() - start

        # A amostragem de pivôs pode estourar 1,0 por uma fração mínima
        # (a estimativa é reescalada por n/k); o contrato exige [0, 1].
        scores = {str(node): float(score) for node, score in raw.items()}
        if normalized and k is not None:
            scores = {node: min(max(score, 0.0), 1.0) for node, score in scores.items()}

        result_params: dict[str, Any] = {
            "normalized": normalized,
            "weight_mode": weight_mode,
            "k": k,
            "estimate": k is not None,
        }
        if seed is not None:
            result_params["seed"] = seed

        return CentralityResult(
            projection_id=projection.projection_id,
            metric="betweenness",
            scores=scores,
            params=result_params,
            runtime_s=runtime_s,
            converged=True,
            meta=Meta(
                producer=PRODUCER,
                stats={"n_nodes": n, "n_edges": graph.number_of_edges()},
                notes=(
                    "Brandes (2001) por nx.betweenness_centrality"
                    + (f"; estimativa com {k} pivôs amostrados." if k is not None else ", exata.")
                ),
            ),
        )


CENTRALITIES.register("betweenness", BetweennessCentrality())
