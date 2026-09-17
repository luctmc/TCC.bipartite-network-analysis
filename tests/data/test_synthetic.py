"""Gerador sintético  ``[A]`` — spec A-01.

O gerador é o único código da Frente A que já funciona no dia 0: é dele
que saem as fixtures. Estes testes valem agora, não são ``xfail``.
"""

from __future__ import annotations

import pytest

from edugraph.data.synthetic import DEFAULT_GROUPS, SyntheticSpec, generate


def test_gerador_e_deterministico() -> None:
    """Mesma seed, mesmas matrículas — byte a byte."""
    primeiro = generate(SyntheticSpec(seed=42))
    segundo = generate(SyntheticSpec(seed=42))

    assert primeiro.enrollments == segundo.enrollments
    assert primeiro.planted_group == segundo.planted_group
    assert primeiro.final_result == segundo.final_result


def test_seeds_diferentes_dao_dados_diferentes() -> None:
    """Sem isto, o determinismo acima poderia ser um gerador quebrado."""
    assert (
        generate(SyntheticSpec(seed=42)).enrollments != generate(SyntheticSpec(seed=7)).enrollments
    )


def test_planta_tres_grupos_de_quarenta() -> None:
    """A estrutura plantada é o *ground truth* das specs B-06 e C-06."""
    dataset = generate(SyntheticSpec(seed=42))

    assert dataset.n_students == 120
    tamanhos = {
        grupo: sum(1 for g in dataset.planted_group.values() if g == grupo)
        for grupo in set(dataset.planted_group.values())
    }
    assert tamanhos == {0: 40, 1: 40, 2: 40}


def test_alunos_cursam_de_dois_a_cinco_modulos() -> None:
    """2 a 4 do próprio grupo, mais 0 ou 1 de fora (o ruído)."""
    dataset = generate(SyntheticSpec(seed=42))

    por_aluno: dict[object, int] = {}
    for row in dataset.enrollments:
        por_aluno[row["id_student"]] = por_aluno.get(row["id_student"], 0) + 1

    assert min(por_aluno.values()) >= 2
    assert max(por_aluno.values()) <= 5


def test_ha_ruido_entre_grupos() -> None:
    """Sem ruído, as comunidades seriam perfeitas e o teste da B-06 seria vazio."""
    dataset = generate(SyntheticSpec(seed=42))
    modulos_por_grupo = list(DEFAULT_GROUPS.values())

    fora_do_grupo = 0
    for row in dataset.enrollments:
        student = f"S{row['id_student']}"
        grupo = dataset.planted_group[student]
        if row["code_module"] not in modulos_por_grupo[grupo]:
            fora_do_grupo += 1

    assert fora_do_grupo > 0, "sem ruído, a validação de comunidades seria trivial"


def test_desfechos_usam_o_vocabulario_do_oulad() -> None:
    """``final_result`` só admite os quatro valores do dataset real."""
    dataset = generate(SyntheticSpec(seed=42))
    assert set(dataset.final_result.values()) <= {"Pass", "Distinction", "Fail", "Withdrawn"}


def test_esparsidade_ainda_nao_implementada() -> None:
    """A extensão da A-01 falha com a mensagem certa, não silenciosamente."""
    with pytest.raises(NotImplementedError, match="A-01"):
        generate(SyntheticSpec(seed=42, sparsity=0.5))
