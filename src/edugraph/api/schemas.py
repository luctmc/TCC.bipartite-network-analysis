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


class TruncationInfo(BaseModel):
    """O corte de arestas, declarado no corpo para que a interface avise.

    Um grafo de um milhão de arestas não renderiza e não deve sequer ser
    transferido. Quando corta, mantém **todos os nós** — são eles que
    carregam comunidade e centralidade — e escolhe as arestas por um de
    dois critérios, sempre com desempate determinístico:

    - ``backbone`` (padrão): as ``k_per_node`` arestas mais fortes de cada
      nó, com o maior ``k`` que cabe no limite. Todo nó que tinha vizinho
      continua com pelo menos um.
    - ``top_weight``: as ``max_edges`` arestas de maior peso do grafo
      inteiro. Mais fiel ao peso, mas concentra tudo em poucos nós.
    """

    truncated: bool
    max_edges: int = Field(description="Limite aplicado nesta resposta")
    n_nodes: int = Field(description="Nós no grafo e na resposta — nós nunca são cortados")
    n_edges_total: int = Field(description="Arestas no artefato em disco")
    n_edges_returned: int = Field(description="Arestas nesta resposta")
    criterion: Literal["backbone", "top_weight"] = "backbone"
    k_per_node: int | None = Field(
        default=None,
        description=(
            "No corte backbone, quantas arestas por nó couberam; 0 = nem uma por nó "
            "coube, e ficaram as mais pesadas entre as melhores de cada nó"
        ),
    )


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
    truncation: TruncationInfo
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
