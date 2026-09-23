"""Modularidade Q implementada à mão  ``[B]`` — spec B-03.

Três verificações independentes, porque uma implementação à mão que só
é comparada com a biblioteca não prova nada além de "as duas fazem a
mesma coisa":

1. **Contra o NetworkX**, que é a comparação que o artigo cita (ADR-0010).
2. **Contra a forma ingênua** ``O(n²)``, escrita aqui no teste a partir
   da fórmula do artigo. É ela que garante que a forma fechada por
   comunidade — a que roda — é a mesma conta.
3. **Contra valores conhecidos**: partição trivial dá Q = 0, por
   definição.
"""

from __future__ import annotations

import time

import networkx as nx
import pytest

from edugraph.community.modularity import (
    TOLERANCE,
    compare_with_networkx,
    densify,
    groups_of,
    membership_of,
    modularity,
)
from edugraph.contracts import io
from edugraph.contracts.errors import ContractError


def modularidade_ingenua(
    graph: nx.Graph, membership: dict[str, int], *, weight: str | None = "weight"
) -> float:
    """A soma dupla da definição, ``O(n²)`` — só para conferir a fechada.

    Q = (1/2m) Σᵢⱼ (Aᵢⱼ − kᵢkⱼ/2m) δ(cᵢ, cⱼ)

    Escrita direto da fórmula, sem olhar a implementação: é isso que faz
    dela uma verificação, e não uma tautologia
    (``docs/testes/estrategia.md``).
    """
    nodes = list(graph.nodes)
    strength = {n: float(d) for n, d in graph.degree(weight=weight)}
    two_m = sum(strength.values())
    if two_m == 0:
        return 0.0

    total = 0.0
    for i in nodes:
        for j in nodes:
            if membership[i] != membership[j]:
                continue
            if graph.has_edge(i, j):
                a_ij = 1.0 if weight is None else float(graph[i][j].get(weight, 1.0))
            else:
                a_ij = 0.0
            total += a_ij - strength[i] * strength[j] / two_m
    return total / two_m


# ---------------------------------------------------------------------
# Contra o NetworkX e contra valores conhecidos
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
def test_q_a_mao_bate_com_a_do_networkx(synthetic_projection, artifact_roots) -> None:
    """A comparação que o artigo cita (ADR-0010)."""
    projection = synthetic_projection("student_simple")
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")

    a_mao = modularity(projection.graph, partition.membership, weight="weight")
    grupos = [set(nodes) for nodes in partition.groups().values()]
    referencia = nx.community.modularity(projection.graph, grupos, weight="weight")

    assert abs(a_mao - referencia) < TOLERANCE


def test_q_de_particao_trivial_e_zero() -> None:
    """Tudo numa comunidade só: Q = 0, por definição."""
    graph = nx.Graph()
    graph.add_edge("a", "b", weight=1.0)
    graph.add_edge("b", "c", weight=1.0)

    assert modularity(graph, {"a": 0, "b": 0, "c": 0}, weight="weight") == pytest.approx(0.0)


def test_grafo_sem_arestas_devolve_zero_em_vez_de_dividir_por_zero() -> None:
    graph = nx.Graph()
    graph.add_nodes_from(["a", "b"])
    assert modularity(graph, {"a": 0, "b": 1}) == 0.0


@pytest.mark.dataset("tiny_v1")
def test_forma_fechada_bate_com_a_forma_ingenua(tiny_projection) -> None:
    """A verificação que prova que a otimização não mudou a conta.

    Sobre ``tiny_v1``, onde a forma ``O(n²)`` ainda cabe, e para várias
    partições — inclusive as ruins, que é onde um erro de sinal
    apareceria.
    """
    graph = tiny_projection("student_simple").graph
    particoes = [
        {"S1": 0, "S2": 0, "S3": 0, "S4": 1, "S5": 1, "S6": 0},  # a natural
        {"S1": 0, "S2": 1, "S3": 2, "S4": 3, "S5": 4, "S6": 5},  # todos singletons
        {"S1": 0, "S2": 1, "S3": 0, "S4": 1, "S5": 0, "S6": 1},  # deliberadamente ruim
    ]
    for membership in particoes:
        for weight in ("weight", None):
            assert modularity(graph, membership, weight=weight) == pytest.approx(
                modularidade_ingenua(graph, membership, weight=weight), abs=TOLERANCE
            )


