"""Validação a posteriori da centralidade  ``[C]`` — spec C-06.

**Único módulo da Frente C autorizado a ler ``outcomes.csv``** (ADR-0008,
mesma regra de :mod:`edugraph.community.evaluate`).

A pergunta: as disciplinas que a topologia aponta como gargalo têm, de
fato, taxa de reprovação acima da base? E alunos de alta centralidade
têm desfecho diferente? Se sim, a estrutura tem valor prático; se não, o
artigo reporta que a centralidade estrutural e o desempenho histórico
são dimensões independentes — o que também é um achado.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.types import CentralityResult, Outcomes


def failure_rate_by_discipline(
    ranking: list[str], outcomes: Outcomes, enrollment: dict[str, list[str]]
) -> list[dict[str, Any]]:
    """Taxa de reprovação nas disciplinas críticas × nas demais.

    Parameters
    ----------
    ranking
        Disciplinas em ordem de centralidade (saída da C-03).
    outcomes
        Desfechos históricos.
    enrollment
        Disciplina → alunos, derivado do bipartido.
    """
    raise NotImplementedError("C-06: ver docs/specs/frente-c/C-06-validacao-centralidade.md")


def outcome_by_centrality(
    result: CentralityResult, outcomes: Outcomes, *, quantiles: int = 4
) -> list[dict[str, Any]]:
    """Distribuição de desfechos por quartil de centralidade do aluno.

    Tabela + figura do capítulo 3. Agrupar por quartil é estatística
    descritiva sobre uma variável calculada da topologia — nenhum
    classificador envolvido.
    """
    raise NotImplementedError("C-06: desfecho por faixa de centralidade")
