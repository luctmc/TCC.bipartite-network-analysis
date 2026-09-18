"""Figuras e tabelas da Frente A  ``[A]`` — spec A-07.

Requisito que vem do artigo, não do software (briefing §9): refazer uma
figura na semana da entrega tem que ser um comando, não arqueologia.
Toda figura daqui é gerada a partir de artefatos em disco, nunca de
estado em memória de uma execução anterior.
"""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Any

from edugraph.contracts.types import BipartiteBundle, ProjectionBundle

#: Acima disto, a figura do bipartido amostra alunos em vez de desenhar
#: todos — 28 mil pontos numa coluna não comunicam nada.
MAX_STUDENTS_DRAWN = 300

#: Semente da amostra da figura. Fixa: rodar duas vezes dá a mesma figura.
FIGURE_SAMPLE_SEED = 0

#: Colunas da tabela de estatísticas, na ordem em que aparecem no artigo.
STATS_COLUMNS: tuple[str, ...] = (
    "dataset",
    "granularity",
    "edge_criterion",
    "threshold",
    "n_students",
    "n_disciplines",
    "n_edges",
    "density",
    "mean_degree_student",
    "median_degree_student",
    "mean_degree_discipline",
    "median_degree_discipline",
    "n_isolated_removed",
)


def table_dataset_stats(bundle: BipartiteBundle) -> dict[str, Any]:
    """Uma linha da tabela de estatísticas do dataset (capítulo 3).

    Junta a especificação que gerou o grafo às estatísticas de
    :func:`edugraph.data.bipartite.describe`, para que a linha diga não
    só *quanto* mas *sob que critério*. Formato de :data:`STATS_COLUMNS`.
    """
    from edugraph.data.bipartite import describe

    stats = describe(bundle)
    spec = bundle.spec
    row: dict[str, Any] = {
        "dataset": spec.dataset,
        "granularity": spec.granularity,
        "edge_criterion": spec.edge_criterion,
        "threshold": spec.threshold,
    }
    for col in STATS_COLUMNS[4:]:
        value = stats[col]
        row[col] = int(value) if float(value).is_integer() and col != "density" else value
    return row


def figure_bipartite(
    bundle: BipartiteBundle,
    out: Path,
    *,
    name: str | None = None,
    max_students: int = MAX_STUDENTS_DRAWN,
) -> Path:
    """Figura do bipartido, com os dois lados em colunas.

    Alunos à esquerda, disciplinas à direita, ambos ordenados por id;
    cada aresta é um segmento. Sem layout aleatório: rodar duas vezes dá
    a mesma figura.

    Em grafos com mais de ``max_students`` alunos, a figura desenha uma
    **amostra determinística** (semente :data:`FIGURE_SAMPLE_SEED`) e a
    legenda diz isso — desenhar todos não comunica nada. A legenda é
    gravada também num ``<nome>.caption.txt`` ao lado, para ir direto
    para o artigo.

    Returns
    -------
    Path
        O PNG gravado (SVG e legenda saem ao lado).
    """
    import random

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from edugraph.reporting.figures import FULL_WIDTH_IN, apply_style, save_figure

    graph = bundle.graph
    students_all = sorted(bundle.students)
    disciplines = sorted(bundle.disciplines)

    reduced = len(students_all) > max_students
    if reduced:
        students = sorted(random.Random(FIGURE_SAMPLE_SEED).sample(students_all, max_students))
    else:
        students = students_all

    y_student = {s: i / max(len(students) - 1, 1) for i, s in enumerate(students)}
    y_disc = {d: i / max(len(disciplines) - 1, 1) for i, d in enumerate(disciplines)}

    apply_style()
    fig, ax = plt.subplots(figsize=(FULL_WIDTH_IN, 3.2))
    for s in students:
        for d in graph.neighbors(s):
            ax.plot([0, 1], [y_student[s], y_disc[d]], color="0.75", lw=0.4, alpha=0.5, zorder=1)
    students_label = (
        f"alunos ({len(students)} de {len(students_all)})"
        if reduced
        else (f"alunos ({len(students)})")
    )
    ax.scatter(
        [0] * len(students),
        list(y_student.values()),
        s=8,
        color="#6ea8fe",
        zorder=2,
        label=students_label,
    )
    ax.scatter(
        [1] * len(disciplines),
        list(y_disc.values()),
        s=40,
        color="#f0a868",
        marker="s",
        zorder=3,
        label=f"disciplinas ({len(disciplines)})",
    )
    for d, y in y_disc.items():
        ax.annotate(graph.nodes[d].get("label", d), (1.02, y), fontsize=7, va="center")

    ax.set_xlim(-0.1, 1.25)
    ax.set_xticks([0, 1], ["alunos", "disciplinas"])
    ax.set_yticks([])
    ax.grid(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False)
    ax.set_title(
        f"{bundle.spec.dataset} · {graph.number_of_edges()} arestas "
        f"({bundle.spec.edge_criterion}"
        + (f" ≥ {bundle.spec.threshold:g}" if bundle.spec.threshold is not None else "")
        + ")"
    )
    fig.tight_layout()

    caption = (
        f"Grafo bipartido de {bundle.spec.dataset}: {len(students_all)} alunos, "
        f"{len(disciplines)} disciplinas e {graph.number_of_edges()} arestas "
        f"(critério {bundle.spec.edge_criterion}"
        + (f", limiar {bundle.spec.threshold:g}" if bundle.spec.threshold is not None else "")
        + ")."
    )
    if reduced:
        caption += (
            f" Para legibilidade, a figura mostra uma amostra determinística de "
            f"{len(students)} alunos (semente {FIGURE_SAMPLE_SEED}) e todas as suas arestas; "
            f"as estatísticas do texto referem-se ao grafo completo."
        )

    stem = name or f"fig2-bipartido-{bundle.spec.dataset}"
    written = save_figure(fig, stem, out_dir=out)
    plt.close(fig)
    (out / f"{stem}.caption.txt").write_text(caption + "\n", encoding="utf-8", newline="\n")
    return written[0]


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
