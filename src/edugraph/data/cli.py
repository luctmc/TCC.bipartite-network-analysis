"""CLI da Frente A  ``[A]`` — grupo de comandos ``edugraph data``.

Comandos disponíveis (ver §5.2 do plano de arquitetura)::

    python -m edugraph data synthetic --seed 7 --out data/processed
    python -m edugraph data bipartite configs/synthetic_v1.toml
    python -m edugraph data project --dataset synthetic_dev \\
        --side discipline --weighting resource_allocation
"""

from __future__ import annotations

import argparse
from pathlib import Path


def register(subparsers: argparse._SubParsersAction, parent: argparse.ArgumentParser) -> None:
    """Acrescenta o grupo ``data`` ao parser principal."""
    group = subparsers.add_parser(
        "data",
        parents=[parent],
        help="[A] ETL, grafo bipartido e projeções",
        description="Frente A — dados e modelagem.",
    )
    actions = group.add_subparsers(dest="action", required=True)

    synthetic = actions.add_parser(
        "synthetic", parents=[parent], help="gera o dataset sintético com comunidades plantadas"
    )
    synthetic.add_argument("--seed", type=int, default=42)
    synthetic.add_argument("--dataset", default="synthetic_dev", help="nome do dataset de saída")
    synthetic.add_argument("--out", type=Path, default=Path("data/processed"))
    synthetic.add_argument("--students-per-group", type=int, default=40, dest="students_per_group")
    synthetic.add_argument(
        "--sparsity",
        type=float,
        default=None,
        help="fração de alunos reduzidos a uma matrícula (esparsidade tipo OULAD)",
    )
    synthetic.add_argument("--n-groups", type=int, default=None, dest="n_groups")
    synthetic.add_argument("--modules-per-group", type=int, default=None, dest="modules_per_group")
    synthetic.add_argument(
        "--threshold", type=float, default=60.0, help="nota mínima para a aresta"
    )
    synthetic.set_defaults(func=cmd_synthetic)

    bipartite = actions.add_parser(
        "bipartite", parents=[parent], help="constrói o bipartido a partir de um TOML"
    )
    bipartite.add_argument("config", type=Path, help="arquivo de configs/")
    bipartite.add_argument("--out", type=Path, default=Path("data/processed"))
    bipartite.set_defaults(func=cmd_bipartite)

    project = actions.add_parser("project", parents=[parent], help="projeta o bipartido")
    project.add_argument("--dataset", required=True)
    project.add_argument("--side", choices=["student", "discipline"], required=True)
    project.add_argument("--weighting", choices=["simple", "resource_allocation"], default="simple")
    project.add_argument("--implementation", choices=["manual", "networkx"], default="manual")
    project.add_argument("--min-weight", type=float, default=None, dest="min_weight")
    project.add_argument(
        "--k-core", type=int, default=None, dest="k_core", help="núcleo-k da projeção (A-06)"
    )
    project.add_argument("--out", type=Path, default=Path("data/processed"))
    project.set_defaults(func=cmd_project)

    sample = actions.add_parser(
        "sample", parents=[parent], help="amostra determinística de alunos (A-06)"
    )
    sample.add_argument("--dataset", required=True, help="bipartido de origem")
    sample.add_argument("--n", type=int, required=True, help="nº de alunos na amostra")
    sample.add_argument("--seed", type=int, default=42)
    sample.add_argument("--as", dest="new_name", required=True, help="nome do dataset gerado")
    sample.add_argument("--out", type=Path, default=Path("data/processed"))
    sample.set_defaults(func=cmd_sample)

    cohort = actions.add_parser(
        "cohort", parents=[parent], help="recorta um bipartido por coorte (A-06)"
    )
    cohort.add_argument("--dataset", required=True, help="bipartido de origem")
    cohort.add_argument("--cohort", required=True, help='ex.: "BBB_2013J" ou "2013J"')
    cohort.add_argument("--as", dest="new_name", required=True, help="nome do dataset gerado")
    cohort.add_argument("--out", type=Path, default=Path("data/processed"))
    cohort.set_defaults(func=cmd_cohort)

    etl = actions.add_parser("etl", parents=[parent], help="normaliza o OULAD bruto")
    etl.add_argument("--raw", type=Path, default=Path("data/raw/oulad"))
    etl.add_argument("--cache", type=Path, default=Path("data/interim"))
    etl.set_defaults(func=cmd_etl)

    report = actions.add_parser("report", parents=[parent], help="estatísticas e figuras da frente")
    report.add_argument("--dataset", required=True)
    report.add_argument("--out", type=Path, default=Path("results"))
    report.set_defaults(func=cmd_report)

    compare = actions.add_parser(
        "compare",
        parents=[parent],
        help="à mão × NetworkX nas 4 projeções (metrics/projections.csv + figura)",
    )
    compare.add_argument("--dataset", required=True)
    compare.add_argument("--out", type=Path, default=Path("data/processed"))
    compare.add_argument(
        "--figures", type=Path, default=None, help="diretório da figura (padrão: nenhuma)"
    )
    compare.set_defaults(func=cmd_compare)


