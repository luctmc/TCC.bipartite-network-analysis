"""Projeções de referência via NetworkX  ``[A]`` — spec A-05.

Existem para serem comparadas com a implementação à mão, não para
substituí-la: a comparação (igualdade numérica, tempo, distribuição de
pesos) é o que demonstra domínio na banca e vira tabela do capítulo 3
(ADR-0010).

Qual função do NetworkX corresponde a quê
------------------------------------------
Verificado no NetworkX 3.6.1 (spec A-05 exigia conferir, não supor):

``weighted_projected_graph(B, nodes)``
    Peso = número de vizinhos em comum. **É** a projeção simples.

``collaboration_weighted_projected_graph(B, nodes)``
    Newman (2001): cada vizinho comum ``k`` contribui ``1/(grau(k) − 1)``.
    **Não é** a alocação de recursos de Zhou et al. (2007), que contribui
    ``1/grau(k)``. Em ``tiny_v1``, a disciplina DA (grau 4) contribui 1/3
    por Newman e 1/4 por Zhou — as duas divergem em toda aresta.

``generic_weighted_projected_graph(B, nodes, weight_function)``
    Deixa a fórmula por conta de quem chama. **Não há alocação de
    recursos pronta no NetworkX**; a referência aqui usa a máquina de
    projeção da biblioteca (interseção de vizinhanças, tratamento de nós
    e atributos) com a fórmula de Zhou fornecida por nós em
    :func:`resource_allocation_weight`. É o mais perto de "referência
    independente" que existe, e a diferença está registrada em
    ``docs/artigo/decisoes-metodologicas.md``.

Registradas em :data:`edugraph.contracts.registry.PROJECTIONS` sob
``networkx_simple`` e ``networkx_resource_allocation``.
"""

from __future__ import annotations

from typing import Any

import networkx as nx
from networkx.algorithms import bipartite as nx_bipartite

from edugraph.contracts.registry import PROJECTIONS
from edugraph.contracts.types import (
    BipartiteBundle,
    Meta,
    ProjectionBundle,
    ProjectionSpec,
)

#: Id da spec, gravado em ``meta.producer``.
PRODUCER = "A-05"


def resource_allocation_weight(graph: nx.Graph[Any], u: Any, v: Any) -> float:
    """Peso de Zhou et al. (2007) para ``generic_weighted_projected_graph``.

    Soma ``1/grau(k)`` sobre os vizinhos ``k`` comuns a ``u`` e ``v`` no
    bipartido. Assinatura exigida pelo NetworkX: ``(G, u, v)``.
    """
    return sum(1.0 / graph.degree(k) for k in set(graph[u]) & set(graph[v]))


def _side_nodes(bipartite: BipartiteBundle, spec: ProjectionSpec) -> list[str]:
    return sorted(n for n, d in bipartite.graph.nodes(data=True) if d.get("kind") == spec.side)


def _bundle(
    projected: nx.Graph[Any], bipartite: BipartiteBundle, spec: ProjectionSpec, note: str
) -> ProjectionBundle:
    """Normaliza a saída do NetworkX para o contrato.

    O NetworkX copia os atributos de nó do bipartido (só ``kind`` e
    ``label``, por construção) e grava ``weight`` como ``int`` na
    projeção simples; o contrato pede ``float``. O corte por
    ``min_weight`` é aplicado como na implementação à mão, para que a
    comparação seja justa.
    """
    graph: nx.Graph[Any] = nx.Graph()
    for node in sorted(projected.nodes):
        graph.add_node(node, kind=spec.side, label=bipartite.graph.nodes[node].get("label", node))
    for u, v, data in projected.edges(data=True):
        w = float(data.get("weight", 1.0))
        if spec.min_weight is not None and w < spec.min_weight:
            continue
        graph.add_edge(u, v, weight=w)

    meta = Meta(
        producer=PRODUCER,
        stats={
            "n_nodes": graph.number_of_nodes(),
            "n_edges": graph.number_of_edges(),
            "weighting": spec.weighting,
        },
        notes=note,
    )
    return ProjectionBundle(graph=graph, spec=spec, source=bipartite.spec, meta=meta)


class NetworkXSimpleProjection:
    """``nx.bipartite.weighted_projected_graph`` — equivale exatamente à simples.

    Satisfaz :class:`~edugraph.contracts.protocols.ProjectionAlgorithm`.
    """

    name = "networkx_simple"

    def project(self, bipartite: BipartiteBundle, spec: ProjectionSpec) -> ProjectionBundle:
        if spec.weighting != "simple":
            raise ValueError(
                f"{self.name} só projeta weighting='simple'; recebeu {spec.weighting!r}"
            )
        projected = nx_bipartite.weighted_projected_graph(
            bipartite.graph, _side_nodes(bipartite, spec)
        )
        return _bundle(
            projected,
            bipartite,
            spec,
            "Referência NetworkX: weighted_projected_graph (vizinhos em comum).",
        )


class NetworkXResourceAllocationProjection:
    """``generic_weighted_projected_graph`` com a fórmula de Zhou et al.

    Satisfaz :class:`~edugraph.contracts.protocols.ProjectionAlgorithm`.

    Não existe alocação de recursos pronta no NetworkX;
    ``collaboration_weighted_projected_graph`` é Newman (``1/(k−1)``), e
    **não** é equivalente. Ver o docstring do módulo.
    """

    name = "networkx_resource_allocation"

    def project(self, bipartite: BipartiteBundle, spec: ProjectionSpec) -> ProjectionBundle:
        if spec.weighting != "resource_allocation":
            raise ValueError(
                f"{self.name} só projeta weighting='resource_allocation'; "
                f"recebeu {spec.weighting!r}"
            )
        projected = nx_bipartite.generic_weighted_projected_graph(
            bipartite.graph,
            _side_nodes(bipartite, spec),
            weight_function=resource_allocation_weight,
        )
        return _bundle(
            projected,
            bipartite,
            spec,
            "Referência NetworkX: generic_weighted_projected_graph com a fórmula 1/grau(k) "
            "de Zhou et al. (2007). collaboration_weighted_projected_graph é Newman, "
            "1/(grau(k)-1), e não equivale.",
        )


def newman_collaboration_projection(
    bipartite: BipartiteBundle, spec: ProjectionSpec
) -> ProjectionBundle:
    """``collaboration_weighted_projected_graph`` — Newman (2001), para a comparação.

    Não é registrada como algoritmo do projeto: existe só para
    **demonstrar** que não equivale à alocação de recursos, o que a spec
    A-05 exige documentar em vez de assumir.
    """
    projected = nx_bipartite.collaboration_weighted_projected_graph(
        bipartite.graph, _side_nodes(bipartite, spec)
    )
    return _bundle(projected, bipartite, spec, "Newman (2001): 1/(grau(k)-1). Só para comparação.")


PROJECTIONS.register("networkx_simple", NetworkXSimpleProjection())
PROJECTIONS.register("networkx_resource_allocation", NetworkXResourceAllocationProjection())
