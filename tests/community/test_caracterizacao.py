"""Caracterização e validação a posteriori  ``[B]`` — specs B-05 e B-06.

A caracterização é **saída obrigatória** do TCC (briefing §6.2): uma
partição sem ela diz quem está junto, não por quê.
"""

from __future__ import annotations

import pytest

from edugraph.community.characterize import PROFILE_COLUMNS, characterize
from edugraph.community.evaluate import normalized_mutual_information, outcome_profile
from edugraph.contracts import io

pytestmark = pytest.mark.dataset("synthetic_v1")


@pytest.mark.xfail(reason="B-05 não implementada", raises=NotImplementedError, strict=True)
def test_perfil_tem_as_colunas_do_contrato(artifact_roots) -> None:
    """``profile.csv`` segue :data:`PROFILE_COLUMNS`."""
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    bipartite = io.load_bipartite(artifact_roots, "synthetic_v1")

    rows = characterize(partition, bipartite, top_k=3)
    assert rows
    assert set(rows[0]) == set(PROFILE_COLUMNS)
    assert len(rows) == partition.n_communities


@pytest.mark.xfail(reason="B-05 não implementada", raises=NotImplementedError, strict=True)
def test_disciplinas_predominantes_distinguem_as_comunidades(artifact_roots) -> None:
    """O gerador plantou três áreas; o perfil precisa mostrar isso.

    Se todas as comunidades listassem as mesmas disciplinas, a
    caracterização não estaria caracterizando nada — é o caso de a
    frequência estar sendo medida em absoluto e não em excesso sobre a
    base (ver a nota de implementação da B-05).
    """
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    bipartite = io.load_bipartite(artifact_roots, "synthetic_v1")

    rows = characterize(partition, bipartite, top_k=2)
    grandes = [r for r in rows if int(r["size"]) >= 10]
    assinaturas = {str(r["top_disciplines"]) for r in grandes}

    assert len(assinaturas) == len(grandes), (
        "comunidades grandes com o mesmo conjunto de disciplinas predominantes"
    )


@pytest.mark.xfail(reason="B-06 não implementada", raises=NotImplementedError, strict=True)
def test_nmi_contra_o_grupo_plantado(artifact_roots) -> None:
    """A estrutura descoberta pela topologia recupera o *ground truth*.

    NMI ≥ 0,8 com ruído de 35% no gerador. Se cair muito abaixo, ou o
    Louvain regrediu, ou a projeção mudou de semântica.
    """
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    outcomes = io.load_outcomes(artifact_roots, "synthetic_v1")
    assert outcomes.planted_group is not None

    assert normalized_mutual_information(partition, outcomes.planted_group) >= 0.8


@pytest.mark.xfail(reason="B-06 não implementada", raises=NotImplementedError, strict=True)
def test_desfecho_por_comunidade_cobre_todas(artifact_roots) -> None:
    """Uma linha por comunidade, com a distribuição dos quatro desfechos."""
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    outcomes = io.load_outcomes(artifact_roots, "synthetic_v1")

    rows = outcome_profile(partition, outcomes)
    assert len(rows) == partition.n_communities
