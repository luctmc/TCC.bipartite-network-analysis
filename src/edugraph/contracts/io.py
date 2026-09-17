"""Leitura e escrita dos artefatos — o único lugar que toca o disco.

Formato: uma lista de arestas em CSV mais um ``meta.json`` por artefato
(ADR-0002). CSV abre no pandas, no Excel e no front-end; o ``meta.json``
carrega a especificação que gerou o artefato, que é o que o artigo
precisa citar.

**Escrita canônica.** Nós e arestas saem ordenados, arestas com os
extremos em ordem lexicográfica, floats no ``repr`` mais curto que
retorna ao mesmo valor, quebra de linha ``\\n`` e UTF-8 explícito. Isso
faz de ``escrever → ler → escrever`` uma identidade byte a byte, e é o
que permite versionar fixtures sem que um diff apareça do nada (ADR-0011).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import networkx as nx

from edugraph.contracts.errors import ContractError
from edugraph.contracts.paths import (
    CENTRALITY_DIR,
    EDGES_FILE,
    MEMBERSHIP_FILE,
    META_FILE,
    NODES_FILE,
    OUTCOMES_FILE,
    PROFILE_FILE,
    ArtifactRoots,
    as_roots,
    bipartite_dir,
    centrality_dir,
    community_dir,
    ensure_dir,
    metrics_dir,
    projection_dir,
)
from edugraph.contracts.types import (
    SCHEMA_VERSION,
    BipartiteBundle,
    BipartiteSpec,
    CentralityMetricName,
    CentralityResult,
    Meta,
    Outcomes,
    Partition,
    ProjectionBundle,
    ProjectionSpec,
)

ENCODING = "utf-8"

#: Fim de linha canônico, explícito em **toda** escrita de texto.
#:
#: Sem ele, a tradução padrão do Windows transforma cada ``\n`` em
#: ``\r\n`` e o mesmo artefato sai com bytes diferentes conforme o
#: sistema de quem o gerou — o que quebraria a escrita canônica da
#: ADR-0011 justamente na máquina do grupo. Ver também ``.gitattributes``.
NEWLINE = "\n"

__all__ = [
    "append_metrics_rows",
    "load_bipartite",
    "load_centrality",
    "load_metrics",
    "load_outcomes",
    "load_partition",
    "load_profile",
    "load_projection",
    "save_bipartite",
    "save_centrality",
    "save_outcomes",
    "save_partition",
    "save_profile",
    "save_projection",
]


# ---------------------------------------------------------------------
# Primitivas de escrita canônica
# ---------------------------------------------------------------------


def _fmt(value: Any) -> str:
    """Serializa um valor de célula de forma determinística.

    Floats usam ``repr``, que no CPython devolve a representação decimal
    mais curta que retorna exatamente ao mesmo binário — round-trip sem
    perda e sem ruído de casas decimais no diff.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return repr(value)
    return str(value)


def _write_csv(path: Path, header: list[str], rows: list[list[Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding=ENCODING, newline="") as handle:
        writer = csv.writer(handle, lineterminator=NEWLINE)
        writer.writerow(header)
        for row in rows:
            writer.writerow([_fmt(cell) for cell in row])


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding=ENCODING, newline="") as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        return header, list(reader)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    path.write_text(text + NEWLINE, encoding=ENCODING, newline=NEWLINE)


def _read_json(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding=ENCODING))
    return data


def _meta_payload(meta: Meta, kind: str, **extra: Any) -> dict[str, Any]:
    return {
        "schema_version": meta.schema_version,
        "kind": kind,
        "producer": meta.producer,
        "created_at": meta.created_at,
        "stats": meta.stats,
        "notes": meta.notes,
        **extra,
    }


def _meta_from_payload(payload: dict[str, Any]) -> Meta:
    return Meta(
        schema_version=str(payload.get("schema_version", SCHEMA_VERSION)),
        producer=str(payload.get("producer", "unknown")),
        created_at=str(payload.get("created_at", "")),
        stats=dict(payload.get("stats", {})),
        notes=str(payload.get("notes", "")),
    )


def _check_schema_version(payload: dict[str, Any], where: Path) -> None:
    found = str(payload.get("schema_version", ""))
    if found != SCHEMA_VERSION:
        raise ContractError(
            f"{where}: schema_version '{found}' incompatível com "
            f"'{SCHEMA_VERSION}' esperado por este código. "
            "Regenere o artefato ou consulte a ADR que subiu a versão."
        )


