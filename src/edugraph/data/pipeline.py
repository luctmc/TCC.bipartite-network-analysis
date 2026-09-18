"""Pipeline da Frente A: fonte → bipartido → outcomes → projeções  ``[A]``.

Um único lugar que sabe ler uma :class:`~edugraph.contracts.types.RunConfig`
e produzir os artefatos da frente. É usado pelo estágio ``data`` do
comando ``run``, por ``edugraph data bipartite`` e por
``edugraph data synthetic`` — assim os três caminhos gravam exatamente
a mesma coisa.

Fontes suportadas (``[source] kind`` no TOML):

``synthetic``
    Gerador de :mod:`edugraph.data.synthetic` (``seed``,
    ``students_per_group``). Roda em qualquer máquina.
``oulad``
    ETL de :mod:`edugraph.data.oulad.etl` sobre ``raw_dir`` (spec A-02).
    Exige o OULAD baixado.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import pandas as pd

from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.registry import PROJECTIONS
from edugraph.contracts.types import BipartiteBundle, Outcomes, RunConfig
from edugraph.data.bipartite import build_bipartite
from edugraph.data.projection import manual, networkx_ref  # noqa: F401  (registro)
from edugraph.data.scale import k_core_projection, sample_students
from edugraph.data.synthetic import SyntheticSpec, generate, make_groups

__all__ = ["load_run_config", "load_source", "run_data_stage"]


def load_run_config(path: Path) -> RunConfig:
    """Carrega um TOML de ``configs/``."""
    if not path.exists():
        raise ContractError(f"configuração não encontrada: {path}")
    with path.open("rb") as handle:
        return RunConfig.from_dict(tomllib.load(handle))


def load_source(config: RunConfig) -> tuple[pd.DataFrame, Outcomes]:
    """Devolve a tabela de matrículas e os rótulos históricos da fonte.

    Os rótulos saem daqui **separados** da tabela que vai para o grafo,
    e seguem direto para ``outcomes.csv`` (ADR-0008).
    """
    source: dict[str, Any] = dict(config.source)
    kind = source.get("kind", "synthetic")

    if kind == "synthetic":
        kwargs: dict[str, Any] = {
            "seed": int(source.get("seed", config.bipartite.seed or 42)),
            "students_per_group": int(source.get("students_per_group", 40)),
        }
        if source.get("sparsity") is not None:
            kwargs["sparsity"] = float(source["sparsity"])
        if "n_groups" in source or "modules_per_group" in source:
            kwargs["groups"] = make_groups(
                int(source.get("n_groups", 3)), int(source.get("modules_per_group", 2))
            )
        dataset = generate(SyntheticSpec(**kwargs))
        table = pd.DataFrame(dataset.enrollments)
        outcomes = Outcomes(
            final_result=dict(dataset.final_result),
            planted_group=dict(dataset.planted_group),
        )
        return table, outcomes

    if kind == "oulad":
        from edugraph.data.oulad import etl

        raw_dir = Path(source.get("raw_dir", "data/raw/oulad"))
        cache_dir = Path(source["cache_dir"]) if "cache_dir" in source else None
        # A granularidade decide o grão da tabela: por matrícula (módulo ou
        # módulo_apresentação) ou por avaliação. O desfecho por aluno sai
        # da mesma tabela, pela regra documentada em etl.to_outcomes.
        if config.bipartite.granularity == "assessment":
            table = etl.normalize_assessments(raw_dir, cache_dir=cache_dir)
        else:
            table = etl.normalize(raw_dir, cache_dir=cache_dir)
        outcomes = Outcomes(final_result=etl.to_outcomes(table))
        return table, outcomes

    raise ContractError(f"[source] kind desconhecido: {kind!r} (esperado 'synthetic' ou 'oulad')")


def restrict_outcomes(outcomes: Outcomes, bundle: BipartiteBundle) -> Outcomes:
    """Só alunos presentes no bipartido ficam em ``outcomes.csv``.

    O validador exige que todo desfecho aponte para um nó existente —
    vale depois do critério de aresta e depois de qualquer redução da
    spec A-06 (amostra, coorte).
    """
    survivors = bundle.students
    planted = (
        {k: v for k, v in outcomes.planted_group.items() if k in survivors}
        if outcomes.planted_group is not None
        else None
    )
    return Outcomes(
        final_result={k: v for k, v in outcomes.final_result.items() if k in survivors},
        planted_group=planted,
        meta=outcomes.meta,
    )


def run_data_stage(config: RunConfig, out: Path, *, projections: bool = True) -> list[Path]:
    """Executa a Frente A para uma configuração e devolve os caminhos gravados.

    Parameters
    ----------
    config
        A configuração do experimento.
    out
        Raiz de escrita (``data/processed`` por padrão).
    projections
        ``False`` grava só bipartido e outcomes — é o que
        ``edugraph data bipartite`` faz.
    """
    table, outcomes = load_source(config)
    bundle = build_bipartite(table, config.bipartite)
    dataset = config.bipartite.dataset

    # Reduções de escala (spec A-06), declaradas em [source] do TOML.
    # Ficam em [source] porque são decisão sobre a fonte, não sobre o
    # grafo — e porque RunConfig é contrato congelado. Cada uma deixa
    # rastro em meta.stats["reductions"] do artefato.
    source: dict[str, Any] = dict(config.source)
    if source.get("sample_students"):
        bundle = sample_students(
            bundle, int(source["sample_students"]), seed=int(source.get("sample_seed", 42))
        )

    written: list[Path] = [io.save_bipartite(bundle, out)]
    written.append(io.save_outcomes(restrict_outcomes(outcomes, bundle), out, dataset))

    if projections:
        k = int(source["k_core"]) if source.get("k_core") else None
        for spec in config.projections:
            algorithm = PROJECTIONS.get(f"{spec.implementation}_{spec.weighting}")
            projection = algorithm.project(bundle, spec)  # type: ignore[attr-defined]
            if k is not None:
                projection = k_core_projection(projection, k)
            written.append(io.save_projection(projection, out))

    return written
