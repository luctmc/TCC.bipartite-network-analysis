"""Projeções implementadas à mão  ``[A]`` — spec A-04.

Esta é a implementação que o artigo exige (seção 7 do briefing: "pelo
menos um algoritmo implementado à mão"). Ela é comparada com a do
NetworkX na spec A-05, e a comparação vira tabela do capítulo 3.

O algoritmo
-----------
Seja G = (U ∪ V, E) o bipartido e S o lado a projetar (alunos ou
disciplinas). Para cada nó ``k`` do lado **oposto**, todo par ``(i, j)``
de vizinhos de ``k`` em S ganha uma contribuição ``c(k)`` no peso da
aresta ``i—j`` da projeção:

- **simples**: ``c(k) = 1`` — o peso final é o número de vizinhos em
  comum, a diagonal externa de ``B · Bᵀ``;
- **alocação de recursos** (Zhou et al., 2007): ``c(k) = 1 / grau(k)`` —
  um nó compartilhado por muita gente discrimina pouco e pesa menos.

O percurso é pelos nós do lado oposto, acumulando pares num dicionário:
custo ``Σ_k C(grau(k), 2)``, que é o número de arestas da projeção — e
não ``|S|²``, como seria montar a matriz densa. No OULAD, ``|S|`` chega a
dezenas de milhares de alunos; a matriz não cabe, o dicionário cabe.

Registradas em :data:`edugraph.contracts.registry.PROJECTIONS` sob
``manual_simple`` e ``manual_resource_allocation``.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable
from typing import Any

import networkx as nx

from edugraph.contracts.registry import PROJECTIONS
from edugraph.contracts.types import (
    BipartiteBundle,
    Meta,
    ProjectionBundle,
    ProjectionSpec,
)

#: Id da spec, gravado em ``meta.producer`` de todo artefato daqui.
PRODUCER = "A-04"

#: Função de contribuição: recebe o grau do nó compartilhado no
#: bipartido e devolve quanto ele soma ao peso de cada par de vizinhos.
Contribution = Callable[[int], float]


def _project(
    bipartite: BipartiteBundle, spec: ProjectionSpec, contribution: Contribution
) -> ProjectionBundle:
    """Núcleo comum às duas ponderações.

    Separado para que a diferença entre elas fique reduzida ao que ela
    de fato é — a função de contribuição — e para que o artigo possa
    descrever um único algoritmo com dois pesos.
    """
    graph = bipartite.graph
    side = spec.side

    # Nós do lado projetado, em ordem canônica: são todos os nós da
    # projeção, inclusive os que não compartilham vizinho com ninguém —
    # um aluno isolado continua existindo, só não tem aresta.
    side_nodes = sorted(n for n, d in graph.nodes(data=True) if d.get("kind") == side)
    side_set = set(side_nodes)

    # Acumulador de pesos por par, com a chave ordenada para que (i, j) e
    # (j, i) caiam na mesma entrada. É o que substitui a matriz densa.
    weights: dict[tuple[str, str], float] = {}
    n_shared_used = 0

    for shared in graph.nodes:
        if shared in side_set:
            continue
        neighbors = sorted(n for n in graph.neighbors(shared) if n in side_set)
        if len(neighbors) < 2:
            continue  # sem par, sem contribuição
        n_shared_used += 1
        c = contribution(graph.degree(shared))
        for left, right in itertools.combinations(neighbors, 2):
            weights[left, right] = weights.get((left, right), 0.0) + c

    # Corte por peso mínimo, quando declarado na spec. A estratégia de
    # escala completa é a A-06; aqui só se honra o contrato, para que
    # um ProjectionSpec com min_weight nunca produza artefato inválido.
    if spec.min_weight is not None:
        weights = {pair: w for pair, w in weights.items() if w >= spec.min_weight}

    projected: nx.Graph[Any] = nx.Graph()
    for node in side_nodes:
        projected.add_node(node, kind=side, label=graph.nodes[node].get("label", node))
    for (left, right), w in weights.items():
        projected.add_edge(left, right, weight=w)

    meta = Meta(
        producer=PRODUCER,
        stats={
            "n_nodes": projected.number_of_nodes(),
            "n_edges": projected.number_of_edges(),
            "n_shared_nodes_used": n_shared_used,
            "weighting": spec.weighting,
        },
        notes="Projeção implementada à mão (ADR-0010); referência NetworkX na spec A-05.",
    )
    return ProjectionBundle(graph=projected, spec=spec, source=bipartite.spec, meta=meta)


class SimpleProjection:
    """Peso da aresta = número de vizinhos compartilhados.

    Satisfaz :class:`~edugraph.contracts.protocols.ProjectionAlgorithm`.

    Equivale à diagonal externa de ``B · Bᵀ``, sem montar ``B``. É a
    ponderação enviesada a favor de nós de alto grau: uma disciplina
    obrigatória cursada por todo mundo aproxima todo mundo de todo mundo.
    """

    name = "manual_simple"

    def project(self, bipartite: BipartiteBundle, spec: ProjectionSpec) -> ProjectionBundle:
        if spec.weighting != "simple":
            raise ValueError(
                f"{self.name} só projeta weighting='simple'; recebeu {spec.weighting!r}"
            )
        return _project(bipartite, spec, lambda _degree: 1.0)


class ResourceAllocationProjection:
    """Alocação de recursos (Zhou et al., 2007).

    Satisfaz :class:`~edugraph.contracts.protocols.ProjectionAlgorithm`.

    Cada vizinho comum ``k`` contribui com ``1/grau(k)`` para o peso do
    par. Corrige o viés da projeção simples: em ``tiny_v1``, os pares
    S1-S6 e S3-S4 empatam em 1 na simples, mas aqui ficam 1/4 e 1/3 —
    a disciplina rara discrimina mais que a popular.
    """

    name = "manual_resource_allocation"

    def project(self, bipartite: BipartiteBundle, spec: ProjectionSpec) -> ProjectionBundle:
        if spec.weighting != "resource_allocation":
            raise ValueError(
                f"{self.name} só projeta weighting='resource_allocation'; "
                f"recebeu {spec.weighting!r}"
            )
        return _project(bipartite, spec, lambda degree: 1.0 / degree)


PROJECTIONS.register("manual_simple", SimpleProjection())
PROJECTIONS.register("manual_resource_allocation", ResourceAllocationProjection())
