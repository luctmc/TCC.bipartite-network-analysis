"""Louvain  ``[B]`` — spec B-01.

Otimização gulosa de modularidade (Blondel et al., 2008). Rápido o
bastante para a base inteira, o que faz dele a linha de base contra a
qual o Girvan-Newman é comparado em custo (spec B-04).

**Sem IA.** Louvain é otimização combinatória sobre a estrutura do
grafo, não aprendizado: não há treino, não há rótulo, e o resultado é
rastreável até as arestas. É o que a seção 2 do briefing exige.

Implementação principal: ``python-louvain`` (``community_louvain``), com
``nx.community.louvain_communities`` disponível para comparação — as
duas estão nos requirements e a spec B-01 compara as duas.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.registry import COMMUNITIES
from edugraph.contracts.types import Partition, ProjectionBundle

#: Semente padrão. Louvain é estocástico na ordem de visita dos nós;
#: sem semente fixa, duas execuções dão partições diferentes e nenhuma
#: tabela do artigo é reproduzível (ADR-0011).
DEFAULT_SEED = 42

#: Resolução padrão do método. Valores > 1 favorecem comunidades menores.
DEFAULT_RESOLUTION = 1.0


class LouvainAlgorithm:
    """Satisfaz :class:`~edugraph.contracts.protocols.CommunityAlgorithm`.

    Parameters aceitos em ``run``:

    ``seed`` : int
        Semente do gerador. Padrão :data:`DEFAULT_SEED`.
    ``resolution`` : float
        Resolução da modularidade. Padrão :data:`DEFAULT_RESOLUTION`.
    ``implementation`` : {"python_louvain", "networkx"}
        Qual biblioteca usar. A comparação entre as duas é parte da B-01.
    """

    name = "louvain"

    def run(self, projection: ProjectionBundle, **params: Any) -> Partition:
        """Particiona a projeção e devolve Q, k, tempo e status.

        Notes
        -----
        A implementar em B-01:

        1. Rodar ``community_louvain.best_partition(G, weight="weight",
           random_state=seed)``.
        2. **Densificar os ids** de comunidade para ``0..k-1`` — o
           validador de contrato exige, e a biblioteca não garante.
        3. Medir ``runtime_s`` com ``time.perf_counter``.
        4. Calcular Q com :func:`edugraph.community.modularity.modularity`
           (implementação à mão da B-03), não com a da biblioteca — e a
           B-03 é que confere que as duas batem.
        5. Registrar ``seed``, ``resolution`` e ``implementation`` em
           ``params``, porque eles vão para a tabela do capítulo 3.
        """
        raise NotImplementedError("B-01: ver docs/specs/frente-b/B-01-louvain.md")


COMMUNITIES.register("louvain", LouvainAlgorithm())
