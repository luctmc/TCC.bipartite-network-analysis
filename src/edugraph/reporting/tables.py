"""Escrita das tabelas finais do artigo  ``[T]``.

``results/tables/`` é commitado: são os números que entram no texto, e
tê-los versionados é o que permite comparar a tabela do rascunho com a
da versão final e explicar a diferença.

Escrita canônica, como em :mod:`edugraph.contracts.io`: mesma entrada,
mesmo arquivo byte a byte.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

#: Onde as tabelas do artigo são gravadas.
TABLES_DIR = Path("results/tables")


def write_table(
    name: str,
    rows: list[dict[str, Any]],
    *,
    out_dir: Path = TABLES_DIR,
    columns: list[str] | None = None,
) -> Path:
    """Grava ``<out_dir>/<name>.csv`` em ordem canônica.

    Parameters
    ----------
    name
        Nome do arquivo, sem extensão (ex.: ``"tab3-comunidades"``).
    rows
        Linhas já prontas; nenhuma transformação acontece aqui.
    columns
        Ordem das colunas. O padrão é a ordem de chaves da primeira linha.

    Returns
    -------
    Path
        O arquivo escrito.
    """
    if not rows:
        raise ValueError(f"tabela '{name}' sem linhas")

    header = columns or list(rows[0].keys())
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow(["" if row.get(c) is None else row.get(c) for c in header])
    return path


def to_latex(rows: list[dict[str, Any]], *, columns: list[str] | None = None) -> str:
    """Converte a tabela para ``tabular`` do LaTeX.

    Conveniência para colar no artigo. Implementar quando a primeira
    tabela real existir (onda 4) — antes disso não se sabe qual é o
    formato de número que o modelo do artigo pede.
    """
    raise NotImplementedError("onda 4: exportação LaTeX das tabelas")
