"""Contratos entre as três frentes — **CONGELADO** após o dia 0.

Qualquer mudança neste subpacote exige ADR e aprovação dos três membros
do grupo (ver ADR-0001 e docs/contratos/README.md). Ele é a única
fronteira por onde as frentes se comunicam: tipos verificáveis por mypy,
um layout em disco lido e escrito só por :mod:`edugraph.contracts.io`, e
validadores executados pelos testes de contrato.
"""

from edugraph.contracts.types import (
    SCHEMA_VERSION,
    BipartiteBundle,
    BipartiteSpec,
    CentralityMetricName,
    CentralityResult,
    CommunityAlgorithmName,
    EdgeCriterion,
    Granularity,
    Meta,
    NodeKind,
    Outcomes,
    Partition,
    ProjectionBundle,
    ProjectionSpec,
    RunConfig,
    Weighting,
)

__all__ = [
    "SCHEMA_VERSION",
    "BipartiteBundle",
    "BipartiteSpec",
    "CentralityMetricName",
    "CentralityResult",
    "CommunityAlgorithmName",
    "ContractError",
    "EdgeCriterion",
    "Granularity",
    "Meta",
    "NodeKind",
    "Outcomes",
    "Partition",
    "ProjectionBundle",
    "ProjectionSpec",
    "RunConfig",
    "Weighting",
]

from edugraph.contracts.errors import ContractError