def _graph_rows(graph: nx.Graph) -> tuple[list[list[Any]], list[list[Any]]]:
    """Nós e arestas em ordem canônica."""
    nodes = [
        [node, data.get("kind", ""), data.get("label", node)]
        for node, data in sorted(graph.nodes(data=True), key=lambda item: str(item[0]))
    ]
    edges_raw = []
    for source, target, data in graph.edges(data=True):
        a, b = (str(source), str(target))
        if a > b:
            a, b = b, a
        edges_raw.append((a, b, float(data.get("weight", 1.0))))
    edges = [[a, b, w] for a, b, w in sorted(edges_raw)]
    return nodes, edges


def _graph_from_rows(node_rows: list[dict[str, str]], edge_rows: list[dict[str, str]]) -> nx.Graph:
    graph = nx.Graph()
    for row in node_rows:
        graph.add_node(row["id"], kind=row.get("kind", ""), label=row.get("label", row["id"]))
    for row in edge_rows:
        graph.add_edge(row["source"], row["target"], weight=float(row["weight"]))
    return graph


# ---------------------------------------------------------------------
# BipartiteBundle
# ---------------------------------------------------------------------


def save_bipartite(bundle: BipartiteBundle, root: str | Path, *, validate: bool = True) -> Path:
    """Grava ``<root>/<dataset>/bipartite/`` e devolve o diretório."""
    if validate:
        from edugraph.contracts import validate as _validate

        _validate.validate_bipartite(bundle)

    out = ensure_dir(bipartite_dir(root, bundle.spec.dataset))
    nodes, edges = _graph_rows(bundle.graph)
    _write_csv(out / NODES_FILE, ["id", "kind", "label"], nodes)
    _write_csv(out / EDGES_FILE, ["source", "target", "weight"], edges)
    meta = bundle.meta.with_stats(
        n_students=len(bundle.students),
        n_disciplines=len(bundle.disciplines),
        n_edges=bundle.graph.number_of_edges(),
    )
    _write_json(
        out / META_FILE,
        _meta_payload(meta, "bipartite", spec=bundle.spec.to_dict()),
    )
    return out


def load_bipartite(
    roots: ArtifactRoots | list[str | Path] | str | Path | None, dataset: str
) -> BipartiteBundle:
    """Lê o bipartido do dataset na primeira raiz que o tiver."""
    resolved = as_roots(roots)
    meta_path = resolved.find(dataset, "bipartite", META_FILE)
    payload = _read_json(meta_path)
    _check_schema_version(payload, meta_path)

    _, node_rows = _read_csv(meta_path.parent / NODES_FILE)
    _, edge_rows = _read_csv(meta_path.parent / EDGES_FILE)
    graph = _graph_from_rows(node_rows, edge_rows)
    return BipartiteBundle(
        graph=graph,
        spec=BipartiteSpec.from_dict(payload["spec"]),
        meta=_meta_from_payload(payload),
    )


# ---------------------------------------------------------------------
# ProjectionBundle
# ---------------------------------------------------------------------


def save_projection(bundle: ProjectionBundle, root: str | Path, *, validate: bool = True) -> Path:
    """Grava ``<root>/<dataset>/projections/<projection_id>/``."""
    if validate:
        from edugraph.contracts import validate as _validate

        _validate.validate_projection(bundle)

    out = ensure_dir(projection_dir(root, bundle.source.dataset, bundle.projection_id))
    nodes, edges = _graph_rows(bundle.graph)
    _write_csv(out / NODES_FILE, ["id", "kind", "label"], nodes)
    _write_csv(out / EDGES_FILE, ["source", "target", "weight"], edges)
    meta = bundle.meta.with_stats(
        n_nodes=bundle.graph.number_of_nodes(),
        n_edges=bundle.graph.number_of_edges(),
    )
    _write_json(
        out / META_FILE,
        _meta_payload(
            meta,
            "projection",
            spec=bundle.spec.to_dict(),
            source=bundle.source.to_dict(),
        ),
    )
    return out


def load_projection(
    roots: ArtifactRoots | list[str | Path] | str | Path | None,
    dataset: str,
    projection_id: str,
) -> ProjectionBundle:
    """Lê uma projeção pelo seu id (``student_simple``, …)."""
    resolved = as_roots(roots)
    meta_path = resolved.find(dataset, "projections", projection_id, META_FILE)
    payload = _read_json(meta_path)
    _check_schema_version(payload, meta_path)

    _, node_rows = _read_csv(meta_path.parent / NODES_FILE)
    _, edge_rows = _read_csv(meta_path.parent / EDGES_FILE)
    graph = _graph_from_rows(node_rows, edge_rows)
    return ProjectionBundle(
        graph=graph,
        spec=ProjectionSpec.from_dict(payload["spec"]),
        source=BipartiteSpec.from_dict(payload["source"]),
        meta=_meta_from_payload(payload),
    )


