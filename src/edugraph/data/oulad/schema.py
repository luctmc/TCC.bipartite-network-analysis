"""Esquema das sete tabelas do OULAD  ``[A]`` — spec A-02.

Declarar tipos na leitura não é zelo: ``studentVle.csv`` tem ~10,6
milhões de linhas, e ler com ``usecols`` e ``dtype`` explícitos é a
diferença entre caber e não caber na memória de um notebook (ver a
tabela de riscos do plano de arquitetura).

Os nomes de coluna vêm do dicionário de dados publicado (Kuzilek; Hlosta;
Zdrahal, 2017) e foram conferidos contra ``tests/data/oulad_mini/``, que
reproduz o esquema real. A conferência contra a base completa é o
primeiro passo depois do download: ``python -m edugraph data etl``
falha cedo, nomeando tabela e coluna, se algo não bater.

**O que não é lido, de propósito.** ``studentInfo`` traz gênero, região,
faixa etária, escolaridade, IMD e deficiência. Nenhuma dessas colunas
entra em ``usecols``: elas são exatamente os atributos que a ADR-0008
proíbe no grafo, e a forma mais segura de não vazá-los é não carregá-los.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from edugraph.contracts.errors import ContractError

#: Marcadores de valor ausente. A distribuição do UCI usa ``"?"``; a da
#: Open University, campo vazio. Conferido na base real em 18/09/2026:
#: ``studentAssessment.score`` traz ``?`` onde não há nota.
NA_VALUES: tuple[str, ...] = ("?", "")

#: Nomes dos sete arquivos, como vêm no zip do OULAD.
TABLES: tuple[str, ...] = (
    "assessments",
    "courses",
    "studentAssessment",
    "studentInfo",
    "studentRegistration",
    "studentVle",
    "vle",
)


@dataclass(frozen=True)
class TableSchema:
    """Colunas usadas de uma tabela e seus tipos.

    ``usecols`` é deliberadamente menor que a tabela real: o que não
    entra no grafo nem na validação a posteriori não é lido.
    """

    name: str
    usecols: tuple[str, ...]
    dtypes: dict[str, str]


#: Esquema por tabela. ``string`` (não ``object``) para códigos, ``Int64``
#: anulável onde o OULAD tem vazio, ``float64`` para nota (há ``NaN``).
SCHEMAS: dict[str, TableSchema] = {
    "studentInfo": TableSchema(
        name="studentInfo",
        usecols=("code_module", "code_presentation", "id_student", "final_result"),
        dtypes={
            "code_module": "string",
            "code_presentation": "string",
            "id_student": "int64",
            "final_result": "string",
        },
    ),
    "studentAssessment": TableSchema(
        name="studentAssessment",
        usecols=("id_assessment", "id_student", "score"),
        dtypes={"id_assessment": "int64", "id_student": "int64", "score": "float64"},
    ),
    "assessments": TableSchema(
        name="assessments",
        usecols=("code_module", "code_presentation", "id_assessment", "assessment_type", "weight"),
        dtypes={
            "code_module": "string",
            "code_presentation": "string",
            "id_assessment": "int64",
            "assessment_type": "string",
            "weight": "float64",
        },
    ),
    "studentVle": TableSchema(
        name="studentVle",
        usecols=("code_module", "code_presentation", "id_student", "sum_click"),
        dtypes={
            "code_module": "string",
            "code_presentation": "string",
            "id_student": "int64",
            "sum_click": "int32",
        },
    ),
    "studentRegistration": TableSchema(
        name="studentRegistration",
        usecols=("code_module", "code_presentation", "id_student", "date_unregistration"),
        dtypes={
            "code_module": "string",
            "code_presentation": "string",
            "id_student": "int64",
            "date_unregistration": "Int64",
        },
    ),
    "courses": TableSchema(
        name="courses",
        usecols=("code_module", "code_presentation", "module_presentation_length"),
        dtypes={
            "code_module": "string",
            "code_presentation": "string",
            "module_presentation_length": "int64",
        },
    ),
    "vle": TableSchema(
        name="vle",
        usecols=("id_site", "code_module", "code_presentation", "activity_type"),
        dtypes={
            "id_site": "int64",
            "code_module": "string",
            "code_presentation": "string",
            "activity_type": "string",
        },
    ),
}


def table_path(raw_dir: Path, name: str) -> Path:
    return Path(raw_dir) / f"{name}.csv"


def validate_schema(name: str, columns: list[str]) -> None:
    """Confere que o arquivo tem as colunas que o esquema espera.

    Falhar cedo e com mensagem clara é melhor do que descobrir a coluna
    faltando no meio da agregação de 10 milhões de linhas.

    Raises
    ------
    ContractError
        Nomeando a tabela e as colunas ausentes.
    """
    if name not in SCHEMAS:
        raise ContractError(f"tabela desconhecida do OULAD: {name!r}; esperadas {list(TABLES)}")
    faltando = [c for c in SCHEMAS[name].usecols if c not in columns]
    if faltando:
        raise ContractError(
            f"{name}.csv sem as colunas {faltando}. Colunas presentes: {columns}. "
            "Confira o dicionário de dados do OULAD ou se o arquivo é o certo."
        )


def read_table(raw_dir: Path, name: str, **read_csv_kwargs: Any) -> pd.DataFrame:
    """Lê uma tabela com ``usecols`` e ``dtype`` do esquema, validando antes.

    ``read_csv_kwargs`` passam direto ao pandas — é por aqui que
    ``studentVle`` é lida em ``chunksize`` (ver :mod:`~edugraph.data.oulad.etl`).
    """
    path = table_path(raw_dir, name)
    if not path.exists():
        raise ContractError(
            f"{path} não encontrado. O OULAD é download manual: ver README ou "
            "`python scripts/download_oulad.py`."
        )
    header = list(pd.read_csv(path, nrows=0).columns)
    validate_schema(name, header)
    schema = SCHEMAS[name]
    return pd.read_csv(
        path,
        usecols=list(schema.usecols),
        dtype=schema.dtypes,
        encoding="utf-8",
        # A distribuição do UCI codifica ausente como "?"; a da OU, como
        # vazio. Aceitar os dois é o que faz `score` virar float em vez de
        # explodir na primeira nota faltante.
        na_values=NA_VALUES,
        **read_csv_kwargs,
    )
