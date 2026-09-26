"""Centralidade de autovetor por iteração de potência  ``[C]`` — spec C-02.

Terceira implementação à mão do projeto (ADR-0010). Um nó é central se
está ligado a nós centrais: ``x = (1/λ) A x``, resolvido iterando
``x ← A x / ‖A x‖`` até convergir.

Comparada com ``nx.eigenvector_centrality`` na própria spec.

**O deslocamento ``A + I``.** A iteração roda sobre ``A + I``, não sobre
``A``. Os autovetores são os mesmos e os autovalores só andam uma
unidade, então o vetor principal não muda; o que muda é que, num grafo
bipartido (ou com componente bipartida), ``A`` tem ``−λ`` com o mesmo
módulo de ``λ`` e a iteração pura oscila para sempre entre dois vetores.
Com ``+I``, ``λ + 1`` passa a ser estritamente o maior em módulo. É o
mesmo recurso que o NetworkX usa, e fica registrado em ``params.shift``.

**Convergência não é garantida.** Em grafo desconexo — e a projeção
aluno↔aluno do OULAD tende a ser —, a iteração pode não convergir no
limite de passos. O contrato exige que isso vire ``converged=False`` no
artefato e queda para o cálculo direto por autovalores, nunca uma
exceção que derrube o pipeline.
"""

from __future__ import annotations

import time
from typing import Any

import networkx as nx
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import ArpackNoConvergence, eigsh

from edugraph.centrality._params import check_params
from edugraph.contracts.errors import ContractError
from edugraph.contracts.registry import CENTRALITIES
from edugraph.contracts.types import CentralityResult, Meta, ProjectionBundle

#: Id da spec, gravado em ``meta.producer`` de todo artefato daqui.
PRODUCER = "C-02"

#: Iterações máximas antes de declarar não-convergência.
DEFAULT_MAX_ITER = 1000

#: Critério de parada: variação L1 entre iterações consecutivas.
DEFAULT_TOL = 1e-8

#: Deslocamento espectral somado à diagonal (ver o docstring do módulo).
SHIFT = 1.0

#: Acima disto o fallback usa ARPACK (esparso) em vez de ``eigh`` denso:
#: uma matriz densa de 2.000 nós já ocupa 32 MB.
DENSE_FALLBACK_MAX_NODES = 2000

ACCEPTED_PARAMS: tuple[str, ...] = ("implementation", "max_iter", "tol", "weight")


def _adjacency(projection: ProjectionBundle, weight: str | None) -> tuple[list[str], sp.csr_array]:
    """Matriz de adjacência esparsa, com os nós em ordem de id."""
    nodes = sorted(projection.graph.nodes)
    matrix = nx.to_scipy_sparse_array(projection.graph, nodelist=nodes, weight=weight, format="csr")
    return [str(n) for n in nodes], matrix.astype(float)


def _perron(vector: np.ndarray) -> np.ndarray:
    """Componentes não negativas e norma L2 unitária.

    Por Perron-Frobenius o autovetor principal de uma componente conexa
    tem sinal constante; o solver pode devolvê-lo com o sinal trocado, e
    em grafo desconexo pode combinar componentes com sinais diferentes.
    Tomar o módulo resolve os dois casos sem sair do autoespaço, porque
    os suportes das componentes são disjuntos.
    """
    positive = np.abs(vector)
    norm = float(np.linalg.norm(positive))
    return positive / norm if norm > 0 else positive


def power_iteration(
    matrix: Any, *, max_iter: int = DEFAULT_MAX_ITER, tol: float = DEFAULT_TOL
) -> tuple[Any, bool, int]:
    """Iteração de potência pura, separada para os testes unitários.

    Parte do vetor uniforme ``1/n`` (não aleatório, para ser
    reproduzível), multiplica pela matriz, normaliza por L2 e para quando
    ``‖x_novo − x_velho‖₁ < tol · n``. Não desloca a matriz: quem chama
    decide se passa ``A`` ou ``A + I``.

    Returns
    -------
    tuple
        ``(vetor, convergiu, n_iteracoes)``. Se não convergir, devolve o
        último vetor calculado — cabe a quem chama decidir o fallback.
    """
    n = matrix.shape[0]
    x = np.full(n, 1.0 / n)
    for iteration in range(1, max_iter + 1):
        y = matrix @ x
        norm = float(np.linalg.norm(y))
        if norm == 0.0:
            # A·x = 0: só acontece com a matriz nula, em que todo vetor é
            # autovetor. O uniforme é a resposta sem viés.
            return x, True, iteration
        y = y / norm
        if float(np.abs(y - x).sum()) < tol * n:
            return y, True, iteration
        x = y
    return x, False, max_iter


