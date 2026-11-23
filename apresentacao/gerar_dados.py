"""Gera ``apresentacao/js/dados.js``: os dados reais por trás dos diagramas.

    python apresentacao/gerar_dados.py      (da raiz, com a .venv do projeto)

Lê só ``data/fixtures`` (versionado):

- ``tiny_v1``, o exemplo da fundamentação: matrículas, as duas projeções,
  o rastro real de Louvain e Girvan–Newman do laboratório
  (``edugraph.lab.trace``) e as centralidades das implementações
  registradas da Frente C;
- ``synthetic_v1``, a rede da capa e da modularidade, como a própria API a
  serve (esqueleto de arestas, partição Louvain e centralidades);
- o bloco ``contexto``: os textos e números que o próprio sistema produz
  sobre os seis alunos de ``tiny_v1`` e sobre a turma padrão do laboratório
  (``edugraph.lab.service.run_lab``), para os slides da Introdução.

Os nomes e cursos dos seis alunos são escolha de desenho, como as posições.

Só as posições dos nós da rede grande são escolha de desenho
(``spring_layout`` com semente fixa). Rodar de novo dá o mesmo arquivo.
"""

from __future__ import annotations

import dataclasses
import json
import warnings
from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx

from edugraph.centrality.betweenness import BetweennessCentrality
from edugraph.centrality.degree import DegreeCentrality
from edugraph.centrality.eigenvector import EigenvectorCentrality
from edugraph.contracts import io as cio
from edugraph.contracts.types import ProjectionSpec
from edugraph.data.nullmodel import null_replicas
from edugraph.data.projection.manual import SimpleProjection
from edugraph.lab.trace import girvan_newman_trace, louvain_trace

RAIZ = Path(__file__).resolve().parents[1]
FIXTURES = [RAIZ / "data" / "fixtures"]
SAIDA = Path(__file__).resolve().parent / "js" / "dados.js"


def _tiny() -> dict[str, Any]:
    bip = cio.load_bipartite(FIXTURES, "tiny_v1")
    simples = cio.load_projection(FIXTURES, "tiny_v1", "student_simple")
    alocacao = cio.load_projection(FIXTURES, "tiny_v1", "student_resource_allocation")
    lv = dataclasses.asdict(louvain_trace(simples.graph, seed=42))
    gn = dataclasses.asdict(girvan_newman_trace(simples.graph))

    def scores(metrica: Any) -> dict[str, float]:
        resultado = metrica.compute(simples)
        return {k: round(float(v), 4) for k, v in resultado.scores.items()}

    matriculas = []
    for u, v, d in bip.graph.edges(data=True):
        aluno, disciplina = (u, v) if str(u).startswith("S") else (v, u)
        matriculas.append({"aluno": aluno, "disciplina": disciplina, "nota": d["weight"]})

    def arestas(grafo: nx.Graph[str]) -> list[list[Any]]:
        return [[u, v, round(d["weight"], 4)] for u, v, d in sorted(grafo.edges(data=True))]

    nos = lv["nodes"]
    return {
        "fonte": "data/fixtures/tiny_v1 e edugraph.lab.trace sobre student_simple",
        "matriculas": sorted(matriculas, key=lambda m: (m["disciplina"], m["aluno"])),
        "simples": arestas(simples.graph),
        "alocacao": arestas(alocacao.graph),
        "louvain": {
            "movimentos": [
                {"no": nos[m["members"][0]], "para": nos[m["to"]], "q": round(m["q"], 4)}
                for m in lv["moves"]
            ],
            "membership": lv["membership"],
            "q": round(lv["q"], 4),
        },
        "girvan_newman": {
            "removidas": gn["removed"],
            "cortes": [
                {"k": s["k"], "q": round(s["q"], 4), "n_removidas": s["n_removed"]}
                for s in gn["splits"]
            ],
            "melhor": gn["best"],
            "q": round(gn["q"], 4),
        },
        "centralidade": {
            "grau": scores(DegreeCentrality()),
            "intermediacao": scores(BetweennessCentrality()),
            "autovetor": scores(EigenvectorCentrality()),
        },
    }


