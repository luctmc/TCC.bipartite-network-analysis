"""Configuração comum da suíte  ``[T]``.

A suíte inteira aceita ``--artifacts-root`` (ou a variável de ambiente
``EDUGRAPH_ROOTS``). São os **mesmos testes** que rodam hoje sobre
``data/fixtures`` e amanhã sobre o OULAD em ``data/processed`` — é essa
propriedade que sustenta o paralelismo entre as frentes::

    pytest                                          # sobre as fixtures
    pytest --artifacts-root data/processed          # sobre o OULAD
    pytest --artifacts-root data/processed --artifacts-root data/fixtures

Testes que dependem de um dataset específico declaram isso com
``@pytest.mark.dataset("synthetic_v1")`` e são **pulados**, não
quebrados, quando a raiz em uso não o contém.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from edugraph.contracts import io
from edugraph.contracts.paths import ArtifactRoots

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEST_ROOT = REPO_ROOT / "data" / "fixtures"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--artifacts-root",
        action="append",
        default=[],
        dest="artifacts_root",
        help=(
            "raiz de artefatos a testar; repita para consultar várias em ordem. "
            "Padrão: data/fixtures."
        ),
    )


@pytest.fixture(scope="session")
def artifact_roots(request: pytest.FixtureRequest) -> ArtifactRoots:
    """Raízes sob teste. Padrão: as fixtures versionadas do repositório."""
    given = request.config.getoption("artifacts_root")
    return ArtifactRoots(given or [DEFAULT_TEST_ROOT])


@pytest.fixture(scope="session")
def datasets(artifact_roots: ArtifactRoots) -> list[str]:
    """Todos os datasets visíveis sob as raízes em teste."""
    return artifact_roots.datasets()


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Pula os testes cujo dataset não existe sob a raiz em uso."""
    roots = ArtifactRoots(config.getoption("artifacts_root") or [DEFAULT_TEST_ROOT])
    available = set(roots.datasets())

    for item in items:
        marker = item.get_closest_marker("dataset")
        if marker is None:
            continue
        required = str(marker.args[0])
        if required not in available:
            item.add_marker(
                pytest.mark.skip(
                    reason=(f"dataset '{required}' ausente em {', '.join(str(r) for r in roots)}")
                )
            )


# ---------------------------------------------------------------------
# Atalhos para os datasets usados com mais frequência
# ---------------------------------------------------------------------


@pytest.fixture
def tiny_bipartite(artifact_roots: ArtifactRoots):
    """Bipartido de ``tiny_v1`` — 6 alunos, 3 disciplinas, conferível à mão."""
    return io.load_bipartite(artifact_roots, "tiny_v1")


@pytest.fixture
def tiny_projection(artifact_roots: ArtifactRoots):
    """Fábrica: ``tiny_projection("student_simple")``."""

    def load(projection_id: str):
        return io.load_projection(artifact_roots, "tiny_v1", projection_id)

    return load


@pytest.fixture
def tiny_expected() -> Path:
    """Diretório dos valores derivados à mão de ``tiny_v1``."""
    return DEFAULT_TEST_ROOT / "tiny_v1" / "expected"


@pytest.fixture
def synthetic_projection(artifact_roots: ArtifactRoots):
    """Fábrica: ``synthetic_projection("student_simple")``."""

    def load(projection_id: str):
        return io.load_projection(artifact_roots, "synthetic_v1", projection_id)

    return load


@pytest.fixture
def repo_root() -> Path:
    """Raiz do repositório — usada pelos testes que analisam o código-fonte."""
    return REPO_ROOT
