"""Construção do grafo bipartido G = (U ∪ V, E)  ``[A]`` — spec A-03.

O critério que cria uma aresta e a granularidade do nó "disciplina" são
**parâmetros** de :class:`~edugraph.contracts.types.BipartiteSpec`, não
constantes (ADR-0007). É isso que permite ao capítulo 3 comparar
configurações em vez de defender uma escolha única.

Duas etapas, separadas para serem testáveis sozinhas:

1. :func:`normalize_table` — filtra a coorte, deriva o id de disciplina
   conforme a granularidade e agrega por (aluno, disciplina).
2. :func:`build_bipartite` — aplica o critério de aresta e monta o grafo,
   só com ``kind`` e ``label`` nos nós (ADR-0008).

Ver a decisão D1 do plano de arquitetura para o que cada granularidade
significa no OULAD.
"""

from __future__ import annotations

from typing import Any

import networkx as nx
import pandas as pd

from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import BipartiteBundle, BipartiteSpec, Meta

#: Id da spec, gravado em ``meta.producer``.
PRODUCER = "A-03"

#: Colunas exigidas na tabela de entrada (saída do ETL, A-02, ou do
#: gerador sintético, A-01). ``score_media`` pode ter nulos: matrícula
#: sem avaliação existe na base real.
REQUIRED_COLUMNS: tuple[str, ...] = (
    "id_student",
    "code_module",
    "code_presentation",
    "score_media",
)

#: Colunas opcionais, exigidas só por certas configurações.
OPTIONAL_COLUMNS: tuple[str, ...] = ("final_result", "sum_click", "id_assessment")

#: Desfechos que contam como aprovação no critério ``final_result_pass``.
PASSING_RESULTS: frozenset[str] = frozenset({"Pass", "Distinction"})

#: Colunas da tabela normalizada devolvida por :func:`normalize_table`.
NORMALIZED_COLUMNS: tuple[str, ...] = ("student_id", "discipline_id", "score_media")


# ---------------------------------------------------------------------
# Etapa 1 — normalização
# ---------------------------------------------------------------------


def _require_columns(table: pd.DataFrame, columns: tuple[str, ...], why: str) -> None:
    faltando = [c for c in columns if c not in table.columns]
    if faltando:
        raise ContractError(
            f"tabela de entrada sem as colunas {faltando} ({why}). "
            f"Colunas presentes: {list(table.columns)}"
        )


def filter_cohort(table: pd.DataFrame, cohort: str | None) -> pd.DataFrame:
    """Recorta por coorte: ``"BBB_2013J"`` (módulo_apresentação) ou ``"2013J"``.

    Uma coorte é a unidade que faz sentido pedagógico — uma turma — e é
    a redução preferida da spec A-06. Aqui só se aplica o recorte; a
    estratégia de escala completa é lá.
    """
    if cohort is None:
        return table
    if "_" in cohort:
        chave = table["code_module"].astype(str) + "_" + table["code_presentation"].astype(str)
        return table[chave == cohort]
    return table[table["code_presentation"].astype(str) == cohort]


def discipline_ids(table: pd.DataFrame, spec: BipartiteSpec) -> pd.Series:
    """Id do nó de V para cada linha, conforme ``spec.granularity``.

    ``module``              → ``DAAA``
    ``module_presentation`` → ``DAAA_2013J``
    ``assessment``          → ``D<id_assessment>`` (exige a coluna)
    """
    module = table["code_module"].astype(str)
    if spec.granularity == "module":
        return "D" + module
    if spec.granularity == "module_presentation":
        return "D" + module + "_" + table["code_presentation"].astype(str)
    if spec.granularity == "assessment":
        _require_columns(table, ("id_assessment",), "granularity='assessment'")
        return "D" + table["id_assessment"].astype("int64").astype(str)
    raise ContractError(f"granularity desconhecida: {spec.granularity!r}")


def normalize_table(raw: pd.DataFrame, spec: BipartiteSpec) -> pd.DataFrame:
    """Agrega a tabela em uma linha por (aluno, disciplina).

    Regras de agregação, registradas aqui porque viram parágrafo do
    artigo (``docs/artigo/decisoes-metodologicas.md``):

    - ``score_media``: **média** das notas das linhas agregadas. Um aluno
      que repetiu o módulo em duas apresentações e ``granularity="module"``
      entra com a média das duas.
    - ``sum_click``: **soma** dos cliques.
    - ``final_result``: aprovado se **alguma** das linhas for ``Pass`` ou
      ``Distinction`` — coluna ``passed`` (booleana). Só existe quando a
      entrada traz ``final_result``.

    Returns
    -------
    DataFrame
        Colunas ``student_id`` (``S…``), ``discipline_id`` (``D…``),
        ``score_media`` e, quando disponíveis, ``sum_click`` e ``passed``.
        Ordenado por (aluno, disciplina) para que a saída seja canônica.
    """
    _require_columns(raw, REQUIRED_COLUMNS, "entrada de build_bipartite")

    table = filter_cohort(raw, spec.cohort).copy()
    table["student_id"] = "S" + table["id_student"].astype("int64").astype(str)
    table["discipline_id"] = discipline_ids(table, spec)

    agg: dict[str, Any] = {"score_media": ("score_media", "mean")}
    if "sum_click" in table.columns:
        agg["sum_click"] = ("sum_click", "sum")
    if "final_result" in table.columns:
        table["passed"] = table["final_result"].isin(PASSING_RESULTS)
        agg["passed"] = ("passed", "any")

    grouped = (
        table.groupby(["student_id", "discipline_id"], sort=True, dropna=False)
        .agg(**agg)
        .reset_index()
    )
    return grouped


