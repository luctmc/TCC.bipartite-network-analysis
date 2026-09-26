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

**Empates.** A chave de ``metrics/centrality_top.csv`` inclui ``rank``,
então duas disciplinas nunca dividem uma posição: entre scores iguais,
a de menor ``node_id`` vem antes. Numa projeção degenerada (K₇ em
``synthetic_v1``) a tabela inteira é ordem alfabética — e é por isso
que ela precisa ser lida junto com o score, não só com a posição.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.paths import ArtifactRoots
from edugraph.contracts.types import CentralityResult, ProjectionBundle

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

#: Nome da tabela em ``metrics/``.
METRICS_NAME = "centrality_top"

#: Ordem das métricas nas tabelas: a da Introdução.
METRIC_ORDER: tuple[str, ...] = ("degree", "betweenness", "eigenvector")


def ordered_metrics(results: dict[str, CentralityResult]) -> list[str]:
    """As métricas presentes, na ordem das tabelas (desconhecidas no fim)."""
    known = [m for m in METRIC_ORDER if m in results]
    return known + sorted(set(results) - set(known))


def _projection_id(results: dict[str, CentralityResult]) -> str:
    """O id comum a todos os resultados — misturar projeções é engano."""
    if not results:
        raise ContractError("disciplinas críticas: nenhum resultado de centralidade recebido")
    ids = {r.projection_id for r in results.values()}
    if len(ids) != 1:
        raise ContractError(
            f"disciplinas críticas: os resultados vêm de projeções diferentes {sorted(ids)}; "
            "o ranking compara métricas sobre a mesma projeção"
        )
    return ids.pop()


def rank_disciplines(
    results: dict[str, CentralityResult],
    *,
    top_n: int = 10,
    dataset: str = "",
    labels: dict[str, str] | None = None,
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
    dataset
        Vai para a coluna ``dataset``.
    labels
        ``node_id`` → rótulo legível (``DDDD_2014J`` → ``DDD_2014J``).
        Sem ele, o rótulo repete o id.

    Returns
    -------
    list[dict]
        Uma linha por (métrica, posição), com as colunas de
        :data:`METRICS_COLUMNS`, posições a partir de 1.
    """
    if top_n < 1:
        raise ContractError(f"top_n precisa ser >= 1; recebeu {top_n!r}")
    projection_id = _projection_id(results)
    names = labels or {}

    rows: list[dict[str, Any]] = []
    for metric in ordered_metrics(results):
        # CentralityResult.top já desempata por id (docs/contratos/centrality.md).
        for rank, (node, score) in enumerate(results[metric].top(top_n), start=1):
            rows.append(
                {
                    "dataset": dataset,
                    "projection_id": projection_id,
                    "metric": metric,
                    "rank": rank,
                    "node_id": node,
                    "label": names.get(node, node),
                    "score": score,
                }
            )
    return rows


def critical_set(results: dict[str, CentralityResult], *, top_n: int = 5) -> dict[str, list[str]]:
    """Conjunto de disciplinas críticas por métrica, para o relatório interno.

    Cada lista vem na ordem do ranking (não alfabética): no relatório, a
    primeira é a mais central.
    """
    _projection_id(results)
    return {
        metric: [node for node, _ in results[metric].top(top_n)]
        for metric in ordered_metrics(results)
    }


def write_metrics(rows: list[dict[str, Any]], out: str | Path, dataset: str) -> Path:
    """Acrescenta as linhas a ``metrics/centrality_top.csv``, idempotente pela chave.

    Rodar de novo atualiza as posições em vez de duplicá-las. Atenção: se
    a rodada nova usar um ``top_n`` menor, as posições além dele ficam da
    rodada anterior — é o comportamento da chave do contrato, e por isso
    a CLI usa sempre o mesmo ``top_n`` padrão.
    """
    ordered = [{column: row[column] for column in METRICS_COLUMNS} for row in rows]
    return io.append_metrics_rows(out, dataset, METRICS_NAME, ordered, key=list(METRICS_KEY))


def is_discipline_projection(projection_id: str) -> bool:
    """As projeções sobre as quais o ranking é saída obrigatória."""
    return projection_id.startswith("discipline_")


def labels_of(projection: ProjectionBundle) -> dict[str, str]:
    """``node_id`` → rótulo, lido dos atributos da projeção."""
    return {
        str(node): str(data.get("label", node)) for node, data in projection.graph.nodes(data=True)
    }


def load_results(
    roots: ArtifactRoots, dataset: str, projection_id: str
) -> dict[str, CentralityResult]:
    """As métricas já calculadas para a projeção, na ordem das tabelas."""
    return {
        metric: io.load_centrality(roots, dataset, projection_id, metric)  # type: ignore[arg-type]
        for metric in METRIC_ORDER
        if roots.has(dataset, "centrality", projection_id, f"{metric}.meta.json")
    }
