"""Figuras de comunidades  ``[B]`` — spec B-07.

Sem teste de aparência: comparar imagem é frágil e não paga. O que se
testa é que os arquivos saem nos dois formatos, **com os mesmos bytes a
cada execução**, que a legenda declara o que foi feito com o grafo, e
que os tamanhos de comunidade batem com a conta à mão.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx
import pytest

from edugraph.community.characterize import community_sizes
from edugraph.community.louvain import LouvainAlgorithm
from edugraph.community.report import (
    AGGREGATE_ABOVE,
    LAYOUT_SEED,
    PALETTE_NAME,
    community_colors,
    figure_communities,
    figure_q_vs_time,
    figure_size_distribution,
    sizes_table,
)
from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import BipartiteSpec, Partition, ProjectionBundle, ProjectionSpec


def _blocos(n_por_bloco: int, blocos: int, *, seed: int = 0) -> tuple[ProjectionBundle, Partition]:
    """Projeção sintética com blocos evidentes, para os casos de borda."""
    import random

    rng = random.Random(seed)
    graph: nx.Graph[Any] = nx.Graph()
    membership: dict[str, int] = {}
    for bloco in range(blocos):
        nodes = [f"S{bloco:02d}{i:04d}" for i in range(n_por_bloco)]
        for node in nodes:
            graph.add_node(node, kind="student", label=node)
            membership[node] = bloco
        for _ in range(n_por_bloco * 2):
            a, b = rng.sample(nodes, 2)
            graph.add_edge(a, b, weight=1.0)
    for bloco in range(blocos - 1):
        graph.add_edge(f"S{bloco:02d}0000", f"S{bloco + 1:02d}0000", weight=1.0)

    projection = ProjectionBundle(
        graph=graph,
        spec=ProjectionSpec(side="student", weighting="simple"),
        source=BipartiteSpec(dataset="blocos"),
    )
    partition = Partition(
        algorithm="louvain",
        projection_id="student_simple",
        membership=membership,
        modularity=0.6,
        n_communities=blocos,
        runtime_s=0.5,
    )
    return projection, partition


# ---------------------------------------------------------------------
# figure_communities
# ---------------------------------------------------------------------


@pytest.mark.dataset("tiny_v1")
def test_figura_sai_em_png_e_svg_com_legenda(tiny_projection, tmp_path: Path) -> None:
    projection = tiny_projection("student_simple")
    partition = LouvainAlgorithm().run(projection, seed=42)

    png = figure_communities(partition, projection, tmp_path)

    assert png.name == "fig4-comunidades-tiny_v1-louvain__student_simple.png"
    assert png.stat().st_size > 0
    assert png.with_suffix(".svg").exists()

    legenda = (tmp_path / f"{png.stem}.caption.txt").read_text(encoding="utf-8")
    assert PALETTE_NAME in legenda
    assert f"semente {LAYOUT_SEED}" in legenda
    assert "escala de cinza" in legenda
    assert "agregada" not in legenda  # grafo pequeno: desenhou tudo


@pytest.mark.dataset("tiny_v1")
def test_figura_e_deterministica(tiny_projection, tmp_path: Path) -> None:
    """Rodar duas vezes produz os mesmos bytes (layout com seed fixa)."""
    projection = tiny_projection("student_simple")
    partition = LouvainAlgorithm().run(projection, seed=42)

    a = figure_communities(partition, projection, tmp_path / "a")
    b = figure_communities(partition, projection, tmp_path / "b")

    assert a.read_bytes() == b.read_bytes()
    assert a.with_suffix(".svg").read_bytes() == b.with_suffix(".svg").read_bytes()


def test_grafo_grande_e_agregado_e_a_legenda_diz(tmp_path: Path) -> None:
    """Acima do limite, uma bolha por comunidade — desenhar 600 pontos não comunica."""
    projection, partition = _blocos(200, 3)
    assert projection.graph.number_of_nodes() > AGGREGATE_ABOVE

    png = figure_communities(partition, projection, tmp_path)
    legenda = (tmp_path / f"{png.stem}.caption.txt").read_text(encoding="utf-8")

    assert "agregada" in legenda
    assert f"{projection.graph.number_of_nodes()} no total" in legenda


def test_layout_desconhecido_e_erro(tmp_path: Path) -> None:
    projection, partition = _blocos(5, 2)
    with pytest.raises(ContractError, match="layout"):
        figure_communities(partition, projection, tmp_path, layout="forca_bruta")


@pytest.mark.dataset("tiny_v1")
def test_particao_de_outra_projecao_nao_vira_figura(tiny_projection, tmp_path: Path) -> None:
    """Nó sem comunidade não teria cor — melhor recusar que desenhar errado."""
    projection = tiny_projection("student_simple")
    parcial = Partition(
        algorithm="girvan_newman",
        projection_id="student_simple",
        membership={"S1": 0, "S2": 0},
        modularity=0.0,
        n_communities=1,
        runtime_s=1.0,
    )
    with pytest.raises(ContractError, match="não cobre os nós"):
        figure_communities(parcial, projection, tmp_path)


def test_cores_sao_distintas_e_da_paleta_registrada() -> None:
    cores = community_colors(5)
    assert len(cores) == 5
    assert len({tuple(c) for c in cores}) == 5
    # Luminância monotônica é o que garante a distinção em preto e branco.
    luminancias = [0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b, _ in cores]
    assert luminancias == sorted(luminancias)


# ---------------------------------------------------------------------
# figure_size_distribution
# ---------------------------------------------------------------------


@pytest.mark.dataset("tiny_v1")
def test_tamanhos_de_tiny_batem_com_a_conta_a_mao(tiny_projection) -> None:
    """K4 {S1,S2,S3,S6} colado ao triângulo {S3,S4,S5}: 4 e 2."""
    partition = LouvainAlgorithm().run(tiny_projection("student_simple"), seed=42)
    assert community_sizes(partition) == {0: 4, 1: 2}


@pytest.mark.dataset("synthetic_v1")
def test_distribuicao_de_tamanhos_sai_nos_dois_formatos(
    synthetic_projection, tmp_path: Path
) -> None:
    projection = synthetic_projection("student_simple")
    partitions = [
        LouvainAlgorithm().run(projection, seed=42),
        LouvainAlgorithm().run(projection, seed=7, resolution=2.0),
    ]

    png = figure_size_distribution(partitions, tmp_path, dataset="synthetic_v1")

    assert png.name == "fig5-tamanhos-synthetic_v1.png"
    assert png.with_suffix(".svg").exists()
    legenda = (tmp_path / f"{png.stem}.caption.txt").read_text(encoding="utf-8")
    assert "um painel por algoritmo" in legenda


def test_distribuicao_sem_particao_e_erro(tmp_path: Path) -> None:
    with pytest.raises(ContractError):
        figure_size_distribution([], tmp_path)


# ---------------------------------------------------------------------
# figure_q_vs_time
# ---------------------------------------------------------------------


def test_q_por_tempo_sai_com_a_razao_na_legenda(tmp_path: Path) -> None:
    _, louvain = _blocos(5, 2)
    girvan = Partition(
        algorithm="girvan_newman",
        projection_id="student_simple",
        membership=dict(louvain.membership),
        modularity=0.4,
        n_communities=2,
        runtime_s=50.0,
        status="timeout",
    )

    png = figure_q_vs_time([louvain, girvan], tmp_path, dataset="blocos")
    legenda = (tmp_path / f"{png.stem}.caption.txt").read_text(encoding="utf-8")

    assert png.name == "fig6-q-tempo-blocos.png"
    assert "100× o tempo" in legenda
    assert "ADR-0006" in legenda


def test_particoes_sem_tempo_medido_ficam_de_fora(tmp_path: Path) -> None:
    """As fixtures de referência gravam ``runtime_s = 0``; 1e-6 no eixo log mentiria."""
    _, medida = _blocos(5, 2)
    sem_tempo = Partition(
        algorithm="girvan_newman",
        projection_id="student_simple",
        membership=dict(medida.membership),
        modularity=0.3,
        n_communities=2,
        runtime_s=0.0,
    )

    png = figure_q_vs_time([medida, sem_tempo], tmp_path, dataset="blocos")
    legenda = (tmp_path / f"{png.stem}.caption.txt").read_text(encoding="utf-8")
    assert "1 partições sem tempo medido" in legenda

    with pytest.raises(ContractError, match="tempo medido"):
        figure_q_vs_time([sem_tempo], tmp_path)


def test_tabela_de_tamanhos_acompanha_a_figura() -> None:
    """A figura mostra; a tabela permite conferir."""
    _, partition = _blocos(3, 2)
    linhas = sizes_table([partition])

    assert len(linhas) == 2
    assert {linha["size"] for linha in linhas} == {3}
    assert linhas[0]["algorithm"] == "louvain"


# ---------------------------------------------------------------------
# CLI e índice
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
def test_figures_pela_cli_gera_as_tres_figuras(tmp_path: Path, capsys) -> None:
    from edugraph.__main__ import main

    saida = tmp_path / "figuras"
    assert main(["community", "louvain", "--root", "data/fixtures", "--dataset", "synthetic_v1",
                 "--projection", "student_simple", "--out", str(tmp_path)]) == 0  # fmt: skip
    capsys.readouterr()

    # Duas raízes, como na vida real: a partição saiu para tmp_path, a
    # projeção continua na fixture. ``--partition`` restringe às que
    # interessam, em vez de desenhar também as de referência da fixture.
    code = main(["community", "figures", "--root", str(tmp_path), "--root", "data/fixtures",
                 "--dataset", "synthetic_v1", "--partition", "louvain__student_simple",
                 "--out", str(saida)])  # fmt: skip

    assert code == 0
    nomes = sorted(p.name for p in saida.glob("*.png"))
    assert nomes == [
        "fig4-comunidades-synthetic_v1-louvain__student_simple.png",
        "fig5-tamanhos-synthetic_v1.png",
        "fig6-q-tempo-synthetic_v1.png",
    ]
    assert len(list(saida.glob("*.svg"))) == 3


@pytest.mark.dataset("synthetic_v1")
def test_figuras_entram_no_indice_do_artigo(tmp_path: Path) -> None:
    """Critério de aceite da B-07: o índice é regenerado e inclui as novas."""
    from edugraph.reporting.figures import build_index

    projection = io.load_projection(["data/fixtures"], "synthetic_v1", "student_simple")
    partition = LouvainAlgorithm().run(projection, seed=42)
    figure_communities(partition, projection, tmp_path)
    figure_size_distribution([partition], tmp_path, dataset="synthetic_v1")

    texto = build_index(tmp_path, tmp_path / "indice.md").read_text(encoding="utf-8")

    assert "| 4 | Comunidades na projeção aluno↔aluno | B-07 | presente |" in texto
    assert "| 5 | Distribuição de tamanhos de comunidade | B-07 | presente |" in texto
    assert "| 6 | Q × tempo por algoritmo | B-04/B-07 | pendente |" in texto
