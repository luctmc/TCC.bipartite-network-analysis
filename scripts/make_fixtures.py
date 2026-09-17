"""Gera as fixtures versionadas do repositório  ``[T]``.

    python scripts/make_fixtures.py            # gera as que faltarem
    python scripts/make_fixtures.py --force    # regrava (só com revisão!)
    python scripts/make_fixtures.py --only tiny_v1

**Fixtures são imutáveis.** Quem precisar de outra cria ``synthetic_v2``;
as versões anteriores continuam existindo para os testes que dependem
delas. Isso elimina a classe inteira de conflitos "a fixture mudou e meu
teste quebrou" (§7 do plano de arquitetura). Por isso o script se recusa
a sobrescrever sem ``--force``.

**As implementações aqui são de referência, não das frentes.** O
bipartido e as projeções abaixo usam NetworkX diretamente e existem para
destravar B e C no dia 0. Quando A-03 e A-04 fecharem, elas produzirão
os mesmos artefatos em ``data/processed``, e a comparação com estas
fixtures é justamente um dos testes de aceite daquelas specs.

Os artefatos de comunidade e centralidade de ``synthetic_v1`` são
gerados pela biblioteca e marcados com ``producer="reference"`` no
``meta.json`` — ninguém deve confundi-los com saída da Frente B ou C.

**Regenere sob Python 3.13.** Com peso fracionário (``resource_
allocation``), o Louvain do ``python-louvain`` pode devolver uma
partição diferente (mesma seed, Q muda no 4º decimal) conforme a versão
do Python — não por bug nosso: ``induced_graph()`` da biblioteca itera
``set(partition.values())``, e ordem de iteração de ``set`` não é
garantida estável entre versões do CPython (ao contrário de ``dict``,
garantido desde a 3.7). As fixtures commitadas foram geradas em 3.13, e
é a versão que o job ``fixtures-deterministicas`` da CI fixa — não a
transforme em matriz. Ver ADR-0011.
"""

from __future__ import annotations

import argparse
import itertools
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import networkx as nx

# O script roda de fora do pacote instalado; garante o src/ no path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from edugraph.console import configure as configure_console
from edugraph.contracts import io
from edugraph.contracts.types import (
    BipartiteBundle,
    BipartiteSpec,
    CentralityResult,
    Meta,
    Outcomes,
    Partition,
    ProjectionBundle,
    ProjectionSpec,
)
from edugraph.data.synthetic import SyntheticSpec, generate

FIXTURES_ROOT = Path(__file__).resolve().parents[1] / "data" / "fixtures"

#: Nota mínima para criar uma aresta nas fixtures. Mesmo valor do starter
#: kit, para que os números de referência sejam comparáveis com os dele.
SCORE_THRESHOLD = 60.0

#: Data congelada nos ``meta.json`` das fixtures. Fixtures são versionadas
#: em git e imutáveis: se ``created_at`` fosse o relógio, regenerar a
#: fixture produziria um diff em todo arquivo sem que nenhum dado tivesse
#: mudado, e a escrita canônica da ADR-0011 perderia o sentido.
FIXTURE_CREATED_AT = "2026-09-17T00:00:00+00:00"

#: Fixtures não carregam tempo de execução: ele depende da máquina e
#: mudaria a cada geração. Tempos reais vivem nos artefatos de
#: ``data/processed`` e em ``metrics/``, que é onde o artigo os cita.
FIXTURE_RUNTIME_S = 0.0

#: Todas as quatro projeções: dois lados × duas ponderações.
PROJECTION_SPECS: tuple[ProjectionSpec, ...] = (
    ProjectionSpec(side="student", weighting="simple", implementation="networkx"),
    ProjectionSpec(side="student", weighting="resource_allocation", implementation="networkx"),
    ProjectionSpec(side="discipline", weighting="simple", implementation="networkx"),
    ProjectionSpec(side="discipline", weighting="resource_allocation", implementation="networkx"),
)


# =====================================================================
# Implementações de referência  [T]
# =====================================================================


