"""Registro de algoritmos e estágios por nome.

Cada frente registra suas implementações; o runner e a API resolvem por
string. É a indireção que permite ``__main__.py`` compor as três frentes
sem que nenhuma delas conheça as outras (ADR-0003), e é também o que faz
``--algorithm louvain`` virar um parâmetro de configuração em vez de um
``if`` espalhado pelo código.

O registro é povoado por :func:`load_builtin_implementations`, chamada
uma vez pela raiz de composição. Nenhum módulo de frente a chama.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from edugraph.contracts.errors import ContractError

T = TypeVar("T")


class Registry(Generic[T]):
    """Um dicionário de nome → implementação, com erro legível."""

    def __init__(self, what: str) -> None:
        self._what = what
        self._items: dict[str, T] = {}

    def register(self, name: str, item: T, *, replace: bool = False) -> T:
        """Registra ``item`` sob ``name``.

        Raises
        ------
        ContractError
            Se o nome já estiver ocupado e ``replace`` for falso. Duas
            frentes registrando o mesmo nome é um conflito de merge que
            precisa aparecer agora, não em produção.
        """
        if name in self._items and not replace:
            raise ContractError(
                f"{self._what} {name!r} já registrado por {self._items[name]!r}; "
                "use replace=True se a substituição for intencional"
            )
        self._items[name] = item
        return item

    def get(self, name: str) -> T:
        try:
            return self._items[name]
        except KeyError:
            disponiveis = ", ".join(sorted(self._items)) or "(nenhum)"
            raise ContractError(
                f"{self._what} {name!r} não registrado. Disponíveis: {disponiveis}"
            ) from None

    def names(self) -> list[str]:
        return sorted(self._items)

    def __contains__(self, name: object) -> bool:
        return name in self._items

    def __len__(self) -> int:
        return len(self._items)

    def decorator(self, name: str) -> Callable[[T], T]:
        """Açúcar para registrar uma classe ou função na definição."""

        def wrap(item: T) -> T:
            self.register(name, item)
            return item

        return wrap


#: Projeções: ``simple``, ``resource_allocation``, ``networkx_simple``…  [A]
PROJECTIONS: Registry[object] = Registry("algoritmo de projeção")

#: Comunidades: ``louvain``, ``girvan_newman``.  [B]
COMMUNITIES: Registry[object] = Registry("algoritmo de comunidade")

#: Centralidades: ``degree``, ``betweenness``, ``eigenvector``.  [C]
CENTRALITIES: Registry[object] = Registry("métrica de centralidade")

#: Estágios do comando ``run``: ``data``, ``community``, ``centrality``.  [T]
STAGES: Registry[object] = Registry("estágio")


def clear_all() -> None:
    """Esvazia todos os registros — usado entre testes."""
    for registry in (PROJECTIONS, COMMUNITIES, CENTRALITIES, STAGES):
        registry._items.clear()


def load_builtin_implementations() -> None:
    """Importa os módulos de frente para que eles se registrem.

    **Este é o único ponto do projeto que importa as três frentes**, e
    ele vive no pacote de contratos justamente para que a raiz de
    composição seja trivial. O teste
    ``tests/contract/test_import_boundaries.py`` isenta este arquivo e
    ``__main__.py``, e nenhum outro.

    Carregar o estágio de uma frente registra também os algoritmos dela,
    porque cada ``stage.py`` importa os seus (imports internos à frente,
    permitidos pela ADR-0003).

    Importações tardias e tolerantes: uma frente que não importe não pode
    derrubar as outras. Mas o problema é **avisado**, nunca engolido em
    silêncio — um registro vazio se manifestaria depois como "algoritmo
    não registrado", longe da causa.
    """
    import importlib
    import warnings

    for module in (
        "edugraph.data.stage",
        "edugraph.community.stage",
        "edugraph.centrality.stage",
    ):
        try:
            importlib.import_module(module)
        except ImportError as error:  # pragma: no cover - bug de import numa frente
            warnings.warn(
                f"não foi possível carregar {module}: {error}. "
                "As implementações dessa frente não estarão registradas.",
                RuntimeWarning,
                stacklevel=2,
            )
