"""CLI da Frente B  ``[B]`` — grupo de comandos ``edugraph community``.

A segunda-feira do Gabriel (§5.2 do plano de arquitetura)::

    python -m edugraph community louvain \\
        --root data/fixtures --dataset synthetic_v1 --projection student_simple
    python -m edugraph community girvan-newman \\
        --root data/fixtures --dataset synthetic_v1 --projection student_simple \\
        --time-budget 60

Quando o OULAD chegar: ``--root data/processed --dataset oulad_bbb_2013j``.
Nada mais muda.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def register(subparsers: argparse._SubParsersAction, parent: argparse.ArgumentParser) -> None:
    """Acrescenta o grupo ``community`` ao parser principal."""
    group = subparsers.add_parser(
        "community",
        parents=[parent],
        help="[B] detecção de comunidades",
        description="Frente B — Louvain, Girvan-Newman, modularidade e caracterização.",
    )
    actions = group.add_subparsers(dest="action", required=True)

    louvain = actions.add_parser("louvain", parents=[parent], help="Louvain sobre uma projeção")
    _add_common(louvain)
    louvain.add_argument("--seed", type=int, default=42)
    louvain.add_argument("--resolution", type=float, default=1.0)
    louvain.add_argument(
        "--implementation", choices=["python_louvain", "networkx"], default="python_louvain"
    )
    louvain.set_defaults(func=cmd_louvain)

    gn = actions.add_parser(
        "girvan-newman", parents=[parent], help="Girvan-Newman com orçamento de tempo"
    )
    _add_common(gn)
    gn.add_argument("--time-budget", type=float, default=300.0, dest="time_budget_s")
    gn.add_argument("--target-communities", type=int, default=None, dest="target_communities")
    gn.add_argument("--sample-nodes", type=int, default=None, dest="sample_nodes")
    gn.add_argument("--seed", type=int, default=42)
    gn.set_defaults(func=cmd_girvan_newman)

    characterize = actions.add_parser(
        "characterize", parents=[parent], help="perfil das comunidades (profile.csv)"
    )
    characterize.add_argument("--dataset", required=True)
    characterize.add_argument("--partition", required=True, help="<algoritmo>__<projection_id>")
    characterize.add_argument("--top-k", type=int, default=3, dest="top_k")
    characterize.add_argument("--out", type=Path, default=Path("data/processed"))
    characterize.set_defaults(func=cmd_characterize)

    compare = actions.add_parser(
        "compare", parents=[parent], help="tabela comparativa (metrics/communities.csv)"
    )
    compare.add_argument("--dataset", required=True)
    compare.add_argument("--out", type=Path, default=Path("data/processed"))
    compare.set_defaults(func=cmd_compare)

    evaluate = actions.add_parser(
        "evaluate", parents=[parent], help="validação a posteriori contra outcomes.csv"
    )
    evaluate.add_argument("--dataset", required=True)
    evaluate.add_argument("--partition", required=True)
    evaluate.set_defaults(func=cmd_evaluate)


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--projection", required=True, help="ex.: student_simple")
    parser.add_argument("--out", type=Path, default=Path("data/processed"))


# ---------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------


def cmd_louvain(args: argparse.Namespace) -> int:
    raise NotImplementedError("B-01: ver docs/specs/frente-b/B-01-louvain.md")


def cmd_girvan_newman(args: argparse.Namespace) -> int:
    raise NotImplementedError("B-02: ver docs/specs/frente-b/B-02-girvan-newman.md")


def cmd_characterize(args: argparse.Namespace) -> int:
    raise NotImplementedError("B-05: ver docs/specs/frente-b/B-05-caracterizacao.md")


def cmd_compare(args: argparse.Namespace) -> int:
    raise NotImplementedError("B-04: ver docs/specs/frente-b/B-04-comparacao.md")


def cmd_evaluate(args: argparse.Namespace) -> int:
    raise NotImplementedError("B-06: ver docs/specs/frente-b/B-06-validacao.md")