def _write_text(path: Path, text: str) -> None:
    """Escreve texto com fim de linha LF, em qualquer sistema.

    ``Path.write_text`` sem ``newline`` usa a tradução padrão do sistema:
    no Windows, cada ``\\n`` vira ``\\r\\n``, e a mesma fixture sai com
    bytes diferentes conforme quem a gerou. Ver ADR-0011 e ``.gitattributes``.
    """
    path.write_text(text, encoding="utf-8", newline="\n")


def _meta(producer: str, notes: str) -> Meta:
    """Meta de fixture: data congelada, para que o diff só mude com o dado."""
    return Meta(producer=producer, created_at=FIXTURE_CREATED_AT, notes=notes)


def build_bipartite_reference(
    rows: list[dict[str, Any]], spec: BipartiteSpec, *, producer: str
) -> BipartiteBundle:
    """Bipartido de referência: agrega por (aluno, módulo) e corta pelo limiar.

    Equivale ao ``build_graph.py`` do starter kit, com duas diferenças
    que o contrato exige: prefixo ``D`` (não ``M``) nas disciplinas, e
    nenhum atributo de nó além de ``kind`` e ``label``.
    """
    scores: dict[tuple[str, str], list[float]] = {}
    for row in rows:
        key = (f"S{row['id_student']}", f"D{row['code_module']}")
        scores.setdefault(key, []).append(float(row["score_media"]))

    graph = nx.Graph()
    for (student, discipline), values in scores.items():
        graph.add_node(student, kind="student", label=student[1:])
        graph.add_node(discipline, kind="discipline", label=discipline[1:])
        mean_score = sum(values) / len(values)
        if spec.threshold is None or mean_score >= spec.threshold:
            graph.add_edge(student, discipline, weight=mean_score)

    # Nós isolados pelo corte saem: um aluno sem nenhuma aresta não
    # participa de projeção nenhuma e só polui o artefato.
    graph.remove_nodes_from([n for n, d in graph.degree if d == 0])

    return BipartiteBundle(
        graph=graph,
        spec=spec,
        meta=_meta(
            producer,
            "Implementação de referência do dia 0; a da Frente A é a spec A-03.",
        ),
    )


def project_reference(bipartite: BipartiteBundle, spec: ProjectionSpec) -> ProjectionBundle:
    """Projeção de referência, nas duas ponderações.

    ``simple`` conta vizinhos compartilhados; ``resource_allocation``
    soma ``1/grau`` de cada vizinho compartilhado (Zhou et al., 2007).
    Escrita de forma direta e legível: é referência, não a implementação
    otimizada que a spec A-04 vai entregar.
    """
    graph = bipartite.graph
    side_nodes = sorted(n for n, d in graph.nodes(data=True) if d.get("kind") == spec.side)
    other_nodes = [n for n in graph.nodes if n not in set(side_nodes)]

    projected = nx.Graph()
    for node in side_nodes:
        projected.add_node(node, kind=spec.side, label=graph.nodes[node].get("label", node))

    for shared in other_nodes:
        neighbors = sorted(n for n in graph.neighbors(shared) if n in set(side_nodes))
        degree = graph.degree(shared)
        if degree < 2:
            continue
        contribution = 1.0 if spec.weighting == "simple" else 1.0 / degree
        for left, right in itertools.combinations(neighbors, 2):
            if projected.has_edge(left, right):
                projected[left][right]["weight"] += contribution
            else:
                projected.add_edge(left, right, weight=contribution)

    return ProjectionBundle(
        graph=projected,
        spec=spec,
        source=bipartite.spec,
        meta=_meta("reference", "Projeção de referência do dia 0; a da Frente A é a spec A-04."),
    )


