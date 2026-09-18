"""Gerador sintético  ``[A]`` — spec A-01 (fechada).

O gerador é a base secundária do briefing §8: comunidades plantadas de
propósito servem de *ground truth* para verificar se os algoritmos
recuperam estrutura conhecida. A A-01 acrescentou a esparsidade tipo
OULAD e os grupos configuráveis; o caminho sem esparsidade é o do dia 0
e continua reproduzindo ``synthetic_v1`` byte a byte.
"""

from __future__ import annotations

import statistics
from pathlib import Path

import pytest

from edugraph.data.synthetic import (
    DEFAULT_GROUPS,
    SyntheticDataset,
    SyntheticSpec,
    generate,
    make_groups,
)

REPO = Path(__file__).resolve().parents[2]


def _por_aluno(dataset: SyntheticDataset) -> dict[object, int]:
    contagem: dict[object, int] = {}
    for row in dataset.enrollments:
        contagem[row["id_student"]] = contagem.get(row["id_student"], 0) + 1
    return contagem


def _fracao_no_proprio_grupo(dataset: SyntheticDataset, groups: dict) -> float:
    modulos = list(groups.values())
    dentro = 0
    for row in dataset.enrollments:
        grupo = dataset.planted_group[f"S{row['id_student']}"]
        dentro += row["code_module"] in modulos[grupo]
    return dentro / len(dataset.enrollments)


# ---------------------------------------------------------------------
# O caminho do dia 0 não mudou
# ---------------------------------------------------------------------


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


def test_sem_esparsidade_continua_igual_ao_dia_zero() -> None:
    """300 matrículas com seed 42: é o que gerou ``synthetic_v1``.

    A A-01 só pode sortear números novos quando ``sparsity`` está ligada;
    senão o fluxo do gerador muda e a fixture deixa de ser reproduzível.
    """
    dataset = generate(SyntheticSpec(seed=42))
    assert len(dataset.enrollments) == 300
    assert generate(SyntheticSpec(seed=42, sparsity=0.0)).enrollments == dataset.enrollments


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
    contagem = _por_aluno(generate(SyntheticSpec(seed=42)))
    assert min(contagem.values()) >= 2
    assert max(contagem.values()) <= 5


def test_ha_ruido_entre_grupos() -> None:
    """Sem ruído, as comunidades seriam perfeitas e o teste da B-06 seria vazio."""
    dataset = generate(SyntheticSpec(seed=42))
    assert _fracao_no_proprio_grupo(dataset, DEFAULT_GROUPS) < 1.0


def test_desfechos_usam_o_vocabulario_do_oulad() -> None:
    """``final_result`` só admite os quatro valores do dataset real."""
    dataset = generate(SyntheticSpec(seed=42))
    assert set(dataset.final_result.values()) <= {"Pass", "Distinction", "Fail", "Withdrawn"}


# ---------------------------------------------------------------------
# A-01 — esparsidade tipo OULAD
# ---------------------------------------------------------------------


def test_esparsidade_reduz_matriculas_por_aluno() -> None:
    """A fração de alunos com uma só matrícula acompanha ``sparsity``.

    Medido com seed 42: base (mediana 2, ninguém com uma só) → 0,5 deixa
    48% com uma só e a mediana ainda em 2 (fronteira) → 0,7 leva a
    mediana a 1 com 68%. É por isso que ``synthetic_v2`` usa 0,7: é o
    menor valor que produz o perfil do OULAD, onde a maioria tem uma.
    """
    denso = _por_aluno(generate(SyntheticSpec(seed=42)))
    meio = _por_aluno(generate(SyntheticSpec(seed=42, sparsity=0.5)))
    esparso = _por_aluno(generate(SyntheticSpec(seed=42, sparsity=0.7)))

    def share_single(c: dict[object, int]) -> float:
        return sum(1 for v in c.values() if v == 1) / len(c)

    assert statistics.median(denso.values()) == 2
    assert share_single(denso) == 0.0
    assert 0.4 <= share_single(meio) <= 0.6
    assert statistics.median(esparso.values()) == 1
    assert share_single(esparso) > 0.6
    assert (
        statistics.mean(esparso.values())
        < statistics.mean(meio.values())
        < statistics.mean(denso.values())
    )


def test_esparsidade_nao_muda_o_grupo_plantado() -> None:
    """O aluno continua na sua área; só deixa menos evidência no grafo."""
    denso = generate(SyntheticSpec(seed=42))
    esparso = generate(SyntheticSpec(seed=42, sparsity=0.7))

    assert esparso.planted_group == denso.planted_group
    assert esparso.n_students == 120
    assert all(c >= 1 for c in _por_aluno(esparso).values())


def test_esparsidade_alta_preserva_o_sinal_das_areas() -> None:
    """Mesmo com 70% dos alunos reduzidos, a matrícula que sobra tende a ser da área.

    É o que torna o grupo plantado ainda recuperável (proxy estrutural;
    a medida oficial, NMI, é da spec B-06). Se um dia isto cair abaixo
    do limiar, é achado de limitação e vai para o texto — não é bug.
    """
    esparso = generate(SyntheticSpec(seed=42, sparsity=0.7))
    assert _fracao_no_proprio_grupo(esparso, DEFAULT_GROUPS) > 0.75


def test_esparsidade_e_deterministica() -> None:
    a = generate(SyntheticSpec(seed=42, sparsity=0.7))
    b = generate(SyntheticSpec(seed=42, sparsity=0.7))
    assert a.enrollments == b.enrollments


def test_esparsidade_fora_da_faixa_e_recusada() -> None:
    with pytest.raises(ValueError, match="sparsity"):
        generate(SyntheticSpec(seed=42, sparsity=1.5))


# ---------------------------------------------------------------------
# A-01 — grupos configuráveis
# ---------------------------------------------------------------------


def test_make_groups_distribui_modulos() -> None:
    groups = make_groups(2, 3)
    assert groups == {"grupo_0": ("AAA", "BBB", "CCC"), "grupo_1": ("DDD", "EEE", "FFF")}
    with pytest.raises(ValueError):
        make_groups(0, 3)
    with pytest.raises(ValueError):
        make_groups(9, 3)  # 27 módulos > 26 letras


def test_numero_de_grupos_e_configuravel() -> None:
    groups = make_groups(5, 2)
    dataset = generate(SyntheticSpec(seed=1, groups=groups, students_per_group=10))

    assert dataset.n_students == 50
    assert set(dataset.planted_group.values()) == {0, 1, 2, 3, 4}
    modulos = {row["code_module"] for row in dataset.enrollments}
    assert modulos <= {m for ms in groups.values() for m in ms}


# ---------------------------------------------------------------------
# A-01 — comando `edugraph data synthetic`
# ---------------------------------------------------------------------


def test_data_synthetic_grava_dataset_valido(tmp_path: Path) -> None:
    """``--seed 7 --out DIR`` grava bipartido, outcomes e 4 projeções válidos."""
    from edugraph.__main__ import main
    from edugraph.contracts import io
    from edugraph.contracts.validate import validate_dataset

    code = main(["data", "synthetic", "--seed", "7", "--dataset", "s7",
                 "--sparsity", "0.5", "--out", str(tmp_path)])  # fmt: skip
    assert code == 0

    checked = validate_dataset([tmp_path], "s7")
    assert "bipartite" in checked and "outcomes" in checked
    assert sum(c.startswith("projections/") for c in checked) == 4

    outcomes = io.load_outcomes([tmp_path], "s7")
    assert outcomes.planted_group is not None
    assert set(outcomes.final_result) == io.load_bipartite([tmp_path], "s7").students