# ---------------------------------------------------------------------
# Handlers — cada um fecha com a sua spec
# ---------------------------------------------------------------------


def cmd_synthetic(args: argparse.Namespace) -> int:
    """Gera o dataset sintético e grava bipartido, outcomes e as 4 projeções (A-01).

    Monta uma :class:`~edugraph.contracts.types.RunConfig` em memória com
    os mesmos parâmetros que um TOML de ``configs/`` teria e delega ao
    pipeline — o artefato sai idêntico ao que ``run`` produziria.
    """
    from edugraph.contracts.types import BipartiteSpec, ProjectionSpec, RunConfig
    from edugraph.data.pipeline import run_data_stage

    source: dict[str, object] = {
        "kind": "synthetic",
        "seed": args.seed,
        "students_per_group": args.students_per_group,
    }
    if args.sparsity is not None:
        source["sparsity"] = args.sparsity
    if args.n_groups is not None or args.modules_per_group is not None:
        source["n_groups"] = args.n_groups or 3
        source["modules_per_group"] = args.modules_per_group or 2

    config = RunConfig(
        name=args.dataset,
        bipartite=BipartiteSpec(
            dataset=args.dataset,
            granularity="module",
            edge_criterion="score_threshold",
            threshold=args.threshold,
            seed=args.seed,
        ),
        projections=[
            ProjectionSpec(side=side, weighting=weighting)  # type: ignore[arg-type]
            for side in ("student", "discipline")
            for weighting in ("simple", "resource_allocation")
        ],
        source=source,
    )
    written = run_data_stage(config, args.out)
    for path in written:
        print(f"[data] gravado: {path}")
    return 0


def cmd_bipartite(args: argparse.Namespace) -> int:
    """Constrói o bipartido e o ``outcomes.csv`` de um TOML (spec A-03).

    Só a camada ``bipartite/``; as projeções saem por ``data project`` ou
    pelo comando ``run``.
    """
    from edugraph.data.pipeline import load_run_config, run_data_stage

    config = load_run_config(args.config)
    written = run_data_stage(config, args.out, projections=False)
    for path in written:
        print(f"[data] gravado: {path}")
    return 0


def cmd_project(args: argparse.Namespace) -> int:
    """Projeta o bipartido de ``--dataset`` e grava em ``--out`` (spec A-04).

    Lê o bipartido das raízes (``--root``, ou o padrão), resolve o
    algoritmo no registro por ``<implementation>_<weighting>`` e grava a
    projeção passando pelo validador de contrato.
    """
    from edugraph.contracts import io
    from edugraph.contracts.registry import PROJECTIONS
    from edugraph.contracts.types import ProjectionSpec
    from edugraph.data.projection import manual, networkx_ref  # noqa: F401  (registro)

    bipartite = io.load_bipartite(args.roots, args.dataset)
    spec = ProjectionSpec(
        side=args.side,
        weighting=args.weighting,
        implementation=args.implementation,
        min_weight=args.min_weight,
    )
    algorithm = PROJECTIONS.get(f"{args.implementation}_{args.weighting}")
    bundle = algorithm.project(bipartite, spec)  # type: ignore[attr-defined]
    if args.k_core is not None:
        from edugraph.data.scale import k_core_projection

        bundle = k_core_projection(bundle, args.k_core)
    out = io.save_projection(bundle, args.out)

    graph = bundle.graph
    print(
        f"[data] {spec.projection_id}: {graph.number_of_nodes()} nós, "
        f"{graph.number_of_edges()} arestas → {out}"
    )
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    """À mão × NetworkX nas quatro projeções (spec A-05).

    Grava ``metrics/projections.csv`` em ``--out`` e, com ``--figures``,
    a figura "simples × ponderada" do lado aluno↔aluno e do lado
    disciplina↔disciplina.
    """
    from edugraph.contracts import io
    from edugraph.contracts.registry import PROJECTIONS
    from edugraph.contracts.types import ProjectionSpec
    from edugraph.data.projection.compare import compare_all, write_metrics
    from edugraph.data.report import figure_weight_distributions

    bipartite = io.load_bipartite(args.roots, args.dataset)
    rows = compare_all(bipartite)
    path = write_metrics(rows, args.out, args.dataset)

    print(f"[data] {'projeção':<34} {'arestas':>8} {'max|Δ|':>10} {'manual':>9} {'networkx':>9}")
    for row in rows:
        flag = "ok" if row["equal_within_tolerance"] else "DIVERGE"
        print(
            f"[data] {row['projection_id']:<34} {row['n_edges_manual']:>8} "
            f"{row['max_abs_diff']:>10.2e} {row['runtime_manual_s']:>8.3f}s "
            f"{row['runtime_networkx_s']:>8.3f}s  {flag}"
        )
    print(f"[data] gravado: {path}")

    if args.figures is not None:
        for side in ("student", "discipline"):
            simple = PROJECTIONS.get("manual_simple").project(  # type: ignore[attr-defined]
                bipartite, ProjectionSpec(side=side, weighting="simple")
            )
            ra = PROJECTIONS.get("manual_resource_allocation").project(  # type: ignore[attr-defined]
                bipartite, ProjectionSpec(side=side, weighting="resource_allocation")
            )
            fig = figure_weight_distributions(simple, ra, args.figures)
            print(f"[data] figura: {fig}")

    return 0 if all(r["equal_within_tolerance"] for r in rows) else 1