def louvain_reference(projection: ProjectionBundle, *, seed: int = 42) -> Partition:
    """Partição de referência via ``python-louvain``.

    Marcada com ``producer="reference"``: **não** é saída da Frente B, é
    o que permite à Frente C colorir o grafo no dia 0.
    """
    import community as community_louvain

    graph = projection.graph
    # Sem cronômetro de propósito: fixtures gravam runtime_s = 0 (ver
    # FIXTURE_RUNTIME_S). Tempo é medido nas rodadas reais, em
    # data/processed, que é de onde as tabelas do artigo saem.
    raw = community_louvain.best_partition(graph, weight="weight", random_state=seed)

    membership = _densify(raw)
    groups = _as_groups(membership)
    modularity = nx.community.modularity(graph, groups, weight="weight")

    return Partition(
        algorithm="louvain",
        projection_id=projection.projection_id,
        membership=membership,
        modularity=float(modularity),
        n_communities=len(groups),
        runtime_s=FIXTURE_RUNTIME_S,
        params={"seed": seed, "implementation": "python_louvain", "weight": "weight"},
        status="ok",
        meta=_meta("reference", "Partição de referência do dia 0; a da Frente B é a spec B-01."),
    )


def centrality_reference(projection: ProjectionBundle) -> list[CentralityResult]:
    """As três centralidades de referência sobre uma projeção.

    Intermediação **sem peso**: em NetworkX, peso num caminho mínimo é
    distância, e nas projeções peso alto significa mais afinidade, não
    mais distância. Resolver essa inversão é parte da spec C-01; a
    fixture não antecipa a decisão, apenas registra a escolha em
    ``params``.
    """
    graph = projection.graph
    results: list[CentralityResult] = []

    start = time.perf_counter()
    degree = nx.degree_centrality(graph)
    results.append(
        _centrality_result(
            projection,
            "degree",
            degree,
            time.perf_counter() - start,
            {"normalized": True, "weight": None},
        )
    )

    start = time.perf_counter()
    betweenness = nx.betweenness_centrality(graph, weight=None, normalized=True)
    results.append(
        _centrality_result(
            projection,
            "betweenness",
            betweenness,
            time.perf_counter() - start,
            {"normalized": True, "weight_mode": "none"},
        )
    )

    start = time.perf_counter()
    converged = True
    try:
        eigenvector = nx.eigenvector_centrality(graph, weight="weight", max_iter=1000, tol=1e-10)
    except nx.PowerIterationFailedConvergence:
        converged = False
        eigenvector = nx.eigenvector_centrality_numpy(graph, weight="weight")
    results.append(
        _centrality_result(
            projection,
            "eigenvector",
            {k: abs(v) for k, v in eigenvector.items()},
            time.perf_counter() - start,
            {"weight": "weight", "max_iter": 1000, "tol": 1e-10, "implementation": "networkx"},
            converged=converged,
        )
    )
    return results


def _centrality_result(
    projection: ProjectionBundle,
    metric: str,
    scores: dict[str, float],
    runtime: float,
    params: dict[str, Any],
    *,
    converged: bool = True,
) -> CentralityResult:
    return CentralityResult(
        projection_id=projection.projection_id,
        metric=metric,  # type: ignore[arg-type]
        scores={k: float(v) for k, v in scores.items()},
        params=params,
        runtime_s=FIXTURE_RUNTIME_S,
        converged=converged,
        meta=_meta(
            "reference",
            "Centralidade de referência do dia 0; a da Frente C são as specs C-01/C-02.",
        ),
    )


def _densify(membership: dict[str, int]) -> dict[str, int]:
    """Renumera comunidades para 0..k-1 pela ordem do menor nó de cada uma."""
    first_node: dict[int, str] = {}
    for node, community in sorted(membership.items()):
        first_node.setdefault(community, node)
    order = sorted(first_node, key=lambda c: first_node[c])
    remap = {old: new for new, old in enumerate(order)}
    return {node: remap[c] for node, c in sorted(membership.items())}


def _as_groups(membership: dict[str, int]) -> list[set[str]]:
    groups: dict[int, set[str]] = {}
    for node, community in membership.items():
        groups.setdefault(community, set()).add(node)
    return [groups[c] for c in sorted(groups)]


# =====================================================================
# tiny_v1 — 6 alunos × 3 disciplinas, conferível à mão
# =====================================================================

