"""Validadores sobre todo artefato da raiz em teste  ``[T]``.

Estes são **os mesmos testes** que rodam hoje sobre ``data/fixtures`` e
amanhã sobre o OULAD em ``data/processed``. Quando a Frente A entregar a
projeção de verdade, B e C não mudam uma linha de código — e é este
arquivo que prova isso (briefing §4.4).
"""

from __future__ import annotations

import pytest

from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.paths import ArtifactRoots
from edugraph.contracts.types import (
    BipartiteBundle,
    BipartiteSpec,
    CentralityResult,
    Partition,
    ProjectionSpec,
)
from edugraph.contracts.validate import (
    validate_centrality,
    validate_dataset,
    validate_partition,
    validate_projection,
)


def test_ha_algo_para_validar(datasets: list[str]) -> None:
    """A raiz em teste não está vazia — senão a suíte passaria à toa."""
    assert datasets, "nenhum dataset sob a raiz em teste. Rode 'python scripts/make_fixtures.py'."


def test_todo_dataset_passa_nos_validadores(
    artifact_roots: ArtifactRoots, datasets: list[str]
) -> None:
    """Cada artefato encontrado satisfaz os invariantes da §4.4 do plano."""
    for dataset in datasets:
        checked = validate_dataset(artifact_roots, dataset)
        assert checked, f"dataset '{dataset}' não tem artefato nenhum"


@pytest.mark.dataset("synthetic_v1")
def test_particao_cobre_exatamente_os_nos_da_projecao(
    artifact_roots: ArtifactRoots,
) -> None:
    """Partição e projeção falam do mesmo conjunto de nós."""
    for artifact_id in artifact_roots.partitions("synthetic_v1"):
        partition = io.load_partition(artifact_roots, "synthetic_v1", artifact_id)
        projection = io.load_projection(artifact_roots, "synthetic_v1", partition.projection_id)
        validate_partition(partition, projection)


@pytest.mark.dataset("synthetic_v1")
def test_centralidade_cobre_exatamente_os_nos_da_projecao(
    artifact_roots: ArtifactRoots,
) -> None:
    """Centralidade e projeção falam do mesmo conjunto de nós."""
    for projection_id in artifact_roots.centralities("synthetic_v1"):
        projection = io.load_projection(artifact_roots, "synthetic_v1", projection_id)
        directory = artifact_roots.find("synthetic_v1", "centrality", projection_id)
        for meta_file in sorted(directory.glob("*.meta.json")):
            metric = meta_file.name.removesuffix(".meta.json")
            result = io.load_centrality(artifact_roots, "synthetic_v1", projection_id, metric)
            validate_centrality(result, projection)


# ---------------------------------------------------------------------
# Os validadores realmente recusam o que deveriam recusar
# ---------------------------------------------------------------------


def test_bipartido_com_aresta_do_mesmo_lado_e_recusado() -> None:
    """Aresta aluno-aluno dentro do bipartido é erro de contrato."""
    import networkx as nx

    graph = nx.Graph()
    graph.add_node("S1", kind="student", label="1")
    graph.add_node("S2", kind="student", label="2")
    graph.add_node("DA", kind="discipline", label="A")
    graph.add_edge("S1", "S2", weight=1.0)

    bundle = BipartiteBundle(graph=graph, spec=BipartiteSpec(dataset="x"))
    with pytest.raises(ContractError, match="student-discipline"):
        from edugraph.contracts.validate import validate_bipartite

        validate_bipartite(bundle)


def test_projecao_com_peso_zero_e_recusada() -> None:
    """Peso precisa ser finito e positivo."""
    import networkx as nx

    from edugraph.contracts.types import ProjectionBundle

    graph = nx.Graph()
    graph.add_node("S1", kind="student", label="1")
    graph.add_node("S2", kind="student", label="2")
    graph.add_edge("S1", "S2", weight=0.0)

    bundle = ProjectionBundle(
        graph=graph,
        spec=ProjectionSpec(side="student", weighting="simple"),
        source=BipartiteSpec(dataset="x"),
    )
    with pytest.raises(ContractError, match="positivo"):
        validate_projection(bundle)


def test_particao_com_ids_esparsos_e_recusada() -> None:
    """Ids de comunidade têm de ser densos ``0..k-1``."""
    partition = Partition(
        algorithm="louvain",
        projection_id="student_simple",
        membership={"S1": 0, "S2": 7},
        modularity=0.3,
        n_communities=2,
        runtime_s=0.1,
    )
    with pytest.raises(ContractError, match="densos"):
        validate_partition(partition)


def test_modularidade_fora_da_faixa_e_recusada() -> None:
    """Q vive em [-0,5, 1]."""
    partition = Partition(
        algorithm="louvain",
        projection_id="student_simple",
        membership={"S1": 0, "S2": 1},
        modularity=1.7,
        n_communities=2,
        runtime_s=0.1,
    )
    with pytest.raises(ContractError, match="faixa"):
        validate_partition(partition)


def test_autovetor_negativo_e_recusado() -> None:
    """Perron-Frobenius: componente negativa é sinal de erro de sinal."""
    result = CentralityResult(
        projection_id="student_simple",
        metric="eigenvector",
        scores={"S1": 0.5, "S2": -0.5},
    )
    with pytest.raises(ContractError, match="negativa"):
        validate_centrality(result)


def test_grau_normalizado_fora_de_zero_um_e_recusado() -> None:
    """Grau normalizado acima de 1 denuncia normalização errada."""
    result = CentralityResult(
        projection_id="student_simple",
        metric="degree",
        scores={"S1": 1.4},
        params={"normalized": True},
    )
    with pytest.raises(ContractError, match=r"\[0, 1\]"):
        validate_centrality(result)
