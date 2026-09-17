"""Validação a posteriori das comunidades  ``[B]`` — spec B-06.

**Este é o único módulo da Frente B autorizado a ler ``outcomes.csv``.**
A restrição da seção 2 do briefing é a seguinte: rótulos históricos
entram só na validação, nunca como entrada de algoritmo. Um teste de
contrato (``tests/contract/test_outcomes_isolation.py``) falha se
:func:`edugraph.contracts.io.load_outcomes` for chamada de qualquer
módulo que não seja um ``evaluate.py``.

O que se valida aqui não é acurácia de um modelo — não há modelo. É se
uma estrutura descoberta **apenas pela topologia** guarda relação com o
desfecho conhecido. Se guardar, é achado; se não guardar, também é
achado, e o artigo reporta.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.types import Outcomes, Partition


def normalized_mutual_information(partition: Partition, planted_group: dict[str, int]) -> float:
    """NMI entre a partição encontrada e o grupo plantado.

    Só faz sentido no dataset sintético, onde o grupo plantado existe.
    A fixture ``synthetic_v1`` traz três grupos de 40 alunos com ruído
    de 35%, e a spec B-06 espera NMI ≥ 0,8 na projeção aluno↔aluno.

    Medida de teoria da informação entre duas partições conhecidas —
    não é aprendizado de máquina.
    """
    raise NotImplementedError("B-06: ver docs/specs/frente-b/B-06-validacao.md")


def purity(partition: Partition, planted_group: dict[str, int]) -> float:
    """Pureza: fração de acerto da comunidade majoritária de cada grupo."""
    raise NotImplementedError("B-06: pureza contra o ground truth")


def outcome_profile(partition: Partition, outcomes: Outcomes) -> list[dict[str, Any]]:
    """Distribuição de desfechos por comunidade.

    A tabela de validação do capítulo 3: se uma comunidade concentra
    ``Withdrawn`` muito acima da base, isso é um achado de gestão
    pedagógica obtido sem nenhum classificador.
    """
    raise NotImplementedError("B-06: desfecho por comunidade")