#: Matrículas de ``tiny_v1``. Desenhadas para que projeção simples e
#: alocação de recursos ordenem os pares **de forma diferente**: em
#: simples, S1-S6 e S3-S4 empatam em 1; em alocação de recursos,
#: S1-S6 = 0,25 e S3-S4 = 1/3. É o contraexemplo mínimo do viés que
#: Zhou et al. (2007) corrigem.
TINY_ENROLLMENTS: tuple[tuple[str, str, float], ...] = (
    ("1", "A", 82.0),
    ("1", "B", 71.0),
    ("2", "A", 64.0),
    ("2", "B", 90.0),
    ("3", "A", 77.0),
    ("3", "B", 68.0),
    ("3", "C", 61.0),
    ("4", "C", 85.0),
    ("5", "C", 73.0),
    ("6", "A", 66.0),
)

#: Grupos plantados de ``tiny_v1``: o núcleo {S1,S2,S3,S6} e o par
#: {S4,S5}. S3 é a ponte entre os dois — é ele que a intermediação deve
#: apontar.
TINY_PLANTED: dict[str, int] = {
    "S1": 0,
    "S2": 0,
    "S3": 0,
    "S6": 0,
    "S4": 1,
    "S5": 1,
}

TINY_OUTCOMES: dict[str, str] = {
    "S1": "Pass",
    "S2": "Distinction",
    "S3": "Pass",
    "S4": "Fail",
    "S5": "Withdrawn",
    "S6": "Pass",
}


def make_tiny_v1(out_root: Path) -> None:
    """Gera ``tiny_v1``: a fixture dos testes exatos."""
    rows = [
        {"id_student": student, "code_module": module, "score_media": score}
        for student, module, score in TINY_ENROLLMENTS
    ]
    spec = BipartiteSpec(
        dataset="tiny_v1",
        granularity="module",
        edge_criterion="score_threshold",
        threshold=SCORE_THRESHOLD,
    )
    bipartite = build_bipartite_reference(rows, spec, producer="make_fixtures")
    io.save_bipartite(bipartite, out_root)
    io.save_outcomes(
        Outcomes(final_result=TINY_OUTCOMES, planted_group=TINY_PLANTED),
        out_root,
        "tiny_v1",
    )

    for projection_spec in PROJECTION_SPECS:
        projection = project_reference(bipartite, projection_spec)
        io.save_projection(projection, out_root)

    _write_tiny_expected(out_root / "tiny_v1" / "expected")


