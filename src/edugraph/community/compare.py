"""Comparação Louvain × Girvan-Newman × ponderação  ``[B]`` — spec B-04.

Produz ``metrics/communities.csv``, a **tabela principal do capítulo 3**.
O briefing (§9) pede comparações, não só resultados: a arquitetura torna
trivial rodar as variantes e coletar as saídas porque cada uma é uma
linha desta tabela.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.types import Partition

#: Colunas de ``metrics/communities.csv``.
METRICS_COLUMNS: tuple[str, ...] = (
    "dataset",
    "projection_id",
    "algorithm",
    "modularity",
    "n_communities",
    "largest_community",
    "runtime_s",
    "status",
    "params",
)

#: Chave que identifica uma linha — rodar de novo atualiza em vez de duplicar.
METRICS_KEY: tuple[str, ...] = ("dataset", "projection_id", "algorithm")


def to_metrics_row(partition: Partition, dataset: str) -> dict[str, Any]:
    """Converte uma partição numa linha de ``metrics/communities.csv``."""
    raise NotImplementedError("B-04: ver docs/specs/frente-b/B-04-comparacao.md")


def compare(partitions: list[Partition], dataset: str) -> list[dict[str, Any]]:
    """Tabela comparativa de várias partições do mesmo dataset.

    Inclui as linhas com ``status="timeout"``: uma execução que não
    coube no orçamento é dado do artigo, e omiti-la seria esconder o
    resultado que a seção 8 do briefing manda reportar.
    """
    raise NotImplementedError("B-04: ver docs/specs/frente-b/B-04-comparacao.md")


def agreement(left: Partition, right: Partition) -> dict[str, float]:
    """Concordância entre duas partições do mesmo grafo.

    Informação mútua normalizada e índice de Rand ajustado, calculados
    sobre a estrutura — nenhuma das duas é aprendizado de máquina, são
    medidas de teoria da informação entre duas partições conhecidas.
    """
    raise NotImplementedError("B-04: concordância entre partições")
