"""Louvain  ``[B]`` — spec B-01.

Otimização gulosa de modularidade (Blondel et al., 2008). Rápido o
bastante para a base inteira, o que faz dele a linha de base contra a
qual o Girvan-Newman é comparado em custo (spec B-04).

**Sem IA.** Louvain é otimização combinatória sobre a estrutura do
grafo, não aprendizado: não há treino, não há rótulo, e o resultado é
rastreável até as arestas. É o que a seção 2 do briefing exige.

Implementação principal: ``python-louvain`` (``community_louvain``), com
``nx.community.louvain_communities`` disponível para comparação — as
duas estão nos requirements e a spec B-01 compara as duas.

Q sai daqui pela implementação à mão
------------------------------------
O ``modularity`` deste módulo é sempre o da :mod:`~edugraph.community.modularity`
(spec B-03), nunca o que a biblioteca devolve de brinde. São duas coisas
diferentes: a biblioteca otimiza Q internamente com a **sua** convenção
de peso e resolução, e o número que vai para a tabela do capítulo 3
precisa ser o da fórmula que o artigo descreve.
"""

from __future__ import annotations

import time
from typing import Any

from edugraph.community import check_params
from edugraph.community.modularity import densify, groups_of, membership_of, modularity
from edugraph.contracts.errors import ContractError
from edugraph.contracts.registry import COMMUNITIES
from edugraph.contracts.types import Meta, Partition, ProjectionBundle

#: Id da spec, gravado em ``meta.producer`` de todo artefato daqui.
PRODUCER = "B-01"

#: Semente padrão. Louvain é estocástico na ordem de visita dos nós;
#: sem semente fixa, duas execuções dão partições diferentes e nenhuma
#: tabela do artigo é reproduzível (ADR-0011).
DEFAULT_SEED = 42

#: Resolução padrão do método. Valores > 1 favorecem comunidades menores.
DEFAULT_RESOLUTION = 1.0

#: As duas bibliotecas comparadas pela spec B-01.
IMPLEMENTATIONS: tuple[str, ...] = ("python_louvain", "networkx")

#: A que roda por padrão. É a do starter kit, e a que gerou as fixtures.
DEFAULT_IMPLEMENTATION = "python_louvain"

#: Parâmetros aceitos em ``run`` (ver :func:`edugraph.community.check_params`).
ACCEPTED_PARAMS: frozenset[str] = frozenset({"seed", "resolution", "implementation", "weight"})


def _membership(
    projection: ProjectionBundle,
    *,
    implementation: str,
    seed: int,
    resolution: float,
    weight: str | None,
) -> dict[str, int]:
    """Roda a biblioteca escolhida e devolve o membership já densificado."""
    graph = projection.graph
    if implementation == "python_louvain":
        import community as community_louvain

        raw = community_louvain.best_partition(
            graph, weight=weight, resolution=resolution, random_state=seed
        )
        return densify(raw)

    if implementation == "networkx":
        import networkx as nx

        groups = nx.community.louvain_communities(
            graph, weight=weight, resolution=resolution, seed=seed
        )
        # A ordem das comunidades que o NetworkX devolve depende da ordem
        # de visita; ordenar cada uma antes de numerar deixa a saída
        # estável, e a densificação faz o resto.
        return membership_of([sorted(nodes) for nodes in groups])

    raise ContractError(
        f"implementation={implementation!r} desconhecida; esperado um de {list(IMPLEMENTATIONS)}"
    )


