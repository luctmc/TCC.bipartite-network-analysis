"""Tipos do contrato — dataclasses e Literals que atravessam as frentes.

Todo identificador aqui está em inglês (decisão D2): o código e as
colunas dos CSV falam inglês, coerentes com NetworkX e pandas; a
documentação, as specs e o artigo falam português.

Ver docs/contratos/ para a descrição de cada contrato em prosa.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Any, Literal

import networkx as nx

#: Versão do esquema em disco. Mudar layout, nome de coluna ou semântica
#: de campo exige subir esta versão **e** uma ADR (ver ADR-0002).
SCHEMA_VERSION = "1.0"

# ---------------------------------------------------------------------
# Vocabulário fechado
# ---------------------------------------------------------------------

NodeKind = Literal["student", "discipline"]
"""Os dois lados do bipartido. U = student, V = discipline."""

Weighting = Literal["simple", "resource_allocation"]
"""Ponderação da projeção: contagem simples ou Zhou et al. (2007)."""

Granularity = Literal[
    "module",
    "module_presentation",
    "assessment",
    "vle_site",
    "vle_activity_type",
]
"""O que conta como um nó de V (decisão D1; ADR-0012 para as duas do AVA).

As três primeiras usam a **matrícula** como relação: o nó de V é o
módulo, a apresentação do módulo ou a avaliação. As duas últimas usam o
**comportamento**: o nó de V é um recurso do ambiente virtual
(``vle_site``) ou o tipo de atividade dele (``vle_activity_type``).

