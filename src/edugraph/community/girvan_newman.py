"""Girvan-Newman com orçamento de tempo  ``[B]`` — spec B-02.

Remoção iterativa das arestas de maior intermediação (Girvan; Newman,
2002). Complexidade O(m²n): no starter kit, sobre 120 nós, foi ~645×
mais lento que o Louvain, e sobre o OULAD completo não termina.

**O orçamento de tempo é decisão de arquitetura, não gambiarra**
(ADR-0006). Estourar o orçamento devolve uma
:class:`~edugraph.contracts.types.Partition` com ``status="timeout"`` e
a melhor partição obtida até ali. Isso é resultado a reportar no
capítulo 3 — a seção 8 do briefing pede exatamente isso.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.registry import COMMUNITIES
from edugraph.contracts.types import Partition, ProjectionBundle

#: Orçamento padrão, em segundos. Escolhido para caber numa sessão de
#: trabalho; a CI roda com valores muito menores, e a rodada final do
#: artigo usa o valor documentado em ``configs/``.
DEFAULT_TIME_BUDGET_S = 300.0


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
    """

    name = "girvan_newman"

    def run(self, projection: ProjectionBundle, **params: Any) -> Partition:
        """Particiona por remoção de arestas, respeitando o orçamento.

        Notes
        -----
        A implementar em B-02:

        1. Consumir ``nx.community.girvan_newman`` como iterador,
           checando o relógio **a cada corte** — não dá para interromper
           depois que o gerador entrou numa iteração longa.
        2. Guardar a melhor partição por Q vista até o momento.
        3. Ao estourar o orçamento, devolver essa melhor partição com
           ``status="timeout"`` e registrar em ``params`` quantos cortes
           foram feitos. **Não levantar exceção**: o contrato proíbe.
        4. Se nem o primeiro corte couber no orçamento, devolver
           ``status="skipped"`` com a partição trivial (tudo em uma só
           comunidade) e Q = 0.
        """
        raise NotImplementedError("B-02: ver docs/specs/frente-b/B-02-girvan-newman.md")


COMMUNITIES.register("girvan_newman", GirvanNewmanAlgorithm())
