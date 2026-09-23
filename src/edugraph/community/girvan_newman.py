"""Girvan-Newman com orçamento de tempo  ``[B]`` — spec B-02.

Remoção iterativa das arestas de maior intermediação (Girvan; Newman,
2002). Complexidade O(m²n): no starter kit, sobre 120 nós, foi ~645×
mais lento que o Louvain, e sobre o OULAD completo não termina.

**O orçamento de tempo é decisão de arquitetura, não gambiarra**
(ADR-0006). Estourar o orçamento devolve uma
:class:`~edugraph.contracts.types.Partition` com ``status="timeout"`` e
a melhor partição obtida até ali. Isso é resultado a reportar no
capítulo 3 — a seção 8 do briefing pede exatamente isso.

Onde o relógio é consultado
---------------------------
A spec B-02 prevê a verificação **a cada corte**, porque o gerador do
NetworkX recalcula a intermediação de todas as arestas dentro de cada
iteração e não há como interrompê-lo de fora. Só que um corte custa
dezenas de remoções, cada uma com um cálculo sobre o grafo inteiro: em
``synthetic_v1``, o **primeiro** corte leva 15 s, e um orçamento de 1 s
seria respeitado com 14 s de atraso.

Por isso o relógio é consultado **também a cada remoção de aresta**, pela
função ``most_valuable_edge`` que o gerador chama (ver
:func:`_edge_to_remove`). O comportamento observável é o que a ADR-0006
decidiu — ``status="timeout"`` com a melhor partição vista, nunca
exceção —, e o orçamento passa a ser quase um limite duro: o atraso
máximo é o de um único cálculo de intermediação.

Estourar **antes do primeiro corte** devolve ``status="skipped"``, não
``"timeout"``: nada foi visto do dendrograma, e a partição devolvida é a
trivial. Para o OULAD, onde nem o primeiro corte cabe em orçamento
nenhum, a saída é ``sample_nodes`` (abaixo) ou a redução da spec A-06.

Intermediação sem peso, Q com peso
----------------------------------
A escolha da aresta a remover usa intermediação **não ponderada**: em
NetworkX, peso num caminho mínimo é distância, e nas projeções peso alto
significa mais afinidade, não mais distância (é a mesma inversão que a
spec C-01 discute). Já o Q reportado usa ``weight``, como o do Louvain —
senão as duas linhas da tabela do capítulo 3 não seriam comparáveis. As
duas escolhas ficam registradas em ``params``.

Amostragem e o id da projeção
-----------------------------
Com ``sample_nodes``, o algoritmo roda sobre um subgrafo e a partição
cobre **só** os nós amostrados. Para que isso nunca seja servido como se
fosse a partição da projeção inteira, o ``projection_id`` do artefato
ganha o sufixo ``__sample<N>``: a linha da tabela diz sobre que recorte
ela vale, e o validador de contrato não cruza uma partição parcial com a
projeção cheia. A redução definitiva é a da spec A-06, que gera um
dataset novo (``edugraph data sample --as …``).
"""

from __future__ import annotations

import math
import random
import time
from collections.abc import Callable
from typing import Any

import networkx as nx

from edugraph.community import check_params
from edugraph.community.modularity import groups_of, membership_of, modularity
from edugraph.contracts.errors import ContractError
from edugraph.contracts.registry import COMMUNITIES
from edugraph.contracts.types import Meta, Partition, ProjectionBundle

#: Id da spec, gravado em ``meta.producer`` de todo artefato daqui.
PRODUCER = "B-02"

#: Orçamento padrão, em segundos. Escolhido para caber numa sessão de
#: trabalho; a CI roda com valores muito menores, e a rodada final do
#: artigo usa o valor documentado em ``configs/``.
DEFAULT_TIME_BUDGET_S = 300.0

#: Semente da amostragem de nós. Fixa, para que o recorte seja o mesmo
#: entre execuções (ADR-0011).
DEFAULT_SEED = 42

#: Parâmetros aceitos em ``run`` (ver :func:`edugraph.community.check_params`).
ACCEPTED_PARAMS: frozenset[str] = frozenset(
    {"time_budget_s", "target_communities", "sample_nodes", "seed", "weight"}
)


