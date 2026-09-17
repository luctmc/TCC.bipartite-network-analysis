"""Louvain e modularidade  ``[B]`` — specs B-01, B-02 e B-03.

Todos ``xfail(strict=True)``: falham hoje por stub e avisam o Gabriel
quando passarem a funcionar.

Os testes rodam sobre as **fixtures**, não sobre saída da Frente A. É a
prova do paralelismo: a Frente B pode fechar B-01, B-02 e B-03 inteiras
sem que a Frente A tenha entregue uma linha.
"""

from __future__ import annotations

import pytest

from edugraph.community.girvan_newman import GirvanNewmanAlgorithm
from edugraph.community.louvain import LouvainAlgorithm
from edugraph.community.modularity import modularity


@pytest.mark.dataset("tiny_v1")
@pytest.mark.xfail(reason="B-01 não implementada", raises=NotImplementedError, strict=True)
def test_louvain_recupera_os_dois_grupos_de_tiny(tiny_projection) -> None:
    """``tiny_v1`` é um K4 colado a um triângulo por S3.

    A partição natural é {S1,S2,S3,S6} e {S4,S5} — ou {S4,S5} separado
    com S3 de qualquer um dos lados, já que ele é a ponte. O teste
    aceita as duas leituras e só exige que S4 e S5 fiquem juntos e
    separados de S1, S2 e S6.
    """
    projection = tiny_projection("student_simple")
    partition = LouvainAlgorithm().run(projection, seed=42)

    assert partition.n_communities == 2
    membership = partition.membership
    assert membership["S4"] == membership["S5"]
    assert membership["S1"] == membership["S2"] == membership["S6"]
    assert membership["S1"] != membership["S4"]


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="B-01 não implementada", raises=NotImplementedError, strict=True)
def test_louvain_encontra_as_tres_areas_plantadas(synthetic_projection) -> None:
    """Três comunidades grandes, Q em [0,40, 0,55].

    Faixa, não igualdade: Louvain é estocástico e uma troca de versão da
    biblioteca move o quarto decimal (ver REFERENCE.md da fixture, onde
    a referência é Q ≈ 0,467 com 3 comunidades).
    """
    projection = synthetic_projection("student_simple")
    partition = LouvainAlgorithm().run(projection, seed=42)

    assert 0.40 <= partition.modularity <= 0.55
    grandes = [g for g in partition.groups().values() if len(g) >= 10]
    assert len(grandes) >= 3


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="B-01 não implementada", raises=NotImplementedError, strict=True)
def test_mesma_seed_mesma_particao(synthetic_projection) -> None:
    """Sem isto, nenhuma tabela do artigo é reproduzível (ADR-0011)."""
    projection = synthetic_projection("student_simple")
    primeira = LouvainAlgorithm().run(projection, seed=42)
    segunda = LouvainAlgorithm().run(projection, seed=42)
    assert primeira.membership == segunda.membership


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="B-01 não implementada", raises=NotImplementedError, strict=True)
def test_ids_de_comunidade_sao_densos(synthetic_projection) -> None:
    """O validador de contrato exige ``0..k-1``; a biblioteca não garante."""
    partition = LouvainAlgorithm().run(synthetic_projection("student_simple"), seed=42)
    assert sorted(set(partition.membership.values())) == list(range(partition.n_communities))


# ---------------------------------------------------------------------
# B-02 — Girvan-Newman e o orçamento de tempo
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="B-02 não implementada", raises=NotImplementedError, strict=True)
def test_orcamento_estourado_devolve_timeout_e_nao_excecao(synthetic_projection) -> None:
    """O contrato proíbe levantar: estouro é ``status="timeout"`` (ADR-0006).

    É este comportamento que transforma "o algoritmo não termina" de
    falha em resultado reportável no capítulo 3.
    """
    projection = synthetic_projection("student_simple")
    partition = GirvanNewmanAlgorithm().run(projection, time_budget_s=0.01)

    assert partition.status in ("timeout", "skipped")
    assert partition.membership, "mesmo no timeout, devolve a melhor partição vista"


@pytest.mark.dataset("tiny_v1")
@pytest.mark.xfail(reason="B-02 não implementada", raises=NotImplementedError, strict=True)
def test_girvan_newman_separa_a_ponte_em_tiny(tiny_projection) -> None:
    """Removendo a aresta de maior intermediação, {S4,S5} se descola."""
    projection = tiny_projection("student_simple")
    partition = GirvanNewmanAlgorithm().run(projection, time_budget_s=30.0, target_communities=2)

    assert partition.status == "ok"
    assert partition.membership["S4"] == partition.membership["S5"]
    assert partition.membership["S1"] != partition.membership["S4"]


# ---------------------------------------------------------------------
# B-03 — modularidade à mão
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="B-03 não implementada", raises=NotImplementedError, strict=True)
def test_q_a_mao_bate_com_a_do_networkx(synthetic_projection) -> None:
    """A comparação que o artigo cita (ADR-0010)."""
    import networkx as nx

    from edugraph.community.modularity import TOLERANCE
    from edugraph.contracts import io

    projection = synthetic_projection("student_simple")
    partition = io.load_partition(["data/fixtures"], "synthetic_v1", "louvain__student_simple")

    a_mao = modularity(projection.graph, partition.membership, weight="weight")
    grupos = [set(nodes) for nodes in partition.groups().values()]
    referencia = nx.community.modularity(projection.graph, grupos, weight="weight")

    assert abs(a_mao - referencia) < TOLERANCE


@pytest.mark.xfail(reason="B-03 não implementada", raises=NotImplementedError, strict=True)
def test_q_de_particao_trivial_e_zero() -> None:
    """Tudo numa comunidade só: Q = 0, por definição."""
    import networkx as nx

    graph = nx.Graph()
    graph.add_edge("a", "b", weight=1.0)
    graph.add_edge("b", "c", weight=1.0)

    assert modularity(graph, {"a": 0, "b": 0, "c": 0}, weight="weight") == pytest.approx(0.0)
