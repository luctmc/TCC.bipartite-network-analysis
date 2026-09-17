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
    """ETL → bipartido → projeções, gravando sob ``out``."""

    name = "data"

    def run(self, roots: list[Path], out: Path, config: RunConfig) -> list[Path]:
        """Executa a Frente A inteira para uma configuração.

        Notes
        -----
        A implementar conforme as specs A-01 a A-04 forem fechando:

        1. Carregar a fonte declarada em ``config.source`` (sintética ou
           OULAD).
        2. ``build_bipartite(table, config.bipartite)`` e gravar.
        3. Para cada ``ProjectionSpec`` de ``config.projections``,
           projetar e gravar.
        4. Gravar ``outcomes.csv`` e devolver os caminhos escritos.
        """
        raise NotImplementedError(
            "A-03/A-04: estágio 'data'. Até lá, use --from community sobre artefatos "
            "já existentes em disco (fixtures ou data/processed)."
        )


STAGES.register("data", DataStage())