def _synthetic() -> dict[str, Any]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from fastapi.testclient import TestClient

        from edugraph.api.app import create_app

        cliente = TestClient(create_app(FIXTURES))
    resposta = cliente.get(
        "/datasets/synthetic_v1/projections/student_simple",
        params={
            "partition": "louvain__student_simple",
            "metrics": "degree,betweenness,eigenvector",
            "max_edges": 450,
        },
    ).json()
    inteira = cio.load_projection(FIXTURES, "synthetic_v1", "student_simple").graph
    pos = nx.spring_layout(inteira, weight="weight", seed=16, iterations=300, k=0.32)
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]

    def norm(valor: float, serie: list[float]) -> float:
        return round((valor - min(serie)) / (max(serie) - min(serie)), 4)

    # Maior comunidade = primeira cor, como frontend/src/palette.ts (communityOrder).
    tamanhos = Counter(resposta["community"].values())
    ordem_tam = sorted(tamanhos.items(), key=lambda t: (-t[1], t[0]))
    ordem = {c: i for i, (c, _) in enumerate(ordem_tam)}
    cent = resposta["centrality"]
    nos = [
        [
            n["id"],
            norm(pos[n["id"]][0], xs),
            norm(pos[n["id"]][1], ys),
            ordem[resposta["community"][n["id"]]],
            round(cent["degree"][n["id"]], 4),
            round(cent["betweenness"][n["id"]], 4),
            round(cent["eigenvector"][n["id"]], 4),
        ]
        for n in resposta["nodes"]
    ]
    return {
        "fonte": "GET /datasets/synthetic_v1/projections/student_simple (esqueleto da API)",
        "q": 0.4666,
        "n_arestas_total": resposta["truncation"]["n_edges_total"],
        "k_por_no": resposta["truncation"]["k_per_node"],
        "tamanhos": [n for _, n in ordem_tam],
        "nos": nos,
        "arestas": [[e["source"], e["target"]] for e in resposta["edges"]],
    }


def _nulo() -> dict[str, Any]:
    """Modelo nulo (spec A-08) de ``synthetic_v1``: 5 réplicas, semente 0.

    Mesmos alunos, disciplinas e graus; quem cursou o quê é sorteado. Cada
    réplica é projetada (aluno↔aluno, simples) e passa pelo Louvain com a
    mesma semente da partição de referência (42). A réplica 0 é desenhada
    com o mesmo esqueleto que a API usaria.
    """
    import community as community_louvain
    from edugraph.api.routes import _graph_payload

    bip = cio.load_bipartite(FIXTURES, "synthetic_v1")
    spec = ProjectionSpec(side="student", weighting="simple")
    qs = []
    primeira: nx.Graph[str] | None = None
    for replica in null_replicas(bip, n=5, seed=0):
        grafo = SimpleProjection().project(replica, spec).graph
        particao = community_louvain.best_partition(grafo, weight="weight", random_state=42)
        qs.append(community_louvain.modularity(particao, grafo, weight="weight"))
        primeira = primeira or grafo
    assert primeira is not None
    _, arestas, corte = _graph_payload(primeira, 450, "backbone")
    pos = nx.spring_layout(primeira, weight="weight", seed=16, iterations=300, k=0.32)
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    media = sum(qs) / len(qs)
    desvio = (sum((q - media) ** 2 for q in qs) / len(qs)) ** 0.5
    return {
        "fonte": "null_replicas(synthetic_v1, n=5, seed=0), projeção simples, Louvain semente 42",
        "qs": [round(q, 4) for q in qs],
        "media": round(media, 4),
        "desvio": round(desvio, 4),
        "q_real": 0.4666,
        "z": round((0.4666 - media) / desvio, 1),
        "n_arestas_total": corte.n_edges_total,
        "nos": {
            n: [
                round((p[0] - min(xs)) / (max(xs) - min(xs)), 4),
                round((p[1] - min(ys)) / (max(ys) - min(ys)), 4),
            ]
            for n, p in pos.items()
        },
        "arestas": [[e.source, e.target] for e in arestas],
    }


