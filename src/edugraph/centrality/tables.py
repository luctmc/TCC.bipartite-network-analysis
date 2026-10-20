"""Tabelas finais da C-03, com configuração explícita e legenda.

Não altera o esquema congelado de ``metrics/centrality_top.csv``.
A sensibilidade recalcula em memória, sem substituir a rodada principal.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from edugraph.centrality.critical_disciplines import METRICS_COLUMNS, rank_disciplines
from edugraph.contracts.types import CentralityResult
from edugraph.reporting.tables import write_table

CONFIG_COLUMNS = ("weight_mode", "k", "estimate", "seed")
TABLE_COLUMNS = (*METRICS_COLUMNS, *CONFIG_COLUMNS)


def configuration(result: CentralityResult | None) -> dict[str, Any]:
    """Configuração da intermediação; vazio para outras métricas."""
    if result is None or result.metric != "betweenness":
        return dict.fromkeys(CONFIG_COLUMNS)
    return {name: result.params.get(name) for name in CONFIG_COLUMNS}


def ranking_rows(
    results: dict[str, CentralityResult], *, dataset: str, labels: dict[str, str], top_n: int
) -> list[dict[str, Any]]:
    """Acrescenta parâmetros às linhas finais, sem mudar as linhas do contrato."""
    return [
        {**row, **configuration(results[row["metric"]])}
        for row in rank_disciplines(results, dataset=dataset, labels=labels, top_n=top_n)
    ]


def export_table(name: str, rows: list[dict[str, Any]], *, out: Path, columns: list[str]) -> Path:
    """CSV acompanhado de legenda que explica como reproduzir o ranking."""
    path = write_table(name, rows, out_dir=out, columns=columns)
    caption = (
        "Configuração da intermediação: weight_mode=none usa saltos; inverse usa 1/w "
        "como distância. k registra os pivôs, estimate indica amostragem e seed sua "
        "semente; k vazio com estimate=False indica cálculo exato. Nas linhas de "
        "outras métricas essas colunas ficam vazias. Na tab7, identificam a "
        "intermediação usada nas comparações. A tabela de sensibilidade compara "
        "none e inverse mantendo os demais parâmetros da rodada principal. "
        "Empates no ranking são desfeitos por node_id; correlação nan significa "
        "ranking constante. Os modos calculados constam na coluna weight_mode."
    )
    path.with_suffix(".caption.txt").write_text(caption + "\n", encoding="utf-8", newline="\n")
    return path
