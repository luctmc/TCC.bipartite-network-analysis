"""Estágio ``community`` do comando ``run``  ``[B]``.

Satisfaz :class:`~edugraph.contracts.protocols.Stage`.
"""

from __future__ import annotations

from pathlib import Path

# Registro das implementações da frente (ver nota em data/stage.py).
from edugraph.community import girvan_newman, louvain  # noqa: F401
from edugraph.contracts.registry import STAGES
from edugraph.contracts.types import RunConfig


class CommunityStage:
    """Roda os algoritmos de comunidade configurados sobre as projeções."""

    name = "community"

    def run(self, roots: list[Path], out: Path, config: RunConfig) -> list[Path]:
        """Executa a Frente B para uma configuração.

        Notes
        -----
        A implementar conforme B-01 e B-02 fecharem:

        1. Para cada projeção de ``config.projections``, carregar de
           ``roots`` — que podem ser fixtures.
        2. Para cada algoritmo de ``config.community``, resolver no
           registro e rodar com os parâmetros do TOML.
        3. Gravar a partição e, quando o bipartido existir, o
           ``profile.csv`` da B-05.
        4. Acrescentar as linhas a ``metrics/communities.csv``.
        """
        raise NotImplementedError("B-01/B-02: estágio 'community'")


STAGES.register("community", CommunityStage())
