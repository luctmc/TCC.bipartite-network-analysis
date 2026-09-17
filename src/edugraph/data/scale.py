"""Estratégia de escala  ``[A]`` — spec A-06.

A projeção aluno↔aluno de uma coorte com dois mil alunos chega a milhões
de arestas, e o Girvan-Newman é O(m²n). O plano trata isso como
**limitação a reportar**, não como falha a esconder: as três reduções
abaixo são parâmetros registrados no artefato, de modo que toda tabela do
capítulo 3 diga sobre que recorte ela foi calculada.
"""

from __future__ import annotations

import networkx as nx

from edugraph.contracts.types import BipartiteBundle, ProjectionBundle


def filter_cohort(bundle: BipartiteBundle, cohort: str) -> BipartiteBundle:
    """Subgrafo de uma apresentação (``"BBB_2013J"``).

    A redução preferida: recorta por uma unidade que faz sentido
    pedagógico, não por conveniência computacional.
    """
    raise NotImplementedError("A-06: ver docs/specs/frente-a/A-06-escala.md")


def sample_students(bundle: BipartiteBundle, n: int, *, seed: int) -> BipartiteBundle:
    """Amostra ``n`` alunos com semente fixa.

    Usada para viabilizar o Girvan-Newman (spec B-02). A semente vai
    para ``meta.json``, porque a amostra precisa ser reproduzível para
    o número entrar no artigo.
    """
    raise NotImplementedError("A-06: amostragem determinística")


def k_core(graph: nx.Graph, k: int) -> nx.Graph:
    """Núcleo-k da projeção: remove nós de grau baixo até estabilizar.

    Terceira redução, aplicada sobre a projeção e não sobre o bipartido.
    Muda a topologia de propósito, então a spec exige reportar quantos
    nós saíram.
    """
    raise NotImplementedError("A-06: núcleo-k")


def prune_by_weight(bundle: ProjectionBundle, min_weight: float) -> ProjectionBundle:
    """Corte por peso mínimo, registrado em ``ProjectionSpec.min_weight``.

    O validador de contrato confere que nenhuma aresta abaixo do corte
    sobreviveu, então o corte fica auditável no artefato.
    """
    raise NotImplementedError("A-06: corte por peso mínimo")
