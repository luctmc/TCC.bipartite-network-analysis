"""A restrição inegociável, como teste  ``[T]`` — briefing §2.

"Nenhum componente do sistema pode usar IA, aprendizado de máquina ou
qualquer modelo que dependa de treinamento com dados rotulados." Foi
exigência explícita do orientador e é o diferencial declarado do
trabalho.

Uma regra que vive só na cabeça de três pessoas sobrevive até a primeira
semana de pressa. Aqui ela é uma varredura do código e das dependências
declaradas: importar ``sklearn`` para um "só pra comparar" quebra a CI
antes de virar parágrafo no artigo que não se sustenta na banca.
"""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

#: Bibliotecas de ML e de embeddings de grafo. A lista cobre o que a
#: seção 2 do briefing proíbe nominalmente, mais os vizinhos óbvios.
FORBIDDEN_PACKAGES: frozenset[str] = frozenset(
    {
        "sklearn",
        "scikit_learn",
        "tensorflow",
        "keras",
        "torch",
        "pytorch_lightning",
        "xgboost",
        "lightgbm",
        "catboost",
        "statsmodels",
        "node2vec",
        "gensim",
        "karateclub",
        "stellargraph",
        "dgl",
        "torch_geometric",
        "transformers",
    }
)

#: Nomes que denunciam clustering fora de detecção de comunidades.
FORBIDDEN_NAMES: frozenset[str] = frozenset(
    {"KMeans", "DBSCAN", "AgglomerativeClustering", "SpectralClustering", "Node2Vec"}
)


def _python_files(repo_root: Path) -> list[Path]:
    """Código do projeto: o que roda, não o que documenta."""
    return sorted(
        [
            *(repo_root / "src").rglob("*.py"),
            *(repo_root / "scripts").rglob("*.py"),
            *(repo_root / "tests").rglob("*.py"),
        ]
    )


def test_nenhum_import_de_ml(repo_root: Path) -> None:
    """Nenhum módulo importa biblioteca de aprendizado de máquina."""
    violations: list[str] = []

    for path in _python_files(repo_root):
        if path.name == "test_no_ml.py":  # este arquivo cita os nomes
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative = path.relative_to(repo_root).as_posix()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in FORBIDDEN_PACKAGES:
                        violations.append(f"{relative}:{node.lineno} import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in FORBIDDEN_PACKAGES:
                    violations.append(f"{relative}:{node.lineno} from {node.module}")
                for alias in node.names:
                    if alias.name in FORBIDDEN_NAMES:
                        violations.append(
                            f"{relative}:{node.lineno} from {node.module} import {alias.name}"
                        )

    assert not violations, (
        "restrição inegociável violada (briefing §2 — sem IA/ML):\n  "
        + "\n  ".join(violations)
        + "\n\nToda inferência precisa ser determinística e rastreável até a "
        "estrutura do grafo. Ver docs/artigo/decisoes-metodologicas.md."
    )


def test_dependencias_declaradas_sao_limpas(repo_root: Path) -> None:
    """``pyproject.toml`` não declara dependência de ML."""
    with (repo_root / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    declared: list[str] = list(pyproject["project"].get("dependencies", []))
    for extra in pyproject["project"].get("optional-dependencies", {}).values():
        declared.extend(extra)

    violations = [
        dep
        for dep in declared
        if dep.split("[")[0].split(">")[0].split("=")[0].split("<")[0].strip().lower()
        in {p.replace("_", "-") for p in FORBIDDEN_PACKAGES}
    ]
    assert not violations, f"dependência de ML declarada em pyproject.toml: {violations}"


def test_requirements_sao_limpos(repo_root: Path) -> None:
    """``requirements*.txt`` também."""
    violations: list[str] = []
    for name in ("requirements.txt", "requirements-dev.txt"):
        path = repo_root / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            package = line.split("==")[0].split(">=")[0].strip().lower()
            if package in {p.replace("_", "-") for p in FORBIDDEN_PACKAGES}:
                violations.append(f"{name}: {line}")
    assert not violations, f"dependência de ML em requirements: {violations}"
