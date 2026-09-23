"""Figuras da Frente B  ``[B]`` — spec B-07.

Três figuras do capítulo 3: o grafo com cor por comunidade, a
distribuição de tamanhos e o Q × tempo por algoritmo (esta última
alimenta a tabela da B-04). Todas geradas a partir de artefatos em
disco, com um comando (briefing §9).

Cor que sobrevive à impressão em preto e branco
-----------------------------------------------
A paleta é o **cividis** amostrado em ``k`` pontos: é uma escala
sequencial desenhada para daltonismo e com luminância monotônica, o que
garante que duas comunidades vizinhas na paleta também fiquem em cinzas
diferentes quando o artigo for impresso em preto e branco (critério de
aceite da B-07). Por garantia, a forma do marcador também alterna — cor
e forma dizem a mesma coisa duas vezes.

Grafo grande é agregado, não amostrado
--------------------------------------
Acima de :data:`AGGREGATE_ABOVE` nós, a figura desenha **uma bolha por
comunidade**, com área proporcional ao tamanho e aresta proporcional ao
número de ligações entre as comunidades. Desenhar dois mil pontos não
comunica nada, e amostrar esconderia justamente a estrutura que a figura
existe para mostrar. A legenda diz o que foi feito.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import networkx as nx

from edugraph.community.characterize import community_sizes
from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import Partition, ProjectionBundle

#: Id da spec, gravado nas legendas geradas.
PRODUCER = "B-07"

#: Acima disto, a figura agrega: uma bolha por comunidade.
AGGREGATE_ABOVE = 500

#: Teto de arestas desenhadas no grafo não agregado. Acima disto, só as
#: mais pesadas entram — e a legenda diz quantas ficaram de fora.
MAX_EDGES_DRAWN = 20_000

#: Semente do layout. Fixa: rodar duas vezes dá a mesma figura (ADR-0011).
LAYOUT_SEED = 0

#: Paleta qualitativa, amostrada de uma escala sequencial para que as
#: cores também se distingam em escala de cinza. Registrada aqui porque
#: a spec B-07 exige dizer qual foi usada.
PALETTE_NAME = "cividis"

#: Formas de marcador, cicladas junto com a cor.
MARKERS: tuple[str, ...] = ("o", "s", "^", "D", "v", "P", "X", "*")

#: Layouts aceitos por :func:`figure_communities`.
LAYOUTS: tuple[str, ...] = ("spring", "kamada_kawai", "circular")


def community_colors(k: int) -> list[tuple[float, float, float, float]]:
    """``k`` cores de :data:`PALETTE_NAME`, espaçadas uniformemente."""
    import matplotlib.pyplot as plt

    colormap = plt.get_cmap(PALETTE_NAME)
    if k <= 1:
        return [colormap(0.5)]
    # Evita os extremos da escala, onde o contraste com o fundo cai.
    return [colormap(0.05 + 0.9 * i / (k - 1)) for i in range(k)]


def _positions(graph: nx.Graph[Any], layout: str) -> dict[Any, Any]:
    """Coordenadas dos nós, sempre determinísticas."""
    if layout == "spring":
        return nx.spring_layout(graph, seed=LAYOUT_SEED, weight="weight")
    if layout == "kamada_kawai":
        return nx.kamada_kawai_layout(graph, weight="weight")
    if layout == "circular":
        return nx.circular_layout(graph)
    raise ContractError(f"layout {layout!r} desconhecido; esperado um de {list(LAYOUTS)}")


def _community_graph(partition: Partition, projection: ProjectionBundle) -> nx.Graph[Any]:
    """Grafo agregado: um nó por comunidade, arestas entre elas.

    O laço de cada comunidade guarda o número de arestas internas, que
    vira o tamanho da bolha junto com o número de nós.
    """
    membership = partition.membership
    sizes = community_sizes(partition)
    between: defaultdict[tuple[int, int], float] = defaultdict(float)
    internal: defaultdict[int, float] = defaultdict(float)

    for source, target, data in projection.graph.edges(data=True):
        left, right = membership[source], membership[target]
        weight = float(data.get("weight", 1.0))
        if left == right:
            internal[left] += weight
        else:
            between[min(left, right), max(left, right)] += weight

    aggregated: nx.Graph[Any] = nx.Graph()
    for community, size in sizes.items():
        aggregated.add_node(community, size=size, internal=internal[community])
    for (left, right), weight in between.items():
        aggregated.add_edge(left, right, weight=weight)
    return aggregated


def _draw_edges(
    ax: Any,
    positions: dict[Any, Any],
    edges: list[tuple[Any, Any]],
    *,
    widths: list[float],
    color: str,
    alpha: float,
) -> None:
    """Desenha as arestas como uma coleção única.

    Um ``ax.plot`` por aresta gera um elemento de SVG por aresta: o
    arquivo de ``student_simple`` (1.971 arestas) passava de 480 kB, e
    ``results/figures/`` é versionado. Com ``LineCollection`` o mesmo
    desenho vira um elemento só.

    Rasterizar a camada foi testado e **descartado**: no SVG ela vira um
    PNG em base64 a 300 dpi, que ficou maior que os vetores (1,3 MB
    contra 371 kB).
    """
    from matplotlib.collections import LineCollection

    if not edges:
        return
    segments = [(positions[source], positions[target]) for source, target in edges]
    collection = LineCollection(
        segments,
        colors=color,
        linewidths=widths,
        alpha=alpha,
        zorder=1,
    )
    ax.add_collection(collection)


def _write_caption(out: Path, stem: str, text: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{stem}.caption.txt").write_text(text + "\n", encoding="utf-8", newline="\n")


def figure_communities(
    partition: Partition,
    projection: ProjectionBundle,
    out: Path,
    *,
    layout: str = "spring",
    name: str | None = None,
    aggregate_above: int = AGGREGATE_ABOVE,
) -> Path:
    """Grafo com cor por comunidade.

    Em grafos grandes, a spec B-07 exige agregar (um nó por comunidade,
    área proporcional ao tamanho) em vez de desenhar milhares de pontos
    que não comunicam nada.

    Parameters
    ----------
    partition
        Partição a colorir.
    projection
        A projeção que ela particiona. Precisa ser a mesma: nó fora do
        ``membership`` não teria cor.
    out
        Diretório de saída (``results/figures`` no artigo).
    layout
        Um de :data:`LAYOUTS`. Todos determinísticos.
    name
        Nome do arquivo sem extensão. Padrão:
        ``fig4-comunidades-<dataset>-<artifact_id>``.
    aggregate_above
        Acima de quantos nós agregar.

    Returns
    -------
    Path
        O PNG gravado (o SVG e a legenda saem ao lado).

    Raises
    ------
    ContractError
        Se a partição não cobrir exatamente os nós da projeção.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from edugraph.reporting.figures import COLUMN_WIDTH_IN, apply_style, save_figure

    if set(partition.membership) != set(projection.graph.nodes):
        raise ContractError(
            f"{PRODUCER}: a partição {partition.artifact_id!r} não cobre os nós da projeção "
            f"{projection.projection_id!r}; não há como colorir o que não foi particionado"
        )

    dataset = projection.source.dataset
    sizes = community_sizes(partition)
    colors = community_colors(len(sizes))
    aggregated = projection.graph.number_of_nodes() > aggregate_above

    apply_style()
    fig, ax = plt.subplots(figsize=(COLUMN_WIDTH_IN * 2, 4.2))

    if aggregated:
        graph = _community_graph(partition, projection)
        positions = _positions(graph, layout)
        max_size = max(sizes.values())
        max_weight = max((d["weight"] for _, _, d in graph.edges(data=True)), default=1.0)
        _draw_edges(
            ax,
            positions,
            [(u, v) for u, v, _ in graph.edges(data=True)],
            widths=[
                0.4 + 2.6 * float(d["weight"]) / max_weight for _, _, d in graph.edges(data=True)
            ],
            color="0.6",
            alpha=1.0,
        )
        for index, community in enumerate(sorted(graph.nodes)):
            x, y = positions[community]
            ax.scatter(
                [x],
                [y],
                s=80 + 1600 * sizes[community] / max_size,
                color=[colors[index]],
                marker=MARKERS[index % len(MARKERS)],
                edgecolors="white",
                linewidths=0.8,
                zorder=2,
                label=f"c{community} ({sizes[community]})",
            )
            ax.annotate(str(community), (x, y), ha="center", va="center", fontsize=7, zorder=3)
        desenhadas, omitidas = graph.number_of_edges(), 0
    else:
        graph = projection.graph
        positions = _positions(graph, layout)
        edges = sorted(
            graph.edges(data=True), key=lambda e: (-float(e[2].get("weight", 1.0)), e[0], e[1])
        )
        desenhadas = min(len(edges), MAX_EDGES_DRAWN)
        omitidas = len(edges) - desenhadas
        _draw_edges(
            ax,
            positions,
            [(source, target) for source, target, _ in edges[:desenhadas]],
            widths=[0.3] * desenhadas,
            color="0.8",
            alpha=0.6,
        )
        for index, (community, nodes) in enumerate(partition.groups().items()):
            ax.scatter(
                [positions[node][0] for node in nodes],
                [positions[node][1] for node in nodes],
                s=28,
                color=[colors[index]],
                marker=MARKERS[index % len(MARKERS)],
                edgecolors="white",
                linewidths=0.4,
                zorder=2,
                label=f"c{community} ({len(nodes)})",
            )

    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_title(
        f"{dataset} · {projection.projection_id} · {partition.algorithm} "
        f"(Q = {partition.modularity:.4f}, k = {partition.n_communities}"
        + (f", {partition.status}" if partition.status != "ok" else "")
        + ")"
    )
    # Muita comunidade transforma a legenda em tapume; acima de 12 o
    # número dentro da bolha já identifica cada uma.
    if len(sizes) <= 12:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize=7)
    fig.tight_layout()

    stem = name or f"fig4-comunidades-{dataset}-{partition.artifact_id}"
    written = save_figure(fig, stem, out_dir=out)
    plt.close(fig)

    caption = (
        f"Comunidades na projeção {projection.projection_id} de {dataset}, por "
        f"{partition.algorithm} (Q = {partition.modularity:.4f}, "
        f"{partition.n_communities} comunidades, status {partition.status}). "
        f"Cores da escala {PALETTE_NAME}, que se distingue também em escala de cinza; "
        f"a forma do marcador repete a informação da cor. Layout {layout} com semente "
        f"{LAYOUT_SEED}."
    )
    if aggregated:
        caption += (
            f" Figura **agregada**: cada bolha é uma comunidade, com área proporcional ao "
            f"número de nós ({projection.graph.number_of_nodes()} no total) e a espessura "
            f"da aresta proporcional ao peso das ligações entre as duas comunidades."
        )
    elif omitidas:
        caption += (
            f" Das {desenhadas + omitidas} arestas, a figura desenha as {desenhadas} mais "
            f"pesadas; as {omitidas} restantes foram omitidas por legibilidade."
        )
    _write_caption(out, stem, caption)
    return written[0]


