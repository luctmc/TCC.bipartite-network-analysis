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
    project.add_argument("--out", type=Path, default=Path("data/processed"))
    project.set_defaults(func=cmd_project)

    etl = actions.add_parser("etl", parents=[parent], help="normaliza o OULAD bruto")
    etl.add_argument("--raw", type=Path, default=Path("data/raw/oulad"))
    etl.add_argument("--cache", type=Path, default=Path("data/interim"))
    etl.set_defaults(func=cmd_etl)

    report = actions.add_parser("report", parents=[parent], help="estatísticas e figuras da frente")
    report.add_argument("--dataset", required=True)
    report.add_argument("--out", type=Path, default=Path("results"))
    report.set_defaults(func=cmd_report)


# ---------------------------------------------------------------------
# Handlers — cada um fecha com a sua spec
# ---------------------------------------------------------------------


def cmd_synthetic(args: argparse.Namespace) -> int:
    """Gera o dataset sintético e grava o bipartido e as projeções.

    Notes
    -----
    O gerador (:mod:`edugraph.data.synthetic`) já funciona; o que falta é
    o caminho dele até os artefatos, que depende de A-03 e A-04.
    """
    raise NotImplementedError("A-01/A-03: ver docs/specs/frente-a/")


def cmd_bipartite(args: argparse.Namespace) -> int:
    raise NotImplementedError("A-03: ver docs/specs/frente-a/A-03-bipartido-parametrizavel.md")


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
    out = io.save_projection(bundle, args.out)

    graph = bundle.graph
    print(
        f"[data] {spec.projection_id}: {graph.number_of_nodes()} nós, "
        f"{graph.number_of_edges()} arestas → {out}"
    )
    return 0


def cmd_etl(args: argparse.Namespace) -> int:
    raise NotImplementedError("A-02: ver docs/specs/frente-a/A-02-etl-oulad.md")


def cmd_report(args: argparse.Namespace) -> int:
    raise NotImplementedError("A-07: ver docs/specs/frente-a/A-07-estatisticas-bipartido.md")
