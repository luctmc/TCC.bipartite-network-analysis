"""Normalização do OULAD  ``[A]`` — spec A-02.

Sete tabelas → uma tabela com uma linha por (aluno, disciplina,
apresentação), com nota média, cliques no AVA e desfecho. É a entrada de
:func:`edugraph.data.bipartite.build_bipartite`.

O desfecho (``final_result``) viaja nesta tabela porque é dela que sai o
``outcomes.csv``, mas **não entra no grafo** (ADR-0008).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

#: Colunas da tabela normalizada — o contrato interno da Frente A.
NORMALIZED_COLUMNS: tuple[str, ...] = (
    "id_student",
    "code_module",
    "code_presentation",
    "score_media",
    "sum_click",
    "final_result",
)


def normalize(raw_dir: Path, *, cache_dir: Path | None = None) -> pd.DataFrame:
    """Lê as sete tabelas e devolve a tabela normalizada.

    Parameters
    ----------
    raw_dir
        Diretório com os sete CSV do OULAD (``data/raw/oulad``).
    cache_dir
        Quando dado, grava o resultado em ``data/interim`` e reusa nas
        execuções seguintes. A agregação do ``studentVle`` é cara demais
        para refazer a cada rodada.

    Notes
    -----
    A implementar em A-02:

    1. ``studentAssessment`` ⨝ ``assessments`` → nota média por
       (aluno, módulo, apresentação), ponderada pelo peso da avaliação.
    2. ``studentVle`` agregado por (aluno, módulo, apresentação) →
       ``sum_click``. Ler com ``usecols`` e ``dtype`` do módulo
       :mod:`~edugraph.data.oulad.schema`.
    3. ``studentInfo`` traz ``final_result``.
    4. Descartar matrículas sem nota **e** sem clique.
    5. Gravar em ``cache_dir`` quando pedido.
    """
    raise NotImplementedError("A-02: ver docs/specs/frente-a/A-02-etl-oulad.md")


def load_table(raw_dir: Path, name: str) -> pd.DataFrame:
    """Lê uma das sete tabelas com o esquema declarado."""
    raise NotImplementedError("A-02: leitura tipada das tabelas do OULAD")


def to_outcomes(table: pd.DataFrame) -> dict[str, str]:
    """Extrai o desfecho por aluno para ``bipartite/outcomes.csv``.

    Alunos com mais de uma matrícula: a spec A-02 decide e registra a
    regra (pior desfecho, último desfecho, ou uma linha por matrícula) —
    é uma decisão metodológica que vai para ``docs/artigo/``.
    """
    raise NotImplementedError("A-02: extração dos rótulos históricos")
