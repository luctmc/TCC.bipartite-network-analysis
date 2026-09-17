"""
FRENTE B — Algoritmos de Comunidade
=====================================

Responsabilidade: rodar Louvain e Girvan-Newman sobre a projeção
aluno-aluno gerada pela Frente A, medir modularidade e tempo de
execução, e caracterizar cada comunidade encontrada.

Depende de: data/synthetic/proj_alunos_simples.gml (gerado por
src/etl/build_graph.py -- rode aquele script primeiro).
"""
import time

import community as community_louvain  # pip install python-louvain
import networkx as nx
from networkx.algorithms.community import girvan_newman, modularity

PROJECTION_PATH = "data/synthetic/proj_alunos_simples.gml"


# ---------------------------------------------------------------------
# 1. Louvain
# ---------------------------------------------------------------------
def run_louvain(G: nx.Graph):
    """Retorna (partição como dict {nó: comunidade}, Q, tempo em segundos)."""
    t0 = time.perf_counter()
    partition = community_louvain.best_partition(G, weight="weight", random_state=42)
    dt = time.perf_counter() - t0

    Q = community_louvain.modularity(partition, G, weight="weight")
    return partition, Q, dt


# ---------------------------------------------------------------------
# 2. Girvan-Newman
# ---------------------------------------------------------------------
def run_girvan_newman(G: nx.Graph, n_communities: int):
    """Roda Girvan-Newman até atingir n_communities.

    ATENÇÃO: é caro (recalcula intermediação a cada corte de aresta).
    Em grafos grandes (milhares de nós) isso não termina em tempo
    razoável -- rode num subgrafo de amostra pra comparação, ou apenas
    cite a complexidade teórica na Fundamentação se o dataset real for
    grande demais. Reportar essa limitação em Resultados é legítimo.
    """
    t0 = time.perf_counter()
    comp = girvan_newman(G)
    communities = None
    for communities in comp:
        if len(communities) >= n_communities:
            break
    dt = time.perf_counter() - t0

    partition = {}
    for i, group in enumerate(communities):
        for node in group:
            partition[node] = i

    Q = modularity(G, communities, weight="weight")
    return partition, Q, dt


# ---------------------------------------------------------------------
# 3. Caracterização de comunidades
# ---------------------------------------------------------------------
def characterize(partition: dict, B_original: nx.Graph = None):
    """Agrupa os nós por comunidade -- útil para depois cruzar com
    o grafo bipartido original e ver quais disciplinas predominam
    em cada comunidade (essa parte entra em Resultados)."""
    groups = {}
    for node, comm in partition.items():
        groups.setdefault(comm, []).append(node)
    return groups


# ---------------------------------------------------------------------
# 4. Execução direta para checagem rápida
# ---------------------------------------------------------------------
if __name__ == "__main__":
    G = nx.read_gml(PROJECTION_PATH)
    print(f"[Entrada] {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")

    part_l, Q_l, t_l = run_louvain(G)
    n_comm_l = len(set(part_l.values()))
    print(f"\n[Louvain]       {n_comm_l} comunidades | Q = {Q_l:.4f} | {t_l*1000:.1f} ms")

    part_g, Q_g, t_g = run_girvan_newman(G, n_communities=n_comm_l)
    n_comm_g = len(set(part_g.values()))
    print(f"[Girvan-Newman] {n_comm_g} comunidades | Q = {Q_g:.4f} | {t_g*1000:.1f} ms")

    print(f"\n[Comparação] Girvan-Newman foi {t_g/t_l:.0f}x mais lento que Louvain "
          f"neste grafo de {G.number_of_nodes()} nós.")

    print("\n[Comunidades - Louvain]")
    for comm_id, members in sorted(characterize(part_l).items()):
        print(f"  Comunidade {comm_id}: {len(members)} alunos "
              f"(ex: {members[:3]})")
