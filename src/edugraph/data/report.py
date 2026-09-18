"""Figuras e tabelas da Frente A  ``[A]`` — spec A-07.

Requisito que vem do artigo, não do software (briefing §9): refazer uma
figura na semana da entrega tem que ser um comando, não arqueologia.
Toda figura daqui é gerada a partir de artefatos em disco, nunca de
estado em memória de uma execução anterior.
"""

from __future__ import annotations

import itertools
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
    simple: ProjectionBundle,
    resource_allocation: ProjectionBundle,
    out: Path,
    *,
    name: str | None = None,
    bins: int = 20,
) -> Path:
    """Figura "simples × ponderada": os dois histogramas lado a lado (A-05).

    É onde o efeito de Zhou et al. fica visível: a projeção simples
    concentra os pesos em poucos inteiros; a alocação de recursos os
    espalha, porque cada disciplina compartilhada contribui com
    ``1/grau`` e não com 1.

    Parameters
    ----------
    simple, resource_allocation
        As duas projeções do **mesmo lado** do mesmo bipartido.
    out
        Diretório de saída (``results/figures`` no artigo).
    name
        Nome do arquivo sem extensão. Padrão:
        ``fig3-ponderacoes-<dataset>-<lado>``.

    Returns
    -------
    Path
        O PNG gravado (o SVG sai ao lado, pelo :mod:`edugraph.reporting`).
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from edugraph.data.projection.compare import weight_distribution
    from edugraph.reporting.figures import FULL_WIDTH_IN, apply_style, save_figure

    if simple.spec.side != resource_allocation.spec.side:
        raise ValueError("as duas projeções precisam ser do mesmo lado")

    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(FULL_WIDTH_IN, 2.6), sharey=True)
    lado = "aluno↔aluno" if simple.spec.side == "student" else "disciplina↔disciplina"

    for ax, bundle, titulo in (
        (axes[0], simple, "Projeção simples"),
        (axes[1], resource_allocation, "Alocação de recursos"),
    ):
        hist = weight_distribution(bundle, bins=bins)
        edges = hist["bin_edges"]
        widths = [b - a for a, b in itertools.pairwise(edges)]
        ax.bar(edges[:-1], hist["counts"], width=widths, align="edge", edgecolor="white")
        ax.set_title(f"{titulo} — {bundle.graph.number_of_edges()} arestas")
        ax.set_xlabel("peso da aresta")
    axes[0].set_ylabel("nº de arestas")
    fig.suptitle(f"{simple.source.dataset} · {lado}", y=1.02)
    fig.tight_layout()

    stem = name or f"fig3-ponderacoes-{simple.source.dataset}-{simple.spec.side}"
    written = save_figure(fig, stem, out_dir=out)
    plt.close(fig)
    return written[0]
