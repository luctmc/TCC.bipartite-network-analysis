"""Grafo bipartido parametrizável  ``[A]`` — spec A-03 (fechada).

E o ETL do OULAD (A-02), desenvolvido contra ``tests/data/oulad_mini/``:
sete arquivos minúsculos com o esquema real, para que a Frente A não
fique bloqueada pelo download de ~450 MB.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.paths import ArtifactRoots
from edugraph.contracts.types import BipartiteSpec
from edugraph.contracts.validate import validate_bipartite, validate_dataset
from edugraph.data.bipartite import PRODUCER, build_bipartite, normalize_table
from edugraph.data.synthetic import SyntheticSpec, generate

OULAD_MINI = Path(__file__).parent / "oulad_mini"
REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def tabela_minima() -> pd.DataFrame:
    """Duas matrículas, o bastante para exercitar o critério de aresta."""
    return pd.DataFrame(
        [
            {
                "id_student": 1,
                "code_module": "AAA",
                "code_presentation": "2024J",
                "score_media": 82.0,
                "final_result": "Pass",
            },
            {
                "id_student": 2,
                "code_module": "AAA",
                "code_presentation": "2024J",
                "score_media": 41.0,
                "final_result": "Fail",
            },
        ]
    )


@pytest.fixture
def tabela_rica() -> pd.DataFrame:
    """Duas apresentações, cliques e avaliações — para coorte, AVA e granularidade."""
    return pd.DataFrame(
        [
            # aluno 1: AAA em duas apresentações (média 70), com cliques
            {"id_student": 1, "code_module": "AAA", "code_presentation": "2013J",
             "score_media": 80.0, "sum_click": 5, "id_assessment": 100, "final_result": "Pass"},
            {"id_student": 1, "code_module": "AAA", "code_presentation": "2014J",
             "score_media": 60.0, "sum_click": 0, "id_assessment": 101, "final_result": "Fail"},
            # aluno 2: só BBB 2013J, sem clique
            {"id_student": 2, "code_module": "BBB", "code_presentation": "2013J",
             "score_media": 90.0, "sum_click": 0, "id_assessment": 200, "final_result": "Pass"},
            # aluno 3: AAA 2013J com nota baixa mas ativo no AVA
            {"id_student": 3, "code_module": "AAA", "code_presentation": "2013J",
             "score_media": 30.0, "sum_click": 12, "id_assessment": 100, "final_result": "Withdrawn"},
        ]
    )  # fmt: skip


# ---------------------------------------------------------------------
# A-03 — critério de aresta e granularidade
# ---------------------------------------------------------------------


def test_limiar_de_nota_decide_a_aresta(tabela_minima: pd.DataFrame) -> None:
    """Com limiar 60, o aluno de nota 41 não gera aresta."""
    spec = BipartiteSpec(dataset="t", edge_criterion="score_threshold", threshold=60.0)
    bundle = build_bipartite(tabela_minima, spec)

    assert bundle.graph.has_edge("S1", "DAAA")
    assert not bundle.graph.has_edge("S2", "DAAA")
    assert bundle.graph["S1"]["DAAA"]["weight"] == 82.0


def test_granularidade_muda_o_no_disciplina(tabela_minima: pd.DataFrame) -> None:
    """``module`` → ``DAAA``; ``module_presentation`` → ``DAAA_2024J``.

    É a decisão D1 do plano, materializada como parâmetro: com 7 módulos
    o grafo de disciplinas degenera, e a granularidade mais fina é a
    saída.
    """
    por_modulo = build_bipartite(tabela_minima, BipartiteSpec(dataset="t", granularity="module"))
    por_apresentacao = build_bipartite(
        tabela_minima, BipartiteSpec(dataset="t", granularity="module_presentation")
    )

    assert "DAAA" in por_modulo.graph
    assert "DAAA_2024J" in por_apresentacao.graph


def test_granularidade_assessment(tabela_rica: pd.DataFrame) -> None:
    """``assessment`` usa ``id_assessment`` e exige a coluna."""
    bundle = build_bipartite(tabela_rica, BipartiteSpec(dataset="t", granularity="assessment"))
    assert {"D100", "D101", "D200"} <= set(bundle.disciplines)
    assert bundle.graph.nodes["D100"]["label"] == "100"

    sem_coluna = tabela_rica.drop(columns=["id_assessment"])
    with pytest.raises(ContractError, match="id_assessment"):
        build_bipartite(sem_coluna, BipartiteSpec(dataset="t", granularity="assessment"))


def test_criterio_de_aprovacao_ignora_a_nota(tabela_minima: pd.DataFrame) -> None:
    """``final_result_pass`` cria aresta por desfecho de aprovação.

    Atenção: este critério usa ``final_result``, que é rótulo histórico.
    Ele é legítimo como **definição de aresta** declarada e registrada em
    ``BipartiteSpec`` — não é entrada de algoritmo de inferência. A
    distinção está em docs/artigo/decisoes-metodologicas.md e precisa
    aparecer no texto, porque a banca vai perguntar.
    """
    spec = BipartiteSpec(dataset="t", edge_criterion="final_result_pass")
    bundle = build_bipartite(tabela_minima, spec)

    assert bundle.graph.has_edge("S1", "DAAA")
    assert not bundle.graph.has_edge("S2", "DAAA")
    assert bundle.graph["S1"]["DAAA"]["weight"] == 1.0


def test_criterio_de_atividade_no_ava(tabela_rica: pd.DataFrame) -> None:
    """``vle_activity``: clique decide, nota não."""
    spec = BipartiteSpec(dataset="t", edge_criterion="vle_activity", threshold=10)
    bundle = build_bipartite(tabela_rica, spec)

    assert bundle.graph.has_edge("S3", "DAAA")  # 12 cliques, nota 30
    assert not bundle.graph.has_edge("S2", "DBBB")  # nota 90, zero clique
    assert bundle.graph["S3"]["DAAA"]["weight"] == 12.0


def test_coorte_recorta_por_apresentacao(tabela_rica: pd.DataFrame) -> None:
    """Só matrículas da coorte entram; a média não mistura apresentações."""
    tudo = build_bipartite(tabela_rica, BipartiteSpec(dataset="t", threshold=0.0))
    coorte = build_bipartite(
        tabela_rica, BipartiteSpec(dataset="t", threshold=0.0, cohort="AAA_2013J")
    )

    assert tudo.graph["S1"]["DAAA"]["weight"] == 70.0  # média de 80 e 60
    assert coorte.graph["S1"]["DAAA"]["weight"] == 80.0  # só 2013J
    assert "S2" not in coorte.graph  # BBB não é da coorte


def test_nos_nunca_carregam_rotulo(tabela_rica: pd.DataFrame) -> None:
    """``final_result`` e ``sum_click`` chegam na tabela mas não viram atributo de nó."""
    bundle = build_bipartite(tabela_rica, BipartiteSpec(dataset="t", threshold=60.0))
    for _, data in bundle.graph.nodes(data=True):
        assert set(data) <= {"kind", "label"}, "atributo extra em nó do bipartido (ADR-0008)"


def test_normalize_agrega_por_aluno_e_disciplina(tabela_rica: pd.DataFrame) -> None:
    """Média de nota, soma de cliques, aprovado se alguma linha aprovou."""
    norm = normalize_table(tabela_rica, BipartiteSpec(dataset="t"))
    linha = norm[(norm.student_id == "S1") & (norm.discipline_id == "DAAA")].iloc[0]

    assert linha.score_media == 70.0
    assert linha.sum_click == 5
    assert bool(linha.passed) is True
    assert not norm.duplicated(subset=["student_id", "discipline_id"]).any()


def test_isolados_saem_e_sao_contados(tabela_minima: pd.DataFrame) -> None:
    """Aluno sem aresta não fica no grafo, e o número vai para meta.stats."""
    bundle = build_bipartite(tabela_minima, BipartiteSpec(dataset="t", threshold=60.0))

    assert "S2" not in bundle.graph
    assert bundle.meta.stats["n_isolated_removed"] == 1
    assert bundle.meta.producer == PRODUCER
    validate_bipartite(bundle)


# ---------------------------------------------------------------------
# A-03 — reproduz as fixtures (aposenta build_bipartite_reference)
# ---------------------------------------------------------------------


def _make_fixtures_module():
    spec = importlib.util.spec_from_file_location(
        "make_fixtures", REPO / "scripts/make_fixtures.py"
    )
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _same_graph(a, b) -> None:
    assert set(a.nodes) == set(b.nodes)
    ea = {tuple(sorted((u, v))): d["weight"] for u, v, d in a.edges(data=True)}
    eb = {tuple(sorted((u, v))): d["weight"] for u, v, d in b.edges(data=True)}
    assert ea == pytest.approx(eb, abs=1e-12)
    for n in a.nodes:
        assert a.nodes[n]["kind"] == b.nodes[n]["kind"]
        assert a.nodes[n]["label"] == b.nodes[n]["label"]


@pytest.mark.dataset("tiny_v1")
def test_reproduz_a_fixture_tiny_v1(artifact_roots: ArtifactRoots) -> None:
    mf = _make_fixtures_module()
    rows = [
        {"id_student": s, "code_module": m, "code_presentation": "x", "score_media": score}
        for s, m, score in mf.TINY_ENROLLMENTS
    ]
    spec = BipartiteSpec(dataset="tiny_v1", threshold=mf.SCORE_THRESHOLD)
    produzido = build_bipartite(pd.DataFrame(rows), spec)
    fixture = io.load_bipartite(artifact_roots, "tiny_v1")
    _same_graph(produzido.graph, fixture.graph)


@pytest.mark.dataset("synthetic_v1")
def test_reproduz_a_fixture_synthetic_v1(artifact_roots: ArtifactRoots) -> None:
    """98 alunos, 7 disciplinas, 197 arestas, pesos iguais aos da referência."""
    mf = _make_fixtures_module()
    dataset = generate(SyntheticSpec(seed=42))
    spec = BipartiteSpec(dataset="synthetic_v1", threshold=mf.SCORE_THRESHOLD, seed=42)
    produzido = build_bipartite(pd.DataFrame(dataset.enrollments), spec)
    fixture = io.load_bipartite(artifact_roots, "synthetic_v1")

    _same_graph(produzido.graph, fixture.graph)
    assert produzido.meta.stats["n_isolated_removed"] == 22


# ---------------------------------------------------------------------
# A-03 — o estágio `data` de ponta a ponta
# ---------------------------------------------------------------------


def test_run_only_data_gera_artefatos_validos(tmp_path: Path) -> None:
    """``python -m edugraph run configs/synthetic_v1.toml --only data`` funciona."""
    from edugraph.__main__ import main

    code = main(["run", str(REPO / "configs/synthetic_v1.toml"), "--only", "data",
                 "--out", str(tmp_path)])  # fmt: skip
    assert code == 0

    checked = validate_dataset([tmp_path], "synthetic_dev")
    assert "bipartite" in checked
    assert "outcomes" in checked
    assert {f"projections/{p}" for p in (
        "student_simple", "student_resource_allocation",
        "discipline_simple", "discipline_resource_allocation",
    )} <= set(checked)  # fmt: skip

    outcomes = io.load_outcomes([tmp_path], "synthetic_dev")
    bipartite = io.load_bipartite([tmp_path], "synthetic_dev")
    assert set(outcomes.final_result) == bipartite.students
    assert outcomes.planted_group is not None


def test_data_bipartite_grava_so_a_camada_bipartite(tmp_path: Path) -> None:
    from edugraph.__main__ import main

    code = main(["data", "bipartite", str(REPO / "configs/synthetic_v1.toml"),
                 "--out", str(tmp_path)])  # fmt: skip
    assert code == 0
    assert (tmp_path / "synthetic_dev" / "bipartite" / "outcomes.csv").exists()
    assert not (tmp_path / "synthetic_dev" / "projections").exists()


# ---------------------------------------------------------------------
# ETL do OULAD — spec A-02
# ---------------------------------------------------------------------


def test_oulad_mini_existe_com_as_sete_tabelas() -> None:
    """A fixture que substitui o download de 450 MB está no repositório."""
    esperadas = {
        "assessments.csv",
        "courses.csv",
        "studentAssessment.csv",
        "studentInfo.csv",
        "studentRegistration.csv",
        "studentVle.csv",
        "vle.csv",
    }
    presentes = {p.name for p in OULAD_MINI.glob("*.csv")}
    assert presentes == esperadas, f"faltando: {sorted(esperadas - presentes)}"


def test_oulad_mini_usa_o_esquema_real() -> None:
    """As colunas batem com o dicionário de dados do OULAD.

    Este teste vale agora: ele protege a fixture, não a implementação.
    Se o esquema estiver errado, a spec A-02 será desenvolvida contra
    uma mentira e só descobrirá isso com a base real na mão.
    """
    from edugraph.data.oulad.schema import SCHEMAS

    for name, schema in SCHEMAS.items():
        columns = set(pd.read_csv(OULAD_MINI / f"{name}.csv", nrows=0).columns)
        faltando = set(schema.usecols) - columns
        assert not faltando, f"{name}.csv não tem as colunas {sorted(faltando)}"


@pytest.mark.xfail(reason="A-02 não implementada", raises=NotImplementedError, strict=True)
def test_etl_produz_a_tabela_normalizada() -> None:
    """Sete tabelas → uma linha por (aluno, disciplina, apresentação)."""
    from edugraph.data.oulad.etl import NORMALIZED_COLUMNS, normalize

    table = normalize(OULAD_MINI)
    assert set(NORMALIZED_COLUMNS) <= set(table.columns)
    assert not table.duplicated(subset=["id_student", "code_module", "code_presentation"]).any()
