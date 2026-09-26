"""Relatório interno consolidado  ``[C]`` — spec C-07.

**Saída obrigatória** (briefing §6.2): "relatórios de uso exclusivamente
interno da instituição. O sistema não expõe dados a terceiros."

Consolida o que está em ``metrics/`` numa entrega que alguém da
coordenação consiga ler: as comunidades e o que as caracteriza, as
disciplinas críticas e o que elas significam, e o que **não** se pode
concluir a partir disso.

Três garantias, todas testadas:

- **Nenhum aluno aparece**, nem por id nem por rótulo: o relatório fala
  de comunidades e disciplinas. O perfil de uma partição do lado
  *disciplina* caracteriza as comunidades pelos alunos (B-05), então ele
  não entra — só a lista de disciplinas de cada comunidade. Antes de
  gravar, o texto é varrido atrás de ids de aluno, e o relatório é
  recusado se algum aparecer.
- **Seção faltante vira nota**, não erro: um dataset sem partição ou sem
  centralidade gera o relatório com o que tiver.
- **Determinístico**: sem data nem caminho absoluto no texto; rodar duas
  vezes produz o mesmo arquivo.
"""

from __future__ import annotations

import contextlib
import math
import re
from pathlib import Path
from typing import Any

from edugraph.centrality.critical_disciplines import (
    is_discipline_projection,
    labels_of,
    load_results,
    rank_disciplines,
)
from edugraph.centrality.disagreement import disagreement, rank_correlation
from edugraph.contracts import io
from edugraph.contracts.errors import ArtifactNotFoundError, ContractError
from edugraph.contracts.paths import ArtifactRoots, as_roots
from edugraph.contracts.types import CentralityResult

#: Id da spec, para as mensagens e as legendas desta etapa.
PRODUCER = "C-07"

#: Posições por métrica na tabela de disciplinas críticas do relatório.
TOP_N = 5

#: Comunidades descritas uma a uma; as demais entram só na contagem.
MAX_COMMUNITIES = 8

#: Nós listados por comunidade: uma lista de 187 ids não é lida por ninguém.
MAX_NAMES = 12

METRIC_NAMES: dict[str, str] = {
    "degree": "grau",
    "betweenness": "intermediação",
    "eigenvector": "autovetor",
}

#: Pedaços alfanuméricos do texto. Sem ``_`` na classe de propósito:
#: ``S100282_x`` precisa virar ``S100282`` + ``x`` para ser pego.
_TOKEN = re.compile(r"[A-Za-z0-9]+")

#: Rótulos de aluno mais curtos que isto não entram na guarda (ver
#: :func:`_student_identifiers`); o id com prefixo ``S`` entra sempre.
MIN_LABEL_LEN = 4


# ---------------------------------------------------------------------
# Formatação — o leitor não programa, então vírgula decimal
# ---------------------------------------------------------------------


def _num(value: float, digits: int = 3) -> str:
    if isinstance(value, float) and math.isnan(value):
        return "indefinida"
    return f"{value:.{digits}f}".replace(".", ",")


def _pct(value: float, digits: int = 1) -> str:
    return f"{100 * value:.{digits}f}%".replace(".", ",")


