"""Projeções à mão  ``[A]`` — specs A-04 e A-05.

Todos ``xfail(strict=True)``: falham hoje porque a implementação é stub,
e **passam a falhar por passarem** quando a spec fechar — é o que avisa
o Pedro de que pode tirar o marcador.

Os valores esperados vêm de ``data/fixtures/tiny_v1/expected/``, que foi
derivado no papel (ver o README de lá). Comparar a implementação com a
fixture gerada pelo NetworkX seria comparar duas bibliotecas; comparar
com a derivação à mão é verificar o algoritmo.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from edugraph.contracts.types import BipartiteBundle, ProjectionSpec
from edugraph.data.projection.manual import (
    ResourceAllocationProjection,
    SimpleProjection,
)

pytestmark = pytest.mark.dataset("tiny_v1")


def _expected_edges(path: Path) -> dict[tuple[str, str], float]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {
            (row["source"], row["target"]): float(row["weight"]) for row in csv.DictReader(handle)
        }


@pytest.mark.xfail(reason="A-04 não implementada", raises=NotImplementedError, strict=True)
def test_projecao_simples_aluno_bate_com_o_calculo_a_mao(
    tiny_bipartite: BipartiteBundle, tiny_expected: Path
) -> None:
    """Pesos de ``student_simple`` = nº de disciplinas em comum."""
    spec = ProjectionSpec(side="student", weighting="simple")
    bundle = SimpleProjection().project(tiny_bipartite, spec)

    esperado = _expected_edges(tiny_expected / "student_simple.csv")
    obtido = {tuple(sorted((u, v))): data["weight"] for u, v, data in bundle.graph.edges(data=True)}
    assert obtido == pytest.approx(esperado)


@pytest.mark.xfail(reason="A-04 não implementada", raises=NotImplementedError, strict=True)
def test_alocacao_de_recursos_bate_com_o_calculo_a_mao(
    tiny_bipartite: BipartiteBundle, tiny_expected: Path
) -> None:
    """Cada vizinho comum contribui com ``1/grau`` (Zhou et al., 2007)."""
    spec = ProjectionSpec(side="student", weighting="resource_allocation")
    bundle = ResourceAllocationProjection().project(tiny_bipartite, spec)

    esperado = _expected_edges(tiny_expected / "student_resource_allocation.csv")
    obtido = {tuple(sorted((u, v))): data["weight"] for u, v, data in bundle.graph.edges(data=True)}
    assert obtido == pytest.approx(esperado)


@pytest.mark.xfail(reason="A-04 não implementada", raises=NotImplementedError, strict=True)
def test_projecao_disciplina_disciplina_existe(
    tiny_bipartite: BipartiteBundle, tiny_expected: Path
) -> None:
    """A projeção do lado das disciplinas — a seção 13 do briefing avisa
    que é fácil esquecer dela, e é ela que responde às disciplinas críticas."""
    spec = ProjectionSpec(side="discipline", weighting="simple")
    bundle = SimpleProjection().project(tiny_bipartite, spec)

    esperado = _expected_edges(tiny_expected / "discipline_simple.csv")
    obtido = {tuple(sorted((u, v))): data["weight"] for u, v, data in bundle.graph.edges(data=True)}
    assert obtido == pytest.approx(esperado)


@pytest.mark.xfail(reason="A-04 não implementada", raises=NotImplementedError, strict=True)
def test_as_duas_ponderacoes_ordenam_pares_de_forma_diferente(
    tiny_bipartite: BipartiteBundle,
) -> None:
    """O ponto da alocação de recursos, em um teste.

    Em ``tiny_v1``, S1-S6 e S3-S4 empatam em 1 na projeção simples. Na
    alocação de recursos, S1-S6 = 0,25 e S3-S4 = 1/3: a disciplina rara
    (DC, grau 3) vale mais que a popular (DA, grau 4). Se este teste
    passar a falhar, a correção de viés se perdeu.
    """
    simples = SimpleProjection().project(
        tiny_bipartite, ProjectionSpec(side="student", weighting="simple")
    )
    ra = ResourceAllocationProjection().project(
        tiny_bipartite, ProjectionSpec(side="student", weighting="resource_allocation")
    )

    assert simples.graph["S1"]["S6"]["weight"] == simples.graph["S3"]["S4"]["weight"]
    assert ra.graph["S1"]["S6"]["weight"] < ra.graph["S3"]["S4"]["weight"]


@pytest.mark.xfail(reason="A-05 não implementada", raises=NotImplementedError, strict=True)
def test_manual_e_networkx_batem_ate_1e9(tiny_bipartite: BipartiteBundle) -> None:
    """A comparação que vira tabela do capítulo 3 (ADR-0010)."""
    from edugraph.data.projection.compare import TOLERANCE, compare
    from edugraph.data.projection.networkx_ref import NetworkXSimpleProjection

    spec = ProjectionSpec(side="student", weighting="simple")
    resultado = compare(
        SimpleProjection().project(tiny_bipartite, spec),
        NetworkXSimpleProjection().project(tiny_bipartite, spec),
    )
    assert resultado["max_abs_diff"] < TOLERANCE
    assert resultado["equal_within_tolerance"] is True
