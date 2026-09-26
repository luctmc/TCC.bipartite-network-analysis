"""Estágio ``centrality`` do comando ``run``  ``[C]``.

Satisfaz :class:`~edugraph.contracts.protocols.Stage`.

O que ele faz, para cada configuração de ``configs/``: calcula as métricas
de ``[centrality] metrics`` sobre as projeções de ``[[projections]]`` e
grava um ``CentralityResult`` por (projeção, métrica). Os parâmetros de
cada métrica vêm do bloco ``[centrality.<métrica>]`` do TOML.

Sobre as projeções ``discipline_*`` grava também as linhas de
``metrics/centrality_top.csv`` — as disciplinas críticas (spec C-03),
com ``[centrality] top_n`` posições por métrica.

A CLI (``centrality compute`` e ``centrality all``) usa as mesmas funções
daqui, para que o artefato não dependa de qual porta de entrada o gerou.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Registro das implementações da frente (ver nota em data/stage.py).
from edugraph.centrality import betweenness, degree, eigenvector  # noqa: F401
from edugraph.centrality.critical_disciplines import (
    is_discipline_projection,
    labels_of,
    rank_disciplines,
    write_metrics,
)
from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.paths import ArtifactRoots, as_roots, centrality_dir
from edugraph.contracts.registry import CENTRALITIES, STAGES
from edugraph.contracts.types import CentralityResult, ProjectionBundle, RunConfig
from edugraph.contracts.validate import validate_centrality

#: As três métricas que a Introdução cita, na ordem das tabelas.
DEFAULT_METRICS: tuple[str, ...] = ("degree", "betweenness", "eigenvector")

#: Posições por métrica em ``metrics/centrality_top.csv``. Com 7 ou 22
#: disciplinas, 10 cobre o topo que o artigo discute.
DEFAULT_TOP_N = 10


def metrics_of(config: RunConfig) -> list[str]:
    """Nomes das métricas a calcular, na ordem do TOML."""
    declared = config.centrality.get("metrics", list(DEFAULT_METRICS))
    if isinstance(declared, str):  # `metrics = "degree"` é engano comum
        declared = [declared]
    return [str(name) for name in declared]


def params_of(config: RunConfig, metric: str) -> dict[str, Any]:
    """Bloco ``[centrality.<métrica>]`` do TOML, ou vazio."""
    params = config.centrality.get(metric, {})
    if not isinstance(params, dict):
        raise ContractError(
            f"[centrality.{metric}] precisa ser uma tabela do TOML; recebeu {params!r}"
        )
    return dict(params)


def compute_metric(
    projection: ProjectionBundle, metric: str, params: dict[str, Any] | None = None
) -> CentralityResult:
    """Resolve a métrica no registro, calcula e confere contra a projeção.

    A conferência com a projeção (cobertura exata dos nós) é mais forte
    que a que ``io.save_centrality`` faz sozinho, por isso fica aqui.
    """
    implementation = CENTRALITIES.get(metric)
    result: CentralityResult = implementation.compute(  # type: ignore[attr-defined]
        projection, **(params or {})
    )
    validate_centrality(result, projection)
    return result


def compute_all(
    roots: ArtifactRoots,
    out: Path,
    dataset: str,
    projection_ids: list[str],
    metrics: list[str],
    params: dict[str, dict[str, Any]] | None = None,
) -> list[CentralityResult]:
    """Calcula e grava cada métrica em cada projeção, na ordem dada."""
    results: list[CentralityResult] = []
    for projection_id in projection_ids:
        projection = io.load_projection(roots, dataset, projection_id)
        for metric in metrics:
            result = compute_metric(projection, metric, (params or {}).get(metric))
            io.save_centrality(result, out, dataset)
            results.append(result)
    return results


class CentralityStage:
    """Calcula as métricas configuradas sobre todas as projeções."""

    name = "centrality"

    def run(self, roots: list[Path], out: Path, config: RunConfig) -> list[Path]:
        """Executa a Frente C para uma configuração.

        Lê as projeções das ``roots`` — que podem ser fixtures — e grava
        em ``out``, nunca no lugar de onde leu.
        """
        resolved = as_roots([*roots, out] if roots else [out])
        dataset = config.bipartite.dataset

        projection_ids = [spec.projection_id for spec in config.projections]
        if not projection_ids:
            projection_ids = resolved.projections(dataset)
        if not projection_ids:
            raise ContractError(
                f"estágio 'centrality': nenhuma projeção declarada em {config.name!r} nem "
                f"encontrada para o dataset {dataset!r}. Rode o estágio 'data' antes."
            )

        metrics = metrics_of(config)
        params = {metric: params_of(config, metric) for metric in metrics}
        results = compute_all(resolved, out, dataset, projection_ids, metrics, params)
        written = sorted({centrality_dir(out, dataset, r.projection_id) for r in results})

        top_n = int(config.centrality.get("top_n", DEFAULT_TOP_N))
        rows = critical_rows(resolved, dataset, results, top_n)
        if rows:
            written.append(write_metrics(rows, out, dataset))
        return written


def critical_rows(
    roots: ArtifactRoots, dataset: str, results: list[CentralityResult], top_n: int
) -> list[dict[str, Any]]:
    """Linhas de ``centrality_top.csv`` das projeções de disciplina."""
    by_projection: dict[str, dict[str, CentralityResult]] = {}
    for result in results:
        if is_discipline_projection(result.projection_id):
            by_projection.setdefault(result.projection_id, {})[result.metric] = result

    rows: list[dict[str, Any]] = []
    for projection_id, by_metric in sorted(by_projection.items()):
        labels = labels_of(io.load_projection(roots, dataset, projection_id))
        rows.extend(rank_disciplines(by_metric, top_n=top_n, dataset=dataset, labels=labels))
    return rows


STAGES.register("centrality", CentralityStage())