def _write_tiny_expected(out: Path) -> None:
    """Valores conferidos à mão, para os testes unitários exatos.

    Cada número aqui foi derivado no papel a partir de
    :data:`TINY_ENROLLMENTS`, **não** copiado da saída do NetworkX —
    é isso que torna os testes que os usam uma verificação de verdade.
    A derivação está em docs/testes/estrategia.md.
    """
    out.mkdir(parents=True, exist_ok=True)

    # Graus no bipartido: DA=4 (S1,S2,S3,S6), DB=3 (S1,S2,S3), DC=3 (S3,S4,S5).
    # Projeção aluno↔aluno simples: nº de disciplinas em comum.
    _write_text(
        out / "student_simple.csv",
        "source,target,weight\n"
        "S1,S2,2.0\n"
        "S1,S3,2.0\n"
        "S1,S6,1.0\n"
        "S2,S3,2.0\n"
        "S2,S6,1.0\n"
        "S3,S4,1.0\n"
        "S3,S5,1.0\n"
        "S3,S6,1.0\n"
        "S4,S5,1.0\n",
    )
    # Alocação de recursos: DA contribui 1/4, DB e DC contribuem 1/3.
    quarter = 0.25
    third = 1.0 / 3.0
    _write_text(
        out / "student_resource_allocation.csv",
        "source,target,weight\n"
        f"S1,S2,{quarter + third!r}\n"
        f"S1,S3,{quarter + third!r}\n"
        f"S1,S6,{quarter!r}\n"
        f"S2,S3,{quarter + third!r}\n"
        f"S2,S6,{quarter!r}\n"
        f"S3,S4,{third!r}\n"
        f"S3,S5,{third!r}\n"
        f"S3,S6,{quarter!r}\n"
        f"S4,S5,{third!r}\n",
    )
    # Graus dos alunos: S1=2, S2=2, S3=3, S4=1, S5=1, S6=1.
    # Disciplina↔disciplina simples: nº de alunos em comum.
    _write_text(
        out / "discipline_simple.csv",
        "source,target,weight\nDA,DB,3.0\nDA,DC,1.0\nDB,DC,1.0\n",
    )
    # Alocação de recursos: S1 e S2 contribuem 1/2, S3 contribui 1/3.
    _write_text(
        out / "discipline_resource_allocation.csv",
        f"source,target,weight\nDA,DB,{0.5 + 0.5 + third!r}\nDA,DC,{third!r}\nDB,DC,{third!r}\n",
    )

    # Centralidade sobre student_simple. O grafo é um K4 em
    # {S1,S2,S3,S6} colado a um triângulo {S3,S4,S5}: S3 é o único
    # corte, então concentra toda a intermediação.
    # Grau normalizado por n-1 = 5.  Intermediação normalizada por
    # (n-1)(n-2)/2 = 10; os 6 pares {S1,S2,S6}×{S4,S5} passam por S3.
    _write_text(
        out / "student_simple.centrality.csv",
        "node_id,degree,betweenness\n"
        "S1,0.6,0.0\n"
        "S2,0.6,0.0\n"
        "S3,1.0,0.6\n"
        "S4,0.4,0.0\n"
        "S5,0.4,0.0\n"
        "S6,0.6,0.0\n",
    )

    # Autovetor sobre discipline_simple ponderado (triângulo com
    # DA-DB = 3, DA-DC = DB-DC = 1). Por simetria x = DA = DB, y = DC:
    #   λx = 3x + y   e   λy = 2x   ⇒   λ² − 3λ − 2 = 0   ⇒   λ = (3+√17)/2
    #   y = 2x/λ,  normalizado em L2:  x = 1/√(2 + 4/λ²)
    lam = (3.0 + 17.0**0.5) / 2.0
    x = 1.0 / (2.0 + 4.0 / lam**2) ** 0.5
    y = 2.0 * x / lam
    _write_text(
        out / "discipline_simple.eigenvector.csv",
        f"node_id,score\nDA,{x!r}\nDB,{x!r}\nDC,{y!r}\n",
    )

    _write_text(
        out / "README.md",
        "# Valores esperados de `tiny_v1`\n\n"
        "Derivados no papel a partir de `TINY_ENROLLMENTS`, em "
        "`scripts/make_fixtures.py`. Não são cópia da saída do NetworkX — "
        "é isso que faz dos testes que os consomem uma verificação, e não "
        "uma tautologia.\n\n"
        "| Arquivo | O que contém |\n"
        "|---|---|\n"
        "| `student_simple.csv` | pesos da projeção aluno↔aluno simples |\n"
        "| `student_resource_allocation.csv` | idem, alocação de recursos |\n"
        "| `discipline_simple.csv` | pesos da projeção disciplina↔disciplina |\n"
        "| `discipline_resource_allocation.csv` | idem, alocação de recursos |\n"
        "| `student_simple.centrality.csv` | grau e intermediação (sem peso) |\n"
        "| `discipline_simple.eigenvector.csv` | autovetor, forma fechada |\n\n"
        "A derivação de cada um está comentada em `_write_tiny_expected` e "
        "explicada em `docs/testes/estrategia.md`.\n",
    )


# =====================================================================
# synthetic_v1 — porta do gerador do starter kit
# =====================================================================


