"""Erro único do pacote de contratos."""

from __future__ import annotations


class ContractError(Exception):
    """Violação de um invariante de contrato.

    Levantado por :mod:`edugraph.contracts.validate` e por
    :mod:`edugraph.contracts.io` quando um artefato em disco não
    satisfaz o que a seção 4.4 do plano de arquitetura exige. Carrega
    sempre o que foi violado e onde, porque a mensagem aparece na saída
    dos testes de contrato.
    """


class ArtifactNotFoundError(ContractError):
    """Artefato ausente em todas as raízes consultadas."""
