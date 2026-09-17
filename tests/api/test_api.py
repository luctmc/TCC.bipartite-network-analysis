"""API  ``[C]`` — spec C-04.

``/health`` e ``/datasets`` estão prontas no dia 0 e são testadas de
verdade; as rotas de dados são ``xfail`` até a C-04 fechar.

A aplicação é criada apontada para a fixture. Ela **não sabe** se a
partição veio da Frente B ou da biblioteca — é exatamente essa ignorância
que deixa a Frente C trabalhar sozinha desde o primeiro dia.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from edugraph.api.app import create_app
from edugraph.contracts.types import SCHEMA_VERSION


@pytest.fixture
def client(artifact_roots) -> TestClient:
    return TestClient(create_app(artifact_roots))


# ---------------------------------------------------------------------
# Dia 0 — valem agora
# ---------------------------------------------------------------------


def test_health_responde_200(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["schema_version"] == SCHEMA_VERSION
    assert body["roots"], "a API precisa dizer sobre que raízes está olhando"


def test_datasets_lista_o_que_existe_em_disco(client: TestClient, datasets) -> None:
    response = client.get("/datasets")
    assert response.status_code == 200

    listados = {d["dataset"] for d in response.json()["datasets"]}
    assert listados == set(datasets)


@pytest.mark.dataset("synthetic_v1")
def test_datasets_reporta_o_que_ja_foi_calculado(client: TestClient) -> None:
    """É por aqui que o front monta os seletores sem nomes fixos no código."""
    body = client.get("/datasets").json()
    synthetic = next(d for d in body["datasets"] if d["dataset"] == "synthetic_v1")

    assert synthetic["has_bipartite"] is True
    assert "student_simple" in synthetic["projections"]
    assert "discipline_simple" in synthetic["projections"]
    assert "louvain__student_simple" in synthetic["partitions"]
    assert "student_simple" in synthetic["centralities"]


def test_openapi_e_gerado(client: TestClient) -> None:
    """O front é tipado a partir deste esquema (``edugraph api openapi``)."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/health" in response.json()["paths"]


def test_raiz_sem_build_explica_como_gerar(client: TestClient) -> None:
    """Sem ``npm run build``, ``/`` diz o que fazer em vez de dar 404."""
    response = client.get("/")
    assert response.status_code == 200
    assert "npm" in response.json()["detail"]


# ---------------------------------------------------------------------
# Spec C-04 — rotas de dados
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="C-04 não implementada", strict=True)
def test_projecao_responde_200_e_valida_no_schema(client: TestClient) -> None:
    response = client.get("/datasets/synthetic_v1/projections/student_simple")
    assert response.status_code == 200

    body = response.json()
    assert body["projection_id"] == "student_simple"
    assert len(body["nodes"]) == 98
    assert body["edges"]


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="C-04 não implementada", strict=True)
def test_particao_responde_200(client: TestClient) -> None:
    response = client.get("/datasets/synthetic_v1/communities/louvain__student_simple")
    assert response.status_code == 200

    body = response.json()
    assert body["algorithm"] == "louvain"
    assert body["status"] == "ok"
    assert 0.0 <= body["modularity"] <= 1.0


@pytest.mark.dataset("synthetic_v1")
@pytest.mark.xfail(reason="C-04 não implementada", strict=True)
def test_centralidade_responde_200(client: TestClient) -> None:
    response = client.get("/datasets/synthetic_v1/centrality/discipline_simple/betweenness")
    assert response.status_code == 200
    assert response.json()["metric"] == "betweenness"


@pytest.mark.xfail(reason="C-04 não implementada", strict=True)
def test_dataset_inexistente_da_404(client: TestClient) -> None:
    """E a mensagem diz onde procurou — o engano mais comum é o ``--root``."""
    response = client.get("/datasets/nao_existe/projections/student_simple")
    assert response.status_code == 404
    assert "nao_existe" in response.json()["detail"]
