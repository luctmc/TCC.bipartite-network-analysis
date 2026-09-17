"""Schemas pydantic das respostas da API  ``[C]`` — spec C-04.

O corpo de toda rota valida contra um destes modelos, e é contra eles
que o front-end em ``frontend/`` é tipado. Mudar um schema é mudar o
contrato com o front: sai em PR com os dois lados juntos.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Resposta de ``GET /health``."""

    status: Literal["ok"] = "ok"
    version: str = Field(description="Versão do pacote edugraph")
    schema_version: str = Field(description="Versão do esquema de artefatos em disco")
    roots: list[str] = Field(description="Raízes de artefatos consultadas, em ordem")


class DatasetSummary(BaseModel):
    """Um dataset visível sob alguma das raízes."""

    dataset: str
    has_bipartite: bool
    projections: list[str]
    partitions: list[str]
    centralities: list[str]


class DatasetListResponse(BaseModel):
    """Resposta de ``GET /datasets``."""

    datasets: list[DatasetSummary]


class NodeOut(BaseModel):
    """Um nó, como o front o consome."""

    id: str
    kind: Literal["student", "discipline"]
    label: str


class EdgeOut(BaseModel):
    """Uma aresta ponderada."""

    source: str
    target: str
    weight: float


class GraphResponse(BaseModel):
    """Resposta de ``GET /datasets/{dataset}/projections/{projection_id}``.

    ``community`` e ``centrality`` vêm opcionalmente embutidos para que
    o front possa colorir e dimensionar sem uma segunda requisição —
    são leituras do disco, não cálculo (ADR-0004).
    """

    dataset: str
    projection_id: str
    spec: dict[str, Any]
    nodes: list[NodeOut]
    edges: list[EdgeOut]
    community: dict[str, int] | None = None
    centrality: dict[str, dict[str, float]] | None = None


class PartitionResponse(BaseModel):
    """Resposta de ``GET /datasets/{dataset}/communities/{artifact_id}``."""

    dataset: str
    algorithm: str
    projection_id: str
    modularity: float
    n_communities: int
    runtime_s: float
    status: Literal["ok", "timeout", "skipped"]
    params: dict[str, Any]
    membership: dict[str, int]


class CentralityResponse(BaseModel):
    """Resposta de ``GET /datasets/{dataset}/centrality/{projection_id}/{metric}``."""

    dataset: str
    projection_id: str
    metric: Literal["degree", "betweenness", "eigenvector"]
    converged: bool
    runtime_s: float
    params: dict[str, Any]
    ranking: list[tuple[str, float]]


class MetricsResponse(BaseModel):
    """Resposta de ``GET /datasets/{dataset}/metrics/{name}`` — tabela crua."""

    dataset: str
    name: str
    rows: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    """Corpo de erro. ``detail`` diz o que faltou e onde foi procurado."""

    detail: str