#: Escolha de desenho (NARRATIVA.md, seção 3): alunos 1 a 6 de tiny_v1 = Ana a
#: Felipe; disciplinas A, B e C = as três abaixo. Não é dado do sistema.
NOMES = {"S1": "Ana", "S2": "Bruno", "S3": "Carla", "S4": "Diego", "S5": "Elisa", "S6": "Felipe"}
CURSOS = {
    "S1": "ADS",
    "S2": "ADS",
    "S3": "Engenharia Elétrica",
    "S4": "Engenharia Elétrica",
    "S5": "Engenharia Elétrica",
    "S6": "ADS",
}
DISCIPLINAS = {
    "DA": ["Sistemas de Computação", "Sist. Comp."],
    "DB": ["Algoritmos e Programação", "Algoritmos"],
    "DC": ["Circuitos Elétricos", "Circuitos"],
}


def _contexto() -> dict[str, Any]:
    """O que o sistema diz dos seis alunos e da turma padrão do laboratório."""
    from edugraph.contracts.paths import ArtifactRoots
    from edugraph.lab.service import run_lab

    raizes = ArtifactRoots(FIXTURES)
    tiny = run_lab(roots=raizes, source="tiny_v1", students=6)
    sinais = tiny["insight"]["signals"]
    papeis = tiny["insight"]["roles"]
    bip = cio.load_bipartite(FIXTURES, "tiny_v1")
    notas: dict[str, list[float]] = {}
    for u, v, d in bip.graph.edges(data=True):
        aluno = u if str(u).startswith("S") else v
        notas.setdefault(aluno, []).append(float(d["weight"]))
    todas = [n for lista in notas.values() for n in lista]
    alunos = {
        a: {
            "nome": NOMES[a],
            "curso": CURSOS[a],
            "n_disciplinas": len(notas[a]),
            "nota_media": round(sum(notas[a]) / len(notas[a]), 1),
            "papel": papeis[a]["role"],
            "z_grupo": papeis[a]["z"],
            "tier": sinais["students"][a]["tier"],
            "risco": round(sinais["students"][a]["risk"], 3),
            "why": sinais["students"][a].get("why", []),
        }
        for a in sorted(NOMES)
    }

    # Valores padrão do laboratório (frontend/src/components/LabView.tsx).
    demo = run_lab(roots=raizes, source="demo", students=45, seed=12, noise=0.2)
    ds = demo["insight"]["signals"]
    rotulo = {n["id"]: n["label"] for n in demo["bipartite"]["students"]}

    def cartao(sid: str) -> dict[str, Any]:
        return {"id": sid, "nome": rotulo[sid], "why": ds["students"][sid].get("why", [])}

    # Regra fixa (PLANO-AJUSTE.md, seção 6): o primeiro da lista de atenção da
    # tela; o primeiro talento com selo de apoio; o primeiro que liga grupos.
    talentos = ds["talents"]
    apoio = next(t for t in talentos if "apoio" in ds["students"][t].get("tags", []))
    ponte = next(t for t in talentos if "polimata" in ds["students"][t].get("tags", []))
    return {
        "fonte": "run_lab(tiny_v1) e run_lab(demo, 45 alunos, semente 12, mistura 0,2)",
        "nomes": NOMES,
        "cursos": CURSOS,
        "disciplinas": DISCIPLINAS,
        "alunos": alunos,
        "turma": {
            "nota_media": round(sum(todas) / len(todas), 1),
            "disciplinas_por_aluno": round(len(todas) / len(notas), 2),
        },
        "rotulos": {"tier": sinais["tier_labels"], "perfil": sinais["profile_labels"]},
        "demo": {
            "contagens": ds["counts"],
            "q": round(demo["result"]["q"], 3),
            "grupos": [c["name"] for c in demo["insight"]["communities"]],
            "risco": cartao(ds["attention"][0]),
            "apoio": cartao(apoio),
            "ponte": cartao(ponte),
        },
    }


def main() -> None:
    dados = {"tiny": _tiny(), "synthetic": _synthetic(), "nulo": _nulo(), "contexto": _contexto()}
    corpo = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
    cabecalho = "/* Gerado por gerar_dados.py a partir do repositório; não edite à mão. */"
    texto = f"{cabecalho}\nwindow.EDUGRAPH_DADOS = {corpo};\n"
    SAIDA.write_text(texto, encoding="utf-8", newline="\n")
    syn = dados["synthetic"]
    print(f"js/dados.js: {len(syn['nos'])} nós e {len(syn['arestas'])} arestas em synthetic_v1")


if __name__ == "__main__":
    main()