# ---------------------------------------------------------------------
# Partition
# ---------------------------------------------------------------------


def save_partition(
    partition: Partition, root: str | Path, dataset: str, *, validate: bool = True
) -> Path:
    """Grava ``<root>/<dataset>/communities/<algoritmo>__<projection_id>/``."""
    if validate:
        from edugraph.contracts import validate as _validate

        _validate.validate_partition(partition)

    out = ensure_dir(community_dir(root, dataset, partition.artifact_id))
    rows = [[node, comm] for node, comm in sorted(partition.membership.items())]
    _write_csv(out / MEMBERSHIP_FILE, ["node_id", "community"], rows)
    _write_json(
        out / META_FILE,
        _meta_payload(
            partition.meta,
            "partition",
            algorithm=partition.algorithm,
            projection_id=partition.projection_id,
            modularity=partition.modularity,
            n_communities=partition.n_communities,
            runtime_s=partition.runtime_s,
            status=partition.status,
            params=partition.params,
        ),
    )
    return out


def load_partition(
    roots: ArtifactRoots | list[str | Path] | str | Path | None,
    dataset: str,
    artifact_id: str,
) -> Partition:
    """Lê uma partição por ``<algoritmo>__<projection_id>``."""
    resolved = as_roots(roots)
    meta_path = resolved.find(dataset, "communities", artifact_id, META_FILE)
    payload = _read_json(meta_path)
    _check_schema_version(payload, meta_path)

    _, rows = _read_csv(meta_path.parent / MEMBERSHIP_FILE)
    membership = {row["node_id"]: int(row["community"]) for row in rows}
    return Partition(
        algorithm=payload["algorithm"],
        projection_id=str(payload["projection_id"]),
        membership=membership,
        modularity=float(payload["modularity"]),
        n_communities=int(payload["n_communities"]),
        runtime_s=float(payload.get("runtime_s", 0.0)),
        params=dict(payload.get("params", {})),
        status=payload.get("status", "ok"),
        meta=_meta_from_payload(payload),
    )


def save_profile(
    rows: list[dict[str, Any]], root: str | Path, dataset: str, artifact_id: str
) -> Path:
    """Grava o ``profile.csv`` da partição (caracterização, spec B-05)."""
    if not rows:
        raise ContractError("profile.csv vazio: a caracterização precisa de pelo menos uma linha")
    header = list(rows[0].keys())
    out = community_dir(root, dataset, artifact_id) / PROFILE_FILE
    _write_csv(out, header, [[row.get(col) for col in header] for row in rows])
    return out


def load_profile(
    roots: ArtifactRoots | list[str | Path] | str | Path | None,
    dataset: str,
    artifact_id: str,
) -> list[dict[str, str]]:
    resolved = as_roots(roots)
    path = resolved.find(dataset, "communities", artifact_id, PROFILE_FILE)
    _, rows = _read_csv(path)
    return rows


# ---------------------------------------------------------------------
# CentralityResult
# ---------------------------------------------------------------------


def save_centrality(
    result: CentralityResult, root: str | Path, dataset: str, *, validate: bool = True
) -> Path:
    """Grava ``<root>/<dataset>/centrality/<projection_id>/<metric>.csv``."""
    if validate:
        from edugraph.contracts import validate as _validate

        _validate.validate_centrality(result)

    out = ensure_dir(centrality_dir(root, dataset, result.projection_id))
    rows = [[node, score] for node, score in sorted(result.scores.items())]
    _write_csv(out / f"{result.metric}.csv", ["node_id", "score"], rows)
    _write_json(
        out / f"{result.metric}.meta.json",
        _meta_payload(
            result.meta,
            "centrality",
            projection_id=result.projection_id,
            metric=result.metric,
            params=result.params,
            runtime_s=result.runtime_s,
            converged=result.converged,
        ),
    )
    return out


