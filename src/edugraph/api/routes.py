"""Rotas da API  ``[C]``.

No dia 0 estão prontas ``/health`` e ``/datasets`` — o bastante para a
API subir sobre a fixture e para o front-end ter contra o que se
desenvolver. As demais rotas são a **spec C-04**.

Toda rota lê de :class:`~edugraph.contracts.paths.ArtifactRoots` e
devolve 404 com a lista de raízes consultadas quando não encontra — o
engano mais comum em desenvolvimento é esquecer o ``--root``.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from edugraph import __version__
from edugraph.api.schemas import (
    CentralityResponse,
    DatasetListResponse,
    DatasetSummary,
    GraphResponse,
    HealthResponse,
    MetricsResponse,
    PartitionResponse,
)
from edugraph.contracts.errors import ArtifactNotFoundError
from edugraph.contracts.paths import ArtifactRoots
from edugraph.contracts.types import SCHEMA_VERSION

router = APIRouter()


def _roots(request: Request) -> ArtifactRoots:
    """Raízes configuradas na criação da aplicação."""
    roots: ArtifactRoots = request.app.state.roots
    return roots


# ---------------------------------------------------------------------
# Dia 0 — prontas
# ---------------------------------------------------------------------


@router.get("/health", response_model=HealthResponse, tags=["meta"])
def health(request: Request) -> HealthResponse:
    """Diz que a API está de pé e sobre que raízes ela está olhando."""
    roots = _roots(request)
    return HealthResponse(
        version=__version__,
        schema_version=SCHEMA_VERSION,
        roots=[str(r) for r in roots],
    )


@router.get("/datasets", response_model=DatasetListResponse, tags=["meta"])
def list_datasets(request: Request) -> DatasetListResponse:
    """Lista os datasets visíveis e o que cada um já tem calculado.

    É o que permite ao front-end montar os seletores sem conhecer
    antecipadamente nenhum nome de dataset ou de projeção.
    """
    roots = _roots(request)
    summaries = [
        DatasetSummary(
            dataset=dataset,
            has_bipartite=roots.has(dataset, "bipartite", "meta.json"),
            projections=roots.projections(dataset),
            partitions=roots.partitions(dataset),
            centralities=roots.centralities(dataset),
        )
        for dataset in roots.datasets()
    ]
    return DatasetListResponse(datasets=summaries)


# ---------------------------------------------------------------------
# Spec C-04 — rotas de dados
# ---------------------------------------------------------------------


@router.get(
    "/datasets/{dataset}/projections/{projection_id}",
    response_model=GraphResponse,
    tags=["grafo"],
)
def get_projection(dataset: str, projection_id: str, request: Request) -> GraphResponse:
    """Grafo da projeção, opcionalmente com comunidade e centralidade.

    Notes
    -----
    A implementar em C-04: carregar com
    :func:`edugraph.contracts.io.load_projection`; quando os parâmetros
    de consulta ``partition`` e ``metrics`` vierem, embutir também a
    partição e as centralidades pedidas. Grafos grandes precisam de
    corte por peso mínimo ou limite de arestas — o front não renderiza
    um milhão de arestas, e a spec C-04 define o limite e o devolve no
    corpo para que a interface possa avisar.
    """
    raise NotImplementedError("C-04: ver docs/specs/frente-c/C-04-api.md")


@router.get(
    "/datasets/{dataset}/bipartite",
    response_model=GraphResponse,
    tags=["grafo"],
)
def get_bipartite(dataset: str, request: Request) -> GraphResponse:
    """Grafo bipartido do dataset."""
    raise NotImplementedError("C-04: ver docs/specs/frente-c/C-04-api.md")


@router.get(
    "/datasets/{dataset}/communities/{artifact_id}",
    response_model=PartitionResponse,
    tags=["comunidades"],
)
def get_partition(dataset: str, artifact_id: str, request: Request) -> PartitionResponse:
    """Uma partição, com Q, k, tempo e status."""
    raise NotImplementedError("C-04: ver docs/specs/frente-c/C-04-api.md")


@router.get(
    "/datasets/{dataset}/centrality/{projection_id}/{metric}",
    response_model=CentralityResponse,
    tags=["centralidade"],
)
def get_centrality(
    dataset: str, projection_id: str, metric: str, request: Request
) -> CentralityResponse:
    """Ranking de uma métrica de centralidade sobre uma projeção."""
    raise NotImplementedError("C-04: ver docs/specs/frente-c/C-04-api.md")


@router.get(
    "/datasets/{dataset}/metrics/{name}",
    response_model=MetricsResponse,
    tags=["métricas"],
)
def get_metrics(dataset: str, name: str, request: Request) -> MetricsResponse:
    """Tabela de ``metrics/<name>.csv`` como JSON.

    É por aqui que o front mostra a comparação Louvain × Girvan-Newman
    sem recalcular nada.
    """
    raise NotImplementedError("C-04: ver docs/specs/frente-c/C-04-api.md")


# ---------------------------------------------------------------------
# Tradução de erro de contrato em 404
# ---------------------------------------------------------------------


def not_found(error: ArtifactNotFoundError) -> HTTPException:
    """Converte a ausência de artefato em 404 com a mensagem do contrato."""
    return HTTPException(status_code=404, detail=str(error))
