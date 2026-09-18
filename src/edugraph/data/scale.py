"""Estratégia de escala  ``[A]`` — spec A-06.

A projeção aluno↔aluno de uma coorte com dois mil alunos chega a milhões
de arestas, e o Girvan-Newman é O(m²n). O plano trata isso como
**limitação a reportar**, não como falha a esconder: as reduções abaixo
são registradas no artefato, de modo que toda tabela do capítulo 3 diga
sobre que recorte ela foi calculada.

Nenhuma redução é silenciosa. Cada uma acrescenta uma entrada em
``meta.stats["reductions"]`` do artefato resultante, com o que foi feito,
com que parâmetros e quanto saiu — e preserva o ``producer`` original,
porque a proveniência continua sendo do quem gerou o grafo.

As quatro reduções, da preferida à mais invasiva:

1. :func:`filter_cohort` — recorta por uma unidade com sentido
   pedagógico (uma turma). Exige que o nó disciplina carregue a
   apresentação (``granularity="module_presentation"``); com
   ``granularity="module"`` a informação já se perdeu, e o recorte
   precisa ser feito antes, por ``BipartiteSpec.cohort`` (spec A-03).
2. :func:`prune_by_weight` — corte por peso mínimo na projeção,
   registrado em ``ProjectionSpec.min_weight`` e conferido pelo
   validador. Não muda o conjunto de nós.
3. :func:`sample_students` — amostra de alunos com semente fixa. Muda
   quem está no grafo; a semente vai para o artefato.
4. :func:`k_core` — núcleo-k da projeção. Muda a topologia de propósito;
   a spec exige reportar quantos nós saíram.
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Any

import networkx as nx

from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import BipartiteBundle, Meta, ProjectionBundle

#: Id da spec, gravado em cada entrada de ``meta.stats["reductions"]``.
PRODUCER = "A-06"


def _with_reduction(meta: Meta, **entry: Any) -> Meta:
    """Acrescenta uma redução ao histórico do artefato, preservando o resto."""
    history = list(meta.stats.get("reductions", []))
    history.append({"producer": PRODUCER, **entry})
    return meta.with_stats(reductions=history)


# ---------------------------------------------------------------------
# 1. Coorte
# ---------------------------------------------------------------------


def _discipline_matches(discipline_id: str, cohort: str) -> bool:
    """``"BBB_2013J"`` casa com ``DBBB_2013J``; ``"2013J"`` casa com ``D*_2013J``."""
    if "_" in cohort:
        return discipline_id == f"D{cohort}"
    return discipline_id.endswith(f"_{cohort}")


def filter_cohort(bundle: BipartiteBundle, cohort: str) -> BipartiteBundle:
    """Subgrafo de uma apresentação (``"BBB_2013J"``) ou de um período (``"2013J"``).

    Mantém as disciplinas da coorte e os alunos ligados a elas. Alunos
    que só cursavam disciplinas de fora saem; disciplinas de fora saem.

    Raises
    ------
    ContractError
        Se nenhuma disciplina do bipartido carrega apresentação no id —
        isto é, se ele foi construído com ``granularity="module"``. Nesse
        caso o recorte precisa acontecer na tabela, via
        ``BipartiteSpec.cohort`` (A-03), e a mensagem diz isso.
    """
    graph = bundle.graph
    disciplines = sorted(bundle.disciplines)
    keep_disciplines = [d for d in disciplines if _discipline_matches(d, cohort)]

    if not keep_disciplines:
        carries_presentation = any("_" in d[1:] for d in disciplines)
        if not carries_presentation:
            raise ContractError(
                f"filter_cohort({cohort!r}): o bipartido de {bundle.spec.dataset!r} tem "
                f"granularity={bundle.spec.granularity!r} e os ids de disciplina não carregam "
                "apresentação. Recorte na tabela com BipartiteSpec(cohort=...) (spec A-03) "
                "ou construa com granularity='module_presentation'."
            )
        raise ContractError(
            f"filter_cohort({cohort!r}): nenhuma disciplina casa. Exemplos presentes: "
            f"{disciplines[:5]}"
        )

    keep_students = sorted({s for d in keep_disciplines for s in graph.neighbors(d)})
    sub: nx.Graph[Any] = graph.subgraph([*keep_students, *keep_disciplines]).copy()

    meta = _with_reduction(
        bundle.meta,
        kind="filter_cohort",
        cohort=cohort,
        n_students_before=len(bundle.students),
        n_students_after=len(keep_students),
        n_disciplines_before=len(disciplines),
        n_disciplines_after=len(keep_disciplines),
    )
    return BipartiteBundle(graph=sub, spec=replace(bundle.spec, cohort=cohort), meta=meta)


# ---------------------------------------------------------------------
# 2. Corte por peso
# ---------------------------------------------------------------------


def prune_by_weight(bundle: ProjectionBundle, min_weight: float) -> ProjectionBundle:
    """Remove arestas com ``weight < min_weight``; nós ficam, mesmo isolados.

    O corte vai para ``ProjectionSpec.min_weight``, e o validador de
    contrato passa a conferir que nenhuma aresta abaixo dele sobreviveu —
    o corte fica auditável no artefato.

    **Não use isto para caber na memória.** O corte age sobre a projeção
    já construída: ele reduz o artefato gravado, não o pico. Sobre a base
    inteira do OULAD a projeção aluno↔aluno passa de 5 GB *antes* de
    chegar aqui (medido na A-06). O que reduz o pico é :func:`filter_cohort`
    ou :func:`sample_students`, que agem antes de projetar.
    """
    if min_weight <= 0:
        raise ContractError(f"min_weight precisa ser positivo; recebeu {min_weight!r}")

    graph: nx.Graph[Any] = bundle.graph.copy()
    drop = [(u, v) for u, v, d in graph.edges(data=True) if float(d["weight"]) < min_weight]
    graph.remove_edges_from(drop)

    meta = _with_reduction(
        bundle.meta,
        kind="prune_by_weight",
        min_weight=min_weight,
        n_edges_before=bundle.graph.number_of_edges(),
        n_edges_after=graph.number_of_edges(),
        n_edges_removed=len(drop),
    )
    return ProjectionBundle(
        graph=graph,
        spec=replace(bundle.spec, min_weight=min_weight),
        source=bundle.source,
        meta=meta,
    )


# ---------------------------------------------------------------------
# 3. Amostra de alunos
# ---------------------------------------------------------------------


def sample_students(bundle: BipartiteBundle, n: int, *, seed: int) -> BipartiteBundle:
    """Amostra ``n`` alunos com semente fixa; disciplinas sem aluno saem.

    Usada para viabilizar o Girvan-Newman (spec B-02). A semente e o
    tamanho vão para o artefato, porque a amostra precisa ser
    reproduzível para o número entrar no artigo. Se ``n`` for maior ou
    igual ao total, nada muda — e isso também fica registrado.
    """
    if n <= 0:
        raise ContractError(f"n precisa ser positivo; recebeu {n!r}")

    students = sorted(bundle.students)
    chosen = students if n >= len(students) else sorted(random.Random(seed).sample(students, n))

    graph: nx.Graph[Any] = bundle.graph.subgraph([*chosen, *bundle.disciplines]).copy()
    orphan_disciplines = [d for d in bundle.disciplines if graph.degree(d) == 0]
    graph.remove_nodes_from(orphan_disciplines)

    meta = _with_reduction(
        bundle.meta,
        kind="sample_students",
        n=n,
        seed=seed,
        n_students_before=len(students),
        n_students_after=len(chosen),
        n_disciplines_removed=len(orphan_disciplines),
    )
    return BipartiteBundle(graph=graph, spec=bundle.spec, meta=meta)


# ---------------------------------------------------------------------
# 4. Núcleo-k
# ---------------------------------------------------------------------


def k_core(graph: nx.Graph[Any], k: int) -> nx.Graph[Any]:
    """Núcleo-k: remove nós de grau < ``k`` até estabilizar (cópia, não view)."""
    if k < 1:
        raise ContractError(f"k precisa ser >= 1; recebeu {k!r}")
    core: nx.Graph[Any] = nx.k_core(graph, k).copy()
    return core


def k_core_projection(bundle: ProjectionBundle, k: int) -> ProjectionBundle:
    """Núcleo-k da projeção, com o número de nós removidos no artefato.

    Terceira redução, aplicada sobre a projeção e não sobre o bipartido.
    Muda a topologia de propósito: a spec exige reportar quantos nós
    saíram, e a partição ou centralidade calculada depois vale só para o
    núcleo.
    """
    core = k_core(bundle.graph, k)
    meta = _with_reduction(
        bundle.meta,
        kind="k_core",
        k=k,
        n_nodes_before=bundle.graph.number_of_nodes(),
        n_nodes_after=core.number_of_nodes(),
        n_nodes_removed=bundle.graph.number_of_nodes() - core.number_of_nodes(),
        n_edges_after=core.number_of_edges(),
    )
    return ProjectionBundle(graph=core, spec=bundle.spec, source=bundle.source, meta=meta)


def reductions_of(meta: Meta) -> list[dict[str, Any]]:
    """As reduções registradas num artefato, na ordem em que foram aplicadas."""
    return list(meta.stats.get("reductions", []))
