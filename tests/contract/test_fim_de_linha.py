"""Fim de linha LF em todo artefato  ``[T]`` — ADR-0011.

A escrita canônica promete que o mesmo artefato tem os mesmos bytes
independentemente de quem o gerou. No Windows isso não é automático:
``Path.write_text`` sem ``newline`` traduz ``\\n`` para ``\\r\\n``, e a
promessa se perde silenciosamente — os testes de round-trip continuam
passando, porque comparam o que o próprio sistema escreveu.

O sintoma só apareceria no grupo: regenerar as fixtures no Windows
passaria a acusar diff na árvore inteira, e o sinal "diff em
`data/fixtures/` significa mudança real" deixaria de valer.

Estes testes travam a regra nos dois lados: nos artefatos já gravados e
na escrita nova.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pytest

from edugraph.contracts import io
from edugraph.contracts.paths import ArtifactRoots
from edugraph.contracts.types import (
    BipartiteBundle,
    BipartiteSpec,
    CentralityResult,
    Outcomes,
    Partition,
)

#: Extensões de texto que o contrato governa.
TEXT_SUFFIXES = {".csv", ".json", ".md"}


def _crlf_files(root: Path) -> list[str]:
    encontrados = []
    for path in sorted(root.rglob("*")):
        if not (path.is_file() and path.suffix in TEXT_SUFFIXES):
            continue
        if b"\r\n" in path.read_bytes():
            encontrados.append(str(path.relative_to(root)))
    return encontrados


def test_fixtures_versionadas_nao_tem_crlf(artifact_roots: ArtifactRoots) -> None:
    """Nenhum artefato sob a raiz em teste usa CRLF."""
    violations: list[str] = []
    for root in artifact_roots:
        if root.is_dir():
            violations.extend(f"{root}/{p}" for p in _crlf_files(root))

    assert not violations, (
        "artefato com CRLF (ADR-0011: escrita canônica é LF):\n  "
        + "\n  ".join(violations)
        + '\n\nCausa provável: uma escrita de texto sem newline="\\n". '
        "Ver contracts.io.NEWLINE e .gitattributes."
    )


def test_escrita_de_artefato_usa_lf(tmp_path: Path) -> None:
    """Grava um de cada tipo e confere os bytes.

    É o teste que pega a regressão **na origem**, e não só nas fixtures
    já commitadas: se alguém acrescentar uma escrita nova sem
    ``newline``, ela falha aqui.
    """
    graph = nx.Graph()
    graph.add_node("S1", kind="student", label="1")
    graph.add_node("DA", kind="discipline", label="A")
    graph.add_edge("S1", "DA", weight=80.0)

    io.save_bipartite(BipartiteBundle(graph=graph, spec=BipartiteSpec(dataset="x")), tmp_path)
    io.save_outcomes(Outcomes(final_result={"S1": "Pass"}), tmp_path, "x")
    io.save_partition(
        Partition(
            algorithm="louvain",
            projection_id="student_simple",
            membership={"S1": 0},
            modularity=0.0,
            n_communities=1,
            runtime_s=0.0,
        ),
        tmp_path,
        "x",
    )
    io.save_centrality(
        CentralityResult(projection_id="student_simple", metric="degree", scores={"S1": 0.0}),
        tmp_path,
        "x",
    )
    io.append_metrics_rows(
        tmp_path, "x", "communities", [{"dataset": "x", "q": 0.1}], key=["dataset"]
    )
    io.save_profile([{"community": 0, "size": 1}], tmp_path, "x", "louvain__student_simple")

    violations = _crlf_files(tmp_path)
    assert not violations, f"escrita nova produziu CRLF: {violations}"


@pytest.mark.dataset("tiny_v1")
def test_meta_json_termina_em_nova_linha(artifact_roots: ArtifactRoots) -> None:
    """Arquivo de texto termina com ``\\n``, como manda o costume POSIX.

    Sem isso, o diff de um `meta.json` alterado mostra a última linha
    como removida e reinserida, poluindo a revisão.
    """
    meta = artifact_roots.find("tiny_v1", "bipartite", "meta.json")
    conteudo = meta.read_bytes()
    assert conteudo.endswith(b"\n")
    assert not conteudo.endswith(b"\r\n")
