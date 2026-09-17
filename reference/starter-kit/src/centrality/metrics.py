"""
FRENTE C — Centralidade, Visualização e Aplicação
====================================================

Responsabilidade: calcular as três centralidades sobre as duas
projeções (aluno-aluno e disciplina-disciplina), e expor tudo via API
para o front-end consumir.

Depende de: data/synthetic/proj_alunos_simples.gml e
proj_disciplinas.gml (gerados por src/etl/build_graph.py).
"""
import networkx as nx

PROJ_ALUNOS_PATH = "data/synthetic/proj_alunos_simples.gml"
PROJ_DISCIPLINAS_PATH = "data/synthetic/proj_disciplinas.gml"


# ---------------------------------------------------------------------
# 1. As três centralidades
# ---------------------------------------------------------------------
def compute_centralities(G: nx.Graph) -> dict:
    """Retorna um dict {métrica: {nó: valor}} com as três medidas.

    - grau: networkx já normaliza por (n-1)
    - intermediação: usa Brandes internamente (algoritmo padrão do nx)
    - autovetor: iteração de potência; pode não convergir em grafos
      desconexos -- por isso max_iter alto e um fallback tratado
    """
    degree = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)

    try:
        eigenvector = nx.eigenvector_centrality(G, weight="weight", max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        # grafo desconexo ou mal-condicionado: cai para a aproximação
        # por numpy, que resolve via autovalores diretamente
        eigenvector = nx.eigenvector_centrality_numpy(G, weight="weight")

    return {"grau": degree, "intermediacao": betweenness, "autovetor": eigenvector}


# ---------------------------------------------------------------------
# 2. Comparação entre métricas -- onde elas discordam
# ---------------------------------------------------------------------
def top_n(scores: dict, n: int = 5):
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:n]


def find_disagreement(centralities: dict, n: int = 5):
    """Nós que aparecem no top-N de uma métrica mas não de outra --
    é justamente essa discordância que vira discussão em Resultados
    (ver base-fundamentacao.md, seção 2.4.4)."""
    top_deg = {n_ for n_, _ in top_n(centralities["grau"], n)}
    top_btw = {n_ for n_, _ in top_n(centralities["intermediacao"], n)}
    top_eig = {n_ for n_, _ in top_n(centralities["autovetor"], n)}

    return {
        "so_intermediacao": top_btw - top_deg - top_eig,
        "so_autovetor": top_eig - top_deg - top_btw,
        "so_grau": top_deg - top_btw - top_eig,
        "nos_3_metricas": top_deg & top_btw & top_eig,
    }


# ---------------------------------------------------------------------
# 3. Execução direta para checagem rápida
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Projeção aluno-aluno ===")
    G_alunos = nx.read_gml(PROJ_ALUNOS_PATH)
    c_alunos = compute_centralities(G_alunos)
    for metrica, scores in c_alunos.items():
        print(f"\nTop 5 por {metrica}:")
        for node, val in top_n(scores):
            print(f"  {node}: {val:.4f}")

    disagreement = find_disagreement(c_alunos)
    print("\n[Discordância entre métricas]")
    for k, v in disagreement.items():
        print(f"  {k}: {v}")

    print("\n=== Projeção disciplina-disciplina (busca de gargalos curriculares) ===")
    G_disc = nx.read_gml(PROJ_DISCIPLINAS_PATH)
    c_disc = compute_centralities(G_disc)
    print("\nDisciplinas por intermediação (candidatas a 'gargalo' do fluxo curricular):")
    for node, val in top_n(c_disc["intermediacao"], n=len(G_disc)):
        print(f"  {node}: {val:.4f}")
