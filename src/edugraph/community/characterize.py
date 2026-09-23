"""Caracterização das comunidades  ``[B]`` — spec B-05.

**Saída obrigatória** do TCC: a seção 6.2 do briefing exige
"agrupamentos interpretáveis de perfis de estudantes, com caracterização
de quais disciplinas predominam em cada comunidade". Uma partição sem
esta etapa não responde ao objetivo declarado na Introdução — ela diz
*quem está junto*, não *por quê*.

Precisa do bipartido para saber quais disciplinas cada aluno cursou, e é
por isso que ``[B]`` consome ``bipartite/`` além de ``projections/``. No
dia 0, ``data/fixtures/synthetic_v1/bipartite/`` cobre essa dependência.

Frequência em excesso, não em absoluto
--------------------------------------
A disciplina obrigatória que todo mundo cursa aparece em todas as
comunidades e **não caracteriza nenhuma**. O que ordena as disciplinas
de cada comunidade é, portanto, a diferença entre a frequência dentro
dela e a frequência na base:

    excesso(d) = alunos da comunidade em d / tamanho da comunidade
               − alunos da base em d / tamanho da base

A coluna ``top_disciplines`` mostra as três grandezas — a frequência
relativa, a da base e a contagem absoluta — porque quem lê o relatório
interno (spec C-07) precisa das três para não confundir "predominante"
com "numerosa".

**A base é a própria partição**, não o bipartido inteiro: é a população
que foi dividida em comunidades. A diferença só aparece em partição
parcial (Girvan-Newman com ``sample_nodes``), e aí a base certa é mesmo
o recorte analisado.

Os dois lados
-------------
A caracterização generaliza para qualquer lado: os nós da comunidade são
descritos pelos vizinhos deles **no lado oposto** do bipartido. Numa
partição de alunos — o caso que o briefing exige — isso é exatamente
"quais disciplinas predominam". Numa partição de disciplinas, a coluna
passa a listar alunos, o que é bem menos útil; a CLI avisa.
"""

from __future__ import annotations

import itertools
from collections import defaultdict
from typing import Any

from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import BipartiteBundle, Partition

#: Id da spec, para as mensagens e o ``producer`` de quem grava.
PRODUCER = "B-05"

#: Colunas de ``communities/<id>/profile.csv``.
PROFILE_COLUMNS: tuple[str, ...] = (
    "community",
    "size",
    "top_disciplines",
    "mean_degree",
    "internal_density",
    "share_of_nodes",
)

#: Separador entre as disciplinas de ``top_disciplines``. Não é vírgula
#: de propósito: a coluna é lida em planilha, e vírgula dentro de célula
#: exige aspas que confundem quem abre o CSV no Excel.
TOP_SEPARATOR = "; "


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _opposite_neighbours(bipartite: BipartiteBundle, nodes: list[str]) -> dict[str, list[str]]:
    """Vizinho do lado oposto → membros da comunidade ligados a ele."""
    by_neighbour: defaultdict[str, list[str]] = defaultdict(list)
    for node in nodes:
        for neighbour in bipartite.graph.neighbors(node):
            by_neighbour[neighbour].append(node)
    return dict(by_neighbour)


def _internal_density(bipartite: BipartiteBundle, nodes: list[str]) -> float:
    """Fração dos pares da comunidade que compartilham algum vizinho.

    É a densidade da projeção simples **restrita à comunidade**,
    calculada direto do bipartido: cada vizinho do lado oposto forma uma
    clique entre os membros ligados a ele, e a união dessas cliques são
    as arestas internas. Custo ``Σ_d C(grau_c(d), 2)``, o mesmo percurso
    da projeção à mão da spec A-04 — nunca a matriz densa.

    Comunidade de um nó só não tem par: devolve ``0.0``.
    """
    if len(nodes) < 2:
        return 0.0
    pairs: set[tuple[str, str]] = set()
    for members in _opposite_neighbours(bipartite, nodes).values():
        if len(members) < 2:
            continue
        pairs.update(itertools.combinations(sorted(members), 2))
    possible = len(nodes) * (len(nodes) - 1) / 2
    return len(pairs) / possible


