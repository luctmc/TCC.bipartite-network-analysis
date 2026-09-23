"""Louvain e Girvan-Newman  ``[B]`` — specs B-01 e B-02.

Os testes rodam sobre as **fixtures**, não sobre saída da Frente A. É a
prova do paralelismo: a Frente B fecha B-01, B-02 e B-03 inteiras sem
que a Frente A tenha entregue uma linha.

Nada de igualdade exata de Q: Louvain é estocástico e uma troca de
versão da biblioteca move o quarto decimal (ver
``docs/testes/estrategia.md``). As faixas são largas de propósito —
pegam regressão real, não flutuação.
"""

from __future__ import annotations

import networkx as nx
import pytest

from edugraph.community.girvan_newman import GirvanNewmanAlgorithm
from edugraph.community.louvain import LouvainAlgorithm, compare_implementations
from edugraph.community.modularity import modularity
from edugraph.contracts.errors import ContractError
from edugraph.contracts.validate import validate_partition


@pytest.mark.dataset("tiny_v1")
def test_louvain_recupera_os_dois_grupos_de_tiny(tiny_projection) -> None:
    """``tiny_v1`` é um K4 colado a um triângulo por S3.

    A partição natural é {S1,S2,S3,S6} e {S4,S5} — ou {S4,S5} separado
    com S3 de qualquer um dos lados, já que ele é a ponte. O teste
    aceita as duas leituras e só exige que S4 e S5 fiquem juntos e
    separados de S1, S2 e S6.
    """
    projection = tiny_projection("student_simple")
    partition = LouvainAlgorithm().run(projection, seed=42)

    assert partition.n_communities == 2
    membership = partition.membership
    assert membership["S4"] == membership["S5"]
    assert membership["S1"] == membership["S2"] == membership["S6"]
    assert membership["S1"] != membership["S4"]


@pytest.mark.dataset("synthetic_v1")
def test_louvain_encontra_as_tres_areas_plantadas(synthetic_projection) -> None:
    """Três comunidades grandes, Q em [0,40, 0,55].

    Faixa, não igualdade: Louvain é estocástico e uma troca de versão da
    biblioteca move o quarto decimal (ver REFERENCE.md da fixture, onde
    a referência é Q ≈ 0,467 com 3 comunidades).
    """
    projection = synthetic_projection("student_simple")
    partition = LouvainAlgorithm().run(projection, seed=42)

    assert 0.40 <= partition.modularity <= 0.55
    grandes = [g for g in partition.groups().values() if len(g) >= 10]
    assert len(grandes) >= 3


@pytest.mark.dataset("synthetic_v1")
def test_mesma_seed_mesma_particao(synthetic_projection) -> None:
    """Sem isto, nenhuma tabela do artigo é reproduzível (ADR-0011)."""
    projection = synthetic_projection("student_simple")
    primeira = LouvainAlgorithm().run(projection, seed=42)
    segunda = LouvainAlgorithm().run(projection, seed=42)
    assert primeira.membership == segunda.membership


@pytest.mark.dataset("synthetic_v1")
def test_ids_de_comunidade_sao_densos(synthetic_projection) -> None:
    """O validador de contrato exige ``0..k-1``; a biblioteca não garante."""
    partition = LouvainAlgorithm().run(synthetic_projection("student_simple"), seed=42)
    assert sorted(set(partition.membership.values())) == list(range(partition.n_communities))


@pytest.mark.dataset("synthetic_v1")
def test_particao_passa_no_validador_cruzada_com_a_projecao(synthetic_projection) -> None:
    """O cruzamento que impede servir a partição de uma projeção como de outra."""
    projection = synthetic_projection("student_simple")
    partition = LouvainAlgorithm().run(projection, seed=42)

    validate_partition(partition, projection)  # não levanta
    assert partition.status == "ok"


@pytest.mark.dataset("synthetic_v1")
def test_params_registram_o_que_o_artigo_precisa_citar(synthetic_projection) -> None:
    """Sem ``seed``, ``resolution`` e ``implementation``, a linha da tabela não é reproduzível."""
    partition = LouvainAlgorithm().run(
        synthetic_projection("student_simple"), seed=7, resolution=1.5
    )

    assert partition.params["seed"] == 7
    assert partition.params["resolution"] == 1.5
    assert partition.params["implementation"] == "python_louvain"
    assert partition.meta.producer == "B-01"


