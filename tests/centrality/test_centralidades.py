"""Centralidades  ``[C]`` — specs C-01, C-02 e C-03.

Os valores exatos vêm de ``data/fixtures/tiny_v1/expected/``, derivado
no papel. Em ``tiny_v1``, a projeção aluno↔aluno é um K4 em
{S1,S2,S3,S6} colado a um triângulo {S3,S4,S5}: S3 é o único vértice de
corte, e por isso concentra **toda** a intermediação (0,6 normalizado)
enquanto todos os outros ficam em zero.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from edugraph.centrality.betweenness import BetweennessCentrality
from edugraph.centrality.degree import DegreeCentrality
from edugraph.centrality.eigenvector import DEFAULT_TOL, EigenvectorCentrality


def _expected(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.mark.dataset("tiny_v1")
def test_grau_bate_com_o_calculo_a_mao(tiny_projection, tiny_expected: Path) -> None:
    """Grau normalizado por n−1 = 5."""
    projection = tiny_projection("student_simple")
    result = DegreeCentrality().compute(projection, normalized=True, weight=None)

    for row in _expected(tiny_expected / "student_simple.centrality.csv"):
        assert result.scores[row["node_id"]] == pytest.approx(float(row["degree"]))


@pytest.mark.dataset("tiny_v1")
def test_intermediacao_aponta_o_vertice_de_corte(tiny_projection, tiny_expected: Path) -> None:
    """S3 é a ponte: 0,6; todos os outros, 0."""
    projection = tiny_projection("student_simple")
    result = BetweennessCentrality().compute(projection, normalized=True, weight_mode="none")

    for row in _expected(tiny_expected / "student_simple.centrality.csv"):
        assert result.scores[row["node_id"]] == pytest.approx(float(row["betweenness"]))

    assert result.top(1)[0][0] == "S3"


@pytest.mark.dataset("tiny_v1")
def test_scores_cobrem_exatamente_os_nos_da_projecao(tiny_projection) -> None:
    """Contrato: nenhum nó a mais, nenhum a menos, faixa [0, 1]."""
    from edugraph.contracts.validate import validate_centrality

    for projection_id in ("student_simple", "discipline_simple"):
        projection = tiny_projection(projection_id)
        for metric in (DegreeCentrality(), BetweennessCentrality()):
            result = metric.compute(projection)
            assert set(result.scores) == set(projection.graph.nodes)
            validate_centrality(result, projection)


@pytest.mark.dataset("tiny_v1")
def test_params_registram_o_que_muda_o_ranking(tiny_projection) -> None:
    """``normalized`` e ``weight_mode`` sempre; ``k`` e ``seed`` só com amostra."""
    projection = tiny_projection("student_simple")

    exata = BetweennessCentrality().compute(projection)
    assert exata.params["normalized"] is True
    assert exata.params["weight_mode"] == "none"
    assert exata.params["k"] is None
    assert exata.params["estimate"] is False
    assert "seed" not in exata.params

    amostra = BetweennessCentrality().compute(projection, k=3, seed=7)
    assert amostra.params["k"] == 3
    assert amostra.params["seed"] == 7
    assert amostra.params["estimate"] is True

    grau = DegreeCentrality().compute(projection)
    assert grau.params == {"normalized": True, "weight": None, "normalization": "n_minus_1"}


@pytest.mark.dataset("tiny_v1")
def test_k_maior_ou_igual_a_n_e_calculo_exato(tiny_projection) -> None:
    """Pedir mais pivôs que nós não é amostra: o artefato não diz estimativa."""
    projection = tiny_projection("student_simple")
    result = BetweennessCentrality().compute(projection, k=500, seed=42)

    assert result.params["estimate"] is False
    assert result.params["k"] is None
    assert result.scores["S3"] == pytest.approx(0.6)


@pytest.mark.dataset("tiny_v1")
def test_amostra_de_pivos_e_deterministica_com_seed(tiny_projection) -> None:
    projection = tiny_projection("student_simple")
    primeira = BetweennessCentrality().compute(projection, k=3, seed=11)
    segunda = BetweennessCentrality().compute(projection, k=3, seed=11)
    assert primeira.scores == segunda.scores


def test_peso_inverso_encurta_a_aresta_forte_e_nao_altera_a_projecao() -> None:
    """``inverse`` usa 1/w: a aresta de peso alto vira o caminho curto.

    Quadrado A-B-C-D-A com A-B e B-C fortes (peso 10) e A-D, D-C fracos
    (peso 1). Sem peso há dois caminhos mínimos de A a C e B e D dividem
    a intermediação; com ``inverse`` o caminho por B custa 0,2 contra 2,0
    por D, e só B fica com ela. Com ``raw`` é o contrário — a inversão
    de semântica que a C-01 existe para evitar.
    """
    import networkx as nx

    from edugraph.contracts.types import BipartiteSpec, ProjectionBundle, ProjectionSpec

    graph = nx.Graph()
    graph.add_edge("DA", "DB", weight=10.0)
    graph.add_edge("DB", "DC", weight=10.0)
    graph.add_edge("DA", "DD", weight=1.0)
    graph.add_edge("DD", "DC", weight=1.0)
    for node in graph:
        graph.nodes[node]["kind"] = "discipline"
    bundle = ProjectionBundle(
        graph=graph,
        spec=ProjectionSpec(side="discipline", weighting="simple"),
        source=BipartiteSpec(dataset="t"),
    )

    sem_peso = BetweennessCentrality().compute(bundle, weight_mode="none")
    inverso = BetweennessCentrality().compute(bundle, weight_mode="inverse")
    cru = BetweennessCentrality().compute(bundle, weight_mode="raw")

    assert sem_peso.scores["DB"] == pytest.approx(sem_peso.scores["DD"])
    assert inverso.scores["DB"] > 0 and inverso.scores["DD"] == pytest.approx(0.0)
    assert cru.scores["DD"] > 0 and cru.scores["DB"] == pytest.approx(0.0)
    assert all("_distance" not in data for _, _, data in graph.edges(data=True))


@pytest.mark.dataset("tiny_v1")
def test_forca_ponderada_normaliza_pela_maior_forca(tiny_projection) -> None:
    projection = tiny_projection("discipline_simple")  # DA-DB=3, DA-DC=DB-DC=1
    result = DegreeCentrality().compute(projection, weight="weight")

    assert result.scores == pytest.approx({"DA": 1.0, "DB": 1.0, "DC": 0.5})
    assert result.params["normalization"] == "max_strength"


@pytest.mark.dataset("tiny_v1")
def test_parametro_desconhecido_e_recusado(tiny_projection) -> None:
    """``weigth_mode`` digitado errado não pode rodar com o padrão em silêncio."""
    from edugraph.contracts.errors import ContractError

    projection = tiny_projection("student_simple")
    with pytest.raises(ContractError, match="weigth_mode"):
        BetweennessCentrality().compute(projection, weigth_mode="inverse")
    with pytest.raises(ContractError, match="weight_mode"):
        BetweennessCentrality().compute(projection, weight_mode="afinidade")


@pytest.mark.dataset("tiny_v1")
def test_autovetor_bate_com_a_forma_fechada(tiny_projection, tiny_expected: Path) -> None:
    """Triângulo ponderado DA-DB=3, DA-DC=DB-DC=1.

    Por simetria x = DA = DB e y = DC, com λx = 3x + y e λy = 2x, logo
    λ = (3+√17)/2. É um teste de verdade da iteração de potência: o
    valor esperado sai da álgebra, não do NetworkX.
    """
    projection = tiny_projection("discipline_simple")
    result = EigenvectorCentrality().compute(projection, implementation="manual", weight="weight")

    for row in _expected(tiny_expected / "discipline_simple.eigenvector.csv"):
        assert result.scores[row["node_id"]] == pytest.approx(float(row["score"]), abs=1e-8)
    assert result.converged is True


@pytest.mark.dataset("synthetic_v1")
def test_iteracao_de_potencia_bate_com_o_networkx(synthetic_projection) -> None:
    """A comparação que o artigo cita (ADR-0010)."""
    import networkx as nx

    projection = synthetic_projection("student_simple")
    manual = EigenvectorCentrality().compute(projection, implementation="manual")
    # Mesmo critério de parada dos dois lados. Com o tol padrão do
    # NetworkX (1e-6), é a referência que fica a 7e-6 do autovetor exato
    # — a manual, com 1e-8, fica a 8e-8 — e a comparação falharia por
    # imprecisão da biblioteca, não da implementação à mão.
    referencia = nx.eigenvector_centrality(
        projection.graph, weight="weight", max_iter=1000, tol=DEFAULT_TOL
    )

    for node, score in manual.scores.items():
        assert score == pytest.approx(abs(referencia[node]), abs=1e-6)


def test_nao_convergencia_vira_fallback_e_nao_excecao() -> None:
    """O contrato exige ``converged=False`` e fallback, nunca exceção.

    Grafo desconexo é o caso normal na projeção aluno↔aluno do OULAD;
    derrubar o pipeline nele seria inaceitável.
    """
    import networkx as nx

    from edugraph.contracts.types import BipartiteSpec, ProjectionBundle, ProjectionSpec

    graph = nx.Graph()
    graph.add_edge("S1", "S2", weight=1.0)
    graph.add_edge("S3", "S4", weight=1.0)  # componente separada
    for node in graph:
        graph.nodes[node]["kind"] = "student"

    bundle = ProjectionBundle(
        graph=graph,
        spec=ProjectionSpec(side="student", weighting="simple"),
        source=BipartiteSpec(dataset="t"),
    )
    result = EigenvectorCentrality().compute(bundle, implementation="manual", max_iter=5)

    assert set(result.scores) == set(graph.nodes)
    assert all(score >= 0 for score in result.scores.values())


def _bundle(graph, kind: str = "student"):
    from edugraph.contracts.types import BipartiteSpec, ProjectionBundle, ProjectionSpec

    for node in graph:
        graph.nodes[node]["kind"] = kind
    return ProjectionBundle(
        graph=graph,
        spec=ProjectionSpec(side=kind, weighting="simple"),
        source=BipartiteSpec(dataset="t"),
    )


def test_iteracao_de_potencia_acha_autovetor_conhecido() -> None:
    """[[2,1],[1,2]] tem autovalores 3 e 1; o principal é (1,1)/√2.

    E [[2,1],[1,0]] — não simétrico no vetor inicial — converge para
    ((1+√2), 1) normalizado, autovalor 1+√2.
    """
    import numpy as np

    from edugraph.centrality.eigenvector import power_iteration

    vetor, convergiu, _ = power_iteration(np.array([[2.0, 1.0], [1.0, 2.0]]))
    assert convergiu is True
    assert vetor == pytest.approx(np.array([1.0, 1.0]) / np.sqrt(2), abs=1e-12)

    vetor, convergiu, n_iter = power_iteration(np.array([[2.0, 1.0], [1.0, 0.0]]))
    esperado = np.array([1.0 + np.sqrt(2.0), 1.0])
    assert convergiu is True and n_iter > 1
    assert vetor == pytest.approx(esperado / np.linalg.norm(esperado), abs=1e-7)


def test_iteracao_sem_deslocamento_oscila_em_grafo_bipartido() -> None:
    """Estrela de 3 folhas: A tem ±√3, e a iteração pura não converge.

    É o motivo de ``compute`` iterar sobre A + I (ver o módulo).
    """
    import networkx as nx

    from edugraph.centrality.eigenvector import power_iteration

    estrela = nx.to_numpy_array(nx.star_graph(3))
    _, convergiu, _ = power_iteration(estrela, max_iter=200)
    assert convergiu is False

    result = EigenvectorCentrality().compute(_bundle(nx.star_graph(3)))
    assert result.converged is True
    assert result.top(1)[0][0] == "0"


def test_estouro_de_iteracoes_registra_o_fallback() -> None:
    """Com ``max_iter=1`` num caminho, não converge: fallback e ``params``."""
    import networkx as nx

    grafo = nx.path_graph(6)
    result = EigenvectorCentrality().compute(_bundle(nx.relabel_nodes(grafo, str)), max_iter=1)

    assert result.converged is False
    assert result.params["fallback"] == "spectral"
    referencia = nx.eigenvector_centrality_numpy(grafo)
    for node, score in referencia.items():
        assert result.scores[str(node)] == pytest.approx(abs(score), abs=1e-9)


@pytest.mark.dataset("tiny_v1")
def test_implementacao_networkx_bate_com_a_manual(tiny_projection) -> None:
    projection = tiny_projection("student_simple")
    manual = EigenvectorCentrality().compute(projection, implementation="manual")
    referencia = EigenvectorCentrality().compute(projection, implementation="networkx")

    assert referencia.params["implementation"] == "networkx"
    for node, score in manual.scores.items():
        assert score == pytest.approx(referencia.scores[node], abs=1e-6)


def test_validador_recusa_autovetor_com_componente_negativa() -> None:
    from edugraph.contracts.errors import ContractError
    from edugraph.contracts.types import CentralityResult
    from edugraph.contracts.validate import validate_centrality

    ruim = CentralityResult(
        projection_id="student_simple",
        metric="eigenvector",
        scores={"S1": 0.8, "S2": -0.6},
    )
    with pytest.raises(ContractError, match="negativa"):
        validate_centrality(ruim)


# ---------------------------------------------------------------------
# C-03 — disciplinas críticas (saída obrigatória)
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
def test_ranking_de_disciplinas_e_deterministico(synthetic_projection) -> None:
    """Empates desempatam por ``node_id``, senão a tabela muda a cada rodada.

    **Atenção ao caso desta fixture.** Em ``synthetic_v1`` com V =
    módulo, ``discipline_simple`` é o grafo completo K₇: grau e
    intermediação empatam em todos os nós. O desempate determinístico
    não é detalhe, é o que impede a tabela do artigo de mudar sozinha.
    Ver REFERENCE.md da fixture e a decisão D1.
    """
    from edugraph.centrality.critical_disciplines import rank_disciplines

    projection = synthetic_projection("discipline_simple")
    results = {
        "degree": DegreeCentrality().compute(projection),
        "betweenness": BetweennessCentrality().compute(projection),
        "eigenvector": EigenvectorCentrality().compute(projection),
    }

    primeiro = rank_disciplines(results, top_n=7)
    segundo = rank_disciplines(results, top_n=7)
    assert primeiro == segundo


@pytest.mark.dataset("synthetic_v1")
def test_projecao_disciplina_de_synthetic_e_degenerada(synthetic_projection) -> None:
    """Documenta a degeneração da decisão D1 como comportamento esperado.

    Com 7 módulos e alunos cursando de 2 a 4, todo par de disciplinas
    compartilha algum aluno: K₇, intermediação zero em todos os nós.
    Este teste **afirma a degeneração** em vez de fingir que ela não
    existe — se algum dia ele falhar, é porque a granularidade mudou, e
    aí a spec C-03 passa a ter o que ranquear.
    """
    projection = synthetic_projection("discipline_simple")
    result = BetweennessCentrality().compute(projection, weight_mode="none")

    assert projection.graph.number_of_nodes() == 7
    assert projection.graph.number_of_edges() == 21  # C(7,2): grafo completo
    assert all(score == pytest.approx(0.0) for score in result.scores.values())


def _ponte_entre_dois_blocos():
    """Dois K4 ligados por uma disciplina-ponte DB de grau 2.

    DB fica em todos os 16 caminhos entre os blocos (intermediação
    máxima) com o menor grau do grafo; DA1 e DC1, as portas dos blocos,
    lideram o grau e o autovetor. É o perfil que a C-03 procura: ponte
    sem ser popular.
    """
    import networkx as nx

    grafo = nx.Graph()
    for bloco in ("DA", "DC"):
        nos = [f"{bloco}{i}" for i in range(1, 5)]
        grafo.add_edges_from(
            (u, v, {"weight": 1.0}) for i, u in enumerate(nos) for v in nos[i + 1 :]
        )
    grafo.add_edge("DA1", "DB", weight=1.0)
    grafo.add_edge("DB", "DC1", weight=1.0)
    projection = _bundle(grafo, kind="discipline")
    return {
        "degree": DegreeCentrality().compute(projection),
        "betweenness": BetweennessCentrality().compute(projection),
        "eigenvector": EigenvectorCentrality().compute(projection),
    }


def test_discordancia_acha_a_ponte_que_nao_e_popular() -> None:
    from edugraph.centrality.disagreement import disagreement

    resultados = _ponte_entre_dois_blocos()
    conjuntos = disagreement(resultados, top_n=1)

    assert conjuntos == {
        "only_degree": [],
        "only_betweenness": ["DB"],
        "only_eigenvector": [],
        "all_three": [],
    }
    assert resultados["degree"].scores["DB"] == min(resultados["degree"].scores.values())


def test_discordancia_com_top_maior_devolve_listas_ordenadas() -> None:
    from edugraph.centrality.disagreement import disagreement

    conjuntos = disagreement(_ponte_entre_dois_blocos(), top_n=3)
    assert set(conjuntos) == {"only_degree", "only_betweenness", "only_eigenvector", "all_three"}
    for nos in conjuntos.values():
        assert nos == sorted(nos)
    assert "DA1" in conjuntos["all_three"] and "DC1" in conjuntos["all_three"]


def test_discordancia_exige_as_tres_metricas() -> None:
    from edugraph.centrality.disagreement import disagreement
    from edugraph.contracts.errors import ContractError

    resultados = _ponte_entre_dois_blocos()
    del resultados["eigenvector"]
    with pytest.raises(ContractError, match="eigenvector"):
        disagreement(resultados)


def test_ranking_tem_as_colunas_do_contrato_e_desempata_por_id() -> None:
    from edugraph.centrality.critical_disciplines import METRICS_COLUMNS, rank_disciplines

    linhas = rank_disciplines(
        _ponte_entre_dois_blocos(), top_n=3, dataset="t", labels={"DB": "Ponte"}
    )

    assert all(tuple(linha) == METRICS_COLUMNS for linha in linhas)
    assert [linha["metric"] for linha in linhas[::3]] == ["degree", "betweenness", "eigenvector"]
    intermediacao = [linha for linha in linhas if linha["metric"] == "betweenness"]
    assert intermediacao[0]["node_id"] == "DB" and intermediacao[0]["label"] == "Ponte"
    grau = [linha for linha in linhas if linha["metric"] == "degree"]
    assert [linha["node_id"] for linha in grau] == ["DA1", "DC1", "DA2"]  # empates por id
    assert [linha["rank"] for linha in grau] == [1, 2, 3]


@pytest.mark.dataset("synthetic_v1")
def test_top_n_maior_que_o_grafo_devolve_o_ranking_inteiro(synthetic_projection) -> None:
    from edugraph.centrality.critical_disciplines import rank_disciplines

    projection = synthetic_projection("discipline_simple")
    linhas = rank_disciplines({"degree": DegreeCentrality().compute(projection)}, top_n=50)
    assert len(linhas) == 7


def test_ranking_recusa_projecoes_misturadas() -> None:
    from edugraph.centrality.critical_disciplines import rank_disciplines
    from edugraph.contracts.errors import ContractError
    from edugraph.contracts.types import CentralityResult

    resultados = {
        "degree": CentralityResult("discipline_simple", "degree", {"DA": 1.0}),
        "betweenness": CentralityResult("student_simple", "betweenness", {"S1": 0.0}),
    }
    with pytest.raises(ContractError, match="projeções diferentes"):
        rank_disciplines(resultados)


def test_centrality_top_e_idempotente_pela_chave(tmp_path) -> None:
    """Contrato: rodar de novo atualiza as posições, não duplica."""
    from edugraph.centrality.critical_disciplines import rank_disciplines, write_metrics
    from edugraph.contracts import io

    linhas = rank_disciplines(_ponte_entre_dois_blocos(), top_n=3, dataset="t")
    write_metrics(linhas, tmp_path, "t")
    primeira = io.load_metrics(tmp_path, "t", "centrality_top")
    write_metrics(linhas, tmp_path, "t")
    segunda = io.load_metrics(tmp_path, "t", "centrality_top")

    assert primeira == segunda
    assert len(segunda) == 9
    chaves = {(r["dataset"], r["projection_id"], r["metric"], r["rank"]) for r in segunda}
    assert len(chaves) == len(segunda)


def test_spearman_bate_com_o_scipy_e_e_nan_no_empate_total(synthetic_projection) -> None:
    from scipy.stats import spearmanr

    from edugraph.centrality.disagreement import rank_correlation

    resultados = _ponte_entre_dois_blocos()
    nos = sorted(resultados["degree"].scores)
    esperado = spearmanr(
        [resultados["degree"].scores[n] for n in nos],
        [resultados["betweenness"].scores[n] for n in nos],
    ).statistic
    assert rank_correlation(resultados["degree"], resultados["betweenness"]) == pytest.approx(
        esperado
    )

    completo = synthetic_projection("discipline_simple")  # K7: tudo empatado
    grau = DegreeCentrality().compute(completo)
    intermediacao = BetweennessCentrality().compute(completo)
    import math

    assert math.isnan(rank_correlation(grau, intermediacao))


@pytest.mark.dataset("oulad_module_presentation")
def test_granularidade_fina_discrimina_as_disciplinas(artifact_roots) -> None:
    """Critério de aceite da C-03: com V = módulo×apresentação, o ranking
    não empata tudo — senão a decisão D1 precisaria ser revisitada.

    Roda só com ``--artifacts-root data/processed``.
    """
    from edugraph.contracts import io

    projection = io.load_projection(
        artifact_roots, "oulad_module_presentation", "discipline_simple"
    )
    intermediacao = BetweennessCentrality().compute(projection)

    assert projection.graph.number_of_nodes() == 22
    assert len(set(intermediacao.scores.values())) > 10
    assert min(intermediacao.scores.values()) < max(intermediacao.scores.values())


def test_linhas_de_discordancia_trazem_conjuntos_e_correlacoes() -> None:
    from edugraph.centrality.disagreement import DISAGREEMENT_COLUMNS, disagreement_rows

    linhas = disagreement_rows(
        _ponte_entre_dois_blocos(), top_n=1, dataset="t", labels={"DB": "Ponte"}
    )

    assert all(tuple(linha) == DISAGREEMENT_COLUMNS for linha in linhas)
    por_nome = {linha["comparison"]: linha["value"] for linha in linhas}
    assert por_nome["only_betweenness"] == "Ponte"
    assert por_nome["all_three"] == ""
    assert set(por_nome) >= {
        "spearman_degree_betweenness",
        "spearman_degree_eigenvector",
        "spearman_betweenness_eigenvector",
    }


@pytest.mark.dataset("tiny_v1")
def test_k_zero_ou_negativo_e_recusado(tiny_projection) -> None:
    """``k = 0`` no TOML derrubava o estágio com ZeroDivisionError do NetworkX."""
    from edugraph.contracts.errors import ContractError

    projection = tiny_projection("student_simple")
    for k in (0, -3):
        with pytest.raises(ContractError, match="k precisa ser >= 1"):
            BetweennessCentrality().compute(projection, k=k)
