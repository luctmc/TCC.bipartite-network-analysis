"""Validadores — os invariantes da §4.4 do plano, como código executável.

Cada função levanta :class:`~edugraph.contracts.errors.ContractError` com
uma mensagem que diz o que foi violado e onde. Os testes de contrato
(``tests/contract/``) rodam todos eles sobre **todo** artefato encontrado
sob a raiz em uso, seja ela ``data/fixtures`` ou ``data/processed`` — são
os mesmos testes hoje sobre a fixture e amanhã sobre o OULAD.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import networkx as nx

from edugraph.contracts.errors import ContractError
from edugraph.contracts.paths import (
    NODES_FILE,
    ArtifactRoots,
    as_roots,
)
from edugraph.contracts.types import (
    FORBIDDEN_NODE_COLUMNS,
    BipartiteBundle,
    CentralityResult,
    Outcomes,
    Partition,
    ProjectionBundle,
)

#: Prefixo de id exigido por lado. Torna o kind legível no CSV e permite
#: detectar mistura de lados só olhando o arquivo.
KIND_PREFIX: dict[str, str] = {"student": "S", "discipline": "D"}

#: Faixa admissível de modularidade. O limite inferior de -1/2 é o do
#: teorema de Brandes et al. (2008).
MODULARITY_RANGE = (-0.5, 1.0)

__all__ = [
    "validate_bipartite",
    "validate_centrality",
    "validate_dataset",
    "validate_node_file",
    "validate_outcomes",
    "validate_partition",
    "validate_projection",
]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _finite_positive(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and number > 0


# ---------------------------------------------------------------------
# Bipartido
# ---------------------------------------------------------------------


def validate_bipartite(bundle: BipartiteBundle) -> None:
    """Todo nó tem kind; toda aresta cruza os lados; prefixos coerentes."""
    graph = bundle.graph
    where = f"BipartiteBundle(dataset={bundle.spec.dataset!r})"

    for node, data in graph.nodes(data=True):
        kind = data.get("kind")
        _require(
            kind in KIND_PREFIX,
            f"{where}: nó {node!r} tem kind={kind!r}; esperado 'student' ou 'discipline'",
        )
        prefix = KIND_PREFIX[str(kind)]
        _require(
            str(node).startswith(prefix),
            f"{where}: nó {node!r} é '{kind}' e deveria começar com {prefix!r}",
        )

    for source, target, data in graph.edges(data=True):
        kinds = {graph.nodes[source].get("kind"), graph.nodes[target].get("kind")}
        _require(
            kinds == {"student", "discipline"},
            f"{where}: aresta ({source!r}, {target!r}) liga {kinds}; "
            "o bipartido só admite arestas student-discipline",
        )
        _require(
            _finite_positive(data.get("weight", 1.0)),
            f"{where}: aresta ({source!r}, {target!r}) tem weight={data.get('weight')!r}; "
            "esperado número finito e positivo",
        )

    _require(
        nx.number_of_selfloops(graph) == 0,
        f"{where}: o bipartido não admite laços",
    )
    _require(
        bool(bundle.students) and bool(bundle.disciplines),
        f"{where}: os dois lados precisam ter pelo menos um nó "
        f"(alunos={len(bundle.students)}, disciplinas={len(bundle.disciplines)})",
    )


# ---------------------------------------------------------------------
# Projeção
# ---------------------------------------------------------------------


def validate_projection(bundle: ProjectionBundle) -> None:
    """Sem laços, um só lado, pesos finitos e positivos."""
    graph = bundle.graph
    where = f"ProjectionBundle({bundle.projection_id!r})"
    expected_kind = bundle.spec.side

    _require(
        nx.number_of_selfloops(graph) == 0,
        f"{where}: projeção não admite laços",
    )
    _require(
        not graph.is_multigraph(),
        f"{where}: projeção não admite multiarestas",
    )

    for node, data in graph.nodes(data=True):
        kind = data.get("kind")
        _require(
            kind == expected_kind,
            f"{where}: nó {node!r} tem kind={kind!r}, mas spec.side={expected_kind!r}",
        )

    min_weight = bundle.spec.min_weight
    for source, target, data in graph.edges(data=True):
        weight = data.get("weight")
        _require(
            _finite_positive(weight),
            f"{where}: aresta ({source!r}, {target!r}) tem weight={weight!r}; "
            "esperado número finito e positivo",
        )
        if min_weight is not None:
            # `weight is not None` já foi garantido por _finite_positive acima;
            # repetir aqui é o que permite ao mypy estreitar o tipo antes do
            # float() — sem ele, weight seria `Any | None`.
            _require(
                weight is not None and float(weight) >= min_weight,
                f"{where}: aresta ({source!r}, {target!r}) tem weight={weight!r} "
                f"abaixo do corte min_weight={min_weight}",
            )


# ---------------------------------------------------------------------
# Partição
# ---------------------------------------------------------------------


def validate_partition(partition: Partition, projection: ProjectionBundle | None = None) -> None:
    """Ids densos, contagem coerente, Q na faixa, cobertura dos nós.

    Quando ``projection`` é passada, verifica também que o conjunto de
    chaves de ``membership`` é exatamente o conjunto de nós dela — é
    esse cruzamento que impede uma partição de uma projeção ser servida
    como se fosse de outra.
    """
    where = f"Partition({partition.artifact_id!r})"

    _require(bool(partition.membership), f"{where}: membership vazio")

    communities = sorted(set(partition.membership.values()))
    _require(
        communities == list(range(len(communities))),
        f"{where}: ids de comunidade não são densos 0..k-1; encontrados {communities[:10]}…",
    )
    _require(
        partition.n_communities == len(communities),
        f"{where}: n_communities={partition.n_communities} difere das "
        f"{len(communities)} comunidades presentes em membership",
    )

    low, high = MODULARITY_RANGE
    _require(
        math.isfinite(partition.modularity) and low <= partition.modularity <= high,
        f"{where}: modularity={partition.modularity} fora da faixa [{low}, {high}]",
    )
    _require(
        math.isfinite(partition.runtime_s) and partition.runtime_s >= 0,
        f"{where}: runtime_s={partition.runtime_s} inválido",
    )

    if projection is not None:
        nodes = set(projection.graph.nodes)
        keys = set(partition.membership)
        _require(
            keys == nodes,
            f"{where}: membership cobre {len(keys)} nós, mas a projeção "
            f"{projection.projection_id!r} tem {len(nodes)}; "
            f"faltando={sorted(nodes - keys)[:5]} sobrando={sorted(keys - nodes)[:5]}",
        )
        _require(
            partition.projection_id == projection.projection_id,
            f"{where}: projection_id não confere com {projection.projection_id!r}",
        )


# ---------------------------------------------------------------------
# Centralidade
# ---------------------------------------------------------------------


def validate_centrality(
    result: CentralityResult, projection: ProjectionBundle | None = None
) -> None:
    """Valores finitos, faixas por métrica, cobertura dos nós."""
    where = f"CentralityResult({result.projection_id!r}, {result.metric!r})"

    _require(bool(result.scores), f"{where}: scores vazio")

    for node, score in result.scores.items():
        _require(
            math.isfinite(score),
            f"{where}: nó {node!r} tem score={score!r}, que não é finito",
        )

    normalized = bool(result.params.get("normalized", True))
    if result.metric in ("degree", "betweenness") and normalized:
        for node, score in result.scores.items():
            _require(
                0.0 <= score <= 1.0,
                f"{where}: nó {node!r} tem score={score} fora de [0, 1] "
                f"apesar de params.normalized=True",
            )
    if result.metric == "eigenvector":
        for node, score in result.scores.items():
            _require(
                score >= 0.0,
                f"{where}: autovetor com componente negativa no nó {node!r} ({score})",
            )

    if projection is not None:
        nodes = set(projection.graph.nodes)
        keys = set(result.scores)
        _require(
            keys == nodes,
            f"{where}: scores cobrem {len(keys)} nós, mas a projeção tem {len(nodes)}; "
            f"faltando={sorted(nodes - keys)[:5]} sobrando={sorted(keys - nodes)[:5]}",
        )


# ---------------------------------------------------------------------
# Rótulos fora do grafo
# ---------------------------------------------------------------------


def validate_node_file(path: Path) -> None:
    """``nodes.csv`` não pode carregar rótulo, nota ou atributo demográfico.

    Este é o validador que materializa a restrição inegociável da seção
    2 do briefing (ADR-0008): se um desfecho vazar para dentro do grafo,
    um algoritmo pode acabar usando-o como entrada sem que ninguém note.
    """
    with path.open("r", encoding="utf-8", newline="") as handle:
        header = next(csv.reader(handle), [])

    proibidas = sorted(FORBIDDEN_NODE_COLUMNS.intersection({c.strip().lower() for c in header}))
    _require(
        not proibidas,
        f"{path}: colunas proibidas em nodes.csv: {proibidas}. "
        "Rótulo histórico vive em bipartite/outcomes.csv e só é lido por evaluate.py "
        "(ADR-0008).",
    )


def validate_outcomes(outcomes: Outcomes, students: set[str] | None = None) -> None:
    """Desfechos referem-se a alunos existentes e usam o vocabulário do OULAD."""
    where = "Outcomes"
    permitidos = {"Pass", "Distinction", "Fail", "Withdrawn"}

    for student, result in outcomes.final_result.items():
        _require(
            result in permitidos,
            f"{where}: aluno {student!r} tem final_result={result!r}; esperado um de {permitidos}",
        )
    if students is not None:
        desconhecidos = sorted(set(outcomes.final_result) - students)
        _require(
            not desconhecidos,
            f"{where}: desfecho para alunos ausentes do bipartido: {desconhecidos[:5]}",
        )


# ---------------------------------------------------------------------
# Varredura de um dataset inteiro
# ---------------------------------------------------------------------


def validate_dataset(
    roots: ArtifactRoots | list[str | Path] | str | Path | None, dataset: str
) -> list[str]:
    """Valida tudo o que existir do dataset e devolve o que foi checado.

    Usada pelos testes de contrato e pelo comando
    ``python -m edugraph validate``. Camadas ausentes são puladas, porque
    no dia 0 nem toda frente já gravou a sua — o que existe, porém,
    precisa estar correto.
    """
    from edugraph.contracts import io

    resolved = as_roots(roots)
    checked: list[str] = []

    bipartite: BipartiteBundle | None = None
    if resolved.has(dataset, "bipartite", "meta.json"):
        bipartite = io.load_bipartite(resolved, dataset)
        validate_bipartite(bipartite)
        validate_node_file(resolved.find(dataset, "bipartite", NODES_FILE))
        checked.append("bipartite")

    if resolved.has(dataset, "bipartite", "outcomes.csv"):
        outcomes = io.load_outcomes(resolved, dataset)
        validate_outcomes(outcomes, bipartite.students if bipartite else None)
        checked.append("outcomes")

    projections: dict[str, ProjectionBundle] = {}
    for projection_id in resolved.projections(dataset):
        bundle = io.load_projection(resolved, dataset, projection_id)
        validate_projection(bundle)
        validate_node_file(resolved.find(dataset, "projections", projection_id, NODES_FILE))
        projections[projection_id] = bundle
        checked.append(f"projections/{projection_id}")

    for artifact_id in resolved.partitions(dataset):
        partition = io.load_partition(resolved, dataset, artifact_id)
        validate_partition(partition, projections.get(partition.projection_id))
        checked.append(f"communities/{artifact_id}")

    for projection_id in resolved.centralities(dataset):
        directory = resolved.find(dataset, "centrality", projection_id)
        for meta_file in sorted(directory.glob("*.meta.json")):
            metric = meta_file.name.removesuffix(".meta.json")
            result = io.load_centrality(resolved, dataset, projection_id, metric)  # type: ignore[arg-type]
            validate_centrality(result, projections.get(projection_id))
            checked.append(f"centrality/{projection_id}/{metric}")

    return checked
