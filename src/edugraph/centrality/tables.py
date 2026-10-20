"""Tabelas finais da C-03, com configuração explícita e legenda.

Não altera o esquema congelado de ``metrics/centrality_top.csv``.
A sensibilidade recalcula em memória, sem substituir a rodada principal.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

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


TableKind = Literal["critical", "disagreement", "sensitivity"]

#: Cada legenda descreve somente o conteúdo da sua tabela.
CAPTIONS: dict[TableKind, str] = {
    "critical": (
        "Disciplinas críticas por métrica: rank ordena scores em ordem decrescente, "
        "com desempate por node_id. Nas linhas de intermediação, weight_mode=none "
        "usa saltos e inverse usa 1/w como distância; k registra os pivôs, estimate "
        "indica amostragem e seed sua semente. k vazio com estimate=False indica "
        "cálculo exato. Nas linhas de grau e autovetor esses campos ficam vazios."
    ),
    "disagreement": (
        "Discordância entre métricas: comparison identifica os conjuntos do top_n "
        "e as correlações de Spearman; value contém os rótulos ou o coeficiente. "
        "Spearman nan significa ranking constante. weight_mode, k, estimate e seed "
        "identificam a intermediação usada nas comparações: none usa saltos e "
        "inverse usa 1/w como distância. k registra os pivôs e seed sua semente; "
        "k vazio com estimate=False indica cálculo exato."
    ),
    "sensitivity": (
        "Sensibilidade da intermediação: weight_mode identifica o cálculo em saltos "
        "(none) ou com 1/w como distância (inverse), mantendo a normalização e a "
        "amostragem da rodada principal. k registra os pivôs, estimate indica "
        "amostragem e seed sua semente; k vazio com estimate=False indica cálculo "
        "exato. rank ordena os scores dentro de cada modo, com desempate por "
        "node_id. O artefato principal não é sobrescrito."
    ),
}


def export_table(
    name: str,
    rows: list[dict[str, Any]],
    *,
    out: Path,
    columns: list[str],
    kind: TableKind,
) -> Path:
    """CSV acompanhado de legenda específica para o objetivo da tabela."""
    path = write_table(name, rows, out_dir=out, columns=columns)
    path.with_suffix(".caption.txt").write_text(
        CAPTIONS[kind] + "\n", encoding="utf-8", newline="\n"
    )
    return path
