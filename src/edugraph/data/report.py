"""Figuras e tabelas da Frente A  ``[A]`` — spec A-07.

Requisito que vem do artigo, não do software (briefing §9): refazer uma
figura na semana da entrega tem que ser um comando, não arqueologia.
Toda figura daqui é gerada a partir de artefatos em disco, nunca de
estado em memória de uma execução anterior.
"""

from __future__ import annotations

from pathlib import Path

from edugraph.contracts.types import BipartiteBundle, ProjectionBundle


def table_dataset_stats(bundle: BipartiteBundle) -> dict[str, float]:
    """Tabela de estatísticas descritivas do bipartido (capítulo 3)."""
    raise NotImplementedError("A-07: ver docs/specs/frente-a/A-07-estatisticas-bipartido.md")


def figure_bipartite(bundle: BipartiteBundle, out: Path) -> Path:
    """Figura do bipartido, com os dois lados em colunas.

    Em grafos grandes, desenhar todos os nós não comunica nada: a spec
    A-07 exige amostrar ou agregar, e dizer na legenda o que foi feito.
    """
    raise NotImplementedError("A-07: figura do grafo bipartido")


def figure_weight_distributions(
    simple: ProjectionBundle, resource_allocation: ProjectionBundle, out: Path
) -> Path:
    """Figura "simples × ponderada": os dois histogramas lado a lado (A-05)."""
    raise NotImplementedError("A-05: figura da comparação de ponderações")
