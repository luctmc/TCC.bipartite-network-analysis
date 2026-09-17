"""Centralidades  ``[C]`` — specs C-01, C-02 e C-03.

Os valores exatos vêm de ``data/fixtures/tiny_v1/expected/``, derivado
no papel. Em ``tiny_v1``, a projeção aluno↔aluno é um K4 em
{S1,S2,S3,S6} colado a um triângulo {S3,S4,S5}: S3 é o único vértice de
corte, e por isso concentra **toda** a intermediação (0,6 normalizado)
enquanto todos os outros ficam em zero.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from edugraph.centrality.betweenness import BetweennessCentrality
from edugraph.centrality.degree import DegreeCentrality
from edugraph.centrality.eigenvector import EigenvectorCentrality


def _expected(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.mark.dataset("tiny_v1")
@pytest.mark.xfail(reason="C-01 não implementada", raises=NotImplementedError, strict=True)
def test_grau_bate_com_o_calculo_a_mao(tiny_projection, tiny_expected: Path) -> None:
    """Grau normalizado por n−1 = 5."""
    projection = tiny_projection("student_simple")
    result = DegreeCentrality().compute(projection, normalized=True, weight=None)

    for row in _expected(tiny_expected / "student_simple.centrality.csv"):
        assert result.scores[row["node_id"]] == pytest.approx(float(row["degree"]))


@pytest.mark.dataset("tiny_v1")
@pytest.mark.xfail(reason="C-01 não implementada", raises=NotImplementedError, strict=True)
def test_intermediacao_aponta_o_vertice_de_corte(tiny_projection, tiny_expected: Path) -> None:
    """S3 é a ponte: 0,6; todos os outros, 0."""
    projection = tiny_projection("student_simple")
    result = BetweennessCentrality().compute(projection, normalized=True, weight_mode="none")

    for row in _expected(tiny_expected / "student_simple.centrality.csv"):
        assert result.scores[row["node_id"]] == pytest.approx(float(row["betweenness"]))

    assert result.top(1)[0][0] == "S3"


@pytest.mark.dataset("tiny_v1")
@pytest.mark.xfail(reason="C-02 não implementada", raises=NotImplementedError, strict=True)
def test_autovetor_bate_com_a_forma_fechada(tiny_projection, tiny_expected: Path) -> None:
    """Triângulo ponderado DA-DB=3, DA-DC=DB-DC=1.

    Por simetria x = DA = DB e y = DC, com λx = 3x + y e λy = 2x, logo
    λ = (3+√17)/2. É um teste de verdade da iteração de potência: o
    valor esperado sai da álgebra, não do NetworkX.
    """
    projection = tiny_projection("discipline_simple")
    result = EigenvectorCentrality().compute(projection, implementation="manual", weight="weight")

    for row in _expected(tiny_expected / "discipline_simple.eigenvector.csv"):
        assert result.scores[row["node_id"]] == pytest.approx(float(row["score"]), abs=1e-8)
    assert result.converged is True


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="C-02 não implementada", raises=NotImplementedError, strict=True)
def test_iteracao_de_potencia_bate_com_o_networkx(synthetic_projection) -> None:
    """A comparação que o artigo cita (ADR-0010)."""
    import networkx as nx

    projection = synthetic_projection("student_simple")
    manual = EigenvectorCentrality().compute(projection, implementation="manual")
    referencia = nx.eigenvector_centrality(projection.graph, weight="weight", max_iter=1000)

    for node, score in manual.scores.items():
        assert score == pytest.approx(abs(referencia[node]), abs=1e-6)


@pytest.mark.xfail(reason="C-02 não implementada", raises=NotImplementedError, strict=True)
def test_nao_convergencia_vira_fallback_e_nao_excecao() -> None:
    """O contrato exige ``converged=False`` e fallback, nunca exceção.

    Grafo desconexo é o caso normal na projeção aluno↔aluno do OULAD;
    derrubar o pipeline nele seria inaceitável.
    """
    import networkx as nx

    from edugraph.contracts.types import BipartiteSpec, ProjectionBundle, ProjectionSpec

    graph = nx.Graph()
    graph.add_edge("S1", "S2", weight=1.0)
    graph.add_edge("S3", "S4", weight=1.0)  # componente separada
    for node in graph:
        graph.nodes[node]["kind"] = "student"

    bundle = ProjectionBundle(
        graph=graph,
        spec=ProjectionSpec(side="student", weighting="simple"),
        source=BipartiteSpec(dataset="t"),
    )
    result = EigenvectorCentrality().compute(bundle, implementation="manual", max_iter=5)

    assert set(result.scores) == set(graph.nodes)
    assert all(score >= 0 for score in result.scores.values())


# ---------------------------------------------------------------------
# C-03 — disciplinas críticas (saída obrigatória)
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="C-03 não implementada", raises=NotImplementedError, strict=True)
def test_ranking_de_disciplinas_e_deterministico(synthetic_projection) -> None:
    """Empates desempatam por ``node_id``, senão a tabela muda a cada rodada.

    **Atenção ao caso desta fixture.** Em ``synthetic_v1`` com V =
    módulo, ``discipline_simple`` é o grafo completo K₇: grau e
    intermediação empatam em todos os nós. O desempate determinístico
    não é detalhe, é o que impede a tabela do artigo de mudar sozinha.
    Ver REFERENCE.md da fixture e a decisão D1.
    """
    from edugraph.centrality.critical_disciplines import rank_disciplines

    projection = synthetic_projection("discipline_simple")
    results = {
        "degree": DegreeCentrality().compute(projection),
        "betweenness": BetweennessCentrality().compute(projection),
        "eigenvector": EigenvectorCentrality().compute(projection),
    }

    primeiro = rank_disciplines(results, top_n=7)
    segundo = rank_disciplines(results, top_n=7)
    assert primeiro == segundo


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="C-01 não implementada", raises=NotImplementedError, strict=True)
def test_projecao_disciplina_de_synthetic_e_degenerada(synthetic_projection) -> None:
    """Documenta a degeneração da decisão D1 como comportamento esperado.

    Com 7 módulos e alunos cursando de 2 a 4, todo par de disciplinas
    compartilha algum aluno: K₇, intermediação zero em todos os nós.
    Este teste **afirma a degeneração** em vez de fingir que ela não
    existe — se algum dia ele falhar, é porque a granularidade mudou, e
    aí a spec C-03 passa a ter o que ranquear.
    """
    projection = synthetic_projection("discipline_simple")
    result = BetweennessCentrality().compute(projection, weight_mode="none")

    assert projection.graph.number_of_nodes() == 7
    assert projection.graph.number_of_edges() == 21  # C(7,2): grafo completo
    assert all(score == pytest.approx(0.0) for score in result.scores.values())