def sample_nodes_subgraph(
    graph: nx.Graph[Any], n: int, *, seed: int = DEFAULT_SEED
) -> nx.Graph[Any]:
    """Subgrafo induzido por uma amostra determinística de ``n`` nós.

    Versão simples, suficiente para destravar a B-02 enquanto a spec
    A-06 não fecha (é o que a própria B-02 prevê). A amostra é sorteada
    sobre os nós **em ordem** e com semente explícita, de modo que duas
    execuções peguem exatamente os mesmos nós.

    Devolve o grafo inteiro quando ``n`` é maior ou igual ao número de
    nós — amostrar mais do que existe não é erro, é não amostrar.
    """
    nodes = sorted(graph.nodes)
    if n >= len(nodes):
        return graph
    if n < 1:
        raise ContractError(f"sample_nodes precisa ser >= 1; recebeu {n!r}")
    chosen = sorted(random.Random(seed).sample(nodes, n))
    return graph.subgraph(chosen).copy()


class _BudgetExceededError(Exception):
    """Sinal interno: o orçamento acabou no meio de um corte.

    Não escapa deste módulo — :meth:`GirvanNewmanAlgorithm.run` o captura
    e o converte em ``status="timeout"``. O contrato proíbe que um
    estouro de orçamento chegue ao chamador como exceção (ADR-0006).
    """


def _edge_to_remove(deadline: float) -> Callable[[nx.Graph[Any]], tuple[Any, Any]]:
    """A função ``most_valuable_edge`` que o gerador do NetworkX chama.

    Faz duas coisas que o padrão da biblioteca não faz:

    1. **Consulta o relógio a cada remoção**, e não só a cada corte. Um
       corte pode custar dezenas de remoções, cada uma com um cálculo de
       intermediação sobre o grafo inteiro; sem isto, o orçamento é
       verificado tarde demais e "300 s" vira meia hora. Reforça a
       ADR-0006 sem mudá-la: o comportamento observável continua sendo
       ``status="timeout"`` com a melhor partição vista.
    2. **Desempata pelo id da aresta.** O padrão da biblioteca é
       ``max(betweenness, key=betweenness.get)``, que em empate devolve a
       primeira na ordem de inserção do grafo — determinístico só
       enquanto ninguém reconstrói o grafo em outra ordem (ADR-0011).
    """

    def most_valuable_edge(graph: nx.Graph[Any]) -> tuple[Any, Any]:
        if time.perf_counter() > deadline:
            raise _BudgetExceededError
        betweenness = nx.edge_betweenness_centrality(graph, weight=None)
        return min(betweenness, key=lambda edge: (-betweenness[edge], edge))

    return most_valuable_edge


def _components_membership(graph: nx.Graph[Any]) -> dict[str, int]:
    """Partição de partida: uma comunidade por componente conexa.

    É a "partição trivial" do contrato — num grafo conexo, tudo numa
    comunidade só, com Q = 0. Num grafo já desconexo, as componentes,
    que é o que o Girvan-Newman devolveria antes de qualquer corte.
    """
    return membership_of([sorted(component) for component in nx.connected_components(graph)])


