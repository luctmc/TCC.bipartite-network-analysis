"""Centralidade de grau  ``[C]`` — spec C-01.

A mais simples das três e a linha de base contra a qual as outras duas
são lidas: um nó pode ter grau alto e intermediação baixa (popular, mas
não ponte), e é dessa discordância que sai a discussão da spec C-03.

Duas variantes, ambas registradas: ``degree`` (contagem de vizinhos,
normalizada por n−1) e a força ponderada, que soma os pesos. A spec
C-01 decide qual vai para o artigo e registra o porquê.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.registry import CENTRALITIES
from edugraph.contracts.types import CentralityResult, ProjectionBundle


class DegreeCentrality:
    """Satisfaz :class:`~edugraph.contracts.protocols.CentralityMetric`.

    Parameters aceitos em ``compute``:

    ``normalized`` : bool
        Divide por n−1. Padrão ``True`` — o validador de contrato exige
        scores em [0, 1] quando este parâmetro é verdadeiro.
    ``weight`` : str | None
        ``"weight"`` para a força ponderada, ``None`` para a contagem.
    """

    name = "degree"

    def compute(self, projection: ProjectionBundle, **params: Any) -> CentralityResult:
        """Notes
        -----
        A implementar em C-01: ``nx.degree_centrality`` para a contagem;
        para a força ponderada não há função pronta equivalente, então
        somar os pesos e normalizar pela maior força, registrando a
        escolha de normalização em ``params``.
        """
        raise NotImplementedError("C-01: ver docs/specs/frente-c/C-01-grau-intermediacao.md")


CENTRALITIES.register("degree", DegreeCentrality())
