"""Disciplinas críticas no fluxo curricular  ``[C]`` — spec C-03.

**Saída obrigatória** (briefing §6.2), e a que a seção 13 do briefing
avisa ser fácil de esquecer: a centralidade precisa ser aplicada sobre
os nós de **disciplina**, na projeção disciplina↔disciplina, não só
sobre alunos.

O que é uma "disciplina crítica" aqui: um nó de alta intermediação na
projeção disciplina↔disciplina é um ponto por onde passa a ligação entre
partes do currículo que, de outro modo, estariam distantes — um gargalo
estrutural. Nada disso depende de desfecho: o gargalo é topológico, e a
relação dele com a taxa de reprovação é justamente o que a spec C-06
verifica **a posteriori**.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.types import CentralityResult

#: Colunas de ``metrics/centrality_top.csv``.
METRICS_COLUMNS: tuple[str, ...] = (
    "dataset",
    "projection_id",
    "metric",
    "rank",
    "node_id",
    "label",
    "score",
)

METRICS_KEY: tuple[str, ...] = ("dataset", "projection_id", "metric", "rank")


def rank_disciplines(
    results: dict[str, CentralityResult], *, top_n: int = 10
) -> list[dict[str, Any]]:
    """Ranking das disciplinas por cada métrica, no formato da tabela.

    Parameters
    ----------
    results
        Métrica → resultado, sobre a projeção ``discipline_*``.
    top_n
        Quantas posições reportar. Com 7 ou 22 disciplinas, ``top_n``
        maior que o grafo devolve o ranking inteiro — o que é o caso
        desejável para o artigo.

    Notes
    -----
    A implementar em C-03. Desempate por ``node_id`` para que a tabela
    seja determinística; empates em centralidade são comuns em grafos
    pequenos e densos como a projeção disciplina↔disciplina com V =
    módulo (ver a decisão D1).
    """
    raise NotImplementedError("C-03: ver docs/specs/frente-c/C-03-disciplinas-criticas.md")


def critical_set(results: dict[str, CentralityResult], *, top_n: int = 5) -> dict[str, list[str]]:
    """Conjunto de disciplinas críticas por métrica, para o relatório interno."""
    raise NotImplementedError("C-03: conjunto de disciplinas críticas")
