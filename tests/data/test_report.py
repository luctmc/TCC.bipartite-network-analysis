"""Estatísticas e figura do bipartido  ``[A]`` — spec A-07.

Requisito do artigo, não do software (briefing §9): refazer uma figura
tem que ser um comando. Sem teste de aparência — comparar imagem é
frágil e não paga; o que se testa é que os arquivos saem, com os nomes
certos, nos dois formatos, **com os mesmos bytes a cada execução**, e
que a legenda diz quando houve amostragem.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from edugraph.contracts import io
from edugraph.contracts.paths import ArtifactRoots
from edugraph.contracts.types import BipartiteSpec
from edugraph.data.bipartite import build_bipartite, describe
from edugraph.data.report import (
    FIGURE_SAMPLE_SEED,
    STATS_COLUMNS,
    figure_bipartite,
    table_dataset_stats,
)
from edugraph.data.synthetic import SyntheticSpec, generate, make_groups
from edugraph.reporting.figures import PLANNED_FIGURES, build_index

REPO = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------
# describe / tabela
# ---------------------------------------------------------------------


@pytest.mark.dataset("tiny_v1")
def test_describe_tiny_bate_com_os_valores_a_mao(tiny_bipartite) -> None:
    """6 alunos, 3 disciplinas, 10 arestas; densidade 10/18; graus S=10/6, D=10/3."""
    stats = describe(tiny_bipartite)

    assert (stats["n_students"], stats["n_disciplines"], stats["n_edges"]) == (6, 3, 10)
    assert stats["density"] == pytest.approx(10 / 18)
    assert stats["mean_degree_student"] == pytest.approx(10 / 6)
    assert stats["mean_degree_discipline"] == pytest.approx(10 / 3)
    # graus dos alunos: S1=2 S2=2 S3=3 S4=1 S5=1 S6=1 → ordenado 1,1,1,2,2,3
    assert stats["median_degree_student"] == 1  # posição int(0.5*5)=2 → 1
    assert stats["max_degree_student"] == 3
    assert stats["max_degree_discipline"] == 4  # DA


@pytest.mark.dataset("synthetic_v1")
def test_describe_synthetic_v1(artifact_roots: ArtifactRoots) -> None:
    """98 alunos, 7 disciplinas, 197 arestas — os números do REFERENCE.md."""
    stats = describe(io.load_bipartite(artifact_roots, "synthetic_v1"))
    assert (stats["n_students"], stats["n_disciplines"], stats["n_edges"]) == (98, 7, 197)
    assert 0 < stats["density"] < 1


@pytest.mark.dataset("tiny_v1")
def test_linha_da_tabela_carrega_a_especificacao(tiny_bipartite) -> None:
    """A linha diz sob que critério os números valem, não só quanto."""
    row = table_dataset_stats(tiny_bipartite)

    assert list(row) == list(STATS_COLUMNS)
    assert row["dataset"] == "tiny_v1"
    assert row["edge_criterion"] == "score_threshold" and row["threshold"] == 60.0
    assert row["n_edges"] == 10 and isinstance(row["n_edges"], int)
    assert isinstance(row["density"], float)


# ---------------------------------------------------------------------
# figura
# ---------------------------------------------------------------------


@pytest.mark.dataset("tiny_v1")
def test_figura_sai_em_png_e_svg_com_legenda(tiny_bipartite, tmp_path: Path) -> None:
    png = figure_bipartite(tiny_bipartite, tmp_path)

    assert png.name == "fig2-bipartido-tiny_v1.png" and png.stat().st_size > 0
    assert png.with_suffix(".svg").exists()
    caption = (tmp_path / "fig2-bipartido-tiny_v1.caption.txt").read_text(encoding="utf-8")
    assert "6 alunos, 3 disciplinas e 10 arestas" in caption
    assert "amostra" not in caption  # pequeno: desenhou tudo


@pytest.mark.dataset("tiny_v1")
def test_figura_e_deterministica(tiny_bipartite, tmp_path: Path) -> None:
    """Rodar duas vezes produz os mesmos bytes (sem data nos metadados, sem layout aleatório)."""
    a = figure_bipartite(tiny_bipartite, tmp_path / "a")
    b = figure_bipartite(tiny_bipartite, tmp_path / "b")

    assert a.read_bytes() == b.read_bytes()
    assert a.with_suffix(".svg").read_bytes() == b.with_suffix(".svg").read_bytes()


def test_grafo_grande_e_amostrado_e_a_legenda_diz(tmp_path: Path) -> None:
    """Acima do limite, a figura amostra alunos e a legenda declara isso."""
    dataset = generate(
        SyntheticSpec(seed=1, groups=make_groups(4, 2), students_per_group=300)
    )  # 1.200 alunos
    bundle = build_bipartite(
        pd.DataFrame(dataset.enrollments), BipartiteSpec(dataset="g", threshold=0.0)
    )
    assert len(bundle.students) > 1000

    figure_bipartite(bundle, tmp_path, max_students=200)
    caption = (tmp_path / "fig2-bipartido-g.caption.txt").read_text(encoding="utf-8")

    assert f"{len(bundle.students)} alunos" in caption  # o total real, sempre
    assert "amostra determinística de 200 alunos" in caption
    assert f"semente {FIGURE_SAMPLE_SEED}" in caption
    assert "estatísticas do texto referem-se ao grafo completo" in caption


# ---------------------------------------------------------------------
# índice de figuras
# ---------------------------------------------------------------------


def test_indice_cruza_plano_e_disco(tmp_path: Path) -> None:
    figs = tmp_path / "figs"
    figs.mkdir()
    (figs / "fig2-bipartido-x.png").write_bytes(b"png")
    (figs / "fig2-bipartido-x.svg").write_bytes(b"svg")
    (figs / "fig2-bipartido-x.caption.txt").write_text("legenda de teste", encoding="utf-8")
    (figs / "rascunho.png").write_bytes(b"png")

    index = build_index(figs, tmp_path / "indice.md")
    text = index.read_text(encoding="utf-8")

    assert "Arquivo gerado" in text
    assert "| 2 | Grafo bipartido | A-07 | presente | `fig2-bipartido-x.{png,svg}`" in text
    assert "| 4 | Comunidades na projeção aluno↔aluno | B-07 | pendente | — |" in text
    assert "## Fora do plano" in text and "`rascunho` (png)" in text
    assert "**`fig2-bipartido-x`** — legenda de teste" in text
    assert text.count("| pendente |") == len(PLANNED_FIGURES) - 1


def test_indice_sem_figuras_e_todo_pendente(tmp_path: Path) -> None:
    index = build_index(tmp_path / "vazio", tmp_path / "indice.md")
    text = index.read_text(encoding="utf-8")
    assert text.count("| pendente |") == len(PLANNED_FIGURES)
    assert "Fora do plano" not in text


def test_indice_e_deterministico(tmp_path: Path) -> None:
    a = build_index(tmp_path / "vazio", tmp_path / "a.md").read_bytes()
    b = build_index(tmp_path / "vazio", tmp_path / "b.md").read_bytes()
    assert a == b


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------


def test_data_report_grava_tabela_e_figura(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from edugraph.__main__ import main

    code = main(["data", "report", "--root", "data/fixtures", "--dataset", "tiny_v1",
                 "--out", str(tmp_path)])  # fmt: skip
    assert code == 0
    assert (tmp_path / "tables" / "tab1-estatisticas-tiny_v1.csv").exists()
    assert (tmp_path / "figures" / "fig2-bipartido-tiny_v1.png").exists()
    assert (tmp_path / "figures" / "fig2-bipartido-tiny_v1.caption.txt").exists()
    assert "n_edges" in capsys.readouterr().out

    linhas = (
        (tmp_path / "tables" / "tab1-estatisticas-tiny_v1.csv")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    assert linhas[0].split(",") == list(STATS_COLUMNS)
    assert len(linhas) == 2


def test_figures_index_pela_cli(tmp_path: Path) -> None:
    from edugraph.__main__ import main

    code = main(
        ["figures", "--index", "--dir", str(tmp_path / "f"), "--to", str(tmp_path / "i.md")]
    )
    assert code == 0
    assert (tmp_path / "i.md").exists()
    assert main(["figures"]) == 0  # sem --index: não faz nada, não falha
