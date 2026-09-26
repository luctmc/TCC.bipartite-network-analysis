"""API  ``[C]`` — spec C-04.

``/health`` e ``/datasets`` estão prontas no dia 0 e são testadas de
verdade; as rotas de dados são a C-04, testadas sobre a fixture.

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


def test_raiz_sem_build_explica_como_gerar(artifact_roots, tmp_path, monkeypatch) -> None:
    """Sem ``npm run build``, ``/`` diz o que fazer em vez de dar 404.

    A pasta do build é trocada por uma vazia: quem já rodou o build na
    própria máquina não pode ver este teste quebrar por isso.
    """
    import edugraph.api.app as app_module

    monkeypatch.setattr(app_module, "STATIC_DIR", tmp_path / "static")
    client = TestClient(create_app(artifact_roots))
    response = client.get("/")
    assert response.status_code == 200
    assert "npm" in response.json()["detail"]


# ---------------------------------------------------------------------
# Spec C-04 — rotas de dados
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
def test_projecao_responde_200_e_valida_no_schema(client: TestClient) -> None:
    response = client.get("/datasets/synthetic_v1/projections/student_simple")
    assert response.status_code == 200

    body = response.json()
    assert body["projection_id"] == "student_simple"
    assert len(body["nodes"]) == 98
    assert body["edges"]


@pytest.mark.dataset("synthetic_v1")
def test_particao_responde_200(client: TestClient) -> None:
    response = client.get("/datasets/synthetic_v1/communities/louvain__student_simple")
    assert response.status_code == 200

    body = response.json()
    assert body["algorithm"] == "louvain"
    assert body["status"] == "ok"
    assert 0.0 <= body["modularity"] <= 1.0


@pytest.mark.dataset("synthetic_v1")
def test_centralidade_responde_200(client: TestClient) -> None:
    response = client.get("/datasets/synthetic_v1/centrality/discipline_simple/betweenness")
    assert response.status_code == 200
    assert response.json()["metric"] == "betweenness"


def test_dataset_inexistente_da_404(client: TestClient) -> None:
    """E a mensagem diz onde procurou — o engano mais comum é o ``--root``."""
    response = client.get("/datasets/nao_existe/projections/student_simple")
    assert response.status_code == 404
    assert "nao_existe" in response.json()["detail"]


@pytest.mark.dataset("synthetic_v1")
def test_projecao_acima_do_limite_corta_e_declara_o_corte(client: TestClient) -> None:
    """``top_weight``: fica o subconjunto de maior peso **e** o corpo diz que cortou."""
    inteira = client.get("/datasets/synthetic_v1/projections/student_simple").json()
    total = inteira["truncation"]["n_edges_total"]
    assert inteira["truncation"]["truncated"] is False
    assert len(inteira["edges"]) == total

    cortada = client.get(
        "/datasets/synthetic_v1/projections/student_simple",
        params={"max_edges": 10, "cut": "top_weight"},
    ).json()
    corte = cortada["truncation"]
    assert corte["truncated"] is True
    assert corte["criterion"] == "top_weight"
    assert corte["n_edges_total"] == total
    assert corte["n_edges_returned"] == len(cortada["edges"]) == 10
    assert len(cortada["nodes"]) == len(inteira["nodes"])  # nós nunca são cortados

    menor_mantido = min(e["weight"] for e in cortada["edges"])
    descartados = [e for e in inteira["edges"] if e not in cortada["edges"]]
    assert all(e["weight"] <= menor_mantido for e in descartados)


@pytest.mark.dataset("synthetic_v1")
def test_corte_padrao_e_o_esqueleto_e_nao_deixa_no_solto(client: TestClient) -> None:
    """``backbone``: as k arestas mais fortes de cada nó, com o maior k que cabe.

    Todo aluno que tinha vizinho continua com pelo menos um — o corte por
    peso global deixaria a maioria solta.
    """
    url = "/datasets/synthetic_v1/projections/student_simple"
    inteira = client.get(url).json()
    cortada = client.get(url, params={"max_edges": 150}).json()
    corte = cortada["truncation"]

    assert corte["truncated"] is True
    assert corte["criterion"] == "backbone"
    assert corte["k_per_node"] >= 1
    assert corte["n_edges_returned"] == len(cortada["edges"]) <= 150

    com_vizinho = {n for e in inteira["edges"] for n in (e["source"], e["target"])}
    tocados = {n for e in cortada["edges"] for n in (e["source"], e["target"])}
    assert tocados == com_vizinho


def test_esqueleto_fica_com_a_aresta_mais_forte_de_cada_no() -> None:
    """Estrela ponderada + uma aresta fraca entre folhas: com k = 1, a folha
    fica com a aresta forte para o centro, não com a fraca."""
    from edugraph.api.routes import _backbone

    arestas = [
        ("A", "B", 5.0),
        ("A", "C", 4.0),
        ("A", "D", 3.0),
        ("B", "C", 1.0),
    ]
    mantidas, k = _backbone(arestas, max_edges=3)
    assert k == 1
    assert sorted(mantidas) == [("A", "B", 5.0), ("A", "C", 4.0), ("A", "D", 3.0)]


@pytest.mark.dataset("synthetic_v1")
def test_corte_e_deterministico(client: TestClient) -> None:
    url = "/datasets/synthetic_v1/projections/student_simple"
    primeiro = client.get(url, params={"max_edges": 25}).json()["edges"]
    segundo = client.get(url, params={"max_edges": 25}).json()["edges"]
    assert primeiro == segundo


@pytest.mark.dataset("synthetic_v1")
def test_particao_e_metricas_vem_embutidas(client: TestClient) -> None:
    response = client.get(
        "/datasets/synthetic_v1/projections/student_simple",
        params={"partition": "louvain__student_simple", "metrics": "degree,betweenness"},
    )
    assert response.status_code == 200
    body = response.json()
    ids = {node["id"] for node in body["nodes"]}

    assert set(body["community"]) == ids
    assert sorted(body["centrality"]) == ["betweenness", "degree"]
    assert set(body["centrality"]["degree"]) == ids


@pytest.mark.dataset("synthetic_v1")
def test_metrica_inexistente_da_422(client: TestClient) -> None:
    response = client.get(
        "/datasets/synthetic_v1/projections/student_simple", params={"metrics": "pagerank"}
    )
    assert response.status_code == 422
    assert "pagerank" in response.json()["detail"]


@pytest.mark.dataset("synthetic_v1")
def test_particao_inexistente_da_404_citando_as_raizes(client: TestClient) -> None:
    response = client.get("/datasets/synthetic_v1/communities/louvain__nao_existe")
    assert response.status_code == 404
    assert "louvain__nao_existe" in response.json()["detail"]


@pytest.mark.dataset("synthetic_v1")
def test_bipartido_responde_com_os_dois_lados(client: TestClient) -> None:
    body = client.get("/datasets/synthetic_v1/bipartite").json()
    assert body["projection_id"] == "bipartite"
    assert {node["kind"] for node in body["nodes"]} == {"student", "discipline"}


@pytest.mark.dataset("synthetic_v1")
def test_ranking_vem_ordenado_e_respeita_top(client: TestClient) -> None:
    url = "/datasets/synthetic_v1/centrality/student_simple/degree"
    ranking = client.get(url).json()["ranking"]
    assert ranking == sorted(ranking, key=lambda par: (-par[1], par[0]))
    assert client.get(url, params={"top": 3}).json()["ranking"] == ranking[:3]


@pytest.mark.dataset("synthetic_v1")
def test_metrics_devolve_a_tabela_com_numeros(artifact_roots, tmp_path) -> None:
    """``metrics/<nome>.csv`` vira JSON, com número onde a célula é número."""
    from edugraph.contracts import io

    io.append_metrics_rows(
        tmp_path,
        "synthetic_v1",
        "exemplo",
        [{"algorithm": "louvain", "modularity": 0.4666, "n_communities": 3}],
        key=["algorithm"],
    )
    client = TestClient(create_app([tmp_path, *artifact_roots]))
    body = client.get("/datasets/synthetic_v1/metrics/exemplo").json()

    assert body["rows"] == [{"algorithm": "louvain", "modularity": 0.4666, "n_communities": 3}]


def test_openapi_descreve_as_rotas_de_dados(client: TestClient) -> None:
    """``edugraph api openapi`` é o que tipa o front: as cinco rotas estão lá."""
    paths = client.app.openapi()["paths"]  # type: ignore[attr-defined]
    for rota in (
        "/datasets/{dataset}/projections/{projection_id}",
        "/datasets/{dataset}/bipartite",
        "/datasets/{dataset}/communities/{artifact_id}",
        "/datasets/{dataset}/centrality/{projection_id}/{metric}",
        "/datasets/{dataset}/metrics/{name}",
    ):
        assert rota in paths
        assert "post" not in paths[rota]  # somente leitura (ADR-0004)


def test_esqueleto_declara_k_zero_quando_nem_uma_por_no_cabe() -> None:
    """Três arestas disjuntas e limite 2: não há como dar um vizinho a cada nó."""
    from edugraph.api.routes import _backbone

    arestas = [("A", "B", 3.0), ("C", "D", 2.0), ("E", "F", 1.0)]
    mantidas, k = _backbone(arestas, max_edges=2)
    assert k == 0
    assert mantidas == [("A", "B", 3.0), ("C", "D", 2.0)]


@pytest.mark.dataset("synthetic_v1")
def test_particao_de_outra_projecao_da_422(client: TestClient) -> None:
    response = client.get(
        "/datasets/synthetic_v1/projections/discipline_simple",
        params={"partition": "louvain__student_simple"},
    )
    assert response.status_code == 422
    assert "student_simple" in response.json()["detail"]
