"""Esquema das sete tabelas do OULAD  ``[A]`` — spec A-02.

Declarar tipos na leitura não é zelo: ``studentVle.csv`` tem ~10,6
milhões de linhas, e ler com ``usecols`` e ``dtype`` explícitos é a
diferença entre caber e não caber na memória de um notebook (ver a
tabela de riscos do plano de arquitetura).
"""

from __future__ import annotations

from dataclasses import dataclass

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


#: Esquema por tabela. Preencher em A-02 conferindo contra o dicionário
#: de dados do OULAD — os nomes abaixo vêm da documentação publicada e
#: precisam ser validados contra o arquivo real antes de virar verdade.
SCHEMAS: dict[str, TableSchema] = {
    "studentInfo": TableSchema(
        name="studentInfo",
        usecols=(
            "code_module",
            "code_presentation",
            "id_student",
            "final_result",
        ),
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
        usecols=("code_module", "code_presentation", "id_assessment", "assessment_type"),
        dtypes={
            "code_module": "string",
            "code_presentation": "string",
            "id_assessment": "int64",
            "assessment_type": "string",
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
}


def validate_schema(name: str, columns: list[str]) -> None:
    """Confere que o arquivo lido tem as colunas que o esquema espera.

    Implementar em A-02: falhar cedo e com mensagem clara é melhor do
    que descobrir a coluna faltando no meio da agregação de 10 milhões
    de linhas.
    """
    raise NotImplementedError("A-02: ver docs/specs/frente-a/A-02-etl-oulad.md")
