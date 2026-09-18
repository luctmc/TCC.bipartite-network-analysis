"""Estágio ``data`` do comando ``run``  ``[A]``.

Satisfaz :class:`~edugraph.contracts.protocols.Stage`. Registrado sob o
nome ``data``; o runner nunca importa este módulo diretamente, resolve-o
pelo registro.
"""

from __future__ import annotations

from pathlib import Path

from edugraph.contracts.registry import STAGES
from edugraph.contracts.types import RunConfig

# Importados pelo efeito colateral do registro: ao carregar o estágio da
# frente, as suas implementações passam a ser resolvíveis por nome. São
# imports internos à própria frente, permitidos pela ADR-0003.
from edugraph.data.projection import manual, networkx_ref  # noqa: F401


class DataStage:
    """Fonte → bipartido → outcomes → projeções, gravando sob ``out``.

    A lógica vive em :func:`edugraph.data.pipeline.run_data_stage`, que
    é compartilhada com os comandos ``data bipartite`` e ``data synthetic``.
    """

    name = "data"

    def run(self, roots: list[Path], out: Path, config: RunConfig) -> list[Path]:
        from edugraph.data.pipeline import run_data_stage

        # ``roots`` não é usado: a Frente A é a origem do pipeline e lê só
        # a fonte declarada em ``config.source``, nunca artefatos.
        return run_data_stage(config, out)


STAGES.register("data", DataStage())
