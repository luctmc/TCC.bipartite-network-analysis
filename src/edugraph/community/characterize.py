"""Caracterização das comunidades  ``[B]`` — spec B-05.

**Saída obrigatória** do TCC: a seção 6.2 do briefing exige
"agrupamentos interpretáveis de perfis de estudantes, com caracterização
de quais disciplinas predominam em cada comunidade". Uma partição sem
esta etapa não responde ao objetivo declarado na Introdução — ela diz
*quem está junto*, não *por quê*.

Precisa do bipartido para saber quais disciplinas cada aluno cursou, e é
por isso que ``[B]`` consome ``bipartite/`` além de ``projections/``. No
dia 0, ``data/fixtures/synthetic_v1/bipartite/`` cobre essa dependência.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.types import BipartiteBundle, Partition

#: Colunas de ``communities/<id>/profile.csv``.
PROFILE_COLUMNS: tuple[str, ...] = (
    "community",
    "size",
    "top_disciplines",
    "mean_degree",
    "internal_density",
    "share_of_nodes",
)


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

    Notes
    -----
    A implementar em B-05: para cada comunidade, contar as disciplinas
    dos seus alunos no bipartido e listar as ``top_k`` mais frequentes
    **em excesso sobre a base** — a disciplina obrigatória que todo
    mundo cursa aparece em todas as comunidades e não caracteriza
    nenhuma. Reportar a frequência relativa, não só a absoluta.
    """
    raise NotImplementedError("B-05: ver docs/specs/frente-b/B-05-caracterizacao.md")


def community_sizes(partition: Partition) -> dict[int, int]:
    """Tamanho de cada comunidade, para a figura de distribuição (B-07)."""
    raise NotImplementedError("B-05: distribuição de tamanhos")