@pytest.mark.dataset("synthetic_v1")
def test_parametro_desconhecido_e_erro_e_nao_silencio(synthetic_projection) -> None:
    """``resolucao=2`` em vez de ``resolution=2`` não pode passar batido."""
    with pytest.raises(ContractError, match="resolucao"):
        LouvainAlgorithm().run(synthetic_projection("student_simple"), resolucao=2.0)


@pytest.mark.dataset("synthetic_v1")
def test_as_duas_bibliotecas_concordam(synthetic_projection) -> None:
    """A comparação que a spec B-01 exige registrar.

    Se um dia divergirem, o artigo precisa dizer qual foi usada e o que
    muda — por isso o teste compara Q, k e a concordância entre as duas
    partições, não só o Q.
    """
    linha = compare_implementations(synthetic_projection("student_simple"), seed=42)

    assert linha["abs_diff"] < 1e-9
    assert linha["n_communities_python_louvain"] == linha["n_communities_networkx"]
    assert linha["nmi"] == pytest.approx(1.0)


@pytest.mark.dataset("synthetic_v1")
def test_resolucao_maior_quebra_em_mais_comunidades(synthetic_projection) -> None:
    """γ > 1 favorece comunidades menores — é o que o parâmetro promete."""
    projection = synthetic_projection("student_simple")
    padrao = LouvainAlgorithm().run(projection, seed=42, resolution=1.0)
    fina = LouvainAlgorithm().run(projection, seed=42, resolution=3.0)

    assert fina.n_communities > padrao.n_communities


# ---------------------------------------------------------------------
# B-02 — Girvan-Newman e o orçamento de tempo
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
def test_orcamento_estourado_devolve_timeout_e_nao_excecao(synthetic_projection) -> None:
    """O contrato proíbe levantar: estouro é ``status="timeout"`` (ADR-0006).

    É este comportamento que transforma "o algoritmo não termina" de
    falha em resultado reportável no capítulo 3.

    Com 0,01 s nem o primeiro corte cabe — sobre 1.971 arestas ele leva
    ~15 s —, então o status é ``skipped``. O teste aceita os dois, porque
    o que ele garante é a ausência de exceção e a partição devolvida.
    """
    projection = synthetic_projection("student_simple")
    partition = GirvanNewmanAlgorithm().run(projection, time_budget_s=0.01)

    assert partition.status in ("timeout", "skipped")
    assert partition.membership, "mesmo no timeout, devolve a melhor partição vista"


@pytest.mark.dataset("tiny_v1")
def test_girvan_newman_separa_a_ponte_em_tiny(tiny_projection) -> None:
    """Removendo a aresta de maior intermediação, {S4,S5} se descola."""
    projection = tiny_projection("student_simple")
    partition = GirvanNewmanAlgorithm().run(projection, time_budget_s=30.0, target_communities=2)

    assert partition.status == "ok"
    assert partition.membership["S4"] == partition.membership["S5"]
    assert partition.membership["S1"] != partition.membership["S4"]


@pytest.mark.dataset("synthetic_v1")
def test_orcamento_estourado_devolve_particao_trivial_valida(synthetic_projection) -> None:
    """Estouro antes do primeiro corte: partição trivial, Q = 0, artefato válido."""
    projection = synthetic_projection("student_simple")
    partition = GirvanNewmanAlgorithm().run(projection, time_budget_s=0.0)

    assert partition.status == "skipped"
    assert partition.n_communities == 1
    assert partition.modularity == pytest.approx(0.0)
    assert partition.params["n_cuts"] == 0
    validate_partition(partition, projection)  # vale como artefato como qualquer outro


@pytest.mark.dataset("tiny_v1")
def test_sem_alvo_para_no_melhor_q_do_dendrograma(tiny_projection) -> None:
    """``target_communities=None``: o nível escolhido é o de maior Q.

    O teste refaz o dendrograma inteiro com o NetworkX e confere que
    nenhum nível tem Q maior que o devolvido.
    """
    projection = tiny_projection("student_simple")
    partition = GirvanNewmanAlgorithm().run(projection, time_budget_s=60.0)

    assert partition.status == "ok"
    todos = [
        modularity(projection.graph, {n: i for i, c in enumerate(nivel) for n in c})
        for nivel in nx.community.girvan_newman(projection.graph)
    ]
    assert partition.modularity == pytest.approx(max(todos))


