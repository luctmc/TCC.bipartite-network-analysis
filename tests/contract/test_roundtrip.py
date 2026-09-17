"""Round-trip e escrita canônica  ``[T]`` — ADR-0002 e ADR-0011.

Escrever → ler → escrever precisa preservar o grafo, a especificação e
os metadados, **e** produzir o mesmo arquivo byte a byte. Sem isso,
fixtures versionadas geram diff do nada e ninguém consegue distinguir
"mudou o dado" de "mudou o formatador".
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pytest

from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.paths import ArtifactRoots
from edugraph.contracts.types import (
    BipartiteBundle,
    BipartiteSpec,
    CentralityResult,
    Meta,
    Outcomes,
    Partition,
    ProjectionBundle,
    ProjectionSpec,
)


@pytest.mark.dataset("tiny_v1")
def test_bipartido_sobrevive_ao_round_trip(artifact_roots: ArtifactRoots, tmp_path: Path) -> None:
    original = io.load_bipartite(artifact_roots, "tiny_v1")
    io.save_bipartite(original, tmp_path)
    again = io.load_bipartite([tmp_path], "tiny_v1")

    assert nx.utils.graphs_equal(original.graph, again.graph)
    assert original.spec == again.spec
    assert original.meta.producer == again.meta.producer


@pytest.mark.dataset("tiny_v1")
def test_projecao_sobrevive_ao_round_trip(artifact_roots: ArtifactRoots, tmp_path: Path) -> None:
    for projection_id in artifact_roots.projections("tiny_v1"):
        original = io.load_projection(artifact_roots, "tiny_v1", projection_id)
        io.save_projection(original, tmp_path)
        again = io.load_projection([tmp_path], "tiny_v1", projection_id)

        assert nx.utils.graphs_equal(original.graph, again.graph)
        assert original.spec == again.spec
        assert original.source == again.source


@pytest.mark.dataset("tiny_v1")
def test_escrita_e_byte_a_byte_estavel(artifact_roots: ArtifactRoots, tmp_path: Path) -> None:
    """Gravar duas vezes o mesmo bundle dá exatamente o mesmo arquivo."""
    bundle = io.load_bipartite(artifact_roots, "tiny_v1")

    first = tmp_path / "a"
    second = tmp_path / "b"
    io.save_bipartite(bundle, first)
    io.save_bipartite(bundle, second)

    for name in ("nodes.csv", "edges.csv", "meta.json"):
        left = (first / "tiny_v1" / "bipartite" / name).read_bytes()
        right = (second / "tiny_v1" / "bipartite" / name).read_bytes()
        assert left == right, f"{name} não é determinístico"


@pytest.mark.dataset("tiny_v1")
def test_reescrita_nao_muda_a_fixture(artifact_roots: ArtifactRoots, tmp_path: Path) -> None:
    """Ler a fixture e regravá-la reproduz os mesmos bytes.

    É este teste que garante que ``git status`` fica limpo depois de um
    round-trip — o que, por sua vez, é o que faz de um diff em
    ``data/fixtures/`` um sinal confiável.
    """
    bundle = io.load_bipartite(artifact_roots, "tiny_v1")
    io.save_bipartite(bundle, tmp_path)

    for name in ("nodes.csv", "edges.csv"):
        original = artifact_roots.find("tiny_v1", "bipartite", name).read_bytes()
        rewritten = (tmp_path / "tiny_v1" / "bipartite" / name).read_bytes()
        assert original == rewritten, f"{name} mudou ao ser reescrito"


def test_particao_sobrevive_ao_round_trip(tmp_path: Path) -> None:
    partition = Partition(
        algorithm="louvain",
        projection_id="student_simple",
        membership={"S1": 0, "S2": 0, "S3": 1},
        modularity=0.42,
        n_communities=2,
        runtime_s=1.5,
        params={"seed": 42, "resolution": 1.0},
        status="ok",
        meta=Meta(producer="teste"),
    )
    io.save_partition(partition, tmp_path, "x")
    again = io.load_partition([tmp_path], "x", partition.artifact_id)

    assert again.membership == partition.membership
    assert again.modularity == pytest.approx(partition.modularity)
    assert again.params == partition.params
    assert again.status == partition.status


def test_centralidade_sobrevive_ao_round_trip(tmp_path: Path) -> None:
    result = CentralityResult(
        projection_id="student_simple",
        metric="eigenvector",
        scores={"S1": 0.1234567890123456, "S2": 0.7},
        params={"max_iter": 1000, "tol": 1e-8},
        runtime_s=0.25,
        converged=False,
    )
    io.save_centrality(result, tmp_path, "x")
    again = io.load_centrality([tmp_path], "x", "student_simple", "eigenvector")

    assert again.scores == result.scores, "float perdeu precisão no round-trip"
    assert again.converged is False
    assert again.params == result.params


def test_outcomes_sobrevive_ao_round_trip(tmp_path: Path) -> None:
    outcomes = Outcomes(
        final_result={"S1": "Pass", "S2": "Withdrawn"},
        planted_group={"S1": 0, "S2": 1},
    )
    io.save_outcomes(outcomes, tmp_path, "x")
    again = io.load_outcomes([tmp_path], "x")

    assert again.final_result == outcomes.final_result
    assert again.planted_group == outcomes.planted_group


def test_metrics_e_idempotente_por_chave(tmp_path: Path) -> None:
    """Rodar de novo atualiza a linha em vez de duplicá-la."""
    linha = {"dataset": "x", "projection_id": "student_simple", "algorithm": "louvain", "q": 0.4}
    io.append_metrics_rows(tmp_path, "x", "communities", [linha], key=["dataset", "algorithm"])
    io.append_metrics_rows(
        tmp_path, "x", "communities", [{**linha, "q": 0.5}], key=["dataset", "algorithm"]
    )

    rows = io.load_metrics([tmp_path], "x", "communities")
    assert len(rows) == 1
    assert rows[0]["q"] == "0.5"


def test_schema_version_incompativel_e_recusada(tmp_path: Path) -> None:
    """Artefato de versão antiga falha na leitura, com mensagem clara."""
    graph = nx.Graph()
    graph.add_node("S1", kind="student", label="1")
    graph.add_node("DA", kind="discipline", label="A")
    graph.add_edge("S1", "DA", weight=1.0)
    io.save_bipartite(BipartiteBundle(graph=graph, spec=BipartiteSpec(dataset="x")), tmp_path)

    meta_path = tmp_path / "x" / "bipartite" / "meta.json"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace('"1.0"', '"0.9"'), encoding="utf-8"
    )

    with pytest.raises(ContractError, match="schema_version"):
        io.load_bipartite([tmp_path], "x")


def test_artefato_ausente_lista_as_raizes_consultadas(tmp_path: Path) -> None:
    """A mensagem de erro diz onde procurou — o engano mais comum é o --root."""
    from edugraph.contracts.errors import ArtifactNotFoundError

    with pytest.raises(ArtifactNotFoundError) as excinfo:
        io.load_bipartite([tmp_path / "a", tmp_path / "b"], "inexistente")

    message = str(excinfo.value)
    assert "inexistente" in message
    assert str(tmp_path / "a") in message
    assert str(tmp_path / "b") in message


def test_primeira_raiz_com_o_artefato_vence(tmp_path: Path) -> None:
    """``--root data/processed --root data/fixtures`` sobrepõe sem copiar."""
    spec = ProjectionSpec(side="student", weighting="simple")
    source = BipartiteSpec(dataset="x")

    for root, weight in ((tmp_path / "baixa", 1.0), (tmp_path / "alta", 9.0)):
        graph = nx.Graph()
        graph.add_node("S1", kind="student", label="1")
        graph.add_node("S2", kind="student", label="2")
        graph.add_edge("S1", "S2", weight=weight)
        io.save_projection(ProjectionBundle(graph=graph, spec=spec, source=source), root)

    bundle = io.load_projection([tmp_path / "alta", tmp_path / "baixa"], "x", "student_simple")
    assert bundle.graph["S1"]["S2"]["weight"] == 9.0
