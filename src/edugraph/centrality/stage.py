"""Estágio ``centrality`` do comando ``run``  ``[C]``.

Satisfaz :class:`~edugraph.contracts.protocols.Stage`.
"""

from __future__ import annotations

from pathlib import Path

# Registro das implementações da frente (ver nota em data/stage.py).
from edugraph.centrality import betweenness, degree, eigenvector  # noqa: F401
from edugraph.contracts.registry import STAGES
from edugraph.contracts.types import RunConfig


class CentralityStage:
    """Calcula as métricas configuradas sobre todas as projeções."""

    name = "centrality"

    def run(self, roots: list[Path], out: Path, config: RunConfig) -> list[Path]:
        """Executa a Frente C para uma configuração.

        Notes
        -----
        A implementar conforme C-01 a C-03 fecharem:

        1. Para cada projeção de ``config.projections``, carregar de
           ``roots``.
        2. Para cada métrica de ``config.centrality``, resolver no
           registro e calcular.
        3. Gravar os ``CentralityResult`` e acrescentar as linhas a
           ``metrics/centrality_top.csv`` — as das projeções
           ``discipline_*`` são as disciplinas críticas.
        """
        raise NotImplementedError("C-01/C-02: estágio 'centrality'")


STAGES.register("centrality", CentralityStage())
