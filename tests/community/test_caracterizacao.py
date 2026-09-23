"""Caracterização e validação a posteriori  ``[B]`` — specs B-05 e B-06.

A caracterização é **saída obrigatória** do TCC (briefing §6.2): uma
partição sem ela diz quem está junto, não por quê.

A validação é a etapa em que o rótulo histórico entra — e a única
(ADR-0008). O que ela mede não é acurácia de modelo: é a relação entre
uma estrutura descoberta pela topologia e categorias já conhecidas.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from edugraph.community.characterize import (
    PROFILE_COLUMNS,
    characterize,
    community_sizes,
    describe_partition,
)
from edugraph.community.evaluate import (
    MIN_REPLICAS,
    OUTCOME_COLUMNS,
    is_null_replica,
    modularity_z_score,
    normalized_mutual_information,
    null_baseline,
    null_replicas_of,
    outcome_profile,
    purity,
    unknown_outcomes,
)
from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import Meta, Outcomes, Partition

pytestmark = pytest.mark.dataset("synthetic_v1")


@pytest.fixture
def louvain_synthetic(artifact_roots) -> Partition:
    """A partição de referência de ``synthetic_v1`` (3 áreas plantadas)."""
    return io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")


# ---------------------------------------------------------------------
# B-05 — caracterização
# ---------------------------------------------------------------------


def test_perfil_tem_as_colunas_do_contrato(artifact_roots) -> None:
    """``profile.csv`` segue :data:`PROFILE_COLUMNS`."""
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    bipartite = io.load_bipartite(artifact_roots, "synthetic_v1")

    rows = characterize(partition, bipartite, top_k=3)
    assert rows
    assert set(rows[0]) == set(PROFILE_COLUMNS)
    assert len(rows) == partition.n_communities


def test_disciplinas_predominantes_distinguem_as_comunidades(artifact_roots) -> None:
    """O gerador plantou três áreas; o perfil precisa mostrar isso.

    Se todas as comunidades listassem as mesmas disciplinas, a
    caracterização não estaria caracterizando nada — é o caso de a
    frequência estar sendo medida em absoluto e não em excesso sobre a
    base (ver a nota de implementação da B-05).
    """
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    bipartite = io.load_bipartite(artifact_roots, "synthetic_v1")

    rows = characterize(partition, bipartite, top_k=2)
    grandes = [r for r in rows if int(r["size"]) >= 10]
    assinaturas = {str(r["top_disciplines"]) for r in grandes}

    assert len(assinaturas) == len(grandes), (
        "comunidades grandes com o mesmo conjunto de disciplinas predominantes"
    )


def test_as_tres_areas_plantadas_aparecem_no_perfil(artifact_roots) -> None:
    """exatas (AAA-BBB-CCC), sistemas (DDD-EEE) e humanas (FFF-GGG).

    O gerador planta três áreas; as três comunidades grandes precisam
    refletir isso, senão a caracterização não responde ao objetivo
    declarado na Introdução.
    """
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    bipartite = io.load_bipartite(artifact_roots, "synthetic_v1")

    rows = characterize(partition, bipartite, top_k=2)
    assinaturas = {r["top_disciplines"].split()[0] for r in rows if int(r["size"]) >= 10}

    areas = {frozenset(("AAA", "BBB", "CCC")), frozenset(("DDD", "EEE")), frozenset(("FFF", "GGG"))}
    assert len(assinaturas) == 3
    assert all(any(sigla in area for area in areas) for sigla in assinaturas)


def test_perfil_reporta_frequencia_relativa_ao_lado_da_absoluta(artifact_roots) -> None:
    """A disciplina obrigatória que todo mundo cursa não caracteriza ninguém."""
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    bipartite = io.load_bipartite(artifact_roots, "synthetic_v1")

    rows = characterize(partition, bipartite, top_k=1)
    for row in rows:
        assert "base" in row["top_disciplines"]
        assert "n=" in row["top_disciplines"]
        assert 0.0 <= row["internal_density"] <= 1.0
        assert row["mean_degree"] > 0
    assert sum(row["share_of_nodes"] for row in rows) == pytest.approx(1.0)


def test_tamanhos_somam_o_total_de_nos(artifact_roots) -> None:
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    sizes = community_sizes(partition)

    assert sum(sizes.values()) == len(partition.membership)
    assert sorted(sizes) == list(range(partition.n_communities))
    assert describe_partition(partition)["largest_community"] == max(sizes.values())


def test_particao_de_outro_dataset_e_erro(artifact_roots) -> None:
    """Cruzar partição e bipartido de datasets diferentes daria ficção."""
    bipartite = io.load_bipartite(artifact_roots, "synthetic_v1")
    alheia = Partition(
        algorithm="louvain",
        projection_id="student_simple",
        membership={"S999999": 0},
        modularity=0.0,
        n_communities=1,
        runtime_s=0.0,
    )
    with pytest.raises(ContractError, match="não existem no bipartido"):
        characterize(alheia, bipartite)


@pytest.mark.dataset("tiny_v1")
def test_perfil_de_tiny_bate_com_a_conta_a_mao(tiny_bipartite) -> None:
    """``tiny_v1``: DA = {S1,S2,S3,S6}, DB = {S1,S2,S3}, DC = {S3,S4,S5}.

    Com a partição natural {S1,S2,S3,S6} e {S4,S5}: a primeira tem grau
    médio (2+2+3+1)/4 = 2 e todos os pares compartilham DA — densidade
    interna 1; a segunda tem grau médio 1 e o par S4-S5 compartilha DC —
    densidade 1 também. A disciplina de maior excesso na segunda é C
    (100% contra 50% da base).
    """
    partition = Partition(
        algorithm="louvain",
        projection_id="student_simple",
        membership={"S1": 0, "S2": 0, "S3": 0, "S4": 1, "S5": 1, "S6": 0},
        modularity=0.0,
        n_communities=2,
        runtime_s=0.0,
    )
    rows = characterize(partition, tiny_bipartite, top_k=1)

    primeira, segunda = rows
    assert primeira["size"] == 4 and primeira["mean_degree"] == pytest.approx(2.0)
    assert primeira["internal_density"] == pytest.approx(1.0)
    assert segunda["size"] == 2 and segunda["mean_degree"] == pytest.approx(1.0)
    assert segunda["top_disciplines"].startswith("C 100.0% (base 50.0%, n=2)")


# ---------------------------------------------------------------------
# B-06 — contra o grupo plantado
# ---------------------------------------------------------------------


def test_nmi_contra_o_grupo_plantado(artifact_roots) -> None:
    """A estrutura descoberta pela topologia recupera o *ground truth*.

    NMI ≥ 0,8 com ruído de 35% no gerador. Se cair muito abaixo, ou o
    Louvain regrediu, ou a projeção mudou de semântica.
    """
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    outcomes = io.load_outcomes(artifact_roots, "synthetic_v1")
    assert outcomes.planted_group is not None

    assert normalized_mutual_information(partition, outcomes.planted_group) >= 0.8


def test_particao_identica_ao_plantado_da_nmi_e_pureza_um(louvain_synthetic) -> None:
    """Critério de aceite da B-06, sem depender de nenhum dataset real."""
    plantado = dict(louvain_synthetic.membership)

    assert normalized_mutual_information(louvain_synthetic, plantado) == pytest.approx(1.0)
    assert purity(louvain_synthetic, plantado) == pytest.approx(1.0)


def test_pureza_alta_com_nmi_menor_e_o_esperado(artifact_roots) -> None:
    """Pureza sozinha não basta: ela sobe quando a partição é mais fina."""
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    outcomes = io.load_outcomes(artifact_roots, "synthetic_v1")

    assert purity(partition, outcomes.planted_group) >= 0.9


def test_sem_no_em_comum_com_o_plantado_e_erro(louvain_synthetic) -> None:
    with pytest.raises(ContractError, match="nó em comum"):
        normalized_mutual_information(louvain_synthetic, {"NAO_EXISTE": 0})


@pytest.mark.dataset("synthetic_v2")
def test_pureza_bate_com_o_numero_de_referencia_da_fixture(artifact_roots) -> None:
    """Verificação cruzada: `synthetic_v2/REFERENCE.md` traz 0,864 e 0,840.

    Aqueles números saíram de ``scripts/make_fixtures.py``, escrito antes
    desta spec e por outro caminho. Bater com eles é a melhor evidência
    de que a pureza daqui está certa — comparar a implementação só
    consigo mesma não provaria nada.
    """
    outcomes = io.load_outcomes(artifact_roots, "synthetic_v2")
    esperado = {"student_simple": 0.864, "student_resource_allocation": 0.840}

    for projection_id, valor in esperado.items():
        partition = io.load_partition(artifact_roots, "synthetic_v2", f"louvain__{projection_id}")
        assert purity(partition, outcomes.planted_group) == pytest.approx(valor, abs=5e-4)


@pytest.mark.dataset("synthetic_v2")
def test_esparsidade_derruba_o_nmi_sem_derrubar_a_pureza(artifact_roots) -> None:
    """O achado que justifica reportar as duas medidas, não uma.

    ``synthetic_v2`` tem os mesmos grupos plantados de ``synthetic_v1``,
    com 70% dos alunos reduzidos a uma matrícula. A pureza mal se move
    (0,86 contra 0,95), mas o NMI cai de 0,82 para ~0,50: as comunidades
    continuam homogêneas e deixaram de corresponder aos grupos.
    """
    outcomes = io.load_outcomes(artifact_roots, "synthetic_v2")
    partition = io.load_partition(artifact_roots, "synthetic_v2", "louvain__student_simple")

    assert purity(partition, outcomes.planted_group) > 0.8
    assert normalized_mutual_information(partition, outcomes.planted_group) < 0.6


# ---------------------------------------------------------------------
# B-06 — contra o acaso (réplicas nulas da spec A-08)
# ---------------------------------------------------------------------


def test_z_score_com_replicas_suficientes_aponta_estrutura() -> None:
    """Os números medidos em ``synthetic_v1`` (A-08): 0,4666 contra 0,208 ± 0,017."""
    base = modularity_z_score(0.4666, [0.21, 0.19, 0.22, 0.20, 0.23])

    assert base["n_replicas"] == 5
    assert base["z"] > 10
    assert base["verdict"] == "estrutura"


def test_z_score_abaixo_do_limiar_e_indistinguivel_do_acaso() -> None:
    """O caso do OULAD ``module_presentation``: Q real menor que o nulo."""
    base = modularity_z_score(0.7728, [0.78, 0.781, 0.782, 0.779, 0.783])

    assert base["z"] < 0
    assert base["verdict"] == "indistinguível do acaso"


def test_poucas_replicas_nao_viram_veredito() -> None:
    """Com menos de cinco réplicas o desvio não sustenta conclusão."""
    assert modularity_z_score(0.5, [0.2, 0.25])["verdict"] == "poucas réplicas"
    assert modularity_z_score(0.5, [])["verdict"] == "sem réplicas"
    assert math.isnan(modularity_z_score(0.5, [0.2])["z"])
    assert MIN_REPLICAS >= 5


def test_replica_nula_e_reconhecida_pelo_artefato_e_nao_pelo_nome() -> None:
    """O critério é ``meta.stats["null_model"]`` (ADR-0003: B não importa A)."""
    stats = {"null_model": {"source_dataset": "synthetic_v1", "seed": 0}}

    assert is_null_replica(stats, "synthetic_v1")
    assert not is_null_replica(stats, "outro_dataset")
    assert not is_null_replica({"n_edges": 10}, "synthetic_v1")


def test_linha_de_base_nula_encontra_as_replicas_em_disco(tmp_path: Path, artifact_roots) -> None:
    """Grava uma réplica de mentira e confere que a busca a acha.

    O ``data/processed`` do OULAD não existe na máquina de quem roda os
    testes; o que se verifica aqui é o mecanismo, com um artefato
    montado em ``tmp_path``.
    """
    from dataclasses import replace

    bipartite = io.load_bipartite(artifact_roots, "synthetic_v1")
    projection = io.load_projection(artifact_roots, "synthetic_v1", "student_simple")

    replica = replace(
        bipartite,
        spec=replace(bipartite.spec, dataset="synthetic_v1_null0"),
        meta=Meta(
            producer="A-08",
            stats={"null_model": {"source_dataset": "synthetic_v1", "seed": 0}},
        ),
    )
    io.save_bipartite(replica, tmp_path)
    io.save_projection(
        replace(projection, source=replica.spec, meta=Meta(producer="A-04")), tmp_path
    )

    assert null_replicas_of([tmp_path], "synthetic_v1") == ["synthetic_v1_null0"]

    base = null_baseline([tmp_path], "synthetic_v1", "student_simple", 0.4666)
    assert base["n_replicas"] == 1
    assert base["replicas"] == ["synthetic_v1_null0"]
    assert base["verdict"] == "poucas réplicas"


def test_replica_sem_a_projecao_e_pulada_e_contada(tmp_path: Path, artifact_roots) -> None:
    """Inventar um zero rebaixaria a média do nulo e inflaria o z."""
    from dataclasses import replace

    bipartite = io.load_bipartite(artifact_roots, "synthetic_v1")
    replica = replace(
        bipartite,
        spec=replace(bipartite.spec, dataset="synthetic_v1_null9"),
        meta=Meta(producer="A-08", stats={"null_model": {"source_dataset": "synthetic_v1"}}),
    )
    io.save_bipartite(replica, tmp_path)

    base = null_baseline([tmp_path], "synthetic_v1", "student_simple", 0.4666)

    assert base["n_replicas"] == 0
    assert base["skipped"] == ["synthetic_v1_null9"]
    assert base["verdict"] == "sem réplicas"


# ---------------------------------------------------------------------
# B-06 — contra o desfecho histórico
# ---------------------------------------------------------------------


def test_desfecho_por_comunidade_cobre_todas(artifact_roots) -> None:
    """Uma linha por comunidade, com a distribuição dos quatro desfechos."""
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    outcomes = io.load_outcomes(artifact_roots, "synthetic_v1")

    rows = outcome_profile(partition, outcomes)
    assert len(rows) == partition.n_communities


def test_perfil_de_desfecho_traz_a_taxa_da_base_ao_lado(artifact_roots) -> None:
    """Critério de aceite: ver o excesso sobre a base sem cálculo adicional."""
    partition = io.load_partition(artifact_roots, "synthetic_v1", "louvain__student_simple")
    outcomes = io.load_outcomes(artifact_roots, "synthetic_v1")

    rows = outcome_profile(partition, outcomes)

    assert list(rows[0]) == list(OUTCOME_COLUMNS)
    for row in rows:
        assert row["n_labeled"] == row["size"], "toda a fixture tem desfecho"
        taxas = [row[f"rate_{r}"] for r in ("Distinction", "Pass", "Fail", "Withdrawn")]
        assert sum(taxas) == pytest.approx(1.0)
        # A taxa da base é a mesma em todas as linhas: é a referência.
        assert row["base_rate_Withdrawn"] == pytest.approx(rows[0]["base_rate_Withdrawn"])
        assert row["top_excess"] >= 0


def test_comunidade_que_concentra_withdrawn_fica_visivel() -> None:
    """O achado de gestão pedagógica, sem nenhum classificador."""
    partition = Partition(
        algorithm="louvain",
        projection_id="student_simple",
        membership={"S1": 0, "S2": 0, "S3": 1, "S4": 1},
        modularity=0.0,
        n_communities=2,
        runtime_s=0.0,
    )
    outcomes = Outcomes(
        final_result={"S1": "Withdrawn", "S2": "Withdrawn", "S3": "Pass", "S4": "Pass"}
    )

    rows = outcome_profile(partition, outcomes)

    assert rows[0]["rate_Withdrawn"] == pytest.approx(1.0)
    assert rows[0]["base_rate_Withdrawn"] == pytest.approx(0.5)
    assert rows[0]["top_excess_outcome"] == "Withdrawn"
    assert rows[0]["top_excess"] == pytest.approx(0.5)


def test_no_sem_desfecho_nao_entra_nas_taxas() -> None:
    """No OULAD nem todo aluno da projeção aparece em ``outcomes.csv``."""
    partition = Partition(
        algorithm="louvain",
        projection_id="student_simple",
        membership={"S1": 0, "S2": 0, "S3": 0},
        modularity=0.0,
        n_communities=1,
        runtime_s=0.0,
    )
    outcomes = Outcomes(final_result={"S1": "Pass", "S2": "Fail"})

    rows = outcome_profile(partition, outcomes)

    assert rows[0]["size"] == 3
    assert rows[0]["n_labeled"] == 2
    assert rows[0]["rate_Pass"] == pytest.approx(0.5)
    assert unknown_outcomes(partition, outcomes) == 1


def test_sem_grupo_plantado_o_perfil_de_desfecho_continua_valendo() -> None:
    """Caso OULAD: ``planted_group`` é ``None`` e nada quebra."""
    partition = Partition(
        algorithm="louvain",
        projection_id="student_simple",
        membership={"S1": 0, "S2": 1},
        modularity=0.0,
        n_communities=2,
        runtime_s=0.0,
    )
    outcomes = Outcomes(final_result={"S1": "Pass", "S2": "Fail"}, planted_group=None)

    assert outcomes.planted_group is None
    assert len(outcome_profile(partition, outcomes)) == 2


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------


def test_characterize_pela_cli_grava_profile(tmp_path: Path, capsys) -> None:
    from edugraph.__main__ import main

    code = main(["community", "characterize", "--root", "data/fixtures",
                 "--dataset", "synthetic_v1", "--partition", "louvain__student_simple",
                 "--out", str(tmp_path)])  # fmt: skip

    assert code == 0
    profile = tmp_path / "synthetic_v1" / "communities" / "louvain__student_simple" / "profile.csv"
    assert profile.exists()
    assert profile.read_text(encoding="utf-8").splitlines()[0].split(",") == list(PROFILE_COLUMNS)
    assert "disciplinas predominantes" in capsys.readouterr().out


def test_evaluate_pela_cli_reporta_nmi_e_desfecho(tmp_path: Path, capsys) -> None:
    from edugraph.__main__ import main

    code = main(["community", "evaluate", "--root", "data/fixtures",
                 "--dataset", "synthetic_v1", "--partition", "louvain__student_simple",
                 "--out", str(tmp_path)])  # fmt: skip
    saida = capsys.readouterr().out

    assert code == 0
    assert "NMI" in saida and "pureza" in saida
    assert "Withdrawn" in saida
    tabela = tmp_path / "tables" / "tab5-validacao-synthetic_v1-louvain__student_simple.csv"
    assert tabela.exists()
    assert tabela.read_text(encoding="utf-8").splitlines()[0].split(",") == list(OUTCOME_COLUMNS)