class LouvainAlgorithm:
    """Satisfaz :class:`~edugraph.contracts.protocols.CommunityAlgorithm`.

    Parameters aceitos em ``run``:

    ``seed`` : int
        Semente do gerador. Padrão :data:`DEFAULT_SEED`.
    ``resolution`` : float
        Resolução da modularidade. Padrão :data:`DEFAULT_RESOLUTION`.
    ``implementation`` : {"python_louvain", "networkx"}
        Qual biblioteca usar. A comparação entre as duas é parte da B-01.
    ``weight`` : str | None
        Atributo de peso; ``None`` roda sobre o grafo não ponderado.
    """

    name = "louvain"

    def run(self, projection: ProjectionBundle, **params: Any) -> Partition:
        """Particiona a projeção e devolve Q, k, tempo e status.

        Raises
        ------
        ContractError
            Se a projeção estiver vazia ou se vier um parâmetro que este
            algoritmo não conhece.
        """
        check_params(params, ACCEPTED_PARAMS, "LouvainAlgorithm.run")

        seed = int(params.get("seed", DEFAULT_SEED))
        resolution = float(params.get("resolution", DEFAULT_RESOLUTION))
        implementation = str(params.get("implementation", DEFAULT_IMPLEMENTATION))
        weight = params.get("weight", "weight")

        graph = projection.graph
        if graph.number_of_nodes() == 0:
            raise ContractError(
                f"Louvain: projeção {projection.projection_id!r} não tem nós; "
                "não há o que particionar"
            )

        # O cronômetro cobre só a busca da partição — Q e metadados são
        # conta nossa, e entram na linha do artigo como custo do método,
        # não do algoritmo (ver a nota da B-04 sobre comparabilidade).
        start = time.perf_counter()
        membership = _membership(
            projection,
            implementation=implementation,
            seed=seed,
            resolution=resolution,
            weight=weight,
        )
        runtime_s = time.perf_counter() - start

        groups = groups_of(membership)
        q = modularity(graph, membership, weight=weight, resolution=resolution)
        singletons = sum(1 for nodes in groups.values() if len(nodes) == 1)

        meta = Meta(
            producer=PRODUCER,
            stats={
                "n_nodes": graph.number_of_nodes(),
                "n_edges": graph.number_of_edges(),
                "largest_community": max((len(n) for n in groups.values()), default=0),
                # Um k alto de singletons diz algo muito diferente de um k
                # alto de grupos reais; o artigo precisa reportar os dois
                # (ver docs/contratos/partition.md).
                "n_singletons": singletons,
            },
            notes=(
                "Louvain (Blondel et al., 2008) pela biblioteca; Q pela implementação "
                "à mão da spec B-03. Otimização combinatória, não aprendizado."
            ),
        )
        return Partition(
            algorithm="louvain",
            projection_id=projection.projection_id,
            membership=membership,
            modularity=q,
            n_communities=len(groups),
            runtime_s=runtime_s,
            params={
                "seed": seed,
                "resolution": resolution,
                "implementation": implementation,
                "weight": weight,
            },
            status="ok",
            meta=meta,
        )


def compare_implementations(
    projection: ProjectionBundle,
    *,
    seed: int = DEFAULT_SEED,
    resolution: float = DEFAULT_RESOLUTION,
    weight: str | None = "weight",
) -> dict[str, Any]:
    """``python-louvain`` × ``nx.community.louvain_communities``.

    A comparação que a spec B-01 exige registrar. Não é a comparação da
    ADR-0010 — Louvain **não** foi implementado à mão, e por um motivo
    escrito: a otimização gulosa é onde bugs sutis se escondem. O que se
    compara aqui são duas bibliotecas, para saber se a escolha entre
    elas muda algum número do artigo.

    Returns
    -------
    dict
        Uma linha tabelável: Q, k e tempo de cada uma, mais a
        concordância entre as duas partições (NMI e Rand ajustado).
    """
    from edugraph.community.compare import agreement

    algorithm = LouvainAlgorithm()
    runs = {
        implementation: algorithm.run(
            projection,
            seed=seed,
            resolution=resolution,
            implementation=implementation,
            weight=weight,
        )
        for implementation in IMPLEMENTATIONS
    }
    left, right = runs["python_louvain"], runs["networkx"]
    concordancia = agreement(left, right)

    return {
        "projection_id": projection.projection_id,
        "seed": seed,
        "resolution": resolution,
        "modularity_python_louvain": left.modularity,
        "modularity_networkx": right.modularity,
        "abs_diff": abs(left.modularity - right.modularity),
        "n_communities_python_louvain": left.n_communities,
        "n_communities_networkx": right.n_communities,
        "runtime_python_louvain_s": left.runtime_s,
        "runtime_networkx_s": right.runtime_s,
        "nmi": concordancia["nmi"],
        "adjusted_rand": concordancia["adjusted_rand"],
        "identical": left.membership == right.membership,
    }


COMMUNITIES.register("louvain", LouvainAlgorithm())
