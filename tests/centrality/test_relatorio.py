"""Relatório interno  ``[C]`` — spec C-07.

O relatório é a saída que sai da equipe técnica: quem o lê não programa
e não pode encontrar nele nenhum aluno. Os testes protegem as três
coisas que a spec exige — limitações presentes, nenhum id de aluno,
dataset incompleto sem quebra — e o determinismo.
"""

from __future__ import annotations

import re

import pytest

from edugraph.centrality.report import build_internal_report, check_no_student_ids
from edugraph.contracts.errors import ContractError


@pytest.mark.dataset("synthetic_v1")
def test_relatorio_e_escrito_com_as_secoes(artifact_roots, tmp_path) -> None:
    path = build_internal_report("synthetic_v1", list(artifact_roots), tmp_path)
    texto = path.read_text(encoding="utf-8")

    assert path.name == "relatorio-interno-synthetic_v1.md"
    for secao in (
        "## Os dados",
        "## Comunidades",
        "## Disciplinas críticas",
        "## Relação com o desfecho histórico",
        "## O que esta análise não diz",
    ):
        assert secao in texto
    assert (tmp_path / "figures" / "fig7-disciplinas-synthetic_v1-discipline_simple.png").exists()


@pytest.mark.dataset("synthetic_v1")
def test_limitacoes_dizem_o_que_a_centralidade_nao_diz(artifact_roots, tmp_path) -> None:
    texto = build_internal_report("synthetic_v1", list(artifact_roots), tmp_path).read_text(
        encoding="utf-8"
    )
    limitacoes = texto.split("## O que esta análise não diz", 1)[1]

    assert "Não é um ranking de alunos" in limitacoes
    assert "não quer dizer disciplina difícil" in limitacoes
    assert "Uso exclusivamente interno" in limitacoes


@pytest.mark.dataset("synthetic_v1")
def test_nenhum_aluno_aparece_por_id_nem_por_rotulo(artifact_roots, tmp_path) -> None:
    """Contrato da restrição de uso interno: só agregados."""
    from edugraph.contracts import io

    texto = build_internal_report("synthetic_v1", list(artifact_roots), tmp_path).read_text(
        encoding="utf-8"
    )
    bipartido = io.load_bipartite(artifact_roots, "synthetic_v1")
    alunos = {
        (str(n), str(d.get("label", n)))
        for n, d in bipartido.graph.nodes(data=True)
        if d.get("kind") == "student"
    }
    palavras = set(re.findall(r"\b\w+\b", texto))
    citados = sorted(ident for no, rotulo in alunos for ident in (no, rotulo) if ident in palavras)
    assert citados == []


@pytest.mark.dataset("synthetic_v1")
def test_degeneracao_do_k7_e_avisada(artifact_roots, tmp_path) -> None:
    texto = build_internal_report("synthetic_v1", list(artifact_roots), tmp_path).read_text(
        encoding="utf-8"
    )
    assert "igual para todas as disciplinas" in texto


@pytest.mark.dataset("tiny_v1")
def test_dataset_incompleto_omite_a_secao_com_nota(artifact_roots, tmp_path) -> None:
    """``tiny_v1`` não tem partição nem centralidade em disco: não quebra."""
    texto = build_internal_report("tiny_v1", list(artifact_roots), tmp_path).read_text(
        encoding="utf-8"
    )
    assert "Nenhuma partição em disco" in texto
    assert "Sem centralidades de disciplina em disco" in texto
    assert "## O que esta análise não diz" in texto


@pytest.mark.dataset("synthetic_v1")
def test_rodar_duas_vezes_produz_o_mesmo_arquivo(artifact_roots, tmp_path) -> None:
    primeiro = build_internal_report("synthetic_v1", list(artifact_roots), tmp_path / "a")
    segundo = build_internal_report("synthetic_v1", list(artifact_roots), tmp_path / "b")
    assert primeiro.read_bytes() == segundo.read_bytes()


def test_texto_com_id_de_aluno_e_recusado() -> None:
    with pytest.raises(ContractError, match="S100001"):
        check_no_student_ids("A comunidade 2 inclui S100001.", {"S100001", "S100002"})
    check_no_student_ids("Nenhum aluno aqui; disciplina DDD_2014J.", {"S100001"})


def test_dataset_inexistente_e_recusado(artifact_roots, tmp_path) -> None:
    from edugraph.contracts.errors import ArtifactNotFoundError

    with pytest.raises(ArtifactNotFoundError, match="nao_existe"):
        build_internal_report("nao_existe", list(artifact_roots), tmp_path)
