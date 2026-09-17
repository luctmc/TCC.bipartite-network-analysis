"""Protocolos — as interfaces contra as quais cada frente programa.

O runner genérico e a API conhecem apenas estes ``Protocol``; nunca um
módulo concreto de frente. É o que permite ``__main__.py`` ser a única
raiz de composição do projeto (ADR-0003) e o que faz mypy conferir, sem
execução, que uma implementação registrada serve de fato ao contrato.

São protocolos estruturais: uma implementação não herda de nada, só
precisa ter os atributos e métodos com as assinaturas certas.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from edugraph.contracts.types import (
    BipartiteBundle,
    CentralityResult,
    Partition,
    ProjectionBundle,
    ProjectionSpec,
    RunConfig,
)


@runtime_checkable
class ProjectionAlgorithm(Protocol):
    """Transforma um bipartido numa projeção monopartida ponderada.

    Implementado por ``[A]`` em ``edugraph.data.projection`` — à mão
    (``manual``) e por NetworkX (``networkx_ref``), para a comparação
    que o artigo exige (spec A-05).
    """

    name: str

    def project(self, bipartite: BipartiteBundle, spec: ProjectionSpec) -> ProjectionBundle:
        """Projeta ``bipartite`` sobre o lado e a ponderação de ``spec``."""
        ...


@runtime_checkable
class CommunityAlgorithm(Protocol):
    """Particiona uma projeção em comunidades.

    Implementado por ``[B]`` em ``edugraph.community``. O contrato exige
    que uma execução interrompida por orçamento de tempo devolva uma
    :class:`~edugraph.contracts.types.Partition` com ``status="timeout"``
    em vez de levantar exceção (ADR-0006).
    """

    name: str

    def run(self, projection: ProjectionBundle, **params: Any) -> Partition:
        """Devolve a partição encontrada, com Q, k, tempo e status."""
        ...


@runtime_checkable
class CentralityMetric(Protocol):
    """Calcula uma métrica de centralidade sobre uma projeção.

    Implementado por ``[C]`` em ``edugraph.centrality``. ``compute``
    nunca levanta por falta de convergência: registra ``converged=False``
    e devolve o resultado do fallback (spec C-02).
    """

    name: str

    def compute(self, projection: ProjectionBundle, **params: Any) -> CentralityResult:
        """Devolve os scores por nó, com parâmetros e tempo."""
        ...


@runtime_checkable
class Stage(Protocol):
    """Um estágio do pipeline, tal como o comando ``run`` o enxerga.

    O comando ``python -m edugraph run configs/x.toml`` resolve os
    estágios pelo nome no registro e chama ``run`` em sequência. Um
    estágio lê o que precisa das ``roots`` e grava em ``out`` — nunca
    recebe objetos de outra frente.
    """

    name: str

    def run(self, roots: list[Path], out: Path, config: RunConfig) -> list[Path]:
        """Executa o estágio e devolve os caminhos dos artefatos gravados."""
        ...
