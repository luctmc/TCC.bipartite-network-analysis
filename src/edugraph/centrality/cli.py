"""CLI da Frente C  ``[C]`` — grupo de comandos ``edugraph centrality``.

A segunda-feira do Lucas (§5.2 do plano de arquitetura)::

    python -m edugraph centrality all --root data/fixtures --dataset synthetic_v1
    python -m edugraph api serve --root data/processed --root data/fixtures
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - só para anotação
    from edugraph.contracts.types import CentralityResult


def register(subparsers: argparse._SubParsersAction, parent: argparse.ArgumentParser) -> None:
    """Acrescenta o grupo ``centrality`` ao parser principal."""
    group = subparsers.add_parser(
        "centrality",
        parents=[parent],
        help="[C] métricas de centralidade e disciplinas críticas",
        description="Frente C — grau, intermediação, autovetor e aplicação.",
    )
    actions = group.add_subparsers(dest="action", required=True)

    run_all = actions.add_parser(
        "all", parents=[parent], help="todas as métricas em todas as projeções do dataset"
    )
    run_all.add_argument("--dataset", required=True)
    run_all.add_argument("--projection", default=None, help="restringe a uma projeção")
    run_all.add_argument(
        "--metric",
        action="append",
        choices=["degree", "betweenness", "eigenvector"],
        default=None,
        dest="metrics",
        help="restringe a estas métricas; repita. Padrão: as três",
    )
    _add_metric_params(run_all)
    run_all.add_argument("--out", type=Path, default=Path("data/processed"))
    run_all.set_defaults(func=cmd_all)

    one = actions.add_parser("compute", parents=[parent], help="uma métrica em uma projeção")
    one.add_argument("--dataset", required=True)
    one.add_argument("--projection", required=True)
    one.add_argument("--metric", choices=["degree", "betweenness", "eigenvector"], required=True)
    _add_metric_params(one)
    one.add_argument("--out", type=Path, default=Path("data/processed"))
    one.set_defaults(func=cmd_compute)

    critical = actions.add_parser(
        "critical", parents=[parent], help="disciplinas críticas (metrics/centrality_top.csv)"
    )
    critical.add_argument("--dataset", required=True)
    critical.add_argument(
        "--projection", default=None, help="restringe a uma projeção discipline_*"
    )
    critical.add_argument("--top-n", type=int, default=10, dest="top_n")
    critical.add_argument("--out", type=Path, default=Path("data/processed"))
    critical.add_argument(
        "--tables",
        type=Path,
        default=None,
        help="grava as tabelas 6 e 7 do artigo nesta pasta (ex.: results/tables)",
    )
    critical.set_defaults(func=cmd_critical)

    evaluate = actions.add_parser(
        "evaluate", parents=[parent], help="validação a posteriori contra outcomes.csv"
    )
    evaluate.add_argument("--dataset", required=True)
    evaluate.set_defaults(func=cmd_evaluate)

    report = actions.add_parser("report", parents=[parent], help="relatório interno consolidado")
    report.add_argument("--dataset", required=True)
    report.add_argument("--out", type=Path, default=Path("results"))
    report.set_defaults(func=cmd_report)


def _add_metric_params(parser: argparse.ArgumentParser) -> None:
    """Parâmetros que mudam o ranking — todos acabam em ``params``."""
    parser.add_argument(
        "--weight-mode",
        choices=["none", "inverse", "raw"],
        default="none",
        dest="weight_mode",
        help="peso como distância na intermediação (C-01). Padrão: none",
    )
    parser.add_argument(
        "--k", type=int, default=None, help="pivôs amostrados na intermediação (estimativa)"
    )
    parser.add_argument("--seed", type=int, default=42, help="semente da amostragem de pivôs")
    parser.add_argument(
        "--implementation",
        choices=["manual", "networkx"],
        default="manual",
        help="autovetor à mão ou pelo NetworkX (C-02)",
    )


# ---------------------------------------------------------------------
# Auxiliares comuns aos handlers
# ---------------------------------------------------------------------


def _metric_params(args: argparse.Namespace) -> dict[str, dict[str, Any]]:
    """Os argumentos da linha de comando, repartidos por métrica."""
    betweenness: dict[str, Any] = {"weight_mode": args.weight_mode}
    if args.k is not None:
        betweenness.update(k=args.k, seed=args.seed)
    return {
        "degree": {},
        "betweenness": betweenness,
        "eigenvector": {"implementation": args.implementation},
    }


def _print_result(result: CentralityResult) -> None:
    """Resumo de uma métrica, na mesma forma em todos os comandos."""
    top = ", ".join(f"{node} {score:.4f}" for node, score in result.top(3))
    nota = "" if result.converged else " (fallback: não convergiu)"
    print(
        f"[centrality] {result.projection_id}/{result.metric}: "
        f"{len(result.scores)} nós, {result.runtime_s:.3f}s{nota}; topo: {top}"
    )


# ---------------------------------------------------------------------
# Handlers — cada um fecha com a sua spec
# ---------------------------------------------------------------------


def cmd_all(args: argparse.Namespace) -> int:
    """Todas as métricas em todas as projeções do dataset (C-01, C-02)."""
    from edugraph.centrality.stage import DEFAULT_METRICS, compute_all
    from edugraph.contracts.errors import ArtifactNotFoundError
    from edugraph.contracts.paths import as_roots

    roots = as_roots(args.roots)
    projection_ids = [args.projection] if args.projection else roots.projections(args.dataset)
    if not projection_ids:
        raise ArtifactNotFoundError(
            f"nenhuma projeção do dataset {args.dataset!r} sob "
            f"{', '.join(str(r) for r in roots)}; confira o --root"
        )
    metrics = args.metrics or list(DEFAULT_METRICS)

    results = compute_all(
        roots, args.out, args.dataset, projection_ids, metrics, _metric_params(args)
    )
    for result in results:
        _print_result(result)
    print(f"[centrality] gravado em: {args.out / args.dataset / 'centrality'}")
    return 0


def cmd_compute(args: argparse.Namespace) -> int:
    """Uma métrica em uma projeção (C-01, C-02)."""
    from edugraph.centrality.stage import compute_metric
    from edugraph.contracts import io

    projection = io.load_projection(args.roots, args.dataset, args.projection)
    result = compute_metric(projection, args.metric, _metric_params(args)[args.metric])
    _print_result(result)
    print(f"[centrality] gravado: {io.save_centrality(result, args.out, args.dataset)}")
    return 0


def cmd_critical(args: argparse.Namespace) -> int:
    """Disciplinas críticas, discordância e correlação entre métricas (C-03)."""
    import math

    from edugraph.centrality.critical_disciplines import (
        METRICS_COLUMNS,
        is_discipline_projection,
        labels_of,
        load_results,
        rank_disciplines,
        write_metrics,
    )
    from edugraph.centrality.disagreement import DISAGREEMENT_COLUMNS, disagreement_rows
    from edugraph.contracts import io
    from edugraph.contracts.errors import ArtifactNotFoundError
    from edugraph.contracts.paths import as_roots
    from edugraph.reporting.tables import write_table

    roots = as_roots(args.roots)
    candidates = [args.projection] if args.projection else roots.centralities(args.dataset)
    projection_ids = [p for p in candidates if is_discipline_projection(p)]
    if not projection_ids:
        raise ArtifactNotFoundError(
            f"nenhuma projeção discipline_* com centralidade em {args.dataset!r} sob "
            f"{', '.join(str(r) for r in roots)}; rode `centrality all` antes"
        )

    rows: list[dict[str, Any]] = []
    for projection_id in projection_ids:
        results = load_results(roots, args.dataset, projection_id)
        if not results:
            print(f"[centrality] {projection_id}: sem centralidades calculadas, pulando")
            continue
        labels = labels_of(io.load_projection(roots, args.dataset, projection_id))
        linhas = rank_disciplines(results, top_n=args.top_n, dataset=args.dataset, labels=labels)
        rows.extend(linhas)

        print(f"[centrality] disciplinas críticas — {args.dataset}/{projection_id}")
        for metric in dict.fromkeys(row["metric"] for row in linhas):
            topo = [r for r in linhas if r["metric"] == metric]
            print(
                f"  {metric:<12} " + ", ".join(f"{r['label']} {r['score']:.4f}" for r in topo[:5])
            )

        if all(m in results for m in ("degree", "betweenness", "eigenvector")):
            discordancia = disagreement_rows(
                results, top_n=min(args.top_n, 5), dataset=args.dataset, labels=labels
            )
            for linha in discordancia:
                valor = linha["value"]
                if isinstance(valor, float):
                    valor = (
                        "indefinida (ranking todo empatado)"
                        if math.isnan(valor)
                        else f"{valor:.3f}"
                    )
                print(f"  {linha['comparison']:<34} {valor or '—'}")
            if args.tables is not None:
                tabela = write_table(
                    f"tab7-discordancia-{args.dataset}-{projection_id}",
                    discordancia,
                    out_dir=args.tables,
                    columns=list(DISAGREEMENT_COLUMNS),
                )
                print(f"[centrality] gravado: {tabela}")

        if args.tables is not None:
            tabela = write_table(
                f"tab6-criticas-{args.dataset}-{projection_id}",
                linhas,
                out_dir=args.tables,
                columns=list(METRICS_COLUMNS),
            )
            print(f"[centrality] gravado: {tabela}")

    if not rows:
        return 1
    print(f"[centrality] gravado: {write_metrics(rows, args.out, args.dataset)}")
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    raise NotImplementedError("C-06: ver docs/specs/frente-c/C-06-validacao-centralidade.md")


def cmd_report(args: argparse.Namespace) -> int:
    raise NotImplementedError("C-07: ver docs/specs/frente-c/C-07-relatorio-interno.md")
