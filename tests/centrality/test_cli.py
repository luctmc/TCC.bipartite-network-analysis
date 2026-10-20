"""Integração do estágio e da CLI da Frente C, sem escrever nas fixtures."""

from __future__ import annotations

import csv
import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from edugraph.__main__ import load_config, main
from edugraph.centrality.stage import CentralityStage
from edugraph.contracts import io
from edugraph.contracts.paths import as_roots
from edugraph.contracts.registry import load_builtin_implementations


@pytest.fixture
def copia_fixtures(tmp_path: Path, repo_root: Path) -> Path:
    """A CLI recebe uma raiz própria, mesmo quando só faz leituras."""
    return Path(shutil.copytree(repo_root / "data/fixtures", tmp_path / "fixtures"))


def linhas(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.mark.parametrize("dataset", ["tiny_v1", "synthetic_v1"])
def test_estagio_cobre_nos_e_atualiza_metricas_sem_duplicar(
    dataset: str, copia_fixtures: Path, tmp_path: Path, repo_root: Path
) -> None:
    load_builtin_implementations()
    config = load_config(repo_root / "configs/synthetic_v1.toml")
    config.bipartite = replace(config.bipartite, dataset=dataset)
    out = tmp_path / "out"
    stage = CentralityStage()
    stage.run([copia_fixtures], out, config)
    roots = as_roots([copia_fixtures])
    for projection_id in roots.projections(dataset):
        nodes = set(io.load_projection(roots, dataset, projection_id).graph)
        for metric in ("degree", "betweenness", "eigenvector"):
            result = io.load_centrality([out], dataset, projection_id, metric)
            assert set(result.scores) == nodes
            assert result.meta.schema_version == "1.0"
            assert (
                (out / dataset / "centrality" / projection_id / f"{metric}.csv")
                .read_text(encoding="utf-8")
                .startswith("node_id,score\n")
            )
    table = out / dataset / "metrics/centrality_top.csv"
    before = table.read_bytes()
    stage.run([copia_fixtures], out, config)
    assert table.read_bytes() == before
    rows = linhas(table)
    assert len(rows) == (18 if dataset == "tiny_v1" else 42)
    assert set(rows[0]) == {
        "dataset",
        "projection_id",
        "metric",
        "rank",
        "node_id",
        "label",
        "score",
    }


@pytest.mark.parametrize("dataset", ["tiny_v1", "synthetic_v1"])
def test_comando_all_grava_as_tres_metricas_sem_alterar_entrada(
    dataset: str, copia_fixtures: Path, tmp_path: Path
) -> None:
    before = {
        p.relative_to(copia_fixtures): p.read_bytes()
        for p in copia_fixtures.rglob("*")
        if p.is_file()
    }
    out = tmp_path / "out"
    assert (
        main(
            [
                "centrality",
                "all",
                "--root",
                str(copia_fixtures),
                "--dataset",
                dataset,
                "--out",
                str(out),
            ]
        )
        == 0
    )
    assert len(list((out / dataset / "centrality").rglob("*.csv"))) == 12
    assert before == {
        p.relative_to(copia_fixtures): p.read_bytes()
        for p in copia_fixtures.rglob("*")
        if p.is_file()
    }


def test_comando_compute_preserva_parametros_e_cobertura(
    copia_fixtures: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    assert (
        main(
            [
                "centrality",
                "compute",
                "--root",
                str(copia_fixtures),
                "--dataset",
                "tiny_v1",
                "--projection",
                "student_simple",
                "--metric",
                "betweenness",
                "--weight-mode",
                "inverse",
                "--k",
                "3",
                "--seed",
                "7",
                "--out",
                str(out),
            ]
        )
        == 0
    )
    result = io.load_centrality([out], "tiny_v1", "student_simple", "betweenness")
    assert set(result.scores) == {"S1", "S2", "S3", "S4", "S5", "S6"}
    assert result.params == {
        "normalized": True,
        "weight_mode": "inverse",
        "k": 3,
        "estimate": True,
        "seed": 7,
    }


def test_comando_critical_exporta_tabelas_e_metricas_idempotentes(
    copia_fixtures: Path, tmp_path: Path
) -> None:
    out, tables = tmp_path / "out", tmp_path / "tables"
    args = [
        "centrality",
        "critical",
        "--root",
        str(copia_fixtures),
        "--dataset",
        "synthetic_v1",
        "--out",
        str(out),
        "--tables",
        str(tables),
    ]
    assert main(args) == 0
    files = sorted(tables.glob("*.csv"))
    assert len(files) == 4
    assert all({"dataset", "projection_id"} <= set(linhas(p)[0]) for p in files)
    before = {p: p.read_bytes() for p in files}
    metrics = out / "synthetic_v1/metrics/centrality_top.csv"
    metric_bytes = metrics.read_bytes()
    assert main(args) == 0
    assert before == {p: p.read_bytes() for p in files}
    assert metrics.read_bytes() == metric_bytes


def test_comando_evaluate_exporta_quartis_sem_inventar_ranking_degenerado(
    copia_fixtures: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert (
        main(
            [
                "centrality",
                "evaluate",
                "--root",
                str(copia_fixtures),
                "--dataset",
                "synthetic_v1",
                "--tables",
                str(tmp_path / "tables"),
            ]
        )
        == 0
    )
    assert "não há disciplina crítica a validar" in capsys.readouterr().out
    files = list((tmp_path / "tables").glob("*.csv"))
    assert len(files) == 1
    rows = linhas(files[0])
    assert [r["quantile"] for r in rows] == ["1", "2", "3", "4"]
    assert sum(int(r["n_students"]) for r in rows) == 98
    assert "rate_not_passed" in rows[0]


def test_comando_report_gera_relatorio_agregado(copia_fixtures: Path, tmp_path: Path) -> None:
    out = tmp_path / "report"
    assert (
        main(
            [
                "centrality",
                "report",
                "--root",
                str(copia_fixtures),
                "--dataset",
                "synthetic_v1",
                "--out",
                str(out),
            ]
        )
        == 0
    )
    text = (out / "relatorio-interno-synthetic_v1.md").read_text(encoding="utf-8")
    assert "## Comunidades" in text
    assert "## Disciplinas críticas" in text
    assert "## Relação com o desfecho histórico" in text
    assert "S100055" not in text
    assert list((out / "figures").glob("*.png"))


def test_comando_openapi_imprime_json_com_rotas_de_leitura(
    copia_fixtures: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["api", "openapi", "--root", str(copia_fixtures)]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert "/datasets/{dataset}/centrality/{projection_id}/{metric}" in schema["paths"]
    assert all(set(methods) == {"get"} for methods in schema["paths"].values())


@pytest.mark.parametrize("reload", [False, True])
def test_comando_serve_configura_raizes_sem_deixar_servidor_ativo(
    copia_fixtures: Path, monkeypatch: pytest.MonkeyPatch, reload: bool
) -> None:
    import os

    import uvicorn

    calls = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **kwargs: calls.append((app, kwargs)))
    monkeypatch.setenv("EDUGRAPH_ROOTS", "origem-anterior")
    args = ["api", "serve", "--root", str(copia_fixtures), "--host", "127.0.0.1", "--port", "8765"]
    if reload:
        args.append("--reload")
    assert main(args) == 0
    app, kwargs = calls[0]
    assert kwargs["port"] == 8765
    assert kwargs["host"] == "127.0.0.1"
    if reload:
        assert app == "edugraph.api.app:app"
        assert os.environ["EDUGRAPH_ROOTS"] == str(copia_fixtures)
    else:
        assert list(app.state.roots) == [copia_fixtures]
