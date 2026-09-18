"""Raiz de composição  ``[T]``.

**Este é o único arquivo do projeto que importa mais de uma frente.**
Ele monta os grupos de CLI (``data``, ``community``, ``centrality``,
``api``), o comando ``run`` — que executa estágios resolvidos por nome
no registro — e o comando ``validate``.

O teste ``tests/contract/test_import_boundaries.py`` isenta este arquivo
e ``contracts/registry.py``, e nenhum outro: qualquer import cruzado
entre ``data``, ``community``, ``centrality`` e ``api`` quebra a CI
(ADR-0003).

Ele não precisa ser editado quando uma frente implementa o seu estágio:
até lá o stub levanta ``NotImplementedError`` com o id da spec, e
``run --from community`` parte dos artefatos já existentes em disco.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

from edugraph import __version__
from edugraph.api import cli as api_cli
from edugraph.centrality import cli as centrality_cli
from edugraph.community import cli as community_cli
from edugraph.console import configure as configure_console
from edugraph.contracts.errors import ContractError
from edugraph.contracts.registry import STAGES, load_builtin_implementations
from edugraph.contracts.types import RunConfig
from edugraph.data import cli as data_cli

#: Ordem canônica dos estágios do pipeline.
STAGE_ORDER: tuple[str, ...] = ("data", "community", "centrality")


def build_parser() -> argparse.ArgumentParser:
    """Monta o parser completo da CLI."""
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        action="append",
        dest="roots",
        metavar="DIR",
        help=(
            "raiz de artefatos, consultada na ordem em que aparece. "
            "Repita para sobrepor (ex.: --root data/processed --root data/fixtures). "
            "Padrão: EDUGRAPH_ROOTS, ou data/processed + data/fixtures."
        ),
    )

    parser = argparse.ArgumentParser(
        prog="edugraph",
        description=(
            "Análise topológica e detecção de comunidades em redes educacionais "
            "bipartidas — TCC Grupo 16, UniAnchieta."
        ),
        epilog="Documentação em docs/. Fronteiras entre frentes: docs/adr/ADR-0003-*.md",
    )
    parser.add_argument("--version", action="version", version=f"edugraph {__version__}")

    subparsers = parser.add_subparsers(dest="group", required=True, metavar="GRUPO")

    data_cli.register(subparsers, common)
    community_cli.register(subparsers, common)
    centrality_cli.register(subparsers, common)
    api_cli.register(subparsers, common)
    _register_run(subparsers, common)
    _register_validate(subparsers, common)
    _register_figures(subparsers, common)

    return parser


# ---------------------------------------------------------------------
# run — executa os estágios de uma configuração
# ---------------------------------------------------------------------


def _register_run(subparsers: argparse._SubParsersAction, parent: argparse.ArgumentParser) -> None:
    run = subparsers.add_parser(
        "run",
        parents=[parent],
        help="[T] executa os estágios de uma configuração de configs/",
        description=(
            "Roda o pipeline de ponta a ponta para um arquivo TOML. "
            "Cada configuração vira uma linha das tabelas do capítulo 3."
        ),
    )
    run.add_argument("config", type=Path, help="arquivo TOML de configs/")
    run.add_argument("--out", type=Path, default=Path("data/processed"))
    run.add_argument(
        "--from",
        dest="from_stage",
        choices=STAGE_ORDER,
        default=None,
        help="começa deste estágio, aproveitando o que já está em disco",
    )
    run.add_argument(
        "--only", dest="only", choices=STAGE_ORDER, default=None, help="roda só este estágio"
    )
    run.add_argument("--dry-run", action="store_true", help="lista o que rodaria e sai")
    run.set_defaults(func=cmd_run)


def load_config(path: Path) -> RunConfig:
    """Carrega e valida um TOML de ``configs/``."""
    if not path.exists():
        raise ContractError(f"configuração não encontrada: {path}")
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return RunConfig.from_dict(data)


def cmd_run(args: argparse.Namespace) -> int:
    """Executa os estágios pedidos, em ordem, sobre uma configuração."""
    load_builtin_implementations()
    config = load_config(args.config)

    stages = [s for s in STAGE_ORDER if s in config.stages]
    if args.only:
        stages = [args.only]
    elif args.from_stage:
        stages = stages[stages.index(args.from_stage) :]

    roots = [Path(r) for r in (args.roots or ["data/processed", "data/fixtures"])]
    print(f"[run] configuração '{config.name}' · dataset '{config.bipartite.dataset}'")
    print(f"[run] estágios: {' → '.join(stages) or '(nenhum)'}")

    if args.dry_run:
        for name in stages:
            print(f"[run] {name}: {STAGES.get(name)!r}")
        return 0

    written: list[Path] = []
    for name in stages:
        stage = STAGES.get(name)
        print(f"[run] {name}…")
        written.extend(stage.run(roots, args.out, config))  # type: ignore[attr-defined]

    for path in written:
        print(f"[run] gravado: {path}")
    return 0


# ---------------------------------------------------------------------
# validate — roda os validadores de contrato sobre uma raiz
# ---------------------------------------------------------------------


def _register_validate(
    subparsers: argparse._SubParsersAction, parent: argparse.ArgumentParser
) -> None:
    validate = subparsers.add_parser(
        "validate",
        parents=[parent],
        help="[T] valida todos os artefatos sob as raízes",
        description=(
            "Roda os invariantes de docs/contratos/ sobre cada artefato encontrado. "
            "É o mesmo que tests/contract/ faz, disponível fora do pytest."
        ),
    )
    validate.add_argument("--dataset", default=None, help="restringe a um dataset")
    validate.set_defaults(func=cmd_validate)


def cmd_validate(args: argparse.Namespace) -> int:
    """Valida os artefatos e devolve 1 se algum contrato for violado."""
    from edugraph.contracts.paths import as_roots
    from edugraph.contracts.validate import validate_dataset

    roots = as_roots(args.roots)
    datasets = [args.dataset] if args.dataset else roots.datasets()
    if not datasets:
        print(f"[validate] nenhum dataset sob {', '.join(str(r) for r in roots)}")
        return 1

    falhou = False
    for dataset in datasets:
        try:
            checked = validate_dataset(roots, dataset)
        except ContractError as error:
            falhou = True
            print(f"[validate] {dataset}: FALHOU\n  {error}")
        else:
            print(f"[validate] {dataset}: ok ({len(checked)} artefatos)")
            for item in checked:
                print(f"           · {item}")
    return 1 if falhou else 0


# ---------------------------------------------------------------------
# figures — índice gerado do material do artigo
# ---------------------------------------------------------------------


def _register_figures(
    subparsers: argparse._SubParsersAction, parent: argparse.ArgumentParser
) -> None:
    figures = subparsers.add_parser(
        "figures",
        parents=[parent],
        help="[T] índice das figuras do artigo (gerado, nunca editado à mão)",
        description=(
            "Regenera docs/artigo/indice-figuras.md a partir de results/figures/. "
            "A lista planejada vive em edugraph.reporting.figures.PLANNED_FIGURES."
        ),
    )
    figures.add_argument("--index", action="store_true", help="regenera o índice")
    figures.add_argument("--dir", type=Path, default=None, help="pasta das figuras")
    figures.add_argument("--to", type=Path, default=None, help="arquivo do índice")
    figures.set_defaults(func=cmd_figures)


def cmd_figures(args: argparse.Namespace) -> int:
    """Regenera o índice de figuras. Só ``reporting`` — nenhuma frente."""
    from edugraph.reporting.figures import FIGURES_DIR, INDEX_PATH, build_index

    if not args.index:
        print("[figures] nada a fazer; use --index para regenerar o índice")
        return 0
    path = build_index(args.dir or FIGURES_DIR, args.to or INDEX_PATH)
    print(f"[figures] índice gravado em {path}")
    return 0


# ---------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI."""
    configure_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result: int = args.func(args)
    except NotImplementedError as error:
        # Stub de spec ainda aberta: mensagem útil, não stack trace.
        print(f"[edugraph] não implementado — {error}", file=sys.stderr)
        return 2
    except ContractError as error:
        print(f"[edugraph] erro de contrato — {error}", file=sys.stderr)
        return 1
    return result


if __name__ == "__main__":
    raise SystemExit(main())
