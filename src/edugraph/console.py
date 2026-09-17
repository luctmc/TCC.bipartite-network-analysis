"""Saída de console em UTF-8  ``[T]``.

No Windows, ``sys.stdout`` herda a codepage do console (``cp1252`` no
padrão pt-BR), e imprimir uma seta ou um acento levanta
``UnicodeEncodeError`` no meio de um comando que já fez o trabalho todo.
Como o projeto fala português na CLI, isso não é caso de borda.

A chamada a :func:`configure` fica nos dois pontos de entrada —
``edugraph.__main__`` e ``scripts/make_fixtures.py`` — e em nenhum outro
lugar: biblioteca não mexe em ``sys.stdout``.
"""

from __future__ import annotations

import sys


def configure() -> None:
    """Força UTF-8 na saída padrão, sem quebrar se o fluxo não permitir."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:  # fluxo redirecionado por outro objeto
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):  # pragma: no cover - fluxo fechado
            continue
