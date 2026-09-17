"""Centralidade de autovetor por iteração de potência  ``[C]`` — spec C-02.

Terceira implementação à mão do projeto (ADR-0010). Um nó é central se
está ligado a nós centrais: ``x = (1/λ) A x``, resolvido iterando
``x ← A x / ‖A x‖`` até convergir.

Comparada com ``nx.eigenvector_centrality`` na própria spec.

**Convergência não é garantida.** Em grafo desconexo — e a projeção
aluno↔aluno do OULAD tende a ser —, a iteração pode não convergir. O
contrato exige que isso vire ``converged=False`` no artefato e queda
para o cálculo direto por autovalores, nunca uma exceção que derrube o
pipeline.
"""

from __future__ import annotations

from typing import Any

from edugraph.contracts.registry import CENTRALITIES
from edugraph.contracts.types import CentralityResult, ProjectionBundle

#: Iterações máximas antes de declarar não-convergência.
DEFAULT_MAX_ITER = 1000

#: Critério de parada: variação L1 entre iterações consecutivas.
DEFAULT_TOL = 1e-8


class EigenvectorCentrality:
    """Satisfaz :class:`~edugraph.contracts.protocols.CentralityMetric`.

    Parameters aceitos em ``compute``:

    ``implementation`` : {"manual", "networkx"}
        ``manual`` é a do artigo; ``networkx`` é a de referência.
    ``max_iter`` : int
    ``tol`` : float
    ``weight`` : str | None
    """

    name = "eigenvector"

    def compute(self, projection: ProjectionBundle, **params: Any) -> CentralityResult:
        """Notes
        -----
        A implementar em C-02:

        1. Vetor inicial uniforme ``1/n`` — não aleatório, para que o
           resultado seja reproduzível.
        2. Iterar ``x ← A x``, normalizando por L2 a cada passo.
        3. Parar quando ``‖x_novo − x_velho‖₁ < tol · n``.
        4. Ao estourar ``max_iter``: ``converged=False`` e fallback para
           :func:`fallback_numpy`. O artefato registra os dois fatos.
        5. Garantir componentes não negativas (Perron-Frobenius) — o
           validador de contrato recusa autovetor com componente
           negativa, que costuma ser sinal de sinal trocado na
           normalização.
        """
        raise NotImplementedError("C-02: ver docs/specs/frente-c/C-02-autovetor.md")


def power_iteration(
    matrix: Any, *, max_iter: int = DEFAULT_MAX_ITER, tol: float = DEFAULT_TOL
) -> tuple[Any, bool, int]:
    """Iteração de potência pura, separada para os testes unitários.

    Returns
    -------
    tuple
        ``(vetor, convergiu, n_iteracoes)``.
    """
    raise NotImplementedError("C-02: iteração de potência")


def fallback_numpy(projection: ProjectionBundle, **params: Any) -> dict[str, float]:
    """Cálculo direto por autovalores quando a iteração não converge."""
    raise NotImplementedError("C-02: fallback por decomposição espectral")


CENTRALITIES.register("eigenvector", EigenvectorCentrality())