def make_synthetic_v1(out_root: Path) -> dict[str, Any]:
    """Gera ``synthetic_v1`` e devolve os números de referência."""
    dataset = generate(SyntheticSpec(seed=42))
    spec = BipartiteSpec(
        dataset="synthetic_v1",
        granularity="module",
        edge_criterion="score_threshold",
        threshold=SCORE_THRESHOLD,
        seed=42,
    )
    bipartite = build_bipartite_reference(dataset.enrollments, spec, producer="make_fixtures")
    io.save_bipartite(bipartite, out_root)

    # Só alunos que sobreviveram ao corte entram em outcomes.csv: o
    # validador exige que todo desfecho aponte para um nó existente.
    survivors = bipartite.students
    io.save_outcomes(
        Outcomes(
            final_result={k: v for k, v in dataset.final_result.items() if k in survivors},
            planted_group={k: v for k, v in dataset.planted_group.items() if k in survivors},
        ),
        out_root,
        "synthetic_v1",
    )

    reference: dict[str, Any] = {
        "n_students": len(bipartite.students),
        "n_disciplines": len(bipartite.disciplines),
        "n_edges": bipartite.graph.number_of_edges(),
        "projections": {},
        "communities": {},
        "centrality": {},
    }

    for projection_spec in PROJECTION_SPECS:
        projection = project_reference(bipartite, projection_spec)
        io.save_projection(projection, out_root)
        reference["projections"][projection.projection_id] = {
            "n_nodes": projection.graph.number_of_nodes(),
            "n_edges": projection.graph.number_of_edges(),
        }

        partition = louvain_reference(projection)
        io.save_partition(partition, out_root, "synthetic_v1")
        reference["communities"][projection.projection_id] = {
            "modularity": round(partition.modularity, 4),
            "n_communities": partition.n_communities,
            "largest": max(len(g) for g in partition.groups().values()),
        }

        metric_summary: dict[str, Any] = {}
        for result in centrality_reference(projection):
            io.save_centrality(result, out_root, "synthetic_v1")
            metric_summary[result.metric] = [
                [node, round(score, 4)] for node, score in result.top(3)
            ]
        reference["centrality"][projection.projection_id] = metric_summary

    _write_reference_md(out_root / "synthetic_v1" / "REFERENCE.md", reference)
    return reference


