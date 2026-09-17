"""
FRENTE C — API
================

Amarra as três frentes numa API simples. Roda com:
    uvicorn src.api.main:app --reload

Endpoints:
    GET /communities/{louvain|girvan_newman}
    GET /centrality/{alunos|disciplinas}/{grau|intermediacao|autovetor}
    GET /node/{node_id}
"""
import sys
from pathlib import Path

# permite rodar `uvicorn src.api.main:app` a partir da raiz do projeto
sys.path.append(str(Path(__file__).resolve().parents[2]))

import networkx as nx
from fastapi import FastAPI, HTTPException

from src.centrality.metrics import compute_centralities
from src.community.detect import run_girvan_newman, run_louvain

app = FastAPI(title="Análise Topológica de Redes Educacionais")

PROJ_ALUNOS_PATH = "data/synthetic/proj_alunos_simples.gml"
PROJ_DISCIPLINAS_PATH = "data/synthetic/proj_disciplinas.gml"

_G_alunos = nx.read_gml(PROJ_ALUNOS_PATH)
_G_disciplinas = nx.read_gml(PROJ_DISCIPLINAS_PATH)

_GRAPHS = {"alunos": _G_alunos, "disciplinas": _G_disciplinas}


@app.get("/communities/{algoritmo}")
def get_communities(algoritmo: str):
    if algoritmo == "louvain":
        partition, Q, dt = run_louvain(_G_alunos)
    elif algoritmo == "girvan_newman":
        n_comm = len(set(run_louvain(_G_alunos)[0].values()))
        partition, Q, dt = run_girvan_newman(_G_alunos, n_communities=n_comm)
    else:
        raise HTTPException(404, "algoritmo deve ser 'louvain' ou 'girvan_newman'")

    groups: dict[int, list[str]] = {}
    for node, comm in partition.items():
        groups.setdefault(comm, []).append(node)

    return {
        "algoritmo": algoritmo,
        "modularidade": round(Q, 4),
        "tempo_ms": round(dt * 1000, 2),
        "n_comunidades": len(groups),
        "comunidades": groups,
    }


@app.get("/centrality/{grafo}/{metrica}")
def get_centrality(grafo: str, metrica: str):
    if grafo not in _GRAPHS:
        raise HTTPException(404, "grafo deve ser 'alunos' ou 'disciplinas'")
    scores = compute_centralities(_GRAPHS[grafo])
    if metrica not in scores:
        raise HTTPException(404, "metrica deve ser 'grau', 'intermediacao' ou 'autovetor'")

    ranked = sorted(scores[metrica].items(), key=lambda kv: kv[1], reverse=True)
    return {"grafo": grafo, "metrica": metrica, "ranking": ranked}


@app.get("/node/{node_id}")
def get_node(node_id: str):
    graph = _G_alunos if node_id in _G_alunos else _G_disciplinas
    if node_id not in graph:
        raise HTTPException(404, "nó não encontrado")

    vizinhos = list(graph.neighbors(node_id))
    return {"id": node_id, "grau": graph.degree(node_id), "vizinhos": vizinhos}
