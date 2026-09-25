"""Estágio ``centrality`` do comando ``run``  ``[C]``.

Satisfaz :class:`~edugraph.contracts.protocols.Stage`.

O que ele faz, para cada configuração de ``configs/``: calcula as métricas
de ``[centrality] metrics`` sobre as projeções de ``[[projections]]`` e
grava um ``CentralityResult`` por (projeção, métrica). Os parâmetros de
cada métrica vêm do bloco ``[centrality.<métrica>]`` do TOML.

A CLI (``centrality compute`` e ``centrality all``) usa as mesmas funções
daqui, para que o artefato não dependa de qual porta de entrada o gerou.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Registro das implementações da frente (ver nota em data/stage.py).
from edugraph.centrality import betweenness, degree, eigenvector  # noqa: F401
from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.paths import ArtifactRoots, as_roots, centrality_dir
from edugraph.contracts.registry import CENTRALITIES, STAGES
from edugraph.contracts.types import CentralityResult, ProjectionBundle, RunConfig
from edugraph.contracts.validate import validate_centrality

#: As três métricas que a Introdução cita, na ordem das tabelas.
DEFAULT_METRICS: tuple[str, ...] = ("degree", "betweenness", "eigenvector")


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
        return sorted({centrality_dir(out, dataset, r.projection_id) for r in results})


STAGES.register("centrality", CentralityStage())
