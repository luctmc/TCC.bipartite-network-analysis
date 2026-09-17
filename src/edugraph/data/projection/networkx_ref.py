"""Projeções de referência via NetworkX  ``[A]`` — spec A-05.

Existem para serem comparadas com a implementação à mão, não para
substituí-la: a comparação (igualdade numérica, tempo, distribuição de
pesos) é o que demonstra domínio na banca e vira tabela do capítulo 3
(ADR-0010).
"""

from __future__ import annotations

from edugraph.contracts.registry import PROJECTIONS
from edugraph.contracts.types import BipartiteBundle, ProjectionBundle, ProjectionSpec


class NetworkXSimpleProjection:
    """``nx.bipartite.weighted_projected_graph``.

    Satisfaz :class:`~edugraph.contracts.protocols.ProjectionAlgorithm`.
    """

    name = "networkx_simple"

    def project(self, bipartite: BipartiteBundle, spec: ProjectionSpec) -> ProjectionBundle:
        raise NotImplementedError("A-05: ver docs/specs/frente-a/A-05-comparacao-projecao.md")


class NetworkXResourceAllocationProjection:
    """``nx.bipartite.collaboration_weighted_projected_graph`` e afins.

    Satisfaz :class:`~edugraph.contracts.protocols.ProjectionAlgorithm`.

    Atenção em A-05: as funções prontas do NetworkX para projeção
    ponderada não são todas equivalentes à alocação de recursos de Zhou
    et al. A spec exige verificar qual corresponde e, se nenhuma
    corresponder exatamente, documentar a diferença em vez de forçar a
    comparação.
    """

    name = "networkx_resource_allocation"

    def project(self, bipartite: BipartiteBundle, spec: ProjectionSpec) -> ProjectionBundle:
        raise NotImplementedError("A-05: ver docs/specs/frente-a/A-05-comparacao-projecao.md")


PROJECTIONS.register("networkx_simple", NetworkXSimpleProjection())
PROJECTIONS.register("networkx_resource_allocation", NetworkXResourceAllocationProjection())
