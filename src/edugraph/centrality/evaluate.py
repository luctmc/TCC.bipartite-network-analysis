"""Validação a posteriori da centralidade  ``[C]`` — spec C-06.

**Único módulo da Frente C autorizado a ler ``outcomes.csv``** (ADR-0008,
mesma regra de :mod:`edugraph.community.evaluate`).

A pergunta: as disciplinas que a topologia aponta como gargalo têm, de
fato, taxa de reprovação acima da base? E alunos de alta centralidade
têm desfecho diferente? Se sim, a estrutura tem valor prático; se não, o
artigo reporta que a centralidade estrutural e o desempenho histórico
são dimensões independentes — o que também é um achado.

O desfecho entra **depois** de a centralidade ter sido calculada, como
categoria contra a qual o ranking é comparado; nunca como entrada. Não
há teste de significância (fora de escopo da spec): as tabelas são
descritivas.

Duas ressalvas que acompanham qualquer número daqui
----------------------------------------------------
1. **O desfecho é do aluno, não da matrícula.** O ETL guarda um desfecho
   por aluno, o da apresentação mais recente (A-02). Para quem cursou
   uma só disciplina — 91,8% no ``oulad_module_presentation`` — ele é o
   daquela disciplina; para os demais, pode ser de outra.
2. **A matrícula vem do bipartido.** Com ``edge_criterion =
   score_threshold``, só há aresta onde a nota passou do limiar, então
   quem foi mal numa disciplina pode nem aparecer nela. A taxa absoluta
   fica subestimada; a comparação crítica × base continua válida como
   contraste, porque as duas são medidas sobre a mesma população.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import BipartiteBundle, CentralityResult, Outcomes

#: Id da spec, para as mensagens e as legendas desta etapa.
PRODUCER = "C-06"

#: Os quatro desfechos do OULAD, do melhor para o pior — a mesma ordem da B-06.
FINAL_RESULTS: tuple[str, ...] = ("Distinction", "Pass", "Fail", "Withdrawn")

#: O que conta como "não concluiu com aprovação". ``Withdrawn`` entra
#: junto com ``Fail`` porque, para a gestão, desistir também é não
#: concluir; ``rate_Fail`` continua na tabela para quem quiser só a
#: reprovação estrita.
NOT_PASSED: tuple[str, ...] = ("Fail", "Withdrawn")

_RATE_COLUMNS: tuple[str, ...] = (
    "n_labeled",
    *[f"rate_{r}" for r in FINAL_RESULTS],
    "rate_not_passed",
    "base_rate_not_passed",
    "excess_not_passed",
)

#: Colunas da tabela de reprovação por disciplina (tabela 8).
FAILURE_COLUMNS: tuple[str, ...] = (
    "group",
    "rank",
    "node_id",
    "n_students",
    *_RATE_COLUMNS,
)

#: Colunas da tabela de desfecho por faixa de centralidade.
QUANTILE_COLUMNS: tuple[str, ...] = (
    "quantile",
    "n_students",
    "score_min",
    "score_max",
    *_RATE_COLUMNS,
)


def is_degenerate(result: CentralityResult) -> bool:
    """Todos os scores iguais: não há ranking a validar.

    É o caso da intermediação em ``synthetic_v1``/``discipline_simple``
    (K₇, tudo zero). A spec pede que isso seja **reportado**, não
    transformado numa tabela com uma ordem que só reflete o desempate
    por id.
    """
    values = list(result.scores.values())
    return not values or max(values) - min(values) <= 1e-12


def enrollment_of(bipartite: BipartiteBundle) -> dict[str, list[str]]:
    """Disciplina → alunos ligados a ela no bipartido, em ordem de id."""
    out: dict[str, list[str]] = {}
    disciplines = bipartite.disciplines
    for node in sorted(disciplines):
        out[node] = sorted(str(n) for n in bipartite.graph.neighbors(node))
    return out


def _rates(students: list[str], outcomes: Outcomes) -> dict[str, Any]:
    """Contagem e taxa de cada desfecho sobre os alunos com desfecho conhecido."""
    counts: defaultdict[str, int] = defaultdict(int)
    labeled = 0
    for student in students:
        result = outcomes.final_result.get(student)
        if result is not None:
            counts[result] += 1
            labeled += 1
    rates = {f"rate_{r}": (counts[r] / labeled if labeled else 0.0) for r in FINAL_RESULTS}
    not_passed = sum(counts[r] for r in NOT_PASSED)
    return {
        "n_labeled": labeled,
        **rates,
        "rate_not_passed": not_passed / labeled if labeled else 0.0,
    }


def _with_base(row: dict[str, Any], base: float) -> dict[str, Any]:
    return {**row, "base_rate_not_passed": base, "excess_not_passed": row["rate_not_passed"] - base}


def failure_rate_by_discipline(
    ranking: list[str], outcomes: Outcomes, enrollment: dict[str, list[str]]
) -> list[dict[str, Any]]:
    """Taxa de reprovação nas disciplinas críticas × nas demais.

    Parameters
    ----------
    ranking
        Disciplinas críticas em ordem de centralidade (saída da C-03).
    outcomes
        Desfechos históricos.
    enrollment
        Disciplina → alunos, derivado do bipartido (:func:`enrollment_of`).

    Returns
    -------
    list[dict]
        Uma linha por disciplina crítica (``group = "critical"``), uma
        para o conjunto delas (``"critical_all"``, alunos distintos), uma
        para as **demais** disciplinas (``"others"``) e uma para a base
        (``"base"``, todos os alunos). Cada linha traz a taxa da base ao
        lado e o excesso sobre ela — no formato de :data:`FAILURE_COLUMNS`.
    """
    unknown = [d for d in ranking if d not in enrollment]
    if unknown:
        raise ContractError(
            f"{PRODUCER}: disciplinas do ranking fora do bipartido: {unknown[:5]}; "
            "o ranking e o bipartido precisam ser do mesmo dataset"
        )

    all_students = sorted({s for students in enrollment.values() for s in students})
    base = _rates(all_students, outcomes)["rate_not_passed"]

    rows: list[dict[str, Any]] = []
    for rank, discipline in enumerate(ranking, start=1):
        students = enrollment[discipline]
        rows.append(
            _with_base(
                {
                    "group": "critical",
                    "rank": rank,
                    "node_id": discipline,
                    "n_students": len(students),
                    **_rates(students, outcomes),
                },
                base,
            )
        )

    critical = set(ranking)
    groups = {
        "critical_all": sorted({s for d in ranking for s in enrollment[d]}),
        "others": sorted({s for d, ss in enrollment.items() if d not in critical for s in ss}),
        "base": all_students,
    }
    for group, students in groups.items():
        rows.append(
            _with_base(
                {
                    "group": group,
                    "rank": None,
                    "node_id": None,
                    "n_students": len(students),
                    **_rates(students, outcomes),
                },
                base,
            )
        )
    return [{column: row[column] for column in FAILURE_COLUMNS} for row in rows]


def outcome_by_centrality(
    result: CentralityResult, outcomes: Outcomes, *, quantiles: int = 4
) -> list[dict[str, Any]]:
    """Distribuição de desfechos por quartil de centralidade do aluno.

    Tabela + figura do capítulo 3. Agrupar por quartil é estatística
    descritiva sobre uma variável calculada da topologia — nenhum
    classificador envolvido.

    As faixas são por **posição** (os alunos ordenados por score, com
    desempate por id, divididos em ``quantiles`` partes quase iguais), e
    não por valor: assim toda faixa tem alunos e todo aluno cai em uma.
    Com muitos empates, alunos de mesmo score podem cair em faixas
    vizinhas — ``score_min``/``score_max`` mostram quando isso acontece.
    A faixa 1 é a de **menor** centralidade.
    """
    if quantiles < 1:
        raise ContractError(f"{PRODUCER}: quantiles precisa ser >= 1; recebeu {quantiles!r}")
    ordered = sorted(result.scores.items(), key=lambda kv: (kv[1], kv[0]))
    n = len(ordered)
    if n == 0:
        raise ContractError(f"{PRODUCER}: {result.projection_id}/{result.metric} sem scores")

    base = _rates([node for node, _ in ordered], outcomes)["rate_not_passed"]
    rows: list[dict[str, Any]] = []
    for q in range(quantiles):
        chunk = ordered[q * n // quantiles : (q + 1) * n // quantiles]
        if not chunk:
            continue
        rows.append(
            _with_base(
                {
                    "quantile": q + 1,
                    "n_students": len(chunk),
                    "score_min": chunk[0][1],
                    "score_max": chunk[-1][1],
                    **_rates([node for node, _ in chunk], outcomes),
                },
                base,
            )
        )
    return [{column: row[column] for column in QUANTILE_COLUMNS} for row in rows]


# ---------------------------------------------------------------------
# Figura 8 — desfecho por faixa de centralidade
# ---------------------------------------------------------------------


def figure_outcome_by_quantile(
    rows: list[dict[str, Any]],
    *,
    dataset: str,
    projection_id: str,
    metric: str,
    out: Path,
    name: str | None = None,
) -> list[Path]:
    """Barras empilhadas dos quatro desfechos por faixa, com a base tracejada.

    Recebe as linhas de :func:`outcome_by_centrality` — não lê desfecho
    nenhum. Cores em tons que também se distinguem em cinza, e hachura
    nas duas categorias de não conclusão, para a versão impressa.
    """
    import matplotlib.pyplot as plt

    from edugraph.reporting.figures import COLUMN_WIDTH_IN, apply_style, save_figure

    if not rows:
        raise ContractError(f"{PRODUCER}: nenhuma faixa para a figura")

    apply_style()
    fig, ax = plt.subplots(figsize=(COLUMN_WIDTH_IN, 2.6))
    labels = [f"Q{row['quantile']}" for row in rows]
    # Do mais claro ao mais escuro, na ordem de FINAL_RESULTS: a leitura
    # em cinza continua monotônica.
    colors = {
        "Distinction": "#cfe3f2",
        "Pass": "#7fb3d5",
        "Fail": "#d35400",
        "Withdrawn": "#6e2c00",
    }
    hatches = {"Fail": "//", "Withdrawn": "xx"}
    bottom = [0.0] * len(rows)
    for outcome in FINAL_RESULTS:
        heights = [row[f"rate_{outcome}"] for row in rows]
        ax.bar(
            labels,
            heights,
            bottom=bottom,
            color=colors[outcome],
            hatch=hatches.get(outcome, ""),
            edgecolor="white",
            linewidth=0.5,
            label=outcome,
        )
        bottom = [b + h for b, h in zip(bottom, heights, strict=True)]

    base = rows[0]["base_rate_not_passed"]
    ax.axhline(1 - base, color="black", lw=0.8, ls="--")
    ax.set_ylim(0, 1)
    ax.set_ylabel("fração dos alunos")
    nome = {"degree": "grau", "betweenness": "intermediação", "eigenvector": "autovetor"}
    ax.set_xlabel(f"faixa de {nome.get(metric, metric)} (Q1 = menor)")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize=7)
    fig.tight_layout()

    stem = name or f"fig8-validacao-{dataset}-{projection_id}-{metric}"
    written = save_figure(fig, stem, out_dir=out)
    plt.close(fig)

    caption = (
        f"Desfecho histórico por faixa de centralidade ({metric}) na projeção "
        f"{projection_id} de {dataset}. Faixas por posição no ranking, Q1 = menor "
        f"centralidade. A linha tracejada marca a fração de concluintes da base "
        f"({1 - base:.1%}): quando os aprovados (Distinction + Pass) da faixa ficam "
        f"abaixo dela, a faixa tem mais não conclusão (Fail + Withdrawn) que a base. "
        f"Validação a posteriori (spec {PRODUCER}): o desfecho não entra em nenhum "
        f"cálculo de centralidade."
    )
    caption_path = out / f"{stem}.caption.txt"
    caption_path.write_text(caption + "\n", encoding="utf-8", newline="\n")
    return [*written, caption_path]


# ---------------------------------------------------------------------
# A rodada inteira — o que `centrality evaluate` chama
# ---------------------------------------------------------------------


def _load_metric(
    roots: Any, dataset: str, projection_id: str, metric: str
) -> CentralityResult | None:
    from edugraph.contracts import io

    if not roots.has(dataset, "centrality", projection_id, f"{metric}.meta.json"):
        return None
    return io.load_centrality(roots, dataset, projection_id, metric)  # type: ignore[arg-type]


def evaluate(
    roots: Any,
    dataset: str,
    *,
    discipline_projection: str = "discipline_simple",
    student_projection: str = "student_simple",
    metric: str = "betweenness",
    top_n: int = 5,
    quantiles: int = 4,
) -> dict[str, Any]:
    """Carrega os artefatos, lê os desfechos e monta as duas tabelas.

    É aqui, e não na CLI, que ``load_outcomes`` é chamada: o teste de
    contrato só autoriza módulos ``evaluate.py`` a ler os rótulos.

    Returns
    -------
    dict
        ``disciplines``: linhas de :func:`failure_rate_by_discipline`, ou
        ``None`` se a métrica for degenerada ou não existir;
        ``discipline_note``: por que não há tabela, quando não há;
        ``students`` e ``student_note``: o mesmo para
        :func:`outcome_by_centrality`; ``labels``: ``node_id`` → rótulo.
    """
    from edugraph.contracts import io
    from edugraph.contracts.paths import as_roots

    resolved = as_roots(roots)
    outcomes = io.load_outcomes(resolved, dataset)
    bipartite = io.load_bipartite(resolved, dataset)
    out: dict[str, Any] = {
        "disciplines": None,
        "discipline_note": "",
        "students": None,
        "student_note": "",
        "labels": {str(n): str(d.get("label", n)) for n, d in bipartite.graph.nodes(data=True)},
    }

    disciplinas = _load_metric(resolved, dataset, discipline_projection, metric)
    if disciplinas is None:
        out["discipline_note"] = (
            f"sem {metric} calculada para {discipline_projection}; rode `centrality all` antes"
        )
    elif is_degenerate(disciplinas):
        valor = next(iter(disciplinas.scores.values()))
        out["discipline_note"] = (
            f"{metric} em {discipline_projection} é igual para todas as disciplinas "
            f"({valor:.4f}): não há disciplina crítica a validar. Com V = módulo a projeção "
            "tende ao grafo completo (decisão D1); a validação só é informativa com "
            "granularidade mais fina."
        )
    else:
        ranking = [node for node, _ in disciplinas.top(top_n)]
        out["disciplines"] = failure_rate_by_discipline(ranking, outcomes, enrollment_of(bipartite))

    alunos = _load_metric(resolved, dataset, student_projection, metric)
    if alunos is None:
        out["student_note"] = (
            f"sem {metric} calculada para {student_projection}; rode `centrality all` antes"
        )
    elif is_degenerate(alunos):
        out["student_note"] = (
            f"{metric} em {student_projection} é igual para todos os alunos: as faixas "
            "seriam só a ordem dos ids, e a tabela não é produzida."
        )
    else:
        out["students"] = outcome_by_centrality(alunos, outcomes, quantiles=quantiles)
    return out
