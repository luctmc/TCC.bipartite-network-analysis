"""Normalização do OULAD  ``[A]`` — spec A-02.

Sete tabelas → uma tabela com uma linha por (aluno, módulo,
apresentação), com nota média ponderada, cliques no AVA e desfecho. É a
entrada de :func:`edugraph.data.bipartite.build_bipartite`.

O desfecho (``final_result``) viaja nesta tabela porque é dela que sai o
``outcomes.csv``, mas **não entra no grafo** (ADR-0008): o construtor do
bipartido só grava ``kind`` e ``label`` nos nós.

Decisões registradas (``docs/artigo/decisoes-metodologicas.md``)
---------------------------------------------------------------
- **Nota da matrícula = média ponderada pelo** ``weight`` **da avaliação.**
  No OULAD, TMAs/CMAs somam 100 e o exame vale 100 à parte; a média
  simples daria peso igual a um teste de 5% e ao exame. Quando todos os
  pesos das avaliações entregues são 0 (só CMAs sem peso), cai para a
  média simples — e isso fica registrado por linha em ``score_weighted``.
- **Matrícula sem nota e sem clique é descartada.** Não há evidência
  nenhuma de participação; ela não geraria aresta em critério nenhum.
- **Um desfecho por aluno** (:func:`to_outcomes`): o da apresentação mais
  recente; empate na mesma apresentação, o módulo de código maior. É o
  "estado final" do aluno na base — a regra é arbitrária no empate e por
  isso está escrita.

Memória
-------
``studentVle.csv`` (~10,6 milhões de linhas) é lida em blocos
(``chunksize``) e agregada bloco a bloco; nunca fica inteira em memória.
O resultado vai para ``cache_dir`` com um carimbo (tamanho e mtime dos
sete CSV), e a execução seguinte só relê se algum arquivo mudou.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from edugraph.contracts.errors import ContractError
from edugraph.data.oulad.schema import TABLES, read_table, table_path

#: Colunas da tabela normalizada — o contrato interno da Frente A.
NORMALIZED_COLUMNS: tuple[str, ...] = (
    "id_student",
    "code_module",
    "code_presentation",
    "score_media",
    "score_weighted",
    "n_assessments",
    "sum_click",
    "final_result",
)

#: Colunas da tabela por avaliação (granularidade ``assessment`` da A-03).
ASSESSMENT_COLUMNS: tuple[str, ...] = (
    "id_student",
    "code_module",
    "code_presentation",
    "id_assessment",
    "assessment_type",
    "score_media",
    "final_result",
)

#: Colunas da tabela por recurso do AVA (granularidades ``vle_site`` e
#: ``vle_activity_type`` da A-09). ``score_media`` vem como nulo de
#: propósito: o OULAD não registra nota por recurso, e manter a coluna
#: deixa a tabela com a mesma forma das outras duas — quem consome não
#: precisa saber de qual ETL veio.
VLE_COLUMNS: tuple[str, ...] = (
    "id_student",
    "code_module",
    "code_presentation",
    "id_site",
    "activity_type",
    "sum_click",
    "score_media",
    "final_result",
)

#: Linhas por bloco na leitura de ``studentVle``. 1 milhão de linhas ×
#: 5 colunas estreitas ≈ 50 MB por bloco.
VLE_CHUNKSIZE = 1_000_000

KEY = ["id_student", "code_module", "code_presentation"]

#: Chave da tabela do AVA: a matrícula mais o recurso.
VLE_KEY = [*KEY, "id_site"]

_CACHE_NORMALIZED = "oulad_normalized.csv"
_CACHE_ASSESSMENTS = "oulad_assessments.csv"
_CACHE_VLE = "oulad_vle.csv"


# ---------------------------------------------------------------------
# Cache em data/interim
# ---------------------------------------------------------------------


def _source_stamp(raw_dir: Path) -> dict[str, list[int]]:
    """Tamanho e mtime dos sete CSV — se algum mudar, o cache expira."""
    stamp: dict[str, list[int]] = {}
    for name in TABLES:
        path = table_path(raw_dir, name)
        if path.exists():
            st = path.stat()
            stamp[name] = [st.st_size, int(st.st_mtime_ns)]
    return stamp


def _cache_read(cache_dir: Path | None, filename: str, raw_dir: Path) -> pd.DataFrame | None:
    if cache_dir is None:
        return None
    # Path(): quem chama pode passar str — a CLI passa Path, mas um
    # script ou notebook passa "data/interim" e o `/` explodiria.
    data = Path(cache_dir) / filename
    meta = data.with_suffix(".meta.json")
    if not (data.exists() and meta.exists()):
        return None
    try:
        stamp = json.loads(meta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if stamp != _source_stamp(raw_dir):
        return None
    return pd.read_csv(data, encoding="utf-8", dtype={"code_module": "string",
                                                     "code_presentation": "string",
                                                     "final_result": "string",
                                                     "assessment_type": "string"})  # fmt: skip


def _cache_write(cache_dir: Path | None, filename: str, raw_dir: Path, table: pd.DataFrame) -> None:
    if cache_dir is None:
        return
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    data = cache_dir / filename
    table.to_csv(data, index=False, encoding="utf-8", lineterminator="\n")
    data.with_suffix(".meta.json").write_text(
        json.dumps(_source_stamp(raw_dir), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


# ---------------------------------------------------------------------
# Peças da normalização
# ---------------------------------------------------------------------


def _scores_per_assessment(raw_dir: Path) -> pd.DataFrame:
    """``studentAssessment`` ⨝ ``assessments``: uma linha por (aluno, avaliação)."""
    sa = read_table(raw_dir, "studentAssessment")
    assessments = read_table(raw_dir, "assessments")
    merged = sa.merge(assessments, on="id_assessment", how="inner", validate="many_to_one")
    return merged.dropna(subset=["score"])


def _weighted_scores(per_assessment: pd.DataFrame) -> pd.DataFrame:
    """Nota por matrícula: média ponderada por ``weight``; simples se Σweight = 0."""
    df = per_assessment.copy()
    df["_sw"] = df["score"] * df["weight"]
    grouped = df.groupby(KEY, sort=True).agg(
        _sum_sw=("_sw", "sum"),
        _sum_w=("weight", "sum"),
        _mean=("score", "mean"),
        n_assessments=("score", "size"),
    )
    weighted = grouped["_sum_w"] > 0
    grouped["score_media"] = np.where(
        weighted, grouped["_sum_sw"] / grouped["_sum_w"].where(weighted, 1.0), grouped["_mean"]
    )
    grouped["score_weighted"] = weighted
    return grouped[["score_media", "score_weighted", "n_assessments"]].reset_index()


def _clicks(raw_dir: Path, chunksize: int) -> pd.DataFrame:
    """Σ ``sum_click`` por matrícula, lendo ``studentVle`` em blocos."""
    partials: list[pd.DataFrame] = []
    for chunk in read_table(raw_dir, "studentVle", chunksize=chunksize):
        chunk["sum_click"] = chunk["sum_click"].astype("int64")
        partials.append(chunk.groupby(KEY, sort=False)["sum_click"].sum().reset_index())
    if not partials:
        return pd.DataFrame(columns=[*KEY, "sum_click"])
    return pd.concat(partials).groupby(KEY, sort=True)["sum_click"].sum().reset_index()


def _registrations(raw_dir: Path) -> pd.DataFrame:
    """``studentInfo``: a lista de matrículas e o desfecho de cada uma."""
    info = read_table(raw_dir, "studentInfo")
    if info.duplicated(subset=KEY).any():
        raise ContractError("studentInfo.csv tem (aluno, módulo, apresentação) repetido")
    return info


# ---------------------------------------------------------------------
# API
# ---------------------------------------------------------------------


def normalize(
    raw_dir: Path,
    *,
    cache_dir: Path | None = None,
    chunksize: int = VLE_CHUNKSIZE,
) -> pd.DataFrame:
    """Lê as sete tabelas e devolve a tabela normalizada.

    Parameters
    ----------
    raw_dir
        Diretório com os sete CSV do OULAD (``data/raw/oulad``).
    cache_dir
        Quando dado, grava o resultado em ``data/interim`` e reusa nas
        execuções seguintes enquanto os CSV de origem não mudarem.
    chunksize
        Linhas por bloco na leitura de ``studentVle``.

    Returns
    -------
    DataFrame
        Colunas de :data:`NORMALIZED_COLUMNS`, uma linha por matrícula
        com alguma evidência (nota **ou** clique), ordenada pela chave.
    """
    raw_dir = Path(raw_dir)
    cached = _cache_read(cache_dir, _CACHE_NORMALIZED, raw_dir)
    if cached is not None:
        return cached

    base = _registrations(raw_dir)
    scores = _weighted_scores(_scores_per_assessment(raw_dir))
    clicks = _clicks(raw_dir, chunksize)

    table = base.merge(scores, on=KEY, how="left").merge(clicks, on=KEY, how="left")
    table["n_assessments"] = table["n_assessments"].fillna(0).astype("int64")
    table["sum_click"] = table["sum_click"].fillna(0).astype("int64")
    table["score_weighted"] = table["score_weighted"].fillna(False).astype(bool)

    sem_evidencia = table["score_media"].isna() & (table["sum_click"] == 0)
    table = table.loc[~sem_evidencia, list(NORMALIZED_COLUMNS)]
    table = table.sort_values(KEY, kind="stable").reset_index(drop=True)

    _cache_write(cache_dir, _CACHE_NORMALIZED, raw_dir, table)
    return table


def normalize_vle(
    raw_dir: Path,
    *,
    cache_dir: Path | None = None,
    chunksize: int = VLE_CHUNKSIZE,
    cohort: str | None = None,
) -> pd.DataFrame:
    """Tabela por recurso do AVA, para as granularidades do comportamento (spec A-09).

    Uma linha por (aluno, recurso) com a soma de cliques. É o ETL que
    sustenta a troca do critério de aresta: com o nó de V sendo o
    recurso, o grau mediano do aluno passa de 1 para ~40, e a projeção
    aluno↔aluno deixa de ser indistinguível do acaso (A-08).

    Parameters
    ----------
    raw_dir
        Diretório com os sete CSV do OULAD.
    cache_dir
        Quando dado, grava em ``data/interim`` e reusa enquanto a origem
        não mudar. Ignorado quando ``cohort`` é passada, porque o cache é
        da base inteira.
    chunksize
        Linhas por bloco. ``studentVle`` tem ~10,6 milhões de linhas.
    cohort
        Recorte opcional, aplicado **durante** a leitura dos blocos. É o
        que torna a coorte viável num notebook: filtrar depois exigiria
        materializar a tabela inteira primeiro.

    Returns
    -------
    DataFrame
        Colunas de :data:`VLE_COLUMNS`, ordenada por (aluno, módulo,
        apresentação, recurso).

    Notes
    -----
    ``score_media`` vem nula por construção: o OULAD não registra nota
    por recurso do AVA. A consequência prática é que o critério
    ``score_threshold`` não produz aresta nenhuma sobre esta tabela — o
    critério a usar aqui é ``vle_activity``.
    """
    raw_dir = Path(raw_dir)
    usar_cache = cohort is None
    if usar_cache:
        cached = _cache_read(cache_dir, _CACHE_VLE, raw_dir)
        if cached is not None:
            return cached

    partials: list[pd.DataFrame] = []
    for chunk in read_table(raw_dir, "studentVle", chunksize=chunksize):
        if cohort is not None:
            if "_" in cohort:
                chave = (
                    chunk["code_module"].astype(str) + "_" + chunk["code_presentation"].astype(str)
                )
            else:
                chave = chunk["code_presentation"].astype(str)
            chunk = chunk[chave == cohort]
            if chunk.empty:
                continue
        chunk["sum_click"] = chunk["sum_click"].astype("int64")
        partials.append(chunk.groupby(VLE_KEY, sort=False)["sum_click"].sum().reset_index())

    if not partials:
        vazia = pd.DataFrame(columns=list(VLE_COLUMNS))
        return vazia
    table = pd.concat(partials).groupby(VLE_KEY, sort=True)["sum_click"].sum().reset_index()

    # `vle` traz o tipo de atividade de cada recurso. O merge é por
    # (recurso, módulo, apresentação) porque o mesmo id_site não se
    # repete entre apresentações, mas a tabela declara as três colunas.
    sites = read_table(raw_dir, "vle").drop_duplicates(
        subset=["id_site", "code_module", "code_presentation"]
    )
    table = table.merge(sites, on=["id_site", "code_module", "code_presentation"], how="left")
    table["activity_type"] = table["activity_type"].fillna("unknown").astype("string")

    info = _registrations(raw_dir)[[*KEY, "final_result"]]
    table = table.merge(info, on=KEY, how="left")
    table["score_media"] = pd.Series(float("nan"), index=table.index, dtype="float64")

    table = table[list(VLE_COLUMNS)].sort_values(VLE_KEY, kind="stable").reset_index(drop=True)
    if usar_cache:
        _cache_write(cache_dir, _CACHE_VLE, raw_dir, table)
    return table


def normalize_assessments(raw_dir: Path, *, cache_dir: Path | None = None) -> pd.DataFrame:
    """Tabela por avaliação, para ``granularity="assessment"`` (spec A-03).

    Uma linha por (aluno, avaliação) com a nota obtida; sem cliques,
    porque o AVA não é registrado por avaliação no OULAD — o critério
    ``vle_activity`` não se aplica a esta granularidade.
    """
    raw_dir = Path(raw_dir)
    cached = _cache_read(cache_dir, _CACHE_ASSESSMENTS, raw_dir)
    if cached is not None:
        return cached

    per_assessment = _scores_per_assessment(raw_dir)
    info = _registrations(raw_dir)[[*KEY, "final_result"]]
    table = per_assessment.merge(info, on=KEY, how="inner")
    table = table.rename(columns={"score": "score_media"})[list(ASSESSMENT_COLUMNS)]
    table = table.sort_values([*KEY, "id_assessment"], kind="stable").reset_index(drop=True)

    _cache_write(cache_dir, _CACHE_ASSESSMENTS, raw_dir, table)
    return table


def _presentation_key(code: Any) -> tuple[int, int]:
    """``"2013J"`` → ``(2013, 1)``; ``"2013B"`` → ``(2013, 0)``. B = fev, J = out."""
    s = str(code)
    return int(s[:4]), 1 if s[4:5].upper() == "J" else 0


def to_outcomes(table: pd.DataFrame) -> dict[str, str]:
    """Um desfecho por aluno, chaveado por ``S<id>`` para ``outcomes.csv``.

    Regra: a matrícula da **apresentação mais recente**; empate na mesma
    apresentação, o módulo de código maior. É o estado final do aluno na
    base. Alternativas (qualquer aprovação; a pior) são igualmente
    defensáveis — o que importa é que a escolha está escrita aqui e em
    ``docs/artigo/decisoes-metodologicas.md``.
    """
    faltando = {"id_student", "code_module", "code_presentation", "final_result"} - set(
        table.columns
    )
    if faltando:
        raise ContractError(f"to_outcomes: tabela sem as colunas {sorted(faltando)}")

    df = table[["id_student", "code_module", "code_presentation", "final_result"]].dropna()
    ordem = df["code_presentation"].map(_presentation_key)
    df = df.assign(_year=ordem.map(lambda t: t[0]), _term=ordem.map(lambda t: t[1]))
    df = df.sort_values(["id_student", "_year", "_term", "code_module"], kind="stable")
    last = df.groupby("id_student", sort=True).tail(1)
    return {
        f"S{int(sid)}": str(res)
        for sid, res in zip(last["id_student"], last["final_result"], strict=True)
    }


def load_table(raw_dir: Path, name: str) -> pd.DataFrame:
    """Lê uma das sete tabelas com o esquema declarado (atalho para :func:`read_table`)."""
    return read_table(Path(raw_dir), name)