def _top_neighbours(
    bipartite: BipartiteBundle,
    nodes: list[str],
    base_counts: dict[str, int],
    base_size: int,
    top_k: int,
) -> str:
    """As ``top_k`` disciplinas de maior excesso, já formatadas."""
    size = len(nodes)
    counts = {
        neighbour: len(members)
        for neighbour, members in _opposite_neighbours(bipartite, nodes).items()
    }
    if not counts:
        return ""

    def excess(item: tuple[str, int]) -> tuple[float, int, str]:
        neighbour, count = item
        base = base_counts.get(neighbour, 0) / base_size if base_size else 0.0
        # Desempate por contagem e depois por id: duas disciplinas com o
        # mesmo excesso precisam sair sempre na mesma ordem (ADR-0011).
        return (-(count / size - base), -count, neighbour)

    parts = []
    for neighbour, count in sorted(counts.items(), key=excess)[:top_k]:
        label = bipartite.graph.nodes[neighbour].get("label", neighbour)
        base = base_counts.get(neighbour, 0) / base_size if base_size else 0.0
        parts.append(f"{label} {_pct(count / size)} (base {_pct(base)}, n={count})")
    return TOP_SEPARATOR.join(parts)


def characterize(
    partition: Partition, bipartite: BipartiteBundle, *, top_k: int = 3
) -> list[dict[str, Any]]:
    """Perfil de cada comunidade, no formato de :data:`PROFILE_COLUMNS`.

    Parameters
    ----------
    partition
        Partição sobre a projeção aluno↔aluno.
    bipartite
        Grafo bipartido de origem, para cruzar alunos e disciplinas.
    top_k
        Quantas disciplinas predominantes listar por comunidade.

    Returns
    -------
    list of dict
        Uma linha por comunidade, em ordem de id: ``community``,
        ``size``, ``top_disciplines`` (as ``top_k`` de maior excesso
        sobre a base), ``mean_degree`` (média de disciplinas por aluno),
        ``internal_density`` (ver :func:`_internal_density`) e
        ``share_of_nodes``.

    Raises
    ------
    ContractError
        Se a partição tiver nós que não existem no bipartido — sinal de
        que os dois artefatos são de datasets diferentes, e qualquer
        número calculado ali seria ficção.
    """
    if top_k < 1:
        raise ContractError(f"{PRODUCER}: top_k precisa ser >= 1; recebeu {top_k!r}")

    graph = bipartite.graph
    desconhecidos = sorted(node for node in partition.membership if node not in graph)
    if desconhecidos:
        raise ContractError(
            f"{PRODUCER}: {len(desconhecidos)} nós da partição "
            f"{partition.artifact_id!r} não existem no bipartido "
            f"{bipartite.spec.dataset!r} (ex.: {desconhecidos[:5]}). "
            "Partição e bipartido precisam ser do mesmo dataset."
        )

    groups = partition.groups()
    base_nodes = sorted(partition.membership)
    base_size = len(base_nodes)
    base_counts = {
        neighbour: len(members)
        for neighbour, members in _opposite_neighbours(bipartite, base_nodes).items()
    }

    rows: list[dict[str, Any]] = []
    for community, nodes in groups.items():
        degrees = [graph.degree(node) for node in nodes]
        rows.append(
            {
                "community": community,
                "size": len(nodes),
                "top_disciplines": _top_neighbours(bipartite, nodes, base_counts, base_size, top_k),
                "mean_degree": sum(degrees) / len(nodes),
                "internal_density": _internal_density(bipartite, nodes),
                "share_of_nodes": len(nodes) / base_size,
            }
        )
    return rows


def community_sizes(partition: Partition) -> dict[int, int]:
    """Tamanho de cada comunidade, para a figura de distribuição (B-07)."""
    return {community: len(nodes) for community, nodes in partition.groups().items()}


def describe_partition(partition: Partition) -> dict[str, Any]:
    """Resumo de uma partição em uma linha, para a saída da CLI.

    Inclui ``n_singletons`` porque um ``k`` alto composto de comunidades
    de um nó só diz algo muito diferente de um ``k`` alto de grupos
    reais — o artigo precisa reportar os dois (docs/contratos/partition.md).
    """
    sizes = sorted(community_sizes(partition).values(), reverse=True)
    return {
        "artifact_id": partition.artifact_id,
        "n_communities": partition.n_communities,
        "largest_community": sizes[0] if sizes else 0,
        "smallest_community": sizes[-1] if sizes else 0,
        "n_singletons": sum(1 for size in sizes if size == 1),
        "modularity": partition.modularity,
        "status": partition.status,
    }
