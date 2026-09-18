"""ETL do OULAD  ``[A]`` — spec A-02 (fechada contra ``oulad_mini``).

Tudo aqui roda sobre ``tests/data/oulad_mini/``: sete arquivos com o
esquema real e valores inventados de propósito para exercitar as
junções, a média ponderada, a soma de cliques e a regra de desfecho.
A rodada sobre a base completa é o passo manual que fica para depois do
download (ver o README e a spec).

Valores esperados, derivados à mão do ``oulad_mini``:

=====  =====  ======  ================================  =======  ==========
aluno  mód.   apres.  nota (ponderada por ``weight``)   cliques  desfecho
=====  =====  ======  ================================  =======  ==========
11391  AAA    2013J   (78·10 + 82·20)/30 = 80,667        4+1 = 5  Pass
28400  AAA    2013J   (70·10 + 64·20)/30 = 66            3        Pass
30268  AAA    2013J   45                                 1        Withdrawn
31604  AAA    2014J   91                                 7        Pass
23629  BBB    2013J   38                                 2        Fail
11391  BBB    2013J   (88·5 + 95·5)/10 = 91,5            9        Distinction
=====  =====  ======  ================================  =======  ==========
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import pandas as pd
import pytest

from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import BipartiteSpec
from edugraph.data.bipartite import build_bipartite
from edugraph.data.oulad import download, etl
from edugraph.data.oulad.schema import SCHEMAS, TABLES, read_table, validate_schema

OULAD_MINI = Path(__file__).parent / "oulad_mini"
KEY = ["id_student", "code_module", "code_presentation"]


def _row(table: pd.DataFrame, student: int, module: str, presentation: str) -> pd.Series:
    mask = (
        (table.id_student == student)
        & (table.code_module == module)
        & (table.code_presentation == presentation)
    )
    assert mask.sum() == 1, f"esperava 1 linha para {student}/{module}/{presentation}"
    return table[mask].iloc[0]


# ---------------------------------------------------------------------
# Esquema
# ---------------------------------------------------------------------


def test_esquema_cobre_as_sete_tabelas() -> None:
    assert set(SCHEMAS) == set(TABLES)
    for name in TABLES:
        read_table(OULAD_MINI, name)  # não levanta


def test_esquema_nao_carrega_atributos_demograficos() -> None:
    """A forma mais segura de não vazar gênero/região/idade é não ler (ADR-0008)."""
    proibidas = {"gender", "region", "age_band", "highest_education", "imd_band", "disability"}
    assert not proibidas & set(SCHEMAS["studentInfo"].usecols)
    assert not proibidas & set(read_table(OULAD_MINI, "studentInfo").columns)


def test_coluna_faltando_nomeia_tabela_e_coluna(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match=r"studentInfo\.csv.*final_result"):
        validate_schema("studentInfo", ["code_module", "code_presentation", "id_student"])

    quebrado = tmp_path / "studentVle.csv"
    quebrado.write_text("code_module,code_presentation,id_student\n", encoding="utf-8")
    with pytest.raises(ContractError, match=r"studentVle\.csv.*sum_click"):
        read_table(tmp_path, "studentVle")


def test_tabela_ausente_aponta_para_o_download(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="download manual"):
        read_table(tmp_path, "studentInfo")


# ---------------------------------------------------------------------
# normalize
# ---------------------------------------------------------------------


def test_etl_produz_a_tabela_normalizada() -> None:
    """Sete tabelas → uma linha por (aluno, módulo, apresentação)."""
    table = etl.normalize(OULAD_MINI)

    assert list(table.columns) == list(etl.NORMALIZED_COLUMNS)
    assert not table.duplicated(subset=KEY).any()
    assert len(table) == 6  # as seis matrículas do studentInfo, todas com evidência


def test_nota_e_media_ponderada_pelo_peso_da_avaliacao() -> None:
    """TMA de 10% e TMA de 20%: a segunda pesa o dobro."""
    table = etl.normalize(OULAD_MINI)

    assert _row(table, 11391, "AAA", "2013J").score_media == pytest.approx((78 * 10 + 82 * 20) / 30)
    assert _row(table, 28400, "AAA", "2013J").score_media == pytest.approx(66.0)
    assert _row(table, 11391, "BBB", "2013J").score_media == pytest.approx(91.5)
    assert _row(table, 30268, "AAA", "2013J").score_media == pytest.approx(45.0)
    assert bool(_row(table, 11391, "AAA", "2013J").score_weighted) is True
    assert _row(table, 11391, "AAA", "2013J").n_assessments == 2


def test_media_simples_quando_todos_os_pesos_sao_zero(tmp_path: Path) -> None:
    """CMAs sem peso não podem zerar a nota: cai para a média simples, marcada."""
    shutil.copytree(OULAD_MINI, tmp_path / "raw")
    assessments = tmp_path / "raw" / "assessments.csv"
    txt = assessments.read_text(encoding="utf-8").replace("14984,TMA,19,5.0", "14984,TMA,19,0.0")
    txt = txt.replace("14985,CMA,33,5.0", "14985,CMA,33,0.0")
    assessments.write_text(txt, encoding="utf-8")

    table = etl.normalize(tmp_path / "raw")
    linha = _row(table, 11391, "BBB", "2013J")
    assert linha.score_media == pytest.approx((88 + 95) / 2)
    assert bool(linha.score_weighted) is False


def test_cliques_sao_somados_por_matricula() -> None:
    table = etl.normalize(OULAD_MINI)
    assert _row(table, 11391, "AAA", "2013J").sum_click == 5
    assert _row(table, 11391, "BBB", "2013J").sum_click == 9
    assert _row(table, 31604, "AAA", "2014J").sum_click == 7


def test_leitura_em_blocos_agrega_igual() -> None:
    """``chunksize=2`` obriga a agregação a atravessar blocos — mesmo resultado."""
    inteiro = etl.normalize(OULAD_MINI)
    em_blocos = etl.normalize(OULAD_MINI, chunksize=2)
    pd.testing.assert_frame_equal(inteiro, em_blocos)


def test_matricula_sem_nota_e_sem_clique_e_descartada(tmp_path: Path) -> None:
    shutil.copytree(OULAD_MINI, tmp_path / "raw")
    info = tmp_path / "raw" / "studentInfo.csv"
    with info.open("a", encoding="utf-8") as handle:
        handle.write("AAA,2013J,99999,M,X,X,X,X,0,60,N,Withdrawn\n")

    table = etl.normalize(tmp_path / "raw")
    assert 99999 not in set(table.id_student)
    assert len(table) == 6


def test_desfecho_viaja_na_tabela_mas_nao_no_grafo() -> None:
    """A-02 entrega ``final_result``; A-03 não o grava no nó (ADR-0008)."""
    table = etl.normalize(OULAD_MINI)
    assert set(table.final_result) == {"Pass", "Withdrawn", "Fail", "Distinction"}

    bundle = build_bipartite(table, BipartiteSpec(dataset="mini", threshold=40.0))
    for _, data in bundle.graph.nodes(data=True):
        assert set(data) <= {"kind", "label"}
    assert bundle.graph.has_edge("S11391", "DAAA")
    assert not bundle.graph.has_edge("S23629", "DBBB")  # 38 < 40


# ---------------------------------------------------------------------
# cache
# ---------------------------------------------------------------------


def test_cache_e_reusado_e_expira_quando_a_fonte_muda(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = tmp_path / "raw"
    shutil.copytree(OULAD_MINI, raw)
    cache = tmp_path / "interim"

    primeiro = etl.normalize(raw, cache_dir=cache)
    assert (cache / "oulad_normalized.csv").exists()
    assert (cache / "oulad_normalized.meta.json").exists()

    # Sem mudança na fonte: responde do cache e o studentVle nem é lido —
    # se a agregação de cliques for chamada, o teste explode aqui.
    def _nao_devia_ler(*_: object, **__: object) -> pd.DataFrame:
        raise AssertionError("studentVle.csv foi relido apesar do cache válido")

    monkeypatch.setattr(etl, "_clicks", _nao_devia_ler)
    segundo = etl.normalize(raw, cache_dir=cache)
    monkeypatch.undo()
    pd.testing.assert_frame_equal(primeiro, segundo, check_dtype=False)

    # Fonte alterada: o carimbo muda e o cache é recalculado.
    time.sleep(0.01)
    vle = raw / "studentVle.csv"
    vle.write_text(
        vle.read_text(encoding="utf-8") + "AAA,2013J,11391,546943,-9,100\n", encoding="utf-8"
    )
    terceiro = etl.normalize(raw, cache_dir=cache)
    assert _row(terceiro, 11391, "AAA", "2013J").sum_click == 105


# ---------------------------------------------------------------------
# normalize_assessments e to_outcomes
# ---------------------------------------------------------------------


def test_tabela_por_avaliacao() -> None:
    fine = etl.normalize_assessments(OULAD_MINI)
    assert list(fine.columns) == list(etl.ASSESSMENT_COLUMNS)
    assert len(fine) == 9  # nove entregas em studentAssessment
    assert not fine.duplicated(subset=["id_student", "id_assessment"]).any()

    bundle = build_bipartite(
        fine, BipartiteSpec(dataset="mini", granularity="assessment", threshold=40.0)
    )
    assert "D1752" in bundle.graph and "D14984" in bundle.graph


def test_um_desfecho_por_aluno_pela_apresentacao_mais_recente() -> None:
    """11391 tem AAA (Pass) e BBB (Distinction) em 2013J: empate → módulo maior."""
    outcomes = etl.to_outcomes(etl.normalize(OULAD_MINI))

    assert set(outcomes) == {"S11391", "S28400", "S30268", "S31604", "S23629"}
    assert outcomes["S11391"] == "Distinction"
    assert outcomes["S30268"] == "Withdrawn"


def test_apresentacao_mais_recente_vence() -> None:
    table = pd.DataFrame(
        [
            {"id_student": 1, "code_module": "ZZZ", "code_presentation": "2013J", "final_result": "Fail"},
            {"id_student": 1, "code_module": "AAA", "code_presentation": "2014B", "final_result": "Pass"},
        ]
    )  # fmt: skip
    assert etl.to_outcomes(table) == {"S1": "Pass"}  # 2014B > 2013J, apesar de AAA < ZZZ


# ---------------------------------------------------------------------
# download / verify
# ---------------------------------------------------------------------


def test_verify_aceita_o_mini_e_recusa_diretorio_vazio(tmp_path: Path) -> None:
    assert download.verify(OULAD_MINI) is True
    assert download.verify(tmp_path) is False
    with pytest.raises(ContractError, match="incompleto"):
        download.verify(tmp_path, strict=True)


def test_download_nao_rebaixa_o_que_ja_e_valido(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """Com os sete CSV válidos e sem ``--force``, não toca a rede."""
    dest = tmp_path / "oulad"
    shutil.copytree(OULAD_MINI, dest)
    assert download.download(dest) == dest
    assert "já presente" in capsys.readouterr().out


def test_sha256_sem_referencia_avisa_em_vez_de_falhar(tmp_path: Path) -> None:
    arquivo = tmp_path / "x.zip"
    arquivo.write_bytes(b"conteudo")
    assert download.OULAD_SHA256 == "", "quando preencher, troque este teste pela comparação"
    with pytest.warns(RuntimeWarning, match="OULAD_SHA256 vazio"):
        digest = download._check_sha256(arquivo)
    assert digest == download.sha256_of(arquivo)


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------


def test_data_etl_roda_sobre_o_mini(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from edugraph.__main__ import main

    code = main(["data", "etl", "--raw", str(OULAD_MINI), "--cache", str(tmp_path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "6 matrículas de 5 alunos" in out
    assert (tmp_path / "oulad_normalized.csv").exists()
    assert (tmp_path / "oulad_assessments.csv").exists()