def _save_reduced(bundle, roots, source_dataset: str, new_name: str, out: Path) -> list[Path]:
    """Grava um bipartido reduzido como novo dataset, com outcomes restritos.

    Os rótulos históricos são copiados pelo contrato
    (:func:`edugraph.contracts.io.derive_outcomes`), que filtra e regrava
    sem devolvê-los a esta frente — a Frente A não lê desfecho (ADR-0008).
    """
    from dataclasses import replace

    from edugraph.contracts import io
    from edugraph.contracts.types import BipartiteBundle

    renamed = BipartiteBundle(
        graph=bundle.graph, spec=replace(bundle.spec, dataset=new_name), meta=bundle.meta
    )
    written = [io.save_bipartite(renamed, out)]
    derived = io.derive_outcomes(roots, source_dataset, out, new_name, keep=renamed.students)
    if derived is not None:
        written.append(derived)
    return written


def cmd_sample(args: argparse.Namespace) -> int:
    """Amostra ``--n`` alunos de ``--dataset`` e grava como ``--as`` (spec A-06)."""
    from edugraph.contracts import io
    from edugraph.data.scale import sample_students

    bipartite = io.load_bipartite(args.roots, args.dataset)
    reduced = sample_students(bipartite, args.n, seed=args.seed)
    for path in _save_reduced(reduced, args.roots, args.dataset, args.new_name, args.out):
        print(f"[data] gravado: {path}")
    print(
        f"[data] {args.new_name}: {len(reduced.students)} de {len(bipartite.students)} alunos "
        f"(seed {args.seed}), {len(reduced.disciplines)} disciplinas"
    )
    return 0


def cmd_cohort(args: argparse.Namespace) -> int:
    """Recorta ``--dataset`` pela coorte e grava como ``--as`` (spec A-06)."""
    from edugraph.contracts import io
    from edugraph.data.scale import filter_cohort

    bipartite = io.load_bipartite(args.roots, args.dataset)
    reduced = filter_cohort(bipartite, args.cohort)
    for path in _save_reduced(reduced, args.roots, args.dataset, args.new_name, args.out):
        print(f"[data] gravado: {path}")
    print(
        f"[data] {args.new_name}: coorte {args.cohort!r} — {len(reduced.students)} alunos, "
        f"{len(reduced.disciplines)} disciplinas"
    )
    return 0


def cmd_etl(args: argparse.Namespace) -> int:
    """Normaliza o OULAD bruto e grava o cache em ``--cache`` (spec A-02).

    Exige o download manual em ``--raw`` (ver README). Falha cedo, com
    tabela e coluna nomeadas, se o esquema não bater.
    """
    from edugraph.data.oulad import download, etl

    download.verify(args.raw, strict=True)
    table = etl.normalize(args.raw, cache_dir=args.cache)
    fine = etl.normalize_assessments(args.raw, cache_dir=args.cache)

    n_students = table["id_student"].nunique()
    n_modules = table["code_module"].nunique()
    com_nota = int(table["score_media"].notna().sum())
    ponderadas = int(table["score_weighted"].sum())
    print(f"[etl] {len(table)} matrículas de {n_students} alunos em {n_modules} módulos")
    print(
        f"[etl] {com_nota} com nota ({com_nota / len(table):.0%}); {ponderadas} com média ponderada"
    )
    print(f"[etl] {len(fine)} linhas por avaliação")
    print(f"[etl] cache em {args.cache}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Tabela de estatísticas e figura do bipartido de ``--dataset`` (spec A-07).

    Grava ``<out>/tables/tab1-estatisticas-<dataset>.csv`` e
    ``<out>/figures/fig2-bipartido-<dataset>.{png,svg}`` com a legenda ao
    lado, e regenera o índice de figuras quando ``--out`` é o ``results/``
    do repositório.
    """
    from edugraph.contracts import io
    from edugraph.data.report import STATS_COLUMNS, figure_bipartite, table_dataset_stats
    from edugraph.reporting.figures import FIGURES_DIR, build_index
    from edugraph.reporting.tables import write_table

    bipartite = io.load_bipartite(args.roots, args.dataset)

    row = table_dataset_stats(bipartite)
    table = write_table(
        f"tab1-estatisticas-{args.dataset}", [row], out_dir=args.out / "tables",
        columns=list(STATS_COLUMNS),
    )  # fmt: skip
    print(f"[data] tabela: {table}")
    for col in STATS_COLUMNS[4:]:
        value = row[col]
        print(
            f"[data]   {col:<26} {value:.4f}"
            if isinstance(value, float)
            else f"[data]   {col:<26} {value}"
        )

    figure = figure_bipartite(bipartite, args.out / "figures")
    print(f"[data] figura: {figure}  (+ .svg, .caption.txt)")

    if (args.out / "figures").resolve() == FIGURES_DIR.resolve():
        print(f"[data] índice: {build_index()}")
    return 0