def figure_size_distribution(
    partitions: list[Partition],
    out: Path,
    *,
    dataset: str | None = None,
    name: str | None = None,
) -> Path:
    """Distribuição de tamanhos de comunidade, um painel por algoritmo.

    Dentro do painel, uma curva por projeção: os tamanhos em ordem
    decrescente. É a forma que responde de relance à pergunta que a
    tabela do capítulo 3 deixa em aberto — se o ``k`` grande de um
    algoritmo são grupos de verdade ou uma fila de comunidades de um nó
    só (docs/contratos/partition.md).
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    from edugraph.reporting.figures import FULL_WIDTH_IN, apply_style, save_figure

    if not partitions:
        raise ContractError(f"{PRODUCER}: nenhuma partição para a figura de tamanhos")

    by_algorithm: dict[str, list[Partition]] = {}
    for partition in sorted(partitions, key=lambda p: (p.algorithm, p.projection_id)):
        by_algorithm.setdefault(partition.algorithm, []).append(partition)

    apply_style()
    fig, axes = plt.subplots(
        1, len(by_algorithm), figsize=(FULL_WIDTH_IN, 2.8), sharey=True, squeeze=False
    )
    colors = community_colors(max(len(v) for v in by_algorithm.values()))

    for ax, (algorithm, group) in zip(axes[0], sorted(by_algorithm.items()), strict=True):
        for index, partition in enumerate(group):
            sizes = sorted(community_sizes(partition).values(), reverse=True)
            ax.plot(
                range(1, len(sizes) + 1),
                sizes,
                marker=MARKERS[index % len(MARKERS)],
                color=colors[index % len(colors)],
                markersize=4,
                lw=1.2,
                label=f"{partition.projection_id} (k={partition.n_communities})",
            )
        ax.set_title(algorithm)
        ax.set_xlabel("comunidade (ordenada por tamanho)")
        # Posição na fila é número inteiro: sem isto o eixo mostra "1,5".
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(frameon=False, fontsize=6)
    axes[0][0].set_ylabel("nº de nós")
    if dataset:
        fig.suptitle(dataset, y=1.02)
    fig.tight_layout()

    stem = name or "-".join(filter(None, ["fig5-tamanhos", dataset]))
    written = save_figure(fig, stem, out_dir=out)
    plt.close(fig)

    singletons = sum(
        1 for partition in partitions for size in community_sizes(partition).values() if size == 1
    )
    _write_caption(
        out,
        stem,
        (
            f"Distribuição de tamanhos das comunidades, um painel por algoritmo, sobre "
            f"{len(partitions)} partições" + (f" de {dataset}" if dataset else "") + ". "
            f"Tamanhos em ordem decrescente; {singletons} comunidades de um nó só no total. "
            f"Cores da escala {PALETTE_NAME}."
        ),
    )
    return written[0]


def figure_q_vs_time(
    partitions: list[Partition],
    out: Path,
    *,
    dataset: str | None = None,
    name: str | None = None,
) -> Path:
    """Q × tempo por algoritmo — a figura que acompanha a tabela da B-04.

    Eixo do tempo em escala logarítmica, porque a diferença entre
    Louvain e Girvan-Newman é de ordens de grandeza (o starter kit mediu
    645×; sobre ``synthetic_v1``/``student_simple`` medimos 1.453×) e em
    escala linear os pontos do Louvain colariam todos no zero. Partições
    com ``status`` diferente de ``ok`` saem com o marcador vazado e o
    status escrito ao lado: elas não são comparáveis de igual para igual
    (ADR-0006).

    Partições **sem tempo medido** (``runtime_s = 0``, que é o caso das
    partições de referência das fixtures) ficam de fora: colocá-las em
    ``1e-6`` no eixo log faria a figura afirmar que rodaram num
    microssegundo. Quantas foram excluídas está na legenda.

    Raises
    ------
    ContractError
        Se nenhuma partição tiver tempo medido — não há figura de custo
        a fazer, e é preciso rodar os algoritmos em vez de ler fixtures.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from edugraph.reporting.figures import COLUMN_WIDTH_IN, apply_style, save_figure

    if not partitions:
        raise ContractError(f"{PRODUCER}: nenhuma partição para a figura de Q × tempo")

    medidas = [p for p in partitions if p.runtime_s > 0]
    sem_tempo = len(partitions) - len(medidas)
    if not medidas:
        raise ContractError(
            f"{PRODUCER}: nenhuma das {len(partitions)} partições tem tempo medido "
            "(runtime_s = 0). As partições de referência das fixtures não medem tempo; "
            "rode 'edugraph community louvain/girvan-newman' para ter o que comparar."
        )

    ordered = sorted(medidas, key=lambda p: (p.algorithm, p.projection_id))
    algorithms = sorted({p.algorithm for p in ordered})
    colors = dict(zip(algorithms, community_colors(len(algorithms)), strict=True))

    apply_style()
    fig, ax = plt.subplots(figsize=(COLUMN_WIDTH_IN * 1.8, 3.0))
    for algorithm, partition in ((p.algorithm, p) for p in ordered):
        index = algorithms.index(algorithm)
        completo = partition.status == "ok"
        ax.scatter(
            [partition.runtime_s],
            [partition.modularity],
            s=60,
            marker=MARKERS[index % len(MARKERS)],
            facecolors=colors[algorithm] if completo else "none",
            edgecolors=colors[algorithm],
            linewidths=1.2,
            zorder=2,
        )
        rotulo = partition.projection_id + ("" if completo else f" ({partition.status})")
        ax.annotate(
            rotulo,
            (partition.runtime_s, partition.modularity),
            textcoords="offset points",
            xytext=(6, 3),
            fontsize=6,
        )

    for algorithm in algorithms:
        ax.scatter([], [], color=colors[algorithm], label=algorithm, s=60,
                   marker=MARKERS[algorithms.index(algorithm) % len(MARKERS)])  # fmt: skip

    ax.set_xscale("log")
    ax.set_xlabel("tempo de execução (s, escala log)")
    ax.set_ylabel("modularidade Q")
    ax.set_title("Qualidade × custo" + (f" · {dataset}" if dataset else ""))
    ax.legend(frameon=False, loc="best")
    fig.tight_layout()

    stem = name or "-".join(filter(None, ["fig6-q-tempo", dataset]))
    written = save_figure(fig, stem, out_dir=out)
    plt.close(fig)

    razao = ""
    por_algoritmo: dict[str, float] = {}
    for partition in ordered:
        por_algoritmo.setdefault(partition.algorithm, partition.runtime_s)
    if len(por_algoritmo) == 2:
        lento, rapido = max(por_algoritmo.values()), min(por_algoritmo.values())
        razao = f" O mais lento levou {lento / rapido:.0f}× o tempo do mais rápido."
    excluidas = (
        f" {sem_tempo} partições sem tempo medido (fixtures de referência) ficaram de fora."
        if sem_tempo
        else ""
    )
    _write_caption(
        out,
        stem,
        (
            "Modularidade × tempo de execução"
            + (f" em {dataset}" if dataset else "")
            + f", {len(ordered)} execuções. Marcador vazado indica execução que não "
            f"terminou dentro do orçamento (ADR-0006).{razao} Escala logarítmica no "
            f"tempo.{excluidas}"
        ),
    )
    return written[0]


def sizes_table(partitions: list[Partition]) -> list[dict[str, Any]]:
    """Tamanhos por comunidade em formato longo, para conferência.

    A figura mostra; esta tabela permite verificar. Uma linha por
    ``(algoritmo, projeção, comunidade)``.
    """
    return [
        {
            "algorithm": partition.algorithm,
            "projection_id": partition.projection_id,
            "community": community,
            "size": size,
        }
        for partition in sorted(partitions, key=lambda p: (p.algorithm, p.projection_id))
        for community, size in sorted(community_sizes(partition).items())
    ]
