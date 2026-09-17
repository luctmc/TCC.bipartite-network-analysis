"""Rótulos históricos fora do grafo  ``[T]`` — ADR-0008.

Duas garantias, as duas verificáveis sem executar nada:

1. **Nenhum ``nodes.csv`` carrega desfecho, nota ou atributo
   demográfico.** Se um rótulo vazar para dentro do grafo, um algoritmo
   pode acabar usando-o como entrada sem que ninguém perceba — e o
   trabalho inteiro perde o diferencial declarado.
2. **Só ``evaluate.py`` lê ``outcomes.csv``.** A validação a posteriori
   é a única etapa autorizada a olhar o desfecho (briefing §2).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from edugraph.contracts.paths import ArtifactRoots
from edugraph.contracts.validate import validate_node_file

#: Arquivos autorizados a ler os rótulos históricos.
ALLOWED_OUTCOME_READERS: frozenset[str] = frozenset(
    {
        "edugraph/community/evaluate.py",
        "edugraph/centrality/evaluate.py",
        "edugraph/contracts/io.py",
        "edugraph/contracts/validate.py",
    }
)

#: A função cuja chamada indica leitura de rótulo.
OUTCOME_READER = "load_outcomes"


def test_nodes_csv_nunca_contem_rotulo(artifact_roots: ArtifactRoots) -> None:
    """Varre todo ``nodes.csv`` sob as raízes em teste."""
    checked = 0
    for dataset in artifact_roots.datasets():
        bipartite_nodes = artifact_roots.find_optional(dataset, "bipartite", "nodes.csv")
        if bipartite_nodes is not None:
            validate_node_file(bipartite_nodes)
            checked += 1
        for projection_id in artifact_roots.projections(dataset):
            path = artifact_roots.find(dataset, "projections", projection_id, "nodes.csv")
            validate_node_file(path)
            checked += 1

    assert checked > 0, "nenhum nodes.csv encontrado: a raiz em teste está vazia?"


def test_apenas_evaluate_le_outcomes(repo_root: Path) -> None:
    """Nenhum módulo fora da lista chama ``load_outcomes``."""
    violations: list[str] = []

    for path in sorted((repo_root / "src" / "edugraph").rglob("*.py")):
        relative = path.relative_to(repo_root / "src").as_posix()
        if relative in ALLOWED_OUTCOME_READERS:
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            called = None
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    called = node.func.attr
            if called == OUTCOME_READER:
                violations.append(f"{relative}:{node.lineno}")

            if isinstance(node, ast.ImportFrom) and any(
                alias.name == OUTCOME_READER for alias in node.names
            ):
                violations.append(f"{relative}:{node.lineno} (import)")

    assert not violations, (
        "rótulo histórico lido fora da validação a posteriori (ADR-0008):\n  "
        + "\n  ".join(violations)
        + f"\n\nAutorizados: {sorted(ALLOWED_OUTCOME_READERS)}"
    )


@pytest.mark.dataset("tiny_v1")
def test_outcomes_existe_e_e_separado(artifact_roots: ArtifactRoots) -> None:
    """``outcomes.csv`` vive ao lado do grafo, não dentro dele."""
    outcomes = artifact_roots.find("tiny_v1", "bipartite", "outcomes.csv")
    nodes = artifact_roots.find("tiny_v1", "bipartite", "nodes.csv")

    assert outcomes.exists() and nodes.exists()
    assert outcomes != nodes

    header = nodes.read_text(encoding="utf-8").splitlines()[0]
    assert header == "id,kind,label", (
        f"nodes.csv mudou de esquema: {header!r}. "
        "Acrescentar coluna aqui é mudança de contrato (ADR-0002)."
    )
