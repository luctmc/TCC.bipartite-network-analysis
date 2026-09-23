"""Comparação Louvain × Girvan-Newman × ponderação  ``[B]`` — spec B-04.

Produz ``metrics/communities.csv``, a **tabela principal do capítulo 3**.
O briefing (§9) pede comparações, não só resultados: a arquitetura torna
trivial rodar as variantes e coletar as saídas porque cada uma é uma
linha desta tabela.

A tabela responde, sem cálculo adicional: qual algoritmo deu o maior Q,
qual foi mais rápido e quanto, quantas comunidades cada um achou, e se a
execução coube no orçamento (coluna ``status``).

Concordância entre partições
----------------------------
:func:`agreement` compara duas partições **do mesmo grafo** por
informação mútua normalizada (NMI) e índice de Rand ajustado (ARI). As
duas são implementadas aqui, à mão, sobre a tabela de contingência: são
contas fechadas sobre duas partições já conhecidas — não há treino, não
há rótulo, e `scikit-learn` está proibido pela seção 2 do briefing
(``tests/contract/test_no_ml.py`` recusaria o import).
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
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

#: Nome da tabela em ``metrics/``.
METRICS_NAME = "communities"


def _params_cell(params: dict[str, Any]) -> str:
    """Serializa ``params`` numa célula de CSV, de forma determinística.

    JSON compacto com chaves ordenadas: cabe numa coluna, volta a ser
    dicionário com ``json.loads`` e não muda de bytes entre execuções —
    o que ``str(dict)`` não garante (a ordem seria a de inserção).
    """
    return json.dumps(params, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def to_metrics_row(partition: Partition, dataset: str) -> dict[str, Any]:
    """Converte uma partição numa linha de ``metrics/communities.csv``."""
    groups = partition.groups()
    return {
        "dataset": dataset,
        "projection_id": partition.projection_id,
        "algorithm": partition.algorithm,
        "modularity": partition.modularity,
        "n_communities": partition.n_communities,
        "largest_community": max((len(nodes) for nodes in groups.values()), default=0),
        "runtime_s": partition.runtime_s,
        "status": partition.status,
        "params": _params_cell(partition.params),
    }


def compare(partitions: list[Partition], dataset: str) -> list[dict[str, Any]]:
    """Tabela comparativa de várias partições do mesmo dataset.

    Inclui as linhas com ``status="timeout"``: uma execução que não
    coube no orçamento é dado do artigo, e omiti-la seria esconder o
    resultado que a seção 8 do briefing manda reportar.

    As linhas saem ordenadas por :data:`METRICS_KEY`, que é a mesma
    ordem em que ``append_metrics_rows`` as grava — assim a tabela da
    tela e a do arquivo são a mesma coisa.
    """
    rows = [to_metrics_row(partition, dataset) for partition in partitions]
    return sorted(rows, key=lambda row: tuple(str(row[col]) for col in METRICS_KEY))


def write_metrics(rows: list[dict[str, Any]], out_root: str | Path, dataset: str) -> Path:
    """Grava/atualiza ``metrics/communities.csv`` (idempotente por :data:`METRICS_KEY`).

    Raises
    ------
    ContractError
        Se alguma linha não trouxer exatamente :data:`METRICS_COLUMNS` —
        a tabela do capítulo 3 tem esquema, e mudá-lo exige subir
        ``SCHEMA_VERSION`` (ver docs/contratos/metrics.md).
    """
    ordered = []
    for row in rows:
        faltando = sorted(set(METRICS_COLUMNS) - set(row))
        if faltando:
            raise ContractError(
                f"metrics/{METRICS_NAME}.csv: linha sem as colunas {faltando}. "
                f"Esperado exatamente {list(METRICS_COLUMNS)}."
            )
        ordered.append({col: row[col] for col in METRICS_COLUMNS})
    return io.append_metrics_rows(out_root, dataset, METRICS_NAME, ordered, key=list(METRICS_KEY))


# ---------------------------------------------------------------------
# Concordância entre duas partições
# ---------------------------------------------------------------------


def _contingency(left: dict[str, int], right: dict[str, int]) -> dict[tuple[int, int], int]:
    """Tabela de contingência entre duas partições dos mesmos nós."""
    table: defaultdict[tuple[int, int], int] = defaultdict(int)
    for node, community in left.items():
        table[community, right[node]] += 1
    return dict(table)


def _marginals(table: dict[tuple[int, int], int]) -> tuple[dict[int, int], dict[int, int]]:
    rows: defaultdict[int, int] = defaultdict(int)
    cols: defaultdict[int, int] = defaultdict(int)
    for (a, b), count in table.items():
        rows[a] += count
        cols[b] += count
    return dict(rows), dict(cols)


def _entropy(counts: dict[int, int], total: int) -> float:
    return -sum((c / total) * math.log(c / total) for c in counts.values() if c > 0)


def normalized_mutual_information(left: dict[str, int], right: dict[str, int]) -> float:
    """NMI entre duas atribuições de comunidade sobre os mesmos nós.

    Normalização pela **média aritmética** das entropias, que é a
    convenção mais usada e a que devolve 1 para partições idênticas:

    .. math::

        \\mathrm{NMI} = \\frac{2\\,I(X;Y)}{H(X) + H(Y)}

    Duas partições triviais (tudo numa comunidade só) têm entropia zero
    e são idênticas: o valor é 1 por convenção, não 0/0. Se só uma delas
    for trivial, a informação mútua é zero e o valor é 0.
    """
    total = len(left)
    if total == 0:
        raise ContractError("NMI: partições vazias")

    table = _contingency(left, right)
    rows, cols = _marginals(table)
    h_left, h_right = _entropy(rows, total), _entropy(cols, total)

    if h_left <= 0.0 and h_right <= 0.0:
        return 1.0
    if h_left <= 0.0 or h_right <= 0.0:
        return 0.0

    mutual = sum(
        (count / total) * math.log((count * total) / (rows[a] * cols[b]))
        for (a, b), count in table.items()
        if count > 0
    )
    return 2.0 * mutual / (h_left + h_right)


def adjusted_rand_index(left: dict[str, int], right: dict[str, int]) -> float:
    """Índice de Rand ajustado ao acaso, pela tabela de contingência.

    Conta pares de nós classificados do mesmo jeito pelas duas
    partições, descontando o que o acaso produziria. Vale 1 para
    partições idênticas e ~0 para partições independentes; pode ser
    negativo, o que significa concordância **abaixo** do acaso.
    """
    total = len(left)
    if total < 2:
        raise ContractError("índice de Rand ajustado: são necessários ao menos dois nós")

    def pairs(n: int) -> float:
        return n * (n - 1) / 2.0

    table = _contingency(left, right)
    rows, cols = _marginals(table)

    index = sum(pairs(count) for count in table.values())
    expected_rows = sum(pairs(count) for count in rows.values())
    expected_cols = sum(pairs(count) for count in cols.values())
    expected = expected_rows * expected_cols / pairs(total)
    maximum = (expected_rows + expected_cols) / 2.0

    if math.isclose(maximum, expected):
        # As duas partições são triviais (uma comunidade só, ou todos
        # singletons): não há par a discordar, e o índice é 1 ou 0
        # conforme elas coincidam.
        return 1.0 if left == right else 0.0
    return (index - expected) / (maximum - expected)


def agreement(left: Partition, right: Partition) -> dict[str, float]:
    """Concordância entre duas partições do mesmo grafo.

    Informação mútua normalizada e índice de Rand ajustado, calculados
    sobre a estrutura — nenhuma das duas é aprendizado de máquina, são
    medidas de teoria da informação entre duas partições conhecidas.

    Raises
    ------
    ContractError
        Se as duas não cobrirem exatamente o mesmo conjunto de nós.
        Comparar partições de grafos diferentes devolveria um número
        sem significado.
    """
    if set(left.membership) != set(right.membership):
        faltando = sorted(set(left.membership) - set(right.membership))[:5]
        sobrando = sorted(set(right.membership) - set(left.membership))[:5]
        raise ContractError(
            f"agreement({left.artifact_id!r}, {right.artifact_id!r}): as partições cobrem "
            f"conjuntos de nós diferentes (faltando={faltando} sobrando={sobrando})"
        )
    return {
        "nmi": normalized_mutual_information(left.membership, right.membership),
        "adjusted_rand": adjusted_rand_index(left.membership, right.membership),
    }


def agreement_matrix(partitions: list[Partition]) -> list[dict[str, Any]]:
    """Concordância entre todos os pares de partições da mesma projeção.

    É o que responde "Louvain e Girvan-Newman acharam a mesma coisa?"
    sem depender de Q — dois algoritmos podem chegar ao mesmo Q com
    partições bem diferentes.
    """
    rows: list[dict[str, Any]] = []
    for i, left in enumerate(partitions):
        for right in partitions[i + 1 :]:
            if left.projection_id != right.projection_id:
                continue
            rows.append(
                {
                    "projection_id": left.projection_id,
                    "left": left.algorithm,
                    "right": right.algorithm,
                    **agreement(left, right),
                }
            )
    return sorted(rows, key=lambda row: (row["projection_id"], row["left"], row["right"]))
