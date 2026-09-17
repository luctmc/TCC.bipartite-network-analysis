"""Fronteiras de import entre as frentes  ``[T]`` — ADR-0003.

A seção 4.3 do briefing pede que nenhuma frente importe o módulo de
outra. Aqui isso deixa de ser convenção e vira teste: o código-fonte é
analisado com :mod:`ast` e qualquer import cruzado quebra a CI.

Dois arquivos são isentos, e só eles:

``edugraph/__main__.py``
    A raiz de composição. Monta os grupos de CLI e o comando ``run``.
``edugraph/contracts/registry.py``
    Importa os módulos de estágio por nome para povoar o registro.

Se um terceiro arquivo precisar entrar nesta lista, isso é sinal de que
a fronteira está sendo furada — e a discussão vira ADR, não exceção.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

#: Os subpacotes que não podem se conhecer.
FRONTS: frozenset[str] = frozenset({"data", "community", "centrality", "api"})

#: Caminhos (relativos a ``src/``) isentos da regra.
EXEMPT: frozenset[str] = frozenset(
    {
        "edugraph/__main__.py",
        "edugraph/contracts/registry.py",
    }
)


def _source_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / "src" / "edugraph").rglob("*.py"))


def _front_of(path: Path, repo_root: Path) -> str | None:
    """A qual frente o arquivo pertence, se a alguma."""
    relative = path.relative_to(repo_root / "src")
    parts = relative.parts
    if len(parts) >= 2 and parts[0] == "edugraph" and parts[1] in FRONTS:
        return parts[1]
    return None


def _imported_fronts(path: Path) -> set[str]:
    """Frentes de ``edugraph`` importadas por este arquivo."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found |= _front_in_module(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found |= _front_in_module(node.module)
    return found


def _front_in_module(module: str) -> set[str]:
    parts = module.split(".")
    if len(parts) >= 2 and parts[0] == "edugraph" and parts[1] in FRONTS:
        return {parts[1]}
    return set()


def test_frentes_nao_se_importam(repo_root: Path) -> None:
    """Nenhum módulo de frente importa outra frente."""
    violations: list[str] = []

    for path in _source_files(repo_root):
        relative = path.relative_to(repo_root / "src").as_posix()
        if relative in EXEMPT:
            continue

        own = _front_of(path, repo_root)
        if own is None:
            continue

        crossed = _imported_fronts(path) - {own}
        for other in sorted(crossed):
            violations.append(f"{relative} importa edugraph.{other}")

    assert not violations, (
        "fronteira entre frentes violada (ADR-0003):\n  "
        + "\n  ".join(violations)
        + "\n\nA comunicação entre frentes acontece por artefatos em disco, "
        "nunca por import. Ver docs/adr/ADR-0003-pacote-unico-fronteira-testada.md."
    )


def test_contracts_nao_importa_frente(repo_root: Path) -> None:
    """``contracts`` é a fundação: não pode depender de ninguém acima dele.

    A única exceção é ``registry.load_builtin_implementations``, que
    importa os estágios por nome, dentro da função, para povoar o
    registro — e está em :data:`EXEMPT`.
    """
    violations: list[str] = []

    for path in sorted((repo_root / "src" / "edugraph" / "contracts").rglob("*.py")):
        relative = path.relative_to(repo_root / "src").as_posix()
        if relative in EXEMPT:
            continue
        crossed = _imported_fronts(path)
        for other in sorted(crossed):
            violations.append(f"{relative} importa edugraph.{other}")

    assert not violations, "contracts/ não pode importar frente nenhuma:\n  " + "\n  ".join(
        violations
    )


def test_apenas_dois_arquivos_isentos(repo_root: Path) -> None:
    """A lista de isenções não cresceu sem que alguém percebesse."""
    for relative in EXEMPT:
        assert (repo_root / "src" / relative).exists(), (
            f"isenção aponta para arquivo inexistente: {relative}"
        )
    assert len(EXEMPT) == 2, (
        "a lista de isenções da fronteira mudou. Acrescentar um arquivo aqui "
        "é decisão de arquitetura e exige ADR — ver ADR-0003."
    )


@pytest.mark.parametrize("front", sorted(FRONTS))
def test_frente_existe(repo_root: Path, front: str) -> None:
    """As quatro frentes existem como subpacotes."""
    assert (repo_root / "src" / "edugraph" / front / "__init__.py").exists()
