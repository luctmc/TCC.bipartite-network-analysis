"""Grafo bipartido parametrizável  ``[A]`` — spec A-03.

E o ETL do OULAD (A-02), desenvolvido contra ``tests/data/oulad_mini/``:
sete arquivos minúsculos com o esquema real, para que a Frente A não
fique bloqueada pelo download de ~450 MB.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from edugraph.contracts.types import BipartiteSpec
from edugraph.data.bipartite import build_bipartite

OULAD_MINI = Path(__file__).parent / "oulad_mini"


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


@pytest.mark.xfail(reason="A-03 não implementada", raises=NotImplementedError, strict=True)
def test_limiar_de_nota_decide_a_aresta(tabela_minima: pd.DataFrame) -> None:
    """Com limiar 60, o aluno de nota 41 não gera aresta."""
    spec = BipartiteSpec(dataset="t", edge_criterion="score_threshold", threshold=60.0)
    bundle = build_bipartite(tabela_minima, spec)

    assert bundle.graph.has_edge("S1", "DAAA")
    assert not bundle.graph.has_edge("S2", "DAAA")


@pytest.mark.xfail(reason="A-03 não implementada", raises=NotImplementedError, strict=True)
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


@pytest.mark.xfail(reason="A-03 não implementada", raises=NotImplementedError, strict=True)
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


@pytest.mark.xfail(reason="A-03 não implementada", raises=NotImplementedError, strict=True)
def test_nos_nunca_carregam_rotulo(tabela_minima: pd.DataFrame) -> None:
    """``final_result`` chega na tabela mas não pode virar atributo de nó."""
    bundle = build_bipartite(tabela_minima, BipartiteSpec(dataset="t", threshold=60.0))
    for _, data in bundle.graph.nodes(data=True):
        assert set(data) <= {"kind", "label"}, "atributo extra em nó do bipartido (ADR-0008)"


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
