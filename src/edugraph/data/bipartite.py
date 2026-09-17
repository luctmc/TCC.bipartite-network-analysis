"""Construção do grafo bipartido G = (U ∪ V, E)  ``[A]`` — spec A-03.

O critério que cria uma aresta e a granularidade do nó "disciplina" são
**parâmetros** de :class:`~edugraph.contracts.types.BipartiteSpec`, não
constantes (ADR-0007). É isso que permite ao capítulo 3 comparar
configurações em vez de defender uma escolha única.

Ver a decisão D1 do plano de arquitetura para o que cada granularidade
significa no OULAD.
"""

from __future__ import annotations

import pandas as pd

from edugraph.contracts.types import BipartiteBundle, BipartiteSpec, Meta

#: Colunas exigidas na tabela normalizada de entrada (saída do ETL, A-02,
#: ou do gerador sintético, A-01).
REQUIRED_COLUMNS: tuple[str, ...] = (
    "id_student",
    "code_module",
    "code_presentation",
    "score_media",
)


def build_bipartite(table: pd.DataFrame, spec: BipartiteSpec) -> BipartiteBundle:
    """Constrói o bipartido a partir da tabela normalizada.

    U = estudantes (prefixo ``S``), V = disciplinas (prefixo ``D``). A
    existência de uma aresta é decidida por ``spec.edge_criterion``, e o
    que conta como um nó de V por ``spec.granularity``.

    Parameters
    ----------
    table
        Tabela normalizada, uma linha por (aluno, disciplina, apresentação).
    spec
        Granularidade, critério de aresta, limiar e coorte.

    Returns
    -------
    BipartiteBundle
        Grafo validado por :func:`edugraph.contracts.validate.validate_bipartite`.

    Notes
    -----
    A implementar em A-03:

    1. Filtrar por ``spec.cohort`` quando não for ``None``.
    2. Derivar o id de disciplina conforme ``spec.granularity``
       (``module`` → ``DAAA``; ``module_presentation`` → ``DAAA_2024J``;
       ``assessment`` → id da avaliação).
    3. Agregar por (aluno, disciplina) — média quando o aluno repetiu.
    4. Aplicar ``spec.edge_criterion`` para decidir a existência da aresta
       e definir ``weight``.
    5. Nunca gravar desfecho, nota bruta ou atributo demográfico como
       atributo de nó (ADR-0008); isso vai para ``outcomes.csv``.
    """
    raise NotImplementedError("A-03: ver docs/specs/frente-a/A-03-bipartido-parametrizavel.md")


def normalize_table(raw: pd.DataFrame, spec: BipartiteSpec) -> pd.DataFrame:
    """Agrega a tabela bruta em uma linha por (aluno, disciplina).

    Implementar em A-03 junto de :func:`build_bipartite`; separada para
    que os testes possam checar a agregação sem construir o grafo.
    """
    raise NotImplementedError("A-03: agregação por (aluno, disciplina)")


def describe(bundle: BipartiteBundle) -> dict[str, float]:
    """Estatísticas descritivas do bipartido — insumo da spec A-07.

    Devolve nº de alunos, nº de disciplinas, nº de arestas, densidade e
    grau médio de cada lado, no formato que ``reporting.tables`` grava.
    """
    raise NotImplementedError("A-07: ver docs/specs/frente-a/A-07-estatisticas-bipartido.md")


def default_meta(spec: BipartiteSpec, producer: str) -> Meta:
    """Metadados padrão de um bipartido — usado por A-03 e pelas fixtures."""
    return Meta(producer=producer, stats={"granularity": spec.granularity})
