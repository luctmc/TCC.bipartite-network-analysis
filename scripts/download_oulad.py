"""Baixa o OULAD  ``[A]`` — atalho para a spec A-02.

    python scripts/download_oulad.py
    python scripts/download_oulad.py --check

O download é **passo manual documentado**: são ~450 MB, a pasta
``data/raw/`` fica fora do git, e o grupo baixa uma vez. Este script
existe para automatizar e, principalmente, **verificar** — um download
truncado que só aparece como número estranho na tabela do artigo é o pior
tipo de erro.

Alternativa manual, se o script falhar: baixe o zip do espelho do UCI
(https://archive.ics.uci.edu/dataset/349) ou da página da OU
(https://research.stem.open.ac.uk/ouanalyse/dataset/ — em 18/09/2026 o
link de lá respondia 404), extraia as sete tabelas em ``data/raw/oulad/``
e rode este script com ``--check``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from edugraph.console import configure as configure_console
from edugraph.data.oulad.download import OULAD_URL, download, verify
from edugraph.data.oulad.schema import TABLES

DEFAULT_DEST = Path("data/raw/oulad")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    parser.add_argument("--check", action="store_true", help="só confere o que já está em disco")
    parser.add_argument("--force", action="store_true", help="rebaixa mesmo com download válido")
    args = parser.parse_args(argv)
    configure_console()

    if args.check:
        faltando = [t for t in TABLES if not (args.dest / f"{t}.csv").exists()]
        if faltando:
            print(f"[oulad] faltando em {args.dest}: {', '.join(faltando)}")
            print(f"[oulad] baixe de {OULAD_URL}")
            return 1
        print(f"[oulad] as {len(TABLES)} tabelas estão em {args.dest}")
        return 0 if verify(args.dest) else 1

    download(args.dest, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