class GirvanNewmanAlgorithm:
    """Satisfaz :class:`~edugraph.contracts.protocols.CommunityAlgorithm`.

    Parameters aceitos em ``run``:

    ``time_budget_s`` : float
        Tempo máximo. Ao estourar, devolve ``status="timeout"``.
    ``target_communities`` : int | None
        Critério de parada por número de comunidades. Quando ``None``,
        para no melhor Q encontrado ao longo do dendrograma.
    ``sample_nodes`` : int | None
        Amostra de nós, com ``seed``, para viabilizar grafos grandes
        (ver :mod:`edugraph.data.scale`, spec A-06).
    ``seed`` : int
        Semente da amostragem.
    ``weight`` : str | None
        Atributo de peso usado **no cálculo de Q**. A intermediação que
        escolhe a aresta a remover é sempre não ponderada.
    """

    name = "girvan_newman"

    def run(self, projection: ProjectionBundle, **params: Any) -> Partition:
        """Particiona por remoção de arestas, respeitando o orçamento.

        Nunca levanta por estouro de orçamento: o contrato proíbe
        (ADR-0006). As únicas exceções possíveis são de parâmetro
        inválido ou projeção vazia, que são erro de chamada.
        """
        check_params(params, ACCEPTED_PARAMS, "GirvanNewmanAlgorithm.run")

        budget = float(params.get("time_budget_s", DEFAULT_TIME_BUDGET_S))
        target = params.get("target_communities")
        target_communities = int(target) if target is not None else None
        sample = params.get("sample_nodes")
        sample_nodes = int(sample) if sample is not None else None
        seed = int(params.get("seed", DEFAULT_SEED))
        weight = params.get("weight", "weight")

        full_graph = projection.graph
        if full_graph.number_of_nodes() == 0:
            raise ContractError(
                f"Girvan-Newman: projeção {projection.projection_id!r} não tem nós; "
                "não há o que particionar"
            )

        graph = full_graph
        projection_id = projection.projection_id
        if sample_nodes is not None and sample_nodes < full_graph.number_of_nodes():
            graph = sample_nodes_subgraph(full_graph, sample_nodes, seed=seed)
            # Ver a nota do módulo: partição parcial nunca usa o id da
            # projeção cheia.
            projection_id = f"{projection_id}__sample{graph.number_of_nodes()}"

        record: dict[str, Any] = {
            "time_budget_s": budget,
            "target_communities": target_communities,
            "sample_nodes": sample_nodes,
            "seed": seed,
            "weight": weight,
            "betweenness_weight": None,
            "implementation": "networkx",
            "source_projection_id": projection.projection_id,
            "n_nodes": graph.number_of_nodes(),
            "n_edges": graph.number_of_edges(),
        }

        trivial = _components_membership(graph)
        if graph.number_of_edges() == 0:
            # Sem aresta não há o que remover; as componentes já são a
            # resposta, e Q = 0 por definição.
            return self._partition(
                projection_id, trivial, graph, weight, 0.0, "ok", record, cuts=0,
                stop_reason="no_edges",
            )  # fmt: skip

        if budget <= 0:
            return self._partition(
                projection_id, trivial, graph, weight, 0.0, "skipped", record, cuts=0,
                stop_reason="time_budget",
            )  # fmt: skip

        best_membership: dict[str, int] | None = None
        best_q = -math.inf
        cuts = 0
        status: str = "ok"
        stop_reason = "dendrogram_exhausted"

        start = time.perf_counter()
        deadline = start + budget
        try:
            for communities in nx.community.girvan_newman(
                graph, most_valuable_edge=_edge_to_remove(deadline)
            ):
                cuts += 1
                membership = membership_of([sorted(nodes) for nodes in communities])
                q = modularity(graph, membership, weight=weight)
                # Estritamente maior: em caso de empate fica o corte mais
                # raso, que é o determinístico e o mais barato de explicar.
                if q > best_q:
                    best_q, best_membership = q, membership

                if target_communities is not None and len(communities) >= target_communities:
                    best_membership, best_q = membership, q
                    stop_reason = "target_communities"
                    break

                if time.perf_counter() > deadline:
                    stop_reason = "time_budget"
                    status = "timeout" if cuts > 1 else "skipped"
                    break

                if len(communities) >= graph.number_of_nodes():
                    stop_reason = "dendrogram_exhausted"
                    break
        except _BudgetExceededError:
            # Estouro no meio de um corte: o que estava pronto até o
            # corte anterior vale; o corte em andamento é descartado.
            stop_reason = "time_budget"
            status = "timeout" if cuts >= 1 else "skipped"

        runtime_s = time.perf_counter() - start

        if status == "skipped" or best_membership is None:
            best_membership, best_q = trivial, 0.0

        record["n_cuts"] = cuts
        record["stop_reason"] = stop_reason
        return self._partition(
            projection_id, best_membership, graph, weight, runtime_s, status, record,
            cuts=cuts, stop_reason=stop_reason, q=best_q,
        )  # fmt: skip

    @staticmethod
    def _partition(
        projection_id: str,
        membership: dict[str, int],
        graph: nx.Graph[Any],
        weight: str | None,
        runtime_s: float,
        status: str,
        params: dict[str, Any],
        *,
        cuts: int,
        stop_reason: str,
        q: float | None = None,
    ) -> Partition:
        """Monta a :class:`Partition`, com Q e estatísticas coerentes."""
        groups = groups_of(membership)
        modularity_value = modularity(graph, membership, weight=weight) if q is None else q
        record = {**params, "n_cuts": cuts, "stop_reason": stop_reason}
        meta = Meta(
            producer=PRODUCER,
            stats={
                "n_nodes": graph.number_of_nodes(),
                "n_edges": graph.number_of_edges(),
                "largest_community": max((len(n) for n in groups.values()), default=0),
                "n_singletons": sum(1 for nodes in groups.values() if len(nodes) == 1),
                "n_cuts": cuts,
            },
            notes=(
                "Girvan-Newman (2002) pelo gerador do NetworkX, com orçamento de tempo "
                "(ADR-0006). Estouro é resultado a reportar, não falha."
            ),
        )
        return Partition(
            algorithm="girvan_newman",
            projection_id=projection_id,
            membership=membership,
            modularity=modularity_value,
            n_communities=len(groups),
            runtime_s=max(runtime_s, 0.0),
            params=record,
            status=status,  # type: ignore[arg-type]
            meta=meta,
        )


COMMUNITIES.register("girvan_newman", GirvanNewmanAlgorithm())
