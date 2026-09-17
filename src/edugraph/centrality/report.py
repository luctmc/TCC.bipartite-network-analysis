"""Relatório interno consolidado  ``[C]`` — spec C-07.

**Saída obrigatória** (briefing §6.2): "relatórios de uso exclusivamente
interno da instituição. O sistema não expõe dados a terceiros."

Consolida o que está em ``metrics/`` numa entrega que alguém da
coordenação consiga ler: as comunidades e o que as caracteriza, as
disciplinas críticas e o que elas significam, e o que **não** se pode
concluir a partir disso.
"""

from __future__ import annotations

from pathlib import Path


def build_internal_report(
    dataset: str, roots: list[Path], out: Path, *, fmt: str = "markdown"
) -> Path:
    """Gera o relatório interno a partir dos artefatos em disco.

    Notes
    -----
    A implementar em C-07. O relatório precisa trazer, além dos números,
    a seção de limitações: o que a centralidade estrutural **não** diz,
    para que o documento não seja lido como ranking de alunos. Ver
    docs/artigo/decisoes-metodologicas.md.
    """
    raise NotImplementedError("C-07: ver docs/specs/frente-c/C-07-relatorio-interno.md")


def figure_centrality_ranking(dataset: str, roots: list[Path], out: Path) -> Path:
    """Figura do ranking de disciplinas por intermediação (C-03/C-07)."""
    raise NotImplementedError("C-07: figura do ranking de disciplinas")
