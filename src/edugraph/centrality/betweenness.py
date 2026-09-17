"""Centralidade de intermediação  ``[C]`` — spec C-01.

Fração dos caminhos mínimos que passam por um nó. É a métrica que o
objetivo declarado na Introdução associa a "gargalos no fluxo
educacional": uma disciplina de alta intermediação liga partes do
currículo que, sem ela, ficariam distantes.

Via ``nx.betweenness_centrality``, que usa Brandes (2001) internamente.
Não é implementada à mão: o custo didático é alto e o retorno baixo
perto das outras duas implementações manuais do projeto (ADR-0010).

**Cuidado com o peso.** Em NetworkX, ``weight`` num caminho mínimo é
*distância*, não afinidade: peso alto vira caminho longo. Como nas
projeções peso alto significa *mais* afinidade, a spec C-01 precisa
decidir e registrar se inverte o peso (``1/w``) ou roda sem peso.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.registry import CENTRALITIES
from edugraph.contracts.types import CentralityResult, ProjectionBundle


class BetweennessCentrality:
    """Satisfaz :class:`~edugraph.contracts.protocols.CentralityMetric`.

    Parameters aceitos em ``compute``:

    ``normalized`` : bool
        Padrão ``True``.
    ``weight_mode`` : {"none", "inverse", "raw"}
        Como tratar o peso da projeção como distância. Vai para
        ``params`` e para a legenda da tabela, porque muda o ranking.
    ``k`` : int | None
        Amostragem de pivôs para grafos grandes; com ``seed``, é
        determinística. Estimativa, e a tabela precisa dizer isso.
    """

    name = "betweenness"

    def compute(self, projection: ProjectionBundle, **params: Any) -> CentralityResult:
        raise NotImplementedError("C-01: ver docs/specs/frente-c/C-01-grau-intermediacao.md")


CENTRALITIES.register("betweenness", BetweennessCentrality())
