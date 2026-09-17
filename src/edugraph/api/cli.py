"""CLI da API  ``[C]`` — grupo de comandos ``edugraph api``."""

from __future__ import annotations

import argparse


def register(subparsers: argparse._SubParsersAction, parent: argparse.ArgumentParser) -> None:
    """Acrescenta o grupo ``api`` ao parser principal."""
    group = subparsers.add_parser(
        "api",
        parents=[parent],
        help="[C] API somente leitura sobre os artefatos",
        description="Frente C — API. Não calcula nada (ADR-0004).",
    )
    actions = group.add_subparsers(dest="action", required=True)

    serve = actions.add_parser("serve", parents=[parent], help="sobe o servidor")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--reload", action="store_true", help="recarrega ao salvar")
    serve.set_defaults(func=cmd_serve)

    openapi = actions.add_parser(
        "openapi", parents=[parent], help="imprime o esquema OpenAPI (para tipar o front)"
    )
    openapi.set_defaults(func=cmd_openapi)


def cmd_serve(args: argparse.Namespace) -> int:
    """Sobe o uvicorn sobre as raízes pedidas."""
    import os

    import uvicorn

    from edugraph.api.app import create_app
    from edugraph.contracts.paths import ROOTS_ENV_VAR, as_roots

    roots = as_roots(args.roots)
    print(f"[api] raízes: {', '.join(str(r) for r in roots)}")
    print(f"[api] http://{args.host}:{args.port}  ·  docs em /docs")

    if args.reload:
        # --reload exige que o uvicorn importe a aplicação por string, num
        # processo filho; as raízes viajam pelo ambiente, não pelo objeto.
        os.environ[ROOTS_ENV_VAR] = os.pathsep.join(str(r) for r in roots)
        uvicorn.run("edugraph.api.app:app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run(create_app(roots), host=args.host, port=args.port)
    return 0


def cmd_openapi(args: argparse.Namespace) -> int:
    """Imprime o esquema OpenAPI, entrada do gerador de tipos do front."""
    import json

    from edugraph.api.app import create_app

    print(json.dumps(create_app(args.roots).openapi(), ensure_ascii=False, indent=2))
    return 0
