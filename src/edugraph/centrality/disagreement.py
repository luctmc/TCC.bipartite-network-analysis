"""Discordância entre métricas de centralidade  ``[C]`` — spec C-03.

Onde as três métricas discordam é onde há o que discutir: um nó no topo
da intermediação mas não do grau é ponte sem ser popular — exatamente o
perfil de uma disciplina-gargalo que poucos cursam mas que conecta áreas.
"""

from __future__ import annotations

from edugraph.contracts.types import CentralityResult


def disagreement(results: dict[str, CentralityResult], *, top_n: int = 5) -> dict[str, list[str]]:
    """Os quatro conjuntos de discordância entre as três métricas.

    Returns
    -------
    dict
        ``only_degree``, ``only_betweenness``, ``only_eigenvector`` e
        ``all_three`` — nós no top-N de apenas uma métrica, e nós no
        top-N das três. Listas ordenadas, para a tabela ser estável.
    """
    raise NotImplementedError("C-03: ver docs/specs/frente-c/C-03-disciplinas-criticas.md")


def rank_correlation(left: CentralityResult, right: CentralityResult) -> float:
    """Correlação de Spearman entre dois rankings.

    Quantifica em um número o que os conjuntos de discordância mostram
    caso a caso. Estatística descritiva sobre rankings conhecidos — não
    é modelo nem predição.
    """
    raise NotImplementedError("C-03: correlação entre rankings")
