"""Figuras da Frente B  ``[B]`` — spec B-07.

Duas figuras do capítulo 3: o grafo com cor por comunidade e a
distribuição de tamanhos. Ambas geradas a partir de artefatos em disco,
com um comando (briefing §9).
"""

from __future__ import annotations

from pathlib import Path

from edugraph.contracts.types import Partition, ProjectionBundle


def figure_communities(
    partition: Partition, projection: ProjectionBundle, out: Path, *, layout: str = "spring"
) -> Path:
    """Grafo com cor por comunidade.

    Em grafos grandes, a spec B-07 exige agregar (um nó por comunidade,
    área proporcional ao tamanho) em vez de desenhar milhares de pontos
    que não comunicam nada.
    """
    raise NotImplementedError("B-07: ver docs/specs/frente-b/B-07-figuras.md")


def figure_size_distribution(partitions: list[Partition], out: Path) -> Path:
    """Distribuição de tamanhos de comunidade, um painel por algoritmo."""
    raise NotImplementedError("B-07: distribuição de tamanhos")
