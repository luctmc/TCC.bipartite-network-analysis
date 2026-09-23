"""Modularidade Q implementada à mão  ``[B]`` — spec B-03.

Segunda implementação à mão do projeto (ADR-0010), ao lado da projeção
(``[A]``) e da iteração de potência (``[C]``). Comparada com
``nx.community.modularity`` na própria spec.

.. math::

    Q = \\frac{1}{2m} \\sum_{ij} \\left( A_{ij} - \\frac{k_i k_j}{2m}
        \\right) \\delta(c_i, c_j)

Em grafo ponderado, ``A_ij`` é o peso da aresta, ``k_i`` a força do nó
(soma dos pesos incidentes) e ``m`` metade da soma de todos os pesos.

A forma que roda
----------------
A soma dupla acima é O(n²) e não cabe no OULAD. O que está implementado é
a **forma fechada por comunidade**, algebricamente idêntica:

.. math::

    Q = \\sum_c \\left( \\frac{m_c}{m} - \\gamma
        \\left(\\frac{K_c}{2m}\\right)^2 \\right)

com ``m_c`` = peso das arestas internas à comunidade ``c`` e ``K_c`` =
soma das forças dos seus nós. Um percurso pelas arestas e um pelos nós:
O(m + n). A forma ingênua fica no teste, sobre ``tiny_v1``, como
verificação cruzada — é ela que prova que as duas são a mesma conta.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import networkx as nx

from edugraph.contracts.errors import ContractError

#: Tolerância na comparação com a implementação do NetworkX (spec B-03).
TOLERANCE = 1e-9


def modularity(
    graph: nx.Graph[Any],
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

    Returns
    -------
    float
        Q em ``[-0,5, 1]``. Grafo sem arestas devolve ``0.0``: sem
        aresta não há estrutura a medir, e a fórmula seria 0/0.

    Raises
    ------
    ContractError
        Se algum nó do grafo estiver fora de ``membership``. Ignorar o
        nó faltante daria um Q silenciosamente errado — a força dele
        entra em ``2m`` mas não em ``K_c`` nenhum.

    Notes
    -----
    Convenção de laço: o peso de um laço conta **uma vez** em ``m_c`` e
    **duas** na força do nó, que é o que ``nx.community.modularity`` faz.
    As projeções não admitem laços (o validador recusa), mas a função é
    usada também em grafos de teste montados à mão.
    """
    faltando = [node for node in graph.nodes if node not in membership]
    if faltando:
        raise ContractError(
            f"modularity: {len(faltando)} nós do grafo fora de membership "
            f"(ex.: {faltando[:5]}). A partição precisa cobrir todo o grafo."
        )

    strength: dict[Any, float] = {node: float(value) for node, value in graph.degree(weight=weight)}
    two_m = sum(strength.values())
    if two_m <= 0:
        return 0.0
    m = two_m / 2.0

    internal: defaultdict[int, float] = defaultdict(float)
    for source, target, data in graph.edges(data=True):
        if membership[source] != membership[target]:
            continue
        internal[membership[source]] += 1.0 if weight is None else float(data.get(weight, 1.0))

    total: defaultdict[int, float] = defaultdict(float)
    for node, value in strength.items():
        total[membership[node]] += value

    return sum(
        internal[community] / m - resolution * (strength_sum / two_m) ** 2
        for community, strength_sum in total.items()
    )


def compare_with_networkx(
    graph: nx.Graph[Any], membership: dict[str, int], *, weight: str | None = "weight"
) -> dict[str, float]:
    """Q à mão × ``nx.community.modularity``: os dois valores e a diferença.

    Alimenta a tabela de validação da spec B-03.

    Returns
    -------
    dict
        ``manual``, ``networkx``, ``abs_diff`` e
        ``equal_within_tolerance`` (1.0 ou 0.0, para caber numa célula
        de CSV junto dos outros três).
    """
    manual = modularity(graph, membership, weight=weight)
    groups = [set(nodes) for nodes in groups_of(membership).values()]
    reference = float(nx.community.modularity(graph, groups, weight=weight))
    diff = abs(manual - reference)
    return {
        "manual": manual,
        "networkx": reference,
        "abs_diff": diff,
        "equal_within_tolerance": float(diff < TOLERANCE),
    }


def densify(membership: dict[str, int]) -> dict[str, int]:
    """Renumera comunidades para ``0..k-1`` preservando os agrupamentos.

    Exigido pelo validador de contrato. A ordem é determinística: as
    comunidades são renumeradas pela ordem do menor id de nó de cada
    uma, para que duas execuções equivalentes produzam o mesmo CSV.

    É a mesma regra de ``scripts/make_fixtures.py``, de propósito: uma
    partição da Frente B e a de referência da fixture precisam ser
    comparáveis nó a nó, não só em tamanho de comunidade.
    """
    first_node: dict[int, str] = {}
    for node, community in sorted(membership.items()):
        first_node.setdefault(community, node)
    order = sorted(first_node, key=lambda community: first_node[community])
    remap = {old: new for new, old in enumerate(order)}
    return {node: remap[community] for node, community in sorted(membership.items())}


def groups_of(membership: dict[str, int]) -> dict[int, list[str]]:
    """Comunidade → lista ordenada de nós.

    Mesmo conteúdo de :meth:`edugraph.contracts.types.Partition.groups`,
    disponível antes de a ``Partition`` existir — é o que a B-01 e a
    B-02 precisam enquanto ainda estão escolhendo a melhor partição.
    """
    groups: defaultdict[int, list[str]] = defaultdict(list)
    for node, community in membership.items():
        groups[community].append(node)
    return {community: sorted(nodes) for community, nodes in sorted(groups.items())}


def membership_of(
    groups: list[set[str]] | list[list[str]] | tuple[set[str], ...],
) -> dict[str, int]:
    """Lista de comunidades → ``membership`` densificado.

    O caminho de volta de :func:`groups_of`, usado para converter a
    saída do NetworkX (que devolve tuplas de conjuntos) no formato do
    contrato.
    """
    membership = {node: index for index, nodes in enumerate(groups) for node in nodes}
    return densify(membership)
