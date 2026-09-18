"""Modelo nulo: o mesmo grafo sem estrutura  ``[A]`` — spec A-08.

Por que isto existe
-------------------
A modularidade encontra "comunidades" em **qualquer** grafo esparso,
inclusive em grafos sem nenhuma estrutura (Guimerà et al., 2004). Um
Q = 0,77 no OULAD, sozinho, não é evidência de que existam perfis de
alunos: pode ser só o que a otimização produz naquela distribuição de
grau.

O modelo nulo resolve isso. Ele embaralha **quem cursou o quê**,
preservando exatamente quantas disciplinas cada aluno cursou e
aproximadamente quantos alunos cada disciplina teve. Rodar o mesmo
Louvain nele dá a linha de base: se o Q real não for maior que o Q nulo,
o Q real não significa nada.

Medido em 18/09/2026, projeção aluno↔aluno:

=====================  ========  ==========================  ==========
dataset                 Q real    Q nulo (média ± dp)         veredito
=====================  ========  ==========================  ==========
``synthetic_v1``         0,4666   0,2079 ± 0,0168 (z=+15,4)   estrutura
``synthetic_v2``         0,5392   0,4611 ± 0,0202 (z=+3,9)    estrutura
OULAD ``module_pres.``   0,7728   0,781 (2 réplicas)          **acaso**
=====================  ========  ==========================  ==========

Ou seja: o método **discrimina** — no sintético com grupos plantados o Q
real fica muito acima do nulo. E no OULAD **não há o que discriminar**.
Esse é o resultado, e é ele que impede o trabalho de afirmar o que os
dados não sustentam.

Esta frente só **gera o artefato nulo**; quem calcula Q e compara é a
Frente B (spec B-06), como manda a fronteira da ADR-0003.

O que é preservado, e o que não é
----------------------------------
Preservado exatamente
    O conjunto de alunos, o conjunto de disciplinas, o grau de cada
    aluno (quantas disciplinas cursou) e o número total de arestas.
Preservado em expectativa
    O grau de cada disciplina — as disciplinas são sorteadas de uma urna
    em que cada uma aparece proporcionalmente ao seu grau real.
Destruído de propósito
    Qualquer relação entre alunos: quem estuda com quem passa a ser
    sorteio. É exatamente isso que se quer destruir.

Peso da aresta
    Uniforme (``1.0``). O nulo é sobre a **topologia**; carregar notas
    sorteadas junto criaria um segundo efeito confundido com o primeiro.
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Any

import networkx as nx

from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import BipartiteBundle, Meta

#: Id da spec, gravado em ``meta.producer``.
PRODUCER = "A-08"

#: Peso das arestas do nulo. Ver a nota do módulo.
NULL_EDGE_WEIGHT = 1.0

#: Tentativas por aluno antes de desistir de completar o grau dele. Só
#: importa em grafos muito desbalanceados (poucas disciplinas, alunos de
#: grau alto), onde a urna repete muito.
_MAX_DRAWS_PER_EDGE = 200


def null_bipartite(
    bundle: BipartiteBundle, *, seed: int, dataset: str | None = None
) -> BipartiteBundle:
    """Devolve um bipartido com os mesmos graus e nenhuma estrutura.

    Parameters
    ----------
    bundle
        O bipartido real, que serve de molde.
    seed
        Semente do sorteio. Réplicas diferentes usam sementes diferentes;
        a semente vai para ``meta.stats`` para que a réplica seja
        reproduzível.
    dataset
        Nome do dataset gerado. O padrão acrescenta ``_null<seed>`` ao
        nome do original — assim as réplicas convivem em disco.

    Returns
    -------
    BipartiteBundle
        Mesmos nós, mesmos graus de aluno, arestas sorteadas.

    Raises
    ------
    ContractError
        Se algum dos dois lados estiver vazio.
    """
    graph = bundle.graph
    students = sorted(bundle.students)
    disciplines = sorted(bundle.disciplines)

    if not students or not disciplines:
        raise ContractError("modelo nulo exige os dois lados não vazios")

    # Não há guarda de "grau maior que o nº de disciplinas": num grafo
    # simples o aluno se liga a disciplinas distintas, então
    # grau(aluno) <= |disciplinas| por construção. O caso que precisa de
    # tratamento é outro — a urna concentrada —, resolvido no laço.

    # Urna ponderada pelo grau da disciplina: sortear dela mantém o
    # tamanho relativo das disciplinas, em expectativa.
    urn = [d for d in disciplines for _ in range(graph.degree(d))]
    rng = random.Random(seed)

    null: nx.Graph[Any] = nx.Graph()
    for node in disciplines:
        null.add_node(node, kind="discipline", label=graph.nodes[node].get("label", node))
    for student in students:
        null.add_node(student, kind="student", label=graph.nodes[student].get("label", student))
        degree = graph.degree(student)
        chosen: set[str] = set()
        draws = 0
        limit = degree * _MAX_DRAWS_PER_EDGE
        while len(chosen) < degree and draws < limit:
            chosen.add(rng.choice(urn))
            draws += 1
        if len(chosen) < degree:
            # Urna muito concentrada: completa uniformemente, para não
            # devolver um aluno com grau menor que o real.
            restantes = [d for d in disciplines if d not in chosen]
            chosen.update(rng.sample(restantes, degree - len(chosen)))
        for discipline in chosen:
            null.add_edge(student, discipline, weight=NULL_EDGE_WEIGHT)

    name = dataset or f"{bundle.spec.dataset}_null{seed}"
    meta = Meta(
        producer=PRODUCER,
        stats={
            "null_model": {
                "source_dataset": bundle.spec.dataset,
                "method": "degree_preserving_urn",
                "seed": seed,
                "n_students": len(students),
                "n_disciplines": len(disciplines),
                "n_edges_source": graph.number_of_edges(),
                "n_edges": null.number_of_edges(),
            }
        },
        notes=(
            "Modelo nulo (spec A-08): mesmos graus de aluno, arestas sorteadas. "
            "NÃO são dados reais — serve só de linha de base para a modularidade "
            "(spec B-06). Nunca misturar com o dataset de origem."
        ),
    )
    return BipartiteBundle(
        graph=null, spec=replace(bundle.spec, dataset=name, seed=seed), meta=meta
    )


def null_replicas(bundle: BipartiteBundle, *, n: int, seed: int = 0) -> list[BipartiteBundle]:
    """``n`` réplicas do nulo, com sementes ``seed, seed+1, …``.

    Uma réplica só dá um número; a comparação honesta precisa da média e
    do desvio de várias, para dizer quantos desvios o Q real está acima
    do acaso. Cinco já dão um desvio utilizável.
    """
    if n < 1:
        raise ContractError(f"n precisa ser >= 1; recebeu {n!r}")
    return [null_bipartite(bundle, seed=seed + i) for i in range(n)]


def is_null(bundle: BipartiteBundle) -> bool:
    """``True`` se o artefato foi gerado por este módulo.

    Existe para que a Frente B possa distinguir, sem adivinhar pelo nome,
    um dataset nulo de um real ao montar a tabela de validação.
    """
    return "null_model" in bundle.meta.stats
