"""Resolução de caminhos: ``<root>/<dataset>/<camada>/<id>``.

O mesmo layout vale para ``data/fixtures`` e ``data/processed``. Trocar
de fonte é trocar a raiz — é isso que permite às Frentes B e C
trabalharem sobre fixtures no dia 0 e sobre o OULAD depois sem mudar uma
linha de código (ver plano de arquitetura, §4.3 e §5).

Várias raízes podem ser consultadas em ordem: a primeira que contiver o
artefato vence. Assim ``--root data/processed --root data/fixtures``
deixa a saída real sobrepor a fixture sem copiar nada.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Iterator
from pathlib import Path

from edugraph.contracts.errors import ArtifactNotFoundError

#: Variável de ambiente alternativa ao ``--root``, com raízes separadas
#: por ``os.pathsep`` (``;`` no Windows, ``:`` no Linux).
ROOTS_ENV_VAR = "EDUGRAPH_ROOTS"

#: Raízes padrão, na ordem de busca: saída real primeiro, fixture depois.
DEFAULT_ROOTS: tuple[str, ...] = ("data/processed", "data/fixtures")

BIPARTITE_DIR = "bipartite"
PROJECTIONS_DIR = "projections"
COMMUNITIES_DIR = "communities"
CENTRALITY_DIR = "centrality"
METRICS_DIR = "metrics"

NODES_FILE = "nodes.csv"
EDGES_FILE = "edges.csv"
OUTCOMES_FILE = "outcomes.csv"
META_FILE = "meta.json"
MEMBERSHIP_FILE = "membership.csv"
PROFILE_FILE = "profile.csv"


class ArtifactRoots:
    """Uma lista ordenada de raízes de artefatos.

    Exemplo
    -------
    >>> roots = ArtifactRoots(["data/processed", "data/fixtures"])
    >>> roots.find("synthetic_v1", "bipartite", "nodes.csv")  # doctest: +SKIP
    PosixPath('data/fixtures/synthetic_v1/bipartite/nodes.csv')
    """

    def __init__(self, roots: Iterable[str | Path] | None = None) -> None:
        resolved = [Path(r) for r in (roots if roots is not None else default_roots())]
        if not resolved:
            raise ValueError("ArtifactRoots precisa de pelo menos uma raiz")
        self._roots: tuple[Path, ...] = tuple(resolved)

    @property
    def roots(self) -> tuple[Path, ...]:
        return self._roots

    @property
    def primary(self) -> Path:
        """A raiz de escrita: a primeira da lista."""
        return self._roots[0]

    def __repr__(self) -> str:
        return f"ArtifactRoots({[str(r) for r in self._roots]!r})"

    def __iter__(self) -> Iterator[Path]:
        return iter(self._roots)

    # -- busca -------------------------------------------------------

    def find(self, dataset: str, *parts: str) -> Path:
        """Primeiro caminho existente entre as raízes, ou erro.

        Raises
        ------
        ArtifactNotFoundError
            Quando nenhuma raiz contém o artefato. A mensagem lista
            todas as raízes consultadas, porque o engano mais comum é
            esquecer o ``--root``.
        """
        candidates = [root / dataset / Path(*parts) for root in self._roots]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        tentativas = "\n  ".join(str(c) for c in candidates)
        raise ArtifactNotFoundError(
            f"artefato '{dataset}/{'/'.join(parts)}' não encontrado. Procurado em:\n  {tentativas}"
        )

    def find_optional(self, dataset: str, *parts: str) -> Path | None:
        """Como :meth:`find`, mas devolve ``None`` em vez de levantar."""
        try:
            return self.find(dataset, *parts)
        except ArtifactNotFoundError:
            return None

    def has(self, dataset: str, *parts: str) -> bool:
        return self.find_optional(dataset, *parts) is not None

    # -- listagem ----------------------------------------------------

    def datasets(self) -> list[str]:
        """Todos os datasets visíveis em qualquer raiz, sem repetição."""
        found: set[str] = set()
        for root in self._roots:
            if not root.is_dir():
                continue
            for entry in root.iterdir():
                if entry.is_dir() and not entry.name.startswith("."):
                    found.add(entry.name)
        return sorted(found)

    def projections(self, dataset: str) -> list[str]:
        """Ids de projeção disponíveis para o dataset."""
        return self._list_children(dataset, PROJECTIONS_DIR)

    def partitions(self, dataset: str) -> list[str]:
        """Ids de partição (``<algoritmo>__<projection_id>``)."""
        return self._list_children(dataset, COMMUNITIES_DIR)

    def centralities(self, dataset: str) -> list[str]:
        """Ids de projeção que possuem centralidades calculadas."""
        return self._list_children(dataset, CENTRALITY_DIR)

    def _list_children(self, dataset: str, layer: str) -> list[str]:
        found: set[str] = set()
        for root in self._roots:
            layer_dir = root / dataset / layer
            if not layer_dir.is_dir():
                continue
            for entry in layer_dir.iterdir():
                if entry.is_dir() and not entry.name.startswith("."):
                    found.add(entry.name)
        return sorted(found)


# ---------------------------------------------------------------------
# Construção das raízes
# ---------------------------------------------------------------------


def default_roots() -> list[Path]:
    """Raízes vindas de ``EDUGRAPH_ROOTS`` ou, na falta dela, as padrão."""
    env = os.environ.get(ROOTS_ENV_VAR, "").strip()
    if env:
        return [Path(p) for p in env.split(os.pathsep) if p.strip()]
    return [Path(p) for p in DEFAULT_ROOTS]


def as_roots(roots: ArtifactRoots | Iterable[str | Path] | str | Path | None) -> ArtifactRoots:
    """Normaliza o que o usuário passou na CLI para :class:`ArtifactRoots`."""
    if isinstance(roots, ArtifactRoots):
        return roots
    if roots is None:
        return ArtifactRoots()
    if isinstance(roots, str | Path):
        return ArtifactRoots([roots])
    return ArtifactRoots(roots)


# ---------------------------------------------------------------------
# Caminhos de escrita (sempre relativos a uma raiz única)
# ---------------------------------------------------------------------


def dataset_dir(root: str | Path, dataset: str) -> Path:
    return Path(root) / dataset


def bipartite_dir(root: str | Path, dataset: str) -> Path:
    return dataset_dir(root, dataset) / BIPARTITE_DIR


def projection_dir(root: str | Path, dataset: str, projection_id: str) -> Path:
    return dataset_dir(root, dataset) / PROJECTIONS_DIR / projection_id


def community_dir(root: str | Path, dataset: str, artifact_id: str) -> Path:
    return dataset_dir(root, dataset) / COMMUNITIES_DIR / artifact_id


def centrality_dir(root: str | Path, dataset: str, projection_id: str) -> Path:
    return dataset_dir(root, dataset) / CENTRALITY_DIR / projection_id


def metrics_dir(root: str | Path, dataset: str) -> Path:
    return dataset_dir(root, dataset) / METRICS_DIR


def ensure_dir(path: Path) -> Path:
    """Cria o diretório (e os pais) e o devolve."""
    path.mkdir(parents=True, exist_ok=True)
    return path