def fallback_numpy(projection: ProjectionBundle, **params: Any) -> dict[str, float]:
    """Cálculo direto por autovalores quando a iteração não converge.

    ``eigh`` denso até :data:`DENSE_FALLBACK_MAX_NODES` nós; acima disso,
    ARPACK sobre a matriz esparsa, pedindo só o maior autovalor.
    """
    weight = params.get("weight", "weight")
    nodes, matrix = _adjacency(projection, weight)
    n = len(nodes)

    if n <= DENSE_FALLBACK_MAX_NODES:
        _, vectors = np.linalg.eigh(matrix.toarray())
        principal = vectors[:, -1]  # eigh devolve em ordem crescente
    else:
        try:
            # v0 fixo: sem ele o ARPACK parte de um vetor aleatório, e com
            # autovalor repetido o resultado mudaria entre execuções.
            _, vectors = eigsh(matrix, k=1, which="LA", v0=np.ones(n))
            principal = vectors[:, 0]
        except ArpackNoConvergence as error:
            # Melhor aproximação que o ARPACK chegou a ter, se houver.
            if error.eigenvectors is None or error.eigenvectors.shape[1] == 0:
                raise
            principal = error.eigenvectors[:, -1]

    return dict(zip(nodes, (float(v) for v in _perron(principal)), strict=True))


def _networkx(
    projection: ProjectionBundle, max_iter: int, tol: float, weight: str | None
) -> tuple[dict[str, float], bool, int | None]:
    """A referência: ``nx.eigenvector_centrality`` — que também usa ``A + I``."""
    try:
        raw = nx.eigenvector_centrality(projection.graph, max_iter=max_iter, tol=tol, weight=weight)
    except nx.PowerIterationFailedConvergence:
        return {}, False, None
    return {str(n): abs(float(s)) for n, s in raw.items()}, True, None


def _manual(
    projection: ProjectionBundle, max_iter: int, tol: float, weight: str | None
) -> tuple[dict[str, float], bool, int | None]:
    """A do artigo: iteração de potência sobre ``A + I``."""
    nodes, matrix = _adjacency(projection, weight)
    shifted = matrix + SHIFT * sp.identity(len(nodes), format="csr")
    vector, converged, n_iter = power_iteration(shifted, max_iter=max_iter, tol=tol)
    scores = dict(zip(nodes, (float(v) for v in _perron(vector)), strict=True))
    return scores, converged, n_iter


class EigenvectorCentrality:
    """Satisfaz :class:`~edugraph.contracts.protocols.CentralityMetric`.

    Parameters aceitos em ``compute``:

    ``implementation`` : {"manual", "networkx"}
        ``manual`` é a do artigo; ``networkx`` é a de referência.
    ``max_iter`` : int
    ``tol`` : float
    ``weight`` : str | None
        Padrão ``"weight"``: aqui peso alto é afinidade, no sentido certo
        — ao contrário da intermediação (ver C-01).
    """

    name = "eigenvector"

    def compute(self, projection: ProjectionBundle, **params: Any) -> CentralityResult:
        """Autovetor principal da projeção, com fallback registrado.

        Raises
        ------
        ContractError
            Se a projeção estiver vazia, se ``implementation`` não existir
            ou se vier parâmetro desconhecido. Não-convergência **não**
            levanta: vira ``converged=False`` e fallback.
        """
        check_params(params, ACCEPTED_PARAMS, "EigenvectorCentrality.compute")
        implementation = str(params.get("implementation", "manual"))
        max_iter = int(params.get("max_iter", DEFAULT_MAX_ITER))
        tol = float(params.get("tol", DEFAULT_TOL))
        weight = params.get("weight", "weight")

        if implementation not in ("manual", "networkx"):
            raise ContractError(
                f"autovetor: implementation={implementation!r} não existe; use manual ou networkx"
            )
        graph = projection.graph
        if graph.number_of_nodes() == 0:
            raise ContractError(
                f"autovetor: projeção {projection.projection_id!r} não tem nós; não há o que medir"
            )

        start = time.perf_counter()
        solver = _manual if implementation == "manual" else _networkx
        scores, converged, n_iter = solver(projection, max_iter, tol, weight)
        if not converged:
            scores = fallback_numpy(projection, weight=weight)
        runtime_s = time.perf_counter() - start

        result_params: dict[str, Any] = {
            "implementation": implementation,
            "max_iter": max_iter,
            "tol": tol,
            "weight": weight,
            "shift": SHIFT,
            "fallback": None if converged else "spectral",
        }
        if n_iter is not None:
            result_params["n_iter"] = n_iter

        return CentralityResult(
            projection_id=projection.projection_id,
            metric="eigenvector",
            scores=scores,
            params=result_params,
            runtime_s=runtime_s,
            converged=converged,
            meta=Meta(
                producer=PRODUCER,
                stats={
                    "n_nodes": graph.number_of_nodes(),
                    "n_edges": graph.number_of_edges(),
                    "n_components": nx.number_connected_components(graph),
                },
                notes=(
                    (
                        "Iteração de potência à mão sobre A + I"
                        if implementation == "manual"
                        else "nx.eigenvector_centrality (referência)"
                    )
                    + (
                        "."
                        if converged
                        else "; não convergiu, fallback por decomposição espectral."
                    )
                ),
            ),
        )


CENTRALITIES.register("eigenvector", EigenvectorCentrality())