# ---------------------------------------------------------------------
# Etapa 2 — critério de aresta e grafo
# ---------------------------------------------------------------------


def edge_mask(normalized: pd.DataFrame, spec: BipartiteSpec) -> pd.Series:
    """Quais linhas viram aresta, conforme ``spec.edge_criterion``.

    ``score_threshold``   nota média ≥ ``threshold`` (sem limiar: qualquer nota)
    ``final_result_pass`` desfecho de aprovação — **definição declarada
                          de aresta**, não entrada de algoritmo (ADR-0007)
    ``vle_activity``      cliques ≥ ``threshold`` (sem limiar: > 0)
    """
    crit = spec.edge_criterion
    if crit == "score_threshold":
        score = normalized["score_media"]
        if spec.threshold is None:
            return score.notna()
        return score.notna() & (score >= spec.threshold)
    if crit == "final_result_pass":
        _require_columns(normalized, ("passed",), "edge_criterion='final_result_pass'")
        return normalized["passed"].astype(bool)
    if crit == "vle_activity":
        _require_columns(normalized, ("sum_click",), "edge_criterion='vle_activity'")
        clicks = normalized["sum_click"]
        minimo = spec.threshold if spec.threshold is not None else 0.0
        return clicks.notna() & (clicks > minimo if spec.threshold is None else clicks >= minimo)
    raise ContractError(f"edge_criterion desconhecido: {crit!r}")


def edge_weights(normalized: pd.DataFrame, spec: BipartiteSpec) -> pd.Series:
    """Peso da aresta: a grandeza que o critério olhou.

    Nota média em ``score_threshold``, cliques em ``vle_activity`` e
    ``1.0`` em ``final_result_pass``. As projeções ignoram este peso e
    usam só a existência da aresta; ele fica disponível para o front e
    para estatísticas.
    """
    if spec.edge_criterion == "score_threshold":
        return normalized["score_media"].astype(float)
    if spec.edge_criterion == "vle_activity":
        return normalized["sum_click"].astype(float)
    return pd.Series(1.0, index=normalized.index)


def build_bipartite(table: pd.DataFrame, spec: BipartiteSpec) -> BipartiteBundle:
    """Constrói o bipartido a partir da tabela (bruta ou já normalizada).

    U = estudantes (prefixo ``S``), V = disciplinas (prefixo ``D``). A
    existência de uma aresta é decidida por ``spec.edge_criterion``, e o
    que conta como um nó de V por ``spec.granularity``.

    Nós isolados pelo critério **saem** e o número vai para
    ``meta.stats["n_isolated_removed"]``: um aluno sem nenhuma aresta não
    participa de projeção nenhuma. É número a reportar, não a esconder —
    em ``synthetic_v1``, 22 dos 120 alunos saem.

    Parameters
    ----------
    table
        Tabela com as colunas de :data:`REQUIRED_COLUMNS` (uma linha por
        matrícula) **ou** já normalizada por :func:`normalize_table`.
    spec
        Granularidade, critério de aresta, limiar e coorte.
    """
    if set(NORMALIZED_COLUMNS) <= set(table.columns):
        normalized = table
    else:
        normalized = normalize_table(table, spec)

    keep = normalized[edge_mask(normalized, spec)]
    weights = edge_weights(keep, spec)

    graph: nx.Graph[Any] = nx.Graph()
    # Todos os nós entram primeiro, para que o total antes do corte seja
    # conhecido; os isolados saem em seguida, contados.
    for student in sorted(normalized["student_id"].unique()):
        graph.add_node(student, kind="student", label=student[1:])
    for discipline in sorted(normalized["discipline_id"].unique()):
        graph.add_node(discipline, kind="discipline", label=discipline[1:])

    for (student, discipline), weight in zip(
        zip(keep["student_id"], keep["discipline_id"], strict=True), weights, strict=True
    ):
        graph.add_edge(student, discipline, weight=float(weight))

    isolated = [n for n, d in graph.degree if d == 0]
    graph.remove_nodes_from(isolated)

    meta = Meta(
        producer=PRODUCER,
        stats={
            "granularity": spec.granularity,
            "edge_criterion": spec.edge_criterion,
            "threshold": spec.threshold,
            "cohort": spec.cohort,
            "n_rows_normalized": len(normalized),
            "n_rows_kept": len(keep),
            "n_isolated_removed": len(isolated),
        },
    )
    return BipartiteBundle(graph=graph, spec=spec, meta=meta)


def describe(bundle: BipartiteBundle) -> dict[str, float]:
    """Estatísticas descritivas do bipartido — insumo da spec A-07."""
    raise NotImplementedError("A-07: ver docs/specs/frente-a/A-07-estatisticas-bipartido.md")


def default_meta(spec: BipartiteSpec, producer: str) -> Meta:
    """Metadados padrão de um bipartido."""
    return Meta(producer=producer, stats={"granularity": spec.granularity})
