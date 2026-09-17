"""Implementações registradas satisfazem seus protocolos  ``[T]``.

O runner e a API resolvem algoritmos por nome no registro. Se uma
implementação registrada não tiver a assinatura do protocolo, o erro só
apareceria na execução — e provavelmente na semana da entrega. Aqui ele
aparece na CI.

O ``mypy`` faz a checagem estática das assinaturas; este teste faz a
checagem estrutural em tempo de execução e garante que o registro está
povoado com o que se espera dele.
"""

from __future__ import annotations

import pytest

from edugraph.contracts.errors import ContractError
from edugraph.contracts.protocols import (
    CentralityMetric,
    CommunityAlgorithm,
    ProjectionAlgorithm,
    Stage,
)
from edugraph.contracts.registry import (
    CENTRALITIES,
    COMMUNITIES,
    PROJECTIONS,
    STAGES,
    load_builtin_implementations,
)


@pytest.fixture(scope="module", autouse=True)
def _load() -> None:
    """Povoa o registro uma vez para o módulo inteiro."""
    load_builtin_implementations()


def test_registros_esperados_existem() -> None:
    """Os nomes que os TOML de ``configs/`` usam estão registrados."""
    assert set(STAGES.names()) == {"data", "community", "centrality"}
    assert {"louvain", "girvan_newman"} <= set(COMMUNITIES.names())
    assert {"degree", "betweenness", "eigenvector"} <= set(CENTRALITIES.names())
    assert {"manual_simple", "manual_resource_allocation"} <= set(PROJECTIONS.names())
    assert {"networkx_simple", "networkx_resource_allocation"} <= set(PROJECTIONS.names())


@pytest.mark.parametrize("name", ["manual_simple", "manual_resource_allocation"])
def test_projecoes_satisfazem_o_protocolo(name: str) -> None:
    implementation = PROJECTIONS.get(name)
    assert isinstance(implementation, ProjectionAlgorithm)
    assert implementation.name == name


@pytest.mark.parametrize("name", ["louvain", "girvan_newman"])
def test_comunidades_satisfazem_o_protocolo(name: str) -> None:
    implementation = COMMUNITIES.get(name)
    assert isinstance(implementation, CommunityAlgorithm)
    assert implementation.name == name


@pytest.mark.parametrize("name", ["degree", "betweenness", "eigenvector"])
def test_centralidades_satisfazem_o_protocolo(name: str) -> None:
    implementation = CENTRALITIES.get(name)
    assert isinstance(implementation, CentralityMetric)
    assert implementation.name == name


@pytest.mark.parametrize("name", ["data", "community", "centrality"])
def test_estagios_satisfazem_o_protocolo(name: str) -> None:
    stage = STAGES.get(name)
    assert isinstance(stage, Stage)
    assert stage.name == name


def test_nome_desconhecido_da_erro_util() -> None:
    """A mensagem lista o que existe, em vez de só dizer 'KeyError'."""
    with pytest.raises(ContractError) as excinfo:
        COMMUNITIES.get("leiden")
    message = str(excinfo.value)
    assert "leiden" in message
    assert "louvain" in message


def test_registro_duplicado_e_conflito_explicito() -> None:
    """Duas frentes registrando o mesmo nome falha agora, não depois."""
    from edugraph.contracts.registry import Registry

    registry: Registry[object] = Registry("teste")
    registry.register("x", object())
    with pytest.raises(ContractError, match="já registrado"):
        registry.register("x", object())
    registry.register("x", object(), replace=True)  # intencional, permitido
