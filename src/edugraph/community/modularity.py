"""Modularidade Q implementada à mão  ``[B]`` — spec B-03.

Segunda implementação à mão do projeto (ADR-0010), ao lado da projeção
(``[A]``) e da iteração de potência (``[C]``). Comparada com
``nx.community.modularity`` na própria spec.

.. math::

    Q = \\frac{1}{2m} \\sum_{ij} \\left( A_{ij} - \\frac{k_i k_j}{2m}
        \\right) \\delta(c_i, c_j)

Em grafo ponderado, ``A_ij`` é o peso da aresta, ``k_i`` a força do nó
(soma dos pesos incidentes) e ``m`` metade da soma de todos os pesos.
"""

from __future__ import annotations

import networkx as nx

#: Tolerância na comparação com a implementação do NetworkX (spec B-03).
TOLERANCE = 1e-9


def modularity(
    graph: nx.Graph,
    membership: dict[str, int],
    *,
    weight: str | None = "weight",
    resolution: float = 1.0,
) -> float:
    """Calcula Q à mão.

    Parameters
    ----------
    graph
        Grafo da projeção.
    membership
        Nó → id de comunidade. Precisa cobrir todos os nós do grafo.
    weight
        Atributo de peso; ``None`` trata o grafo como não ponderado.
    resolution
        Parâmetro γ da modularidade generalizada.

    Notes
    -----
    A implementar em B-03 **sem** percorrer todos os pares ``ij``: a
    forma fechada por comunidade,
    ``Q = Σ_c (m_c/m − γ·(K_c/2m)²)``, é O(m) e é a que cabe no OULAD.
    A forma ingênua O(n²) pode ficar nos testes, sobre ``tiny_v1``, como
    verificação cruzada.
    """
    raise NotImplementedError("B-03: ver docs/specs/frente-b/B-03-modularidade.md")


def compare_with_networkx(
    graph: nx.Graph, membership: dict[str, int], *, weight: str | None = "weight"
) -> dict[str, float]:
    """Q à mão × ``nx.community.modularity``: os dois valores e a diferença.

    Alimenta a tabela de validação da spec B-03.
    """
    raise NotImplementedError("B-03: comparação com a implementação de referência")


def densify(membership: dict[str, int]) -> dict[str, int]:
    """Renumera comunidades para ``0..k-1`` preservando os agrupamentos.

    Exigido pelo validador de contrato. A ordem é determinística: as
    comunidades são renumeradas pela ordem do menor id de nó de cada
    uma, para que duas execuções equivalentes produzam o mesmo CSV.
    """
    raise NotImplementedError("B-03: densificação determinística dos ids")
