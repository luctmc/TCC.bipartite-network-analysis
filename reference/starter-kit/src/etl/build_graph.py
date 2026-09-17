"""
FRENTE A — Dados e Modelagem
=============================

Responsabilidade: transformar os CSVs brutos em (1) um grafo bipartido
estudante<->disciplina e (2) duas projeções ponderadas (aluno-aluno e
disciplina-disciplina).

Este arquivo é pensado para rodar sozinho: `python build_graph.py` usa
os dados sintéticos por padrão. Pra usar o OULAD de verdade, troque
DATA_PATH e ajuste load_data() para o schema real do studentInfo.csv
do OULAD (as colunas mudam um pouco -- confira o dicionário de dados
do dataset antes de plugar).
"""
import networkx as nx
import pandas as pd

DATA_PATH = "data/synthetic/studentInfo.csv"
SCORE_THRESHOLD = 60.0  # nota mínima para considerar "bom desempenho" -> aresta


# ---------------------------------------------------------------------
# 1. ETL
# ---------------------------------------------------------------------
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Carrega e limpa os dados brutos.

    Retorna um DataFrame com uma linha por (estudante, disciplina) já
    agregada -- se o aluno cursou o mesmo módulo em presentations
    diferentes, ficamos com a média.
    """
    df = pd.read_csv(path)
    df = df.dropna(subset=["id_student", "code_module", "score_media"])

    agg = (
        df.groupby(["id_student", "code_module"])
        .agg(score_media=("score_media", "mean"))
        .reset_index()
    )
    return agg


# ---------------------------------------------------------------------
# 2. Grafo bipartido
# ---------------------------------------------------------------------
def build_bipartite_graph(df: pd.DataFrame, threshold: float = SCORE_THRESHOLD) -> nx.Graph:
    """Constrói o grafo bipartido G = (U ∪ V, E).

    U = estudantes (bipartite=0), V = disciplinas (bipartite=1).
    Uma aresta existe se o desempenho do aluno na disciplina for >= threshold.
    O peso da aresta é a nota em si -- fica disponível caso algum
    algoritmo queira usar (a projeção por padrão ignora e conta só a
    existência da aresta).
    """
    B = nx.Graph()

    students = df["id_student"].unique()
    modules = df["code_module"].unique()

    B.add_nodes_from((f"S{s}" for s in students), bipartite=0, kind="student")
    B.add_nodes_from((f"M{m}" for m in modules), bipartite=1, kind="module")

    strong = df[df["score_media"] >= threshold]
    for _, row in strong.iterrows():
        B.add_edge(f"S{row.id_student}", f"M{row.code_module}", weight=row.score_media)

    return B


def student_nodes(B: nx.Graph):
    return {n for n, d in B.nodes(data=True) if d["bipartite"] == 0}


def module_nodes(B: nx.Graph):
    return {n for n, d in B.nodes(data=True) if d["bipartite"] == 1}


# ---------------------------------------------------------------------
# 3. Projeções
# ---------------------------------------------------------------------
def project_simple(B: nx.Graph, nodes: set) -> nx.Graph:
    """Projeção simples: peso = número de vizinhos em comum.

    Equivale a P = Bi . Bi^T (contando só a diagonal fora). Rápida e
    direta, mas enviesada a favor de nós de alto grau -- ver Zhou et
    al. (2007), citado na Fundamentação 2.2.3.
    """
    return nx.bipartite.weighted_projected_graph(B, nodes)


def project_resource_allocation(B: nx.Graph, nodes: set) -> nx.Graph:
    """Projeção ponderada por alocação de recursos (Zhou et al., 2007).

    Em vez de contar vizinhos compartilhados igualmente, cada vizinho
    comum contribui com peso 1/grau(vizinho) -- um módulo cursado por
    muita gente (baixa informação discriminativa) pesa menos do que um
    módulo raro e específico. Corrige o viés da projeção simples.
    """
    P = nx.Graph()
    P.add_nodes_from(nodes)

    other_side = set(B.nodes) - nodes
    for shared in other_side:
        neighbors = [n for n in B.neighbors(shared) if n in nodes]
        deg_shared = B.degree(shared)
        if deg_shared == 0:
            continue
        contribution = 1.0 / deg_shared
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                a, b = neighbors[i], neighbors[j]
                if P.has_edge(a, b):
                    P[a][b]["weight"] += contribution
                else:
                    P.add_edge(a, b, weight=contribution)
    return P


# ---------------------------------------------------------------------
# 4. Execução direta para checagem rápida
# ---------------------------------------------------------------------
if __name__ == "__main__":
    df = load_data()
    print(f"[ETL] {df.shape[0]} pares (aluno, disciplina) após agregação")

    B = build_bipartite_graph(df)
    S, M = student_nodes(B), module_nodes(B)
    print(f"[Bipartido] {len(S)} alunos, {len(M)} disciplinas, {B.number_of_edges()} arestas")

    P_alunos_simples = project_simple(B, S)
    P_alunos_ra = project_resource_allocation(B, S)
    P_disciplinas = project_simple(B, M)

    print(f"[Projeção simples aluno-aluno]   {P_alunos_simples.number_of_edges()} arestas")
    print(f"[Projeção resource-alloc aluno]  {P_alunos_ra.number_of_edges()} arestas")
    print(f"[Projeção disciplina-disciplina] {P_disciplinas.number_of_edges()} arestas")

    # salva pra frentes B e C consumirem sem precisar reprocessar
    nx.write_gml(P_alunos_simples, "data/synthetic/proj_alunos_simples.gml")
    nx.write_gml(P_alunos_ra, "data/synthetic/proj_alunos_resource_alloc.gml")
    nx.write_gml(P_disciplinas, "data/synthetic/proj_disciplinas.gml")
    print("[OK] Projeções salvas em data/synthetic/*.gml")