@pytest.mark.dataset("tiny_v1")
def test_com_e_sem_peso_dao_valores_diferentes_e_na_faixa(tiny_projection) -> None:
    """Peso muda o valor, e os dois ficam em [−0,5, 1] (faixa do validador)."""
    graph = tiny_projection("student_simple").graph
    membership = {"S1": 0, "S2": 0, "S3": 0, "S4": 1, "S5": 1, "S6": 0}

    com_peso = modularity(graph, membership, weight="weight")
    sem_peso = modularity(graph, membership, weight=None)

    assert com_peso != sem_peso
    assert all(-0.5 <= q <= 1.0 for q in (com_peso, sem_peso))


@pytest.mark.dataset("synthetic_v1")
def test_resolucao_entra_na_formula(synthetic_projection, artifact_roots) -> None:
    """γ ≠ 1 precisa bater com o NetworkX também — é o mesmo parâmetro."""
    projection = synthetic_projection("student_simple")
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    grupos = [set(nodes) for nodes in partition.groups().values()]

    for resolution in (0.5, 2.0):
        a_mao = modularity(projection.graph, partition.membership, resolution=resolution)
        referencia = nx.community.modularity(
            projection.graph, grupos, weight="weight", resolution=resolution
        )
        assert abs(a_mao - referencia) < TOLERANCE


@pytest.mark.dataset("synthetic_v1")
def test_comparacao_com_networkx_devolve_os_dois_valores(synthetic_projection, artifact_roots):
    """A linha da tabela de validação da spec B-03."""
    projection = synthetic_projection("student_simple")
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")

    linha = compare_with_networkx(projection.graph, partition.membership)

    assert set(linha) == {"manual", "networkx", "abs_diff", "equal_within_tolerance"}
    assert linha["abs_diff"] < TOLERANCE
    assert linha["equal_within_tolerance"] == 1.0


def test_membership_incompleto_e_erro_e_nao_q_errado() -> None:
    """Ignorar um nó faltante daria um Q silenciosamente errado."""
    graph = nx.Graph()
    graph.add_edge("a", "b", weight=1.0)

    with pytest.raises(ContractError, match="membership"):
        modularity(graph, {"a": 0})


# ---------------------------------------------------------------------
# densify — a renumeração que o validador de contrato exige
# ---------------------------------------------------------------------


def test_densify_devolve_ids_densos_preservando_os_agrupamentos() -> None:
    esparso = {"S1": 7, "S2": 7, "S3": 4, "S4": 9}
    denso = densify(esparso)

    assert sorted(set(denso.values())) == [0, 1, 2]
    assert denso["S1"] == denso["S2"]
    assert len({denso["S1"], denso["S3"], denso["S4"]}) == 3


def test_densify_e_deterministico_e_ordena_pelo_menor_no() -> None:
    """A ordem é a do menor id de nó de cada comunidade (ADR-0011).

    É a mesma regra de ``scripts/make_fixtures.py``: sem ela, duas
    execuções equivalentes produziriam CSVs diferentes e um diff em
    ``data/fixtures`` deixaria de significar alguma coisa.
    """
    assert densify({"S3": 9, "S1": 5, "S2": 9}) == {"S1": 0, "S2": 1, "S3": 1}
    # A entrada em outra ordem dá exatamente o mesmo resultado.
    assert densify({"S2": 9, "S3": 9, "S1": 5}) == {"S1": 0, "S2": 1, "S3": 1}


def test_groups_of_e_membership_of_sao_inversos() -> None:
    membership = {"S1": 0, "S2": 1, "S3": 0}
    grupos = list(groups_of(membership).values())
    assert membership_of(grupos) == membership


# ---------------------------------------------------------------------
# Custo — o critério de aceite que prova a forma fechada
# ---------------------------------------------------------------------


def test_cem_mil_arestas_terminam_em_tempo_linear() -> None:
    """Critério de aceite da B-03: medir, para provar a forma fechada.

    A forma ingênua percorreria 20 mil × 20 mil pares — 4×10⁸ iterações
    em Python, dezenas de minutos. A fechada percorre arestas e nós.
    O limite de 5 s é folgado de propósito: ele separa O(m) de O(n²),
    não mede a máquina.
    """
    graph = nx.gnm_random_graph(20_000, 100_000, seed=0)
    graph = nx.relabel_nodes(graph, {node: f"S{node}" for node in graph})
    nx.set_edge_attributes(graph, 1.0, "weight")
    membership = {node: index % 10 for index, node in enumerate(sorted(graph))}

    start = time.perf_counter()
    q = modularity(graph, membership)
    elapsed = time.perf_counter() - start

    assert -0.5 <= q <= 1.0
    assert elapsed < 5.0, f"Q sobre 100 mil arestas levou {elapsed:.1f}s; a forma é linear?"
