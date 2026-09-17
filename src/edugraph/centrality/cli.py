"""CLI da Frente C  ``[C]`` — grupo de comandos ``edugraph centrality``.

A segunda-feira do Lucas (§5.2 do plano de arquitetura)::

    python -m edugraph centrality all --root data/fixtures --dataset synthetic_v1
    python -m edugraph api serve --root data/processed --root data/fixtures
"""

from __future__ import annotations

import argparse
from pathlib import Path


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
    run_all.add_argument("--out", type=Path, default=Path("data/processed"))
    run_all.set_defaults(func=cmd_all)

    one = actions.add_parser("compute", parents=[parent], help="uma métrica em uma projeção")
    one.add_argument("--dataset", required=True)
    one.add_argument("--projection", required=True)
    one.add_argument("--metric", choices=["degree", "betweenness", "eigenvector"], required=True)
    one.add_argument("--implementation", choices=["manual", "networkx"], default="manual")
    one.add_argument("--out", type=Path, default=Path("data/processed"))
    one.set_defaults(func=cmd_compute)

    critical = actions.add_parser(
        "critical", parents=[parent], help="disciplinas críticas (metrics/centrality_top.csv)"
    )
    critical.add_argument("--dataset", required=True)
    critical.add_argument("--top-n", type=int, default=10, dest="top_n")
    critical.add_argument("--out", type=Path, default=Path("data/processed"))
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


# ---------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------


def cmd_all(args: argparse.Namespace) -> int:
    raise NotImplementedError("C-01/C-02: ver docs/specs/frente-c/")


def cmd_compute(args: argparse.Namespace) -> int:
    raise NotImplementedError("C-01/C-02: ver docs/specs/frente-c/")


def cmd_critical(args: argparse.Namespace) -> int:
    raise NotImplementedError("C-03: ver docs/specs/frente-c/C-03-disciplinas-criticas.md")


def cmd_evaluate(args: argparse.Namespace) -> int:
    raise NotImplementedError("C-06: ver docs/specs/frente-c/C-06-validacao-centralidade.md")


def cmd_report(args: argparse.Namespace) -> int:
    raise NotImplementedError("C-07: ver docs/specs/frente-c/C-07-relatorio-interno.md")