A troca existe porque 91,8% dos alunos do OULAD cursam um único módulo,
e com grau 1 a projeção aluno↔aluno não carrega informação relacional —
ver ``docs/artigo/decisoes-metodologicas.md``. ``kind="discipline"``
continua marcando o lado V nas duas famílias: é o marcador do lado, não
uma afirmação de que o nó é uma disciplina.
"""

EdgeCriterion = Literal["score_threshold", "final_result_pass", "vle_activity"]
"""O que cria uma aresta aluno-disciplina (parametrizável, ADR-0007)."""

Implementation = Literal["manual", "networkx"]
"""Implementação à mão (obrigatória no artigo) ou de referência."""

CommunityAlgorithmName = Literal["louvain", "girvan_newman"]

CentralityMetricName = Literal["degree", "betweenness", "eigenvector"]

RunStatus = Literal["ok", "timeout", "skipped"]
"""Resultado da execução. 'timeout' é resultado a reportar, não falha."""

FinalResult = Literal["Pass", "Distinction", "Fail", "Withdrawn"]
"""Desfecho da matrícula no OULAD. Rótulo histórico: nunca entra no grafo."""

#: Colunas proibidas em ``nodes.csv``. Materializa a restrição da seção 2
#: do briefing: rótulo histórico não é atributo de nó (ADR-0008). O
#: validador recusa qualquer artefato que as contenha.
FORBIDDEN_NODE_COLUMNS: frozenset[str] = frozenset(
    {
        "final_result",
        "result",
        "outcome",
        "score",
        "score_media",
        "grade",
        "mark",
        "passed",
        "planted_group",
        "gender",
        "age_band",
        "region",
        "disability",
        "imd_band",
        "highest_education",
    }
)


# ---------------------------------------------------------------------
# Metadados comuns a todo artefato
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class Meta:
    """Cabeçalho de todo artefato, serializado em ``meta.json``.

    ``producer`` é o id da spec ou do script que gravou o artefato
    (``"A-04"``, ``"make_fixtures"``), e é o que permite distinguir uma
    fixture de referência de uma saída real de frente.
    """

    schema_version: str = SCHEMA_VERSION
    producer: str = "unknown"
    created_at: str = field(default_factory=lambda: _dt.datetime.now(_dt.UTC).isoformat())
    stats: dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def with_stats(self, **stats: Any) -> Meta:
        """Devolve uma cópia com ``stats`` acrescidos."""
        merged = {**self.stats, **stats}
        return Meta(
            schema_version=self.schema_version,
            producer=self.producer,
            created_at=self.created_at,
            stats=merged,
            notes=self.notes,
        )


# ---------------------------------------------------------------------
# Especificações — o que o grupo varia e compara no capítulo 3
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class BipartiteSpec:
    """Como o grafo bipartido foi construído.

    Cada combinação distinta destes campos é uma linha das tabelas
    comparativas do capítulo 3. É o que torna o critério de aresta um
    parâmetro, e não uma constante escondida no código (ADR-0007).
    """

    dataset: str
    granularity: Granularity = "module"
    edge_criterion: EdgeCriterion = "score_threshold"
    threshold: float | None = None
    cohort: str | None = None
    seed: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "granularity": self.granularity,
            "edge_criterion": self.edge_criterion,
            "threshold": self.threshold,
            "cohort": self.cohort,
            "seed": self.seed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BipartiteSpec:
        return cls(
            dataset=str(data["dataset"]),
            granularity=data.get("granularity", "module"),
            edge_criterion=data.get("edge_criterion", "score_threshold"),
            threshold=data.get("threshold"),
            cohort=data.get("cohort"),
            seed=data.get("seed"),
        )


@dataclass(frozen=True)
class ProjectionSpec:
    """Qual projeção: de que lado, com que ponderação, por qual implementação.

    ``projection_id`` é derivado (``side`` + ``weighting``) e é a chave
    que nomeia a pasta em disco e aparece em toda tabela de métricas.
    Frentes B e C recebem projeções por este id e nunca precisam saber
    como ela foi calculada.
    """

    side: NodeKind
    weighting: Weighting
    implementation: Implementation = "manual"
    min_weight: float | None = None

    @property
    def projection_id(self) -> str:
        """``student_simple``, ``discipline_resource_allocation``, …"""
        return f"{self.side}_{self.weighting}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "side": self.side,
            "weighting": self.weighting,
            "implementation": self.implementation,
            "min_weight": self.min_weight,
            "projection_id": self.projection_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectionSpec:
        return cls(
            side=data["side"],
            weighting=data["weighting"],
            implementation=data.get("implementation", "manual"),
            min_weight=data.get("min_weight"),
        )


# ---------------------------------------------------------------------
# Bundles — grafo + especificação + metadados
# ---------------------------------------------------------------------


@dataclass
class BipartiteBundle:
    """Grafo bipartido G = (U ∪ V, E) com a especificação que o gerou.

    Nós são ``str`` com prefixo ``S``/``D`` e atributos ``kind`` e
    ``label``. Arestas têm ``weight`` finito e positivo. Produzido por
    ``[A]``, consumido por ``[B]`` (caracterização) e ``[C]`` (API).
    """

    graph: nx.Graph[Any]
    spec: BipartiteSpec
    meta: Meta = field(default_factory=Meta)

    @property
    def students(self) -> set[str]:
        return {n for n, d in self.graph.nodes(data=True) if d.get("kind") == "student"}

    @property
    def disciplines(self) -> set[str]:
        return {n for n, d in self.graph.nodes(data=True) if d.get("kind") == "discipline"}


@dataclass
class ProjectionBundle:
    """Projeção monopartida ponderada, com rastro da origem.

    Grafo simples, sem laços, todos os nós do mesmo ``kind``, ``weight``
    finito e positivo. Produzido por ``[A]``, consumido por ``[B]`` e
    ``[C]``. É o contrato mais usado do projeto.
    """

    graph: nx.Graph[Any]
    spec: ProjectionSpec
    source: BipartiteSpec
    meta: Meta = field(default_factory=Meta)

    @property
    def projection_id(self) -> str:
        return self.spec.projection_id


@dataclass
class Partition:
    """Partição de comunidades sobre uma projeção — saída da Frente B.

    ``status`` distingue uma execução concluída de um estouro de
    orçamento de tempo: Girvan-Newman que não termina devolve
    ``status="timeout"``, e isso é um resultado a reportar (ADR-0006),
    não um erro.
    """

    algorithm: CommunityAlgorithmName
    projection_id: str
    membership: dict[str, int]
    modularity: float
    n_communities: int
    runtime_s: float
    params: dict[str, Any] = field(default_factory=dict)
    status: RunStatus = "ok"
    meta: Meta = field(default_factory=Meta)

    @property
    def artifact_id(self) -> str:
        """``louvain__student_simple`` — nome da pasta em disco."""
        return f"{self.algorithm}__{self.projection_id}"

    def groups(self) -> dict[int, list[str]]:
        """Comunidade → lista ordenada de nós."""
        out: dict[int, list[str]] = {}
        for node, comm in self.membership.items():
            out.setdefault(comm, []).append(node)
        return {c: sorted(ns) for c, ns in sorted(out.items())}


@dataclass
class CentralityResult:
    """Uma métrica de centralidade sobre uma projeção — saída da Frente C.

    ``converged`` registra se a iteração de potência convergiu; quando
    não converge e cai no fallback por autovalores, isso fica no
    artefato e vira nota de rodapé do artigo (spec C-02).
    """

    projection_id: str
    metric: CentralityMetricName
    scores: dict[str, float]
    params: dict[str, Any] = field(default_factory=dict)
    runtime_s: float = 0.0
    converged: bool = True
    meta: Meta = field(default_factory=Meta)

    def top(self, n: int = 5) -> list[tuple[str, float]]:
        """Os ``n`` nós de maior score, com desempate por id (determinístico)."""
        return sorted(self.scores.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


@dataclass
class Outcomes:
    """Rótulos históricos — **nunca** entram em algoritmo (ADR-0008).

    Vivem em ``bipartite/outcomes.csv``, separados de ``nodes.csv``, e
    só podem ser lidos por módulos ``evaluate.py``. Um teste de contrato
    verifica que nenhum outro módulo os lê.
    """

    final_result: dict[str, str]
    planted_group: dict[str, int] | None = None
    meta: Meta = field(default_factory=Meta)


# ---------------------------------------------------------------------
# Configuração de execução
# ---------------------------------------------------------------------


@dataclass
class RunConfig:
    """Uma configuração de experimento, carregada de um TOML de ``configs/``.

    Cada arquivo de ``configs/`` vira uma linha das tabelas comparativas
    do capítulo 3. O comando ``python -m edugraph run configs/x.toml``
    executa os estágios listados em ``stages`` contra esta configuração.
    """

    name: str
    bipartite: BipartiteSpec
    projections: list[ProjectionSpec] = field(default_factory=list)
    community: dict[str, Any] = field(default_factory=dict)
    centrality: dict[str, Any] = field(default_factory=dict)
    stages: list[str] = field(default_factory=lambda: ["data", "community", "centrality"])
    source: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunConfig:
        """Constrói a configuração a partir do TOML já parseado."""
        bip = BipartiteSpec.from_dict(data["bipartite"])
        projs = [ProjectionSpec.from_dict(p) for p in data.get("projections", [])]
        return cls(
            name=str(data.get("name", bip.dataset)),
            bipartite=bip,
            projections=projs,
            community=data.get("community", {}),
            centrality=data.get("centrality", {}),
            stages=data.get("stages", ["data", "community", "centrality"]),
            source=data.get("source", {}),
        )
