"""Projeções implementadas à mão  ``[A]`` — spec A-04.

Esta é a implementação que o artigo exige (seção 7 do briefing: "pelo
menos um algoritmo implementado à mão"). Ela é comparada com a do
NetworkX na spec A-05, e a comparação vira tabela do capítulo 3.

Registradas em :data:`edugraph.contracts.registry.PROJECTIONS` sob
``manual_simple`` e ``manual_resource_allocation``.
"""

from __future__ import annotations

from edugraph.contracts.registry import PROJECTIONS
from edugraph.contracts.types import BipartiteBundle, ProjectionBundle, ProjectionSpec


class SimpleProjection:
    """Peso da aresta = número de vizinhos compartilhados.

    Satisfaz :class:`~edugraph.contracts.protocols.ProjectionAlgorithm`.

    Equivale à diagonal externa de ``B · Bᵀ``. Implementar em A-04
    percorrendo os nós do lado oposto e acumulando pares — não montar a
    matriz densa, que no OULAD não cabe em memória.
    """

    name = "manual_simple"

    def project(self, bipartite: BipartiteBundle, spec: ProjectionSpec) -> ProjectionBundle:
        raise NotImplementedError("A-04: ver docs/specs/frente-a/A-04-projecoes-manuais.md")


class ResourceAllocationProjection:
    """Alocação de recursos (Zhou et al., 2007).

    Satisfaz :class:`~edugraph.contracts.protocols.ProjectionAlgorithm`.

    Cada vizinho comum ``k`` contribui com ``1/grau(k)`` para o peso do
    par. Corrige o viés da projeção simples a favor de nós de alto grau,
    que é exatamente o problema de uma disciplina obrigatória cursada por
    todo mundo.
    """

    name = "manual_resource_allocation"

    def project(self, bipartite: BipartiteBundle, spec: ProjectionSpec) -> ProjectionBundle:
        raise NotImplementedError("A-04: ver docs/specs/frente-a/A-04-projecoes-manuais.md")


PROJECTIONS.register("manual_simple", SimpleProjection())
PROJECTIONS.register("manual_resource_allocation", ResourceAllocationProjection())