def _int(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def _pp(value: float) -> str:
    return f"{100 * value:+.1f} p.p.".replace(".", ",", 1)


# ---------------------------------------------------------------------
# Seções
# ---------------------------------------------------------------------


def _section_data(roots: ArtifactRoots, dataset: str) -> list[str]:
    lines = ["## Os dados", ""]
    try:
        bipartite = io.load_bipartite(roots, dataset)
    except ArtifactNotFoundError:
        return [*lines, "_Sem o grafo bipartido em disco: esta seção foi omitida._", ""]
    spec = bipartite.spec
    lines += [
        f"- **Alunos:** {_int(len(bipartite.students))}",
        f"- **Disciplinas (nós do outro lado):** {_int(len(bipartite.disciplines))}"
        f" — granularidade `{spec.granularity}`",
        f"- **Vínculos aluno–disciplina:** {_int(bipartite.graph.number_of_edges())}"
        f" — critério `{spec.edge_criterion}`"
        + (f", limiar {_num(float(spec.threshold), 0)}" if spec.threshold is not None else ""),
    ]
    if spec.cohort:
        lines.append(f"- **Recorte:** coorte `{spec.cohort}`")
    lines += [
        "",
        "Cada disciplina liga-se às outras pelos alunos que elas compartilham "
        "(projeção disciplina↔disciplina), e cada aluno aos outros pelas disciplinas "
        "em comum (projeção aluno↔aluno). É sobre essas duas redes que as comunidades "
        "e as centralidades abaixo foram calculadas — **sem usar notas, desfechos "
        "ou dados pessoais** como entrada.",
        "",
    ]
    return lines


def _discipline_noun(roots: ArtifactRoots, dataset: str) -> str:
    """Como chamar o nó do lado V: no AVA, ele é um recurso, não uma disciplina."""
    try:
        granularity = io.load_bipartite(roots, dataset).spec.granularity
    except ArtifactNotFoundError:
        return "disciplinas"
    return "recursos do AVA" if granularity == "vle_site" else "disciplinas"


def _section_communities(roots: ArtifactRoots, dataset: str, labels: dict[str, str]) -> list[str]:
    lines = ["## Comunidades", ""]
    partitions = roots.partitions(dataset)
    if not partitions:
        return [
            *lines,
            "_Nenhuma partição em disco para este dataset: esta seção foi omitida. "
            "Rode `python -m edugraph community louvain` (Frente B)._",
            "",
        ]

    lines += [
        "Uma **comunidade** é um grupo de nós mais ligados entre si do que com o resto "
        "da rede. A **modularidade Q** mede quanto: perto de 0, os grupos não se "
        "distinguem do acaso; acima de ~0,3, a divisão costuma ser nítida. Um Q só "
        "vale como evidência comparado ao de redes embaralhadas (linha de base da "
        "spec A-08).",
        "",
        "| Rede | Algoritmo | Q | Comunidades | Maior | Situação |",
        "|---|---|---|---|---|---|",
    ]
    loaded = [io.load_partition(roots, dataset, artifact_id) for artifact_id in partitions]
    for partition in loaded:
        largest = max(len(nodes) for nodes in partition.groups().values())
        lines.append(
            f"| {partition.projection_id} | {partition.algorithm} | "
            f"{_num(partition.modularity)} | {partition.n_communities} | "
            f"{_int(largest)} | {partition.status} |"
        )
    lines.append("")

    for partition in loaded:
        groups = sorted(partition.groups().items(), key=lambda kv: (-len(kv[1]), kv[0]))
        total = len(partition.membership)
        lines += [f"### {partition.algorithm} sobre {partition.projection_id}", ""]
        if partition.projection_id.startswith("student_"):
            lines += _student_communities(roots, dataset, partition.artifact_id, total)
        else:
            noun = _discipline_noun(roots, dataset)
            for community, nodes in groups[:MAX_COMMUNITIES]:
                names = ", ".join(labels.get(n, n) for n in nodes[:MAX_NAMES])
                if len(nodes) > MAX_NAMES:
                    names += f" e mais {len(nodes) - MAX_NAMES}"
                lines.append(
                    f"- **Comunidade {community}** ({len(nodes)} {noun}, "
                    f"{_pct(len(nodes) / total, 0)}): {names}"
                )
            if len(groups) > MAX_COMMUNITIES:
                lines.append(f"- … e mais {len(groups) - MAX_COMMUNITIES} comunidades menores.")
            lines.append("")
    return lines


def _student_communities(
    roots: ArtifactRoots, dataset: str, artifact_id: str, total: int
) -> list[str]:
    """Comunidades de alunos pelo **tamanho** e pelo que as caracteriza — nunca por membro."""
    try:
        profile = io.load_profile(roots, dataset, artifact_id)
    except ArtifactNotFoundError:
        return [
            "_Sem `profile.csv` desta partição (spec B-05): só a tabela acima._",
            "",
        ]
    rows = sorted(profile, key=lambda r: (-int(r["size"]), int(r["community"])))
    lines = [
        "O que caracteriza cada grupo são as disciplinas **mais frequentes nele do que "
        "na base** (frequência na comunidade × na base). Os alunos não são listados.",
        "",
        "| Comunidade | Alunos | Parcela | Disciplinas mais características |",
        "|---|---|---|---|",
    ]
    for row in rows[:MAX_COMMUNITIES]:
        size = int(row["size"])
        lines.append(
            f"| {row['community']} | {_int(size)} | {_pct(size / total, 0)} | "
            f"{row['top_disciplines'] or '—'} |"
        )
    if len(rows) > MAX_COMMUNITIES:
        lines.append(f"| … | | | e mais {len(rows) - MAX_COMMUNITIES} comunidades menores |")
    lines.append("")
    return lines


def _section_critical(roots: ArtifactRoots, dataset: str) -> tuple[list[str], list[str]]:
    """Disciplinas críticas; devolve as linhas e as projeções usadas."""
    lines = ["## Disciplinas críticas", ""]
    projections = [p for p in roots.centralities(dataset) if is_discipline_projection(p)]
    if not projections:
        return [
            *lines,
            "_Sem centralidades de disciplina em disco: esta seção foi omitida. "
            "Rode `python -m edugraph centrality all`._",
            "",
        ], []

    lines += [
        "Três medidas de quão central é uma disciplina na rede do currículo:",
        "",
        "- **Grau** — com quantas outras disciplinas ela compartilha alunos.",
        "- **Intermediação** — com que frequência ela está no caminho mais curto entre "
        "duas outras. Uma disciplina de intermediação alta é um **gargalo estrutural**: "
        "liga partes do currículo que, sem ela, ficariam distantes.",
        "- **Autovetor** — se ela se liga a disciplinas que também são centrais.",
        "",
    ]
    used: list[str] = []
    for projection_id in projections:
        results = load_results(roots, dataset, projection_id)
        if not results:
            continue
        used.append(projection_id)
        labels = labels_of(io.load_projection(roots, dataset, projection_id))
        rows = rank_disciplines(results, top_n=TOP_N, dataset=dataset, labels=labels)
        metrics = [m for m in METRIC_NAMES if m in results]
        by_metric = {m: [r for r in rows if r["metric"] == m] for m in metrics}

        lines += [f"### Rede {projection_id}", ""]
        lines.append(
            "| Posição | " + " | ".join(METRIC_NAMES[m].capitalize() for m in metrics) + " |"
        )
        lines.append("|---|" + "---|" * len(metrics))
        for position in range(max(len(v) for v in by_metric.values())):
            cells = []
            for metric in metrics:
                ranked = by_metric[metric]
                cells.append(
                    f"{ranked[position]['label']} ({_num(ranked[position]['score'])})"
                    if position < len(ranked)
                    else ""
                )
            lines.append(f"| {position + 1}º | " + " | ".join(cells) + " |")
        lines.append("")
        lines += _critical_notes(results, labels)
    return lines, used


def _critical_notes(results: dict[str, CentralityResult], labels: dict[str, str]) -> list[str]:
    lines: list[str] = []
    betweenness = results.get("betweenness")
    if betweenness is not None:
        params = betweenness.params
        modo = {
            "none": "contando passos (sem peso)",
            "inverse": "com o peso como distância (1/peso)",
            "raw": "com o peso bruto",
        }.get(str(params.get("weight_mode")), str(params.get("weight_mode")))
        lines.append(
            f"A intermediação foi calculada {modo}"
            + (
                f", por estimativa com {params.get('k')} pontos de partida sorteados"
                if params.get("estimate")
                else ""
            )
            + "."
        )
        if max(betweenness.scores.values()) - min(betweenness.scores.values()) <= 1e-12:
            lines.append(
                "**Atenção:** a intermediação é igual para todas as disciplinas desta rede "
                "— ela é densa demais para haver gargalo, e a ordem da tabela é só alfabética."
            )
    if all(m in results for m in METRIC_NAMES):
        sets = disagreement(results, top_n=TOP_N)
        only_bridge = ", ".join(labels.get(n, n) for n in sets["only_betweenness"])
        if only_bridge:
            lines.append(
                f"**Pontes que não são populares:** {only_bridge} — estão entre as {TOP_N} "
                "de maior intermediação, mas não entre as de maior grau nem autovetor. É o "
                "perfil de gargalo: poucos alunos em comum com cada vizinha, mas ligando "
                "áreas diferentes."
            )
        rho = rank_correlation(results["betweenness"], results["eigenvector"])
        lines.append(
            f"Correlação (Spearman) entre intermediação e autovetor: {_num(rho, 2)}. "
            "Quanto mais perto de zero, mais as duas medidas apontam disciplinas diferentes."
        )
    # Uma linha em branco depois de cada nota: no Markdown, linhas
    # seguidas viram um parágrafo só.
    return [part for line in lines for part in (line, "")]


def _section_validation(roots: ArtifactRoots, dataset: str, projections: list[str]) -> list[str]:
    lines = ["## Relação com o desfecho histórico", ""]
    # A leitura do desfecho é da C-06 (evaluate.py, único autorizado);
    # aqui só entram as taxas agregadas que ela devolve.
    from edugraph.centrality.evaluate import evaluate

    discipline_projection = (
        "discipline_simple"
        if "discipline_simple" in projections
        else (projections[0] if projections else "discipline_simple")
    )
    try:
        result = evaluate(roots, dataset, discipline_projection=discipline_projection)
    except ArtifactNotFoundError:
        return [
            *lines,
            "_Sem desfechos históricos (`outcomes.csv`) para este dataset: seção omitida._",
            "",
        ]

    lines += [
        "Depois de identificadas as disciplinas críticas — sem olhar nota nem desfecho —, "
        "conferimos se os alunos delas concluem menos. **Não conclusão** = reprovação "
        "(`Fail`) ou desistência (`Withdrawn`).",
        "",
    ]
    rows = result["disciplines"]
    if rows is None:
        lines += [f"_{result['discipline_note']}_", ""]
    else:
        by_group = {r["group"]: r for r in rows}
        critical, base = by_group["critical_all"], by_group["base"]
        lines += [
            f"- Alunos das {TOP_N} disciplinas de maior intermediação: "
            f"**{_pct(critical['rate_not_passed'])}** de não conclusão "
            f"({_int(critical['n_students'])} alunos).",
            f"- Base (todos os alunos): **{_pct(base['rate_not_passed'])}**.",
            f"- Diferença: **{_pp(critical['excess_not_passed'])}**.",
            "",
        ]
        if abs(critical["excess_not_passed"]) < 0.03:
            lines += [
                "A diferença é pequena: **ser gargalo estrutural não é o mesmo que ser "
                "uma disciplina de alta reprovação**. As duas coisas medem dimensões "
                "diferentes, e a centralidade não deve ser lida como um indicador de "
                "desempenho.",
                "",
            ]
    students = result["students"]
    if students is not None:
        low, high = students[0], students[-1]
        lines += [
            f"Entre os alunos, a não conclusão vai de {_pct(low['rate_not_passed'])} na faixa "
            f"de menor intermediação a {_pct(high['rate_not_passed'])} na de maior "
            f"(base {_pct(low['base_rate_not_passed'])}).",
            "",
        ]
        if abs(low["rate_not_passed"] - high["rate_not_passed"]) >= 0.15:
            lines += [
                "**Cuidado com essa diferença.** A posição do aluno na rede reflete o "
                "quanto ele participou; quem desiste participa menos até sair e, por isso, "
                "fica menos central. A relação mostra que as duas coisas andam juntas — "
                "não que a centralidade cause o desfecho nem que sirva para prevê-lo.",
                "",
            ]
    return lines


def _section_limitations(roots: ArtifactRoots, dataset: str) -> list[str]:
    lines = [
        "## O que esta análise não diz",
        "",
        "- **Não é um ranking de alunos.** Nenhum aluno é identificado neste relatório, e "
        "nada aqui deve ser usado para avaliar, selecionar ou rotular pessoas. A posição "
        "de um aluno na rede reflete as disciplinas que ele cursou, não o seu mérito.",
        "- **Disciplina crítica não quer dizer disciplina difícil.** Intermediação alta "
        "significa que a disciplina conecta partes do currículo; não diz nada, por si, "
        "sobre reprovação, qualidade do ensino ou do docente.",
        "- **Comunidade não é turma nem perfil.** É um agrupamento estatístico pela "
        "estrutura de disciplinas em comum; os mesmos dados admitem outras divisões "
        "igualmente defensáveis.",
        "- **Correlação não é causa.** A comparação com o desfecho é descritiva: mostra "
        "se as duas coisas andam juntas, não que uma provoque a outra, e não houve teste "
        "de significância.",
        "- **Depende das escolhas de modelagem.** Granularidade da disciplina, critério "
        "de vínculo e tratamento do peso mudam os resultados; cada escolha está "
        "registrada em `docs/artigo/decisoes-metodologicas.md`.",
    ]
    try:
        spec = io.load_bipartite(roots, dataset).spec
    except ArtifactNotFoundError:
        spec = None
    if spec is not None and spec.edge_criterion == "score_threshold":
        lines.append(
            f"- **Só vínculos com nota a partir de {_num(float(spec.threshold or 0), 0)}.** "
            "Alunos que foram mal numa disciplina podem não aparecer nela; as taxas de não "
            "conclusão acima ficam, por isso, abaixo das reais."
        )
    lines += [
        "- **Uso exclusivamente interno.** Este documento não deve ser divulgado fora da "
        "instituição.",
        "",
    ]
    return lines


# ---------------------------------------------------------------------
# Figura 7 — ranking de disciplinas por intermediação
# ---------------------------------------------------------------------


def figure_centrality_ranking(dataset: str, roots: list[Path], out: Path) -> Path:
    """Figura do ranking de disciplinas por intermediação (C-03/C-07).

    Barras horizontais com todas as disciplinas da projeção
    ``discipline_simple`` (ou da primeira ``discipline_*``), da mais para
    a menos intermediária. Devolve o PNG; o SVG e a legenda ficam ao lado.
    """
    import matplotlib

    # Sem janela: no Windows o backend padrão é o Tk, que falha sem
    # tcl instalado (e não faz sentido num processo de linha de comando).
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from edugraph.reporting.figures import COLUMN_WIDTH_IN, apply_style, save_figure

    resolved = as_roots(roots)
    candidates = [p for p in resolved.centralities(dataset) if is_discipline_projection(p)]
    candidates = [
        p
        for p in sorted(candidates, key=lambda p: (p != "discipline_simple", p))
        if resolved.has(dataset, "centrality", p, "betweenness.meta.json")
    ]
    if not candidates:
        raise ArtifactNotFoundError(
            f"{PRODUCER}: sem intermediação de disciplinas em {dataset!r}; "
            "rode `centrality all` antes"
        )
    projection_id = candidates[0]
    result = io.load_centrality(resolved, dataset, projection_id, "betweenness")
    labels = labels_of(io.load_projection(resolved, dataset, projection_id))
    ranked = result.top(len(result.scores))

    apply_style()
    height = max(2.0, 0.16 * len(ranked) + 0.8)
    fig, ax = plt.subplots(figsize=(COLUMN_WIDTH_IN, height))
    names = [labels.get(node, node) for node, _ in ranked][::-1]
    values = [score for _, score in ranked][::-1]
    ax.barh(names, values, color="#0072B2")
    ax.set_xlabel("intermediação (normalizada)")
    ax.tick_params(axis="y", labelsize=6)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()

    stem = f"fig7-disciplinas-{dataset}-{projection_id}"
    written = save_figure(fig, stem, out_dir=out)
    plt.close(fig)

    params = result.params
    noun = _discipline_noun(resolved, dataset).capitalize()
    caption = (
        f"{noun} de {dataset} ordenados pela intermediação na projeção "
        f"{projection_id} (weight_mode = {params.get('weight_mode')}"
        + (f", estimativa com k = {params.get('k')}" if params.get("estimate") else "")
        + "). Quanto maior a barra, mais caminhos mínimos entre outras disciplinas "
        f"passam por ela. Spec {PRODUCER}."
    )
    (out / f"{stem}.caption.txt").write_text(caption + "\n", encoding="utf-8", newline="\n")
    return written[0]


# ---------------------------------------------------------------------
# O relatório
# ---------------------------------------------------------------------


def _student_identifiers(roots: ArtifactRoots, dataset: str) -> set[str]:
    """Ids **e rótulos** dos alunos, menos o que também nomeia uma disciplina.

    O rótulo de um aluno no OULAD é o número de matrícula (``S100282`` →
    ``100282``); o de um recurso do AVA também é um número. Um token que
    nomeia os dois não identifica ninguém, e contá-lo daria falso alarme.
    """
    try:
        graph = io.load_bipartite(roots, dataset).graph
    except ArtifactNotFoundError:
        return set()
    students: set[str] = set()
    others: set[str] = set()
    for node, data in graph.nodes(data=True):
        label = str(data.get("label", node))
        if data.get("kind") == "student":
            students.add(str(node))
            # Rótulo curto ("3" em tiny_v1) não identifica ninguém e colidiria
            # com qualquer contagem do texto; matrícula tem 4+ caracteres.
            if len(label) >= MIN_LABEL_LEN:
                students.add(label)
        else:
            others.update({str(node), label})
    return students - others


def check_no_student_ids(text: str, student_ids: set[str]) -> None:
    """Recusa o texto se algum id ou rótulo de aluno aparecer nele.

    Compara **tokens exatos** do texto com ``student_ids`` (ids e rótulos
    dos alunos — ver :func:`_student_identifiers`), então pega também o
    número de matrícula sem o prefixo ``S``.

    Raises
    ------
    ContractError
        Com os primeiros encontrados. É a proteção da restrição de uso
        interno: o relatório fala de grupos, nunca de pessoas.
    """
    found = sorted(set(_TOKEN.findall(text)) & student_ids)
    if found:
        raise ContractError(
            f"{PRODUCER}: o relatório citaria alunos individualmente ({found[:5]}); "
            "ele só pode trazer agregados"
        )


def build_internal_report(
    dataset: str, roots: list[Path], out: Path, *, fmt: str = "markdown"
) -> Path:
    """Gera o relatório interno a partir dos artefatos em disco.

    Grava ``<out>/relatorio-interno-<dataset>.md`` e, se houver
    intermediação de disciplinas, a figura 7 em ``<out>/figures``,
    referenciada pelo relatório com caminho relativo.

    Raises
    ------
    ContractError
        Se ``fmt`` não for ``"markdown"`` ou se o texto citar algum aluno.
    """
    if fmt != "markdown":
        raise ContractError(f"{PRODUCER}: formato {fmt!r} não suportado; só markdown")
    resolved = as_roots(roots)
    if dataset not in resolved.datasets():
        raise ArtifactNotFoundError(
            f"dataset {dataset!r} não encontrado em {', '.join(str(r) for r in resolved)}"
        )

    labels: dict[str, Any] = {}
    with contextlib.suppress(ArtifactNotFoundError):  # sem bipartido, rótulo = id
        labels = {
            str(n): str(d.get("label", n))
            for n, d in io.load_bipartite(resolved, dataset).graph.nodes(data=True)
            if d.get("kind") == "discipline"
        }

    lines = [
        f"# Relatório interno — {dataset}",
        "",
        "> **Uso exclusivamente interno da instituição.** Análise topológica da rede de "
        "alunos e disciplinas (TCC Grupo 16, UniAnchieta). O documento fala de grupos e "
        "de disciplinas; nenhum aluno é identificado.",
        "",
    ]
    lines += _section_data(resolved, dataset)
    lines += _section_communities(resolved, dataset, labels)
    critical_lines, used = _section_critical(resolved, dataset)
    lines += critical_lines

    if used:
        try:
            png = figure_centrality_ranking(dataset, list(resolved), out / "figures")
            lines += [
                f"![Disciplinas por intermediação](figures/{png.name})",
                "",
                "_Figura: todas as disciplinas, da de maior para a de menor intermediação._",
                "",
            ]
        except ArtifactNotFoundError:
            pass

    lines += _section_validation(resolved, dataset, used)
    lines += _section_limitations(resolved, dataset)

    text = "\n".join(lines).rstrip() + "\n"
    check_no_student_ids(text, _student_identifiers(resolved, dataset))

    out.mkdir(parents=True, exist_ok=True)
    path = out / f"relatorio-interno-{dataset}.md"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path