def load_centrality(
    roots: ArtifactRoots | list[str | Path] | str | Path | None,
    dataset: str,
    projection_id: str,
    metric: CentralityMetricName,
) -> CentralityResult:
    """Lê uma métrica de centralidade de uma projeção."""
    resolved = as_roots(roots)
    meta_path = resolved.find(dataset, CENTRALITY_DIR, projection_id, f"{metric}.meta.json")
    payload = _read_json(meta_path)
    _check_schema_version(payload, meta_path)

    _, rows = _read_csv(meta_path.parent / f"{metric}.csv")
    scores = {row["node_id"]: float(row["score"]) for row in rows}
    return CentralityResult(
        projection_id=str(payload["projection_id"]),
        metric=payload["metric"],
        scores=scores,
        params=dict(payload.get("params", {})),
        runtime_s=float(payload.get("runtime_s", 0.0)),
        converged=bool(payload.get("converged", True)),
        meta=_meta_from_payload(payload),
    )


# ---------------------------------------------------------------------
# Outcomes — rótulos históricos, fora do grafo (ADR-0008)
# ---------------------------------------------------------------------


def save_outcomes(outcomes: Outcomes, root: str | Path, dataset: str) -> Path:
    """Grava ``<root>/<dataset>/bipartite/outcomes.csv``."""
    out = ensure_dir(bipartite_dir(root, dataset))
    has_planted = outcomes.planted_group is not None
    header = ["student_id", "final_result"] + (["planted_group"] if has_planted else [])
    rows: list[list[Any]] = []
    for student in sorted(outcomes.final_result):
        row: list[Any] = [student, outcomes.final_result[student]]
        if has_planted:
            assert outcomes.planted_group is not None
            row.append(outcomes.planted_group.get(student))
        rows.append(row)
    _write_csv(out / OUTCOMES_FILE, header, rows)
    return out / OUTCOMES_FILE


def load_outcomes(
    roots: ArtifactRoots | list[str | Path] | str | Path | None, dataset: str
) -> Outcomes:
    """Lê os rótulos históricos.

    **Só pode ser chamado de módulos ``evaluate.py``** — a restrição da
    seção 2 do briefing é verificada por um teste de contrato que
    procura chamadas a esta função fora deles.
    """
    resolved = as_roots(roots)
    path = resolved.find(dataset, "bipartite", OUTCOMES_FILE)
    header, rows = _read_csv(path)
    final_result = {row["student_id"]: row["final_result"] for row in rows}
    planted: dict[str, int] | None = None
    if "planted_group" in header:
        planted = {
            row["student_id"]: int(row["planted_group"])
            for row in rows
            if row.get("planted_group", "") != ""
        }
    return Outcomes(final_result=final_result, planted_group=planted)


# ---------------------------------------------------------------------
# metrics/*.csv — o que vira tabela do capítulo 3
# ---------------------------------------------------------------------


def append_metrics_rows(
    root: str | Path,
    dataset: str,
    name: str,
    rows: list[dict[str, Any]],
    *,
    key: list[str],
) -> Path:
    """Insere ou substitui linhas em ``metrics/<name>.csv``.

    Idempotente por ``key``: rodar de novo a mesma configuração atualiza
    a linha em vez de duplicá-la, e a saída fica ordenada pela chave.
    Isso permite acumular as métricas de várias execuções na mesma
    tabela sem que a ordem dependa de quem rodou primeiro.
    """
    if not rows:
        raise ContractError(f"metrics/{name}.csv: nada a escrever")

    path = metrics_dir(root, dataset) / f"{name}.csv"
    existing: list[dict[str, str]] = []
    header: list[str] = list(rows[0].keys())
    if path.exists():
        header_found, existing = _read_csv(path)
        if header_found and set(header_found) != set(header):
            raise ContractError(
                f"{path}: colunas {header_found} diferem das novas {header}. "
                "Mudança de esquema de métrica exige subir SCHEMA_VERSION."
            )
        header = header_found or header

    def key_of(row: dict[str, Any]) -> tuple[str, ...]:
        return tuple(str(row.get(col, "")) for col in key)

    merged: dict[tuple[str, ...], dict[str, Any]] = {key_of(r): dict(r) for r in existing}
    for row in rows:
        merged[key_of(row)] = dict(row)

    ordered = [merged[k] for k in sorted(merged)]
    _write_csv(path, header, [[row.get(col) for col in header] for row in ordered])
    return path


def load_metrics(
    roots: ArtifactRoots | list[str | Path] | str | Path | None, dataset: str, name: str
) -> list[dict[str, str]]:
    """Lê ``metrics/<name>.csv`` como lista de dicionários."""
    resolved = as_roots(roots)
    path = resolved.find(dataset, "metrics", f"{name}.csv")
    _, rows = _read_csv(path)
    return rows