def _write_reference_md(path: Path, reference: dict[str, Any]) -> None:
    """Registra os números de referência recalculados na geração.

    Os testes usam **faixas**, não igualdade: Louvain depende do gerador
    aleatório, e um teste que exige Q = 0,4712 quebra na primeira troca
    de versão da biblioteca. Estes números existem para que uma mudança
    grande apareça na revisão, não para travar a suíte.
    """
    lines = [
        "# `synthetic_v1` — números de referência",
        "",
        "Recalculados na geração da fixture por `scripts/make_fixtures.py`.",
        "Os testes comparam **faixas**, não igualdade exata: Louvain é",
        "estocástico e uma troca de versão da biblioteca move o quarto",
        "decimal sem que nada esteja errado.",
        "",
        "## Bipartido",
        "",
        f"- {reference['n_students']} alunos",
        f"- {reference['n_disciplines']} disciplinas",
        f"- {reference['n_edges']} arestas (critério: nota média ≥ {SCORE_THRESHOLD:.0f})",
        "",
        "## Projeções",
        "",
        "| projeção | nós | arestas |",
        "|---|---:|---:|",
    ]
    for projection_id, stats in reference["projections"].items():
        lines.append(f"| `{projection_id}` | {stats['n_nodes']} | {stats['n_edges']} |")

    lines += [
        "",
        "## Louvain de referência",
        "",
        "Gerado pela biblioteca (`python-louvain`, seed 42) e marcado com",
        '`producer="reference"` no `meta.json`. **Não é saída da Frente B** —',
        "existe para destravar a Frente C no dia 0.",
        "",
        "| projeção | Q | comunidades | maior |",
        "|---|---:|---:|---:|",
    ]
    for projection_id, stats in reference["communities"].items():
        lines.append(
            f"| `{projection_id}` | {stats['modularity']} | "
            f"{stats['n_communities']} | {stats['largest']} |"
        )

    lines += ["", "## Centralidade de referência (top 3)", ""]
    for projection_id, metrics in reference["centrality"].items():
        lines.append(f"### `{projection_id}`")
        lines.append("")
        lines.append("| métrica | 1º | 2º | 3º |")
        lines.append("|---|---|---|---|")
        for metric, top in metrics.items():
            cells = " | ".join(f"`{node}` ({score})" for node, score in top)
            lines.append(f"| {metric} | {cells} |")
        lines.append("")

    lines += [
        "## Comparação com o starter kit",
        "",
        "O starter kit reporta, sobre o mesmo gerador com seed 42:",
        "120 alunos, 7 disciplinas, 197 arestas, Louvain com Q ~ 0,47 e",
        "~25 comunidades. O número de arestas e o Q batem; o número de",
        "comunidades, não, e a diferença é explicada:",
        "",
        "- **98 alunos, não 120.** Os 22 que ficaram sem nenhuma nota ≥ 60",
        "  viram nós isolados e são removidos pelo contrato — um aluno sem",
        "  aresta não participa de projeção nenhuma.",
        "- **3 comunidades, não ~25.** As ~22 comunidades extras do starter",
        "  kit eram exatamente esses nós isolados, cada um virando uma",
        "  comunidade de tamanho 1. As três comunidades grandes são as três",
        "  áreas plantadas pelo gerador, que é o resultado esperado.",
        "- **Q com peso.** A modularidade acima usa `weight`; sem peso o",
        "  valor muda no terceiro decimal.",
        "",
        "O starter kit foi removido do repositório depois de cumprir esse",
        "papel; `reference/README.md` registra o que ele mediu e como",
        "recuperá-lo do histórico do git.",
        "",
        "## Projeção disciplina↔disciplina: o caso degenerado da decisão D1",
        "",
        "`discipline_simple` tem **7 nós e 21 arestas** — é o grafo completo",
        "K₇. Toda intermediação é 0 e todo grau normalizado é 1: com sete",
        "disciplinas e alunos cursando de 2 a 4 delas, qualquer par de",
        "disciplinas compartilha algum aluno.",
        "",
        "Isto **confirma empiricamente a decisão D1** do plano de",
        "arquitetura, antes mesmo do OULAD: com V = módulo, a projeção",
        "disciplina↔disciplina não discrimina nada, e a identificação de",
        "disciplinas críticas (spec C-03, saída obrigatória) precisa de uma",
        "granularidade mais fina — `module_presentation` (22 nós) ou",
        "`assessment`. Só o **peso** das arestas distingue os pares, e é por",
        "isso que o autovetor ponderado acima ainda ordena as disciplinas",
        "enquanto grau e intermediação empatam tudo.",
        "",
        "Consequência prática para a spec C-01: **nenhum teste deve afirmar",
        "que uma disciplina específica lidera a intermediação em",
        "`synthetic_v1`** — nesta fixture, todas empatam em zero. O teste",
        "correto verifica o empate e a degeneração.",
        "",
    ]
    _write_text(path, "\n".join(lines))


# =====================================================================
# Execução
# =====================================================================

FIXTURES = {"tiny_v1": make_tiny_v1, "synthetic_v1": make_synthetic_v1}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gera as fixtures versionadas. Fixtures são imutáveis: "
        "para mudar valores, crie uma versão nova (synthetic_v2).",
    )
    parser.add_argument("--out", type=Path, default=FIXTURES_ROOT)
    parser.add_argument(
        "--only", choices=sorted(FIXTURES), default=None, help="gera só esta fixture"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="apaga e regrava fixtures existentes (exige revisão dos três)",
    )
    args = parser.parse_args(argv)
    configure_console()

    wanted = [args.only] if args.only else sorted(FIXTURES)
    for name in wanted:
        target = args.out / name
        if target.exists():
            if not args.force:
                print(f"[fixtures] {name}: já existe, pulando (use --force para regravar)")
                continue
            print(f"[fixtures] {name}: --force, apagando {target}")
            shutil.rmtree(target)

        print(f"[fixtures] {name}: gerando…")
        result = FIXTURES[name](args.out)
        if result:
            print(
                f"[fixtures] {name}: {result['n_students']} alunos, "
                f"{result['n_disciplines']} disciplinas, {result['n_edges']} arestas"
            )
        print(f"[fixtures] {name}: ok → {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
