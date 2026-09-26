"""Conferência de parâmetros comum às métricas da Frente C  ``[C]``.

Um parâmetro com nome errado no TOML (``weigth_mode``) não pode passar em
silêncio: a métrica rodaria com o padrão e a legenda da tabela diria o
contrário do que foi calculado.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from edugraph.contracts.errors import ContractError


def check_params(params: dict[str, Any], accepted: Iterable[str], where: str) -> None:
    """Recusa parâmetros que a métrica não conhece.

    Raises
    ------
    ContractError
        Com a lista do que sobrou e do que é aceito.
    """
    allowed = set(accepted)
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise ContractError(
            f"{where}: parâmetros desconhecidos {unknown}; aceitos: {sorted(allowed)}"
        )