@pytest.mark.dataset("tiny_v1")
def test_alvo_de_comunidades_para_no_alvo(tiny_projection) -> None:
    """Com alvo, o critério de parada é o número de comunidades, não o Q."""
    projection = tiny_projection("student_simple")
    partition = GirvanNewmanAlgorithm().run(projection, time_budget_s=60.0, target_communities=3)

    assert partition.n_communities == 3
    assert partition.params["stop_reason"] == "target_communities"


@pytest.mark.dataset("synthetic_v1")
def test_amostragem_marca_o_recorte_no_id_da_projecao(synthetic_projection) -> None:
    """Partição parcial nunca se passa pela partição da projeção inteira.

    Sem o sufixo, ``validate_dataset`` cruzaria uma partição de 30 nós
    com uma projeção de 98 e o artefato seria recusado — ou pior, seria
    aceito e a tabela do capítulo 3 mentiria sobre o recorte.
    """
    projection = synthetic_projection("student_simple")
    partition = GirvanNewmanAlgorithm().run(
        projection, time_budget_s=60.0, sample_nodes=30, seed=42, target_communities=2
    )

    assert partition.projection_id == "student_simple__sample30"
    assert partition.artifact_id == "girvan_newman__student_simple__sample30"
    assert len(partition.membership) == 30
    assert partition.params["source_projection_id"] == "student_simple"
    validate_partition(partition)


@pytest.mark.dataset("synthetic_v1")
def test_amostragem_e_deterministica(synthetic_projection) -> None:
    """Mesma semente, mesmos nós amostrados (ADR-0011)."""
    projection = synthetic_projection("student_simple")
    kwargs = {"time_budget_s": 60.0, "sample_nodes": 20, "seed": 7, "target_communities": 2}
    primeira = GirvanNewmanAlgorithm().run(projection, **kwargs)
    segunda = GirvanNewmanAlgorithm().run(projection, **kwargs)

    assert primeira.membership == segunda.membership


def test_grafo_sem_arestas_devolve_componentes_sem_travar() -> None:
    """Caso de borda: sem aresta não há corte, e as componentes são a resposta."""
    from edugraph.contracts.types import BipartiteSpec, ProjectionBundle, ProjectionSpec

    graph: nx.Graph = nx.Graph()
    graph.add_nodes_from(["S1", "S2"], kind="student")
    projection = ProjectionBundle(
        graph=graph,
        spec=ProjectionSpec(side="student", weighting="simple"),
        source=BipartiteSpec(dataset="vazio"),
    )
    partition = GirvanNewmanAlgorithm().run(projection, time_budget_s=1.0)

    assert partition.status == "ok"
    assert partition.n_communities == 2
    assert partition.modularity == pytest.approx(0.0)


# ---------------------------------------------------------------------
# Lento — o número que vai para o artigo (B-02, B-04)
# ---------------------------------------------------------------------


@pytest.mark.slow
@pytest.mark.dataset("synthetic_v1")
def test_custo_relativo_do_girvan_newman_esta_medido(synthetic_projection) -> None:
    """Girvan-Newman completo × Louvain sobre a mesma projeção.

    Medido em 20/09/2026 sobre ``synthetic_v1``/``student_simple`` (98
    nós, 1.971 arestas): Louvain 0,024 s com Q = 0,4666; Girvan-Newman
    34,4 s com Q = 0,4174 — **1.453×** mais lento, com Q menor e o mesmo
    k = 3. É a ordem de grandeza do starter kit (645× sobre 120 nós) e o
    número que sustenta a ADR-0006.

    Fora da CI (``slow``): são mais de 30 s.
    """
    projection = synthetic_projection("student_simple")
    louvain = LouvainAlgorithm().run(projection, seed=42)
    girvan = GirvanNewmanAlgorithm().run(projection, time_budget_s=600.0)

    assert girvan.status == "ok", "600 s deveriam bastar para as 98 nós desta fixture"
    assert girvan.runtime_s > 100 * louvain.runtime_s, "o custo relativo caiu duas ordens?"
    assert girvan.modularity <= louvain.modularity + 1e-9, (
        "Girvan-Newman achando Q maior que o Louvain contradiz o starter kit; conferir"
    )
