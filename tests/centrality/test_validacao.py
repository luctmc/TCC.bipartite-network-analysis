"""Validação a posteriori da centralidade  ``[C]`` — spec C-06.

Os valores esperados sobre ``tiny_v1`` foram derivados à mão a partir de
``bipartite/edges.csv`` e ``bipartite/outcomes.csv``, não da saída da
função (ver ``docs/testes/estrategia.md``):

- base: seis alunos, dois sem conclusão (S4 ``Fail``, S5 ``Withdrawn``)
  → 1/3;
- DC atende S3, S4 e S5 → 2/3, excesso de +1/3;
- DA atende S1, S2, S3 e S6 → 0;
- grau em ``student_simple``: S4 = S5 = 0,4; S1 = S2 = S6 = 0,6; S3 = 1,0.
  Em duas faixas por posição: Q1 = {S4, S5, S1} → 2/3; Q2 = {S2, S6, S3} → 0.
"""

from __future__ import annotations

import pytest

from edugraph.centrality.evaluate import (
    FAILURE_COLUMNS,
    QUANTILE_COLUMNS,
    enrollment_of,
    evaluate,
    failure_rate_by_discipline,
    is_degenerate,
    outcome_by_centrality,
)
from edugraph.contracts.types import CentralityResult, Outcomes

TERCO = 1 / 3


@pytest.fixture
def tiny_outcomes() -> Outcomes:
    """Os desfechos de ``tiny_v1``, escritos aqui para o teste não ler rótulo fora de evaluate."""
    return Outcomes(
        final_result={
            "S1": "Pass",
            "S2": "Distinction",
            "S3": "Pass",
            "S4": "Fail",
            "S5": "Withdrawn",
            "S6": "Pass",
        }
    )


@pytest.mark.dataset("tiny_v1")
def test_matricula_sai_do_bipartido(tiny_bipartite) -> None:
    assert enrollment_of(tiny_bipartite) == {
        "DA": ["S1", "S2", "S3", "S6"],
        "DB": ["S1", "S2", "S3"],
        "DC": ["S3", "S4", "S5"],
    }


@pytest.mark.dataset("tiny_v1")
def test_taxa_da_base_e_das_criticas_batem_com_a_conta_a_mao(tiny_bipartite, tiny_outcomes) -> None:
    linhas = failure_rate_by_discipline(["DC"], tiny_outcomes, enrollment_of(tiny_bipartite))
    por_grupo = {(linha["group"], linha["node_id"]): linha for linha in linhas}

    assert all(tuple(linha) == FAILURE_COLUMNS for linha in linhas)
    dc = por_grupo[("critical", "DC")]
    assert dc["rank"] == 1 and dc["n_students"] == 3
    assert dc["rate_not_passed"] == pytest.approx(2 / 3)
    assert dc["base_rate_not_passed"] == pytest.approx(TERCO)
    assert dc["excess_not_passed"] == pytest.approx(TERCO)
    assert dc["rate_Fail"] == pytest.approx(TERCO)
    assert dc["rate_Withdrawn"] == pytest.approx(TERCO)

    base = por_grupo[("base", None)]
    assert base["n_students"] == 6 and base["rate_not_passed"] == pytest.approx(TERCO)
    assert por_grupo[("others", None)]["rate_not_passed"] == pytest.approx(0.0)


@pytest.mark.dataset("tiny_v1")
def test_faixas_cobrem_todos_os_alunos_uma_linha_por_faixa(tiny_projection, tiny_outcomes) -> None:
    from edugraph.centrality.degree import DegreeCentrality

    grau = DegreeCentrality().compute(tiny_projection("student_simple"))
    faixas = outcome_by_centrality(grau, tiny_outcomes, quantiles=2)

    assert all(tuple(linha) == QUANTILE_COLUMNS for linha in faixas)
    assert [linha["quantile"] for linha in faixas] == [1, 2]
    assert sum(linha["n_students"] for linha in faixas) == 6
    assert faixas[0]["rate_not_passed"] == pytest.approx(2 / 3)
    assert faixas[1]["rate_not_passed"] == pytest.approx(0.0)
    assert faixas[0]["score_min"] == pytest.approx(0.4)
    assert faixas[1]["score_max"] == pytest.approx(1.0)

    quartis = outcome_by_centrality(grau, tiny_outcomes, quantiles=4)
    assert len(quartis) == 4
    assert sum(linha["n_students"] for linha in quartis) == 6


def test_aluno_sem_desfecho_nao_entra_na_taxa() -> None:
    """Taxa sobre ``n_labeled``: aluno sem rótulo não dilui a reprovação."""
    resultado = CentralityResult("student_simple", "degree", {"S1": 0.1, "S2": 0.9, "S9": 0.5})
    desfechos = Outcomes(final_result={"S1": "Fail", "S2": "Pass"})
    (faixa,) = outcome_by_centrality(resultado, desfechos, quantiles=1)
    assert faixa["n_students"] == 3
    assert faixa["n_labeled"] == 2
    assert faixa["rate_not_passed"] == pytest.approx(0.5)


def test_ranking_de_outro_dataset_e_recusado(tiny_outcomes) -> None:
    from edugraph.contracts.errors import ContractError

    with pytest.raises(ContractError, match="fora do bipartido"):
        failure_rate_by_discipline(["DZZZ"], tiny_outcomes, {"DA": ["S1"]})


def test_degeneracao_e_detectada() -> None:
    assert is_degenerate(CentralityResult("discipline_simple", "betweenness", {"A": 0.0, "B": 0.0}))
    assert not is_degenerate(CentralityResult("discipline_simple", "degree", {"A": 0.2, "B": 0.5}))


@pytest.mark.dataset("synthetic_v1")
def test_synthetic_reporta_a_degeneracao_em_vez_de_ranquear(artifact_roots) -> None:
    """Critério de aceite: com K₇, a intermediação das disciplinas é toda
    zero — a validação diz isso, não produz uma tabela sem sentido."""
    resultado = evaluate(artifact_roots, "synthetic_v1", metric="betweenness")

    assert resultado["disciplines"] is None
    assert "igual para todas as disciplinas" in resultado["discipline_note"]
    assert "D1" in resultado["discipline_note"]


@pytest.mark.dataset("synthetic_v1")
def test_synthetic_valida_os_alunos_por_faixa(artifact_roots) -> None:
    resultado = evaluate(artifact_roots, "synthetic_v1", metric="degree")

    faixas = resultado["students"]
    assert faixas is not None and len(faixas) == 4
    assert sum(linha["n_students"] for linha in faixas) == 98
    # O grau das disciplinas em K₇ também é todo igual.
    assert resultado["disciplines"] is None


@pytest.mark.dataset("synthetic_v1")
def test_figura_e_legenda_sao_gravadas(artifact_roots, tmp_path) -> None:
    from edugraph.centrality.evaluate import figure_outcome_by_quantile

    faixas = evaluate(artifact_roots, "synthetic_v1", metric="degree")["students"]
    escritos = figure_outcome_by_quantile(
        faixas,
        dataset="synthetic_v1",
        projection_id="student_simple",
        metric="degree",
        out=tmp_path,
    )

    assert {p.suffix for p in escritos} == {".png", ".svg", ".txt"}
    assert all(p.exists() for p in escritos)
    assert "a posteriori" in (
        tmp_path / "fig8-validacao-synthetic_v1-student_simple-degree.caption.txt"
    ).read_text(encoding="utf-8")
