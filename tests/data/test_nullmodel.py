"""Modelo nulo  ``[A]`` — spec A-08.

O nulo tem uma obrigação dupla: **preservar** os graus (senão não é
comparável com o real) e **destruir** a estrutura (senão não é nulo).
Os testes cobrem as duas, e o segundo é o que importa — um "nulo" que
preserva estrutura faria o trabalho concluir o contrário do certo.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.paths import ArtifactRoots
from edugraph.contracts.types import BipartiteBundle, BipartiteSpec, ProjectionSpec
from edugraph.contracts.validate import validate_bipartite, validate_dataset
from edugraph.data.bipartite import build_bipartite
from edugraph.data.nullmodel import PRODUCER, is_null, null_bipartite, null_replicas
from edugraph.data.projection.manual import SimpleProjection
from edugraph.data.synthetic import SyntheticSpec, generate


@pytest.fixture
def real(artifact_roots: ArtifactRoots) -> BipartiteBundle:
    return io.load_bipartite(artifact_roots, "synthetic_v1")


# ---------------------------------------------------------------------
# Preserva o que tem de preservar
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
def test_preserva_nos_e_grau_de_cada_aluno(real: BipartiteBundle) -> None:
    nulo = null_bipartite(real, seed=1)

    assert nulo.students == real.students
    assert nulo.disciplines == real.disciplines
    for student in real.students:
        assert nulo.graph.degree(student) == real.graph.degree(student)
    assert nulo.graph.number_of_edges() == real.graph.number_of_edges()
    validate_bipartite(nulo)


@pytest.mark.dataset("synthetic_v1")
def test_grau_das_disciplinas_e_preservado_em_expectativa(real: BipartiteBundle) -> None:
    """Não exatamente — a urna é sorteio —, mas na ordem de grandeza certa."""
    nulo = null_bipartite(real, seed=1)
    reais = {d: real.graph.degree(d) for d in sorted(real.disciplines)}
    nulos = {d: nulo.graph.degree(d) for d in sorted(nulo.disciplines)}

    assert sum(nulos.values()) == sum(reais.values())
    correl = pd.Series(nulos).corr(pd.Series(reais))
    assert correl > 0.8, f"graus de disciplina descolaram do real (r={correl:.2f})"


@pytest.mark.dataset("synthetic_v1")
def test_e_deterministico_por_semente(real: BipartiteBundle) -> None:
    a = null_bipartite(real, seed=7)
    b = null_bipartite(real, seed=7)
    c = null_bipartite(real, seed=8)

    assert set(a.graph.edges) == set(b.graph.edges)
    assert set(a.graph.edges) != set(c.graph.edges)


# ---------------------------------------------------------------------
# Destrói o que tem de destruir — o teste que importa
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
def test_destroi_a_estrutura_plantada(real: BipartiteBundle, artifact_roots: ArtifactRoots) -> None:
    """No real, alunos do mesmo grupo compartilham disciplinas; no nulo, não.

    Mede sem tocar em `outcomes.csv`: usa o grupo plantado só como
    rótulo de comparação, lido do artefato pelo próprio contrato — o que
    a Frente A pode fazer porque não é inferência, é verificação de que
    o embaralhamento funcionou.
    """
    outcomes = io.load_outcomes(artifact_roots, "synthetic_v1")
    assert outcomes.planted_group is not None
    grupo = outcomes.planted_group

    def fracao_intragrupo(bundle: BipartiteBundle) -> float:
        """Das arestas da projeção aluno↔aluno, quantas ligam o mesmo grupo."""
        projection = SimpleProjection().project(
            bundle, ProjectionSpec(side="student", weighting="simple")
        )
        pares = [(u, v) for u, v in projection.graph.edges if u in grupo and v in grupo]
        mesmo = sum(1 for u, v in pares if grupo[u] == grupo[v])
        return mesmo / len(pares)

    no_real = fracao_intragrupo(real)
    no_nulo = fracao_intragrupo(null_bipartite(real, seed=3))

    # No real, os grupos plantados fazem os pares se concentrarem dentro
    # do grupo; no nulo, a fração cai para perto do acaso (~1/3 com três
    # grupos de tamanho parecido).
    assert no_real > 0.5
    assert no_nulo < no_real - 0.15
    assert 0.25 < no_nulo < 0.45


def test_nulo_de_grafo_sem_estrutura_fica_parecido_com_ele() -> None:
    """Contraprova: se o real já não tem estrutura, o nulo não muda nada.

    Um dataset com um só grupo (nenhuma área plantada) tem fração
    intragrupo trivialmente 1 — então mede-se outra coisa: o número de
    arestas da projeção, que deve ficar na mesma ordem de grandeza.
    """
    from edugraph.data.synthetic import make_groups

    dataset = generate(
        SyntheticSpec(seed=5, groups=make_groups(1, 6), students_per_group=60, cross_group_prob=0.0)
    )
    real = build_bipartite(pd.DataFrame(dataset.enrollments), BipartiteSpec(dataset="plano"))
    nulo = null_bipartite(real, seed=2)

    def n_arestas(b: BipartiteBundle) -> int:
        return (
            SimpleProjection()
            .project(b, ProjectionSpec(side="student", weighting="simple"))
            .graph.number_of_edges()
        )

    a, n = n_arestas(real), n_arestas(nulo)
    assert abs(a - n) / a < 0.15, f"real {a} vs nulo {n}: deveriam ser parecidos"


# ---------------------------------------------------------------------
# Contrato, réplicas e erros
# ---------------------------------------------------------------------


@pytest.mark.dataset("synthetic_v1")
def test_artefato_se_identifica_como_nulo(real: BipartiteBundle, tmp_path: Path) -> None:
    """`is_null` não depende de adivinhar pelo nome do dataset."""
    nulo = null_bipartite(real, seed=1)

    assert is_null(nulo) and not is_null(real)
    assert nulo.meta.producer == PRODUCER
    assert nulo.spec.dataset == "synthetic_v1_null1"
    assert nulo.meta.stats["null_model"]["source_dataset"] == "synthetic_v1"
    assert "NÃO são dados reais" in nulo.meta.notes

    io.save_bipartite(nulo, tmp_path)
    lido = io.load_bipartite([tmp_path], "synthetic_v1_null1")
    assert is_null(lido), "a marca precisa sobreviver ao round-trip"
    assert validate_dataset([tmp_path], "synthetic_v1_null1") == ["bipartite"]


@pytest.mark.dataset("synthetic_v1")
def test_replicas_usam_sementes_consecutivas(real: BipartiteBundle) -> None:
    replicas = null_replicas(real, n=3, seed=10)

    assert [r.spec.dataset for r in replicas] == [
        "synthetic_v1_null10",
        "synthetic_v1_null11",
        "synthetic_v1_null12",
    ]
    assert len({frozenset(r.graph.edges) for r in replicas}) == 3
    with pytest.raises(ContractError, match="n precisa"):
        null_replicas(real, n=0)


def test_urna_concentrada_ainda_completa_o_grau() -> None:
    """Uma disciplina dominante não pode deixar um aluno com grau menor.

    Com DA de grau 1.000 e DB de grau 1, sortear DB é improvável, e a
    urna sozinha não completaria o grau 2 do aluno. O caminho de reserva
    preenche uniformemente — sem ele, o nulo teria menos arestas que o
    real e a comparação de Q ficaria enviesada a favor do real.
    """
    import networkx as nx

    graph = nx.Graph()
    for d in ("DA", "DB"):
        graph.add_node(d, kind="discipline", label=d[1:])
    graph.add_node("S1", kind="student", label="1")
    graph.add_edge("S1", "DA", weight=1.0)
    graph.add_edge("S1", "DB", weight=1.0)
    for i in range(2, 1001):  # 999 alunos só em DA: urna vira quase toda DA
        graph.add_node(f"S{i}", kind="student", label=str(i))
        graph.add_edge(f"S{i}", "DA", weight=1.0)

    real = BipartiteBundle(graph=graph, spec=BipartiteSpec(dataset="x"))
    nulo = null_bipartite(real, seed=1)

    assert nulo.graph.degree("S1") == 2
    assert nulo.graph.number_of_edges() == real.graph.number_of_edges()
    validate_bipartite(nulo)


def test_lado_vazio_e_recusado() -> None:
    import networkx as nx

    graph = nx.Graph()
    graph.add_node("S1", kind="student", label="1")
    with pytest.raises(ContractError, match="não vazios"):
        null_bipartite(BipartiteBundle(graph=graph, spec=BipartiteSpec(dataset="x")), seed=1)


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------


def test_data_null_grava_replicas_validas(tmp_path: Path) -> None:
    from edugraph.__main__ import main

    code = main(["data", "null", "--root", "data/fixtures", "--dataset", "synthetic_v1",
                 "--replicas", "2", "--seed", "0", "--projections", "--out", str(tmp_path)])  # fmt: skip
    assert code == 0

    for seed in (0, 1):
        nome = f"synthetic_v1_null{seed}"
        checked = validate_dataset([tmp_path], nome)
        assert "bipartite" in checked
        assert "projections/student_simple" in checked
        assert is_null(io.load_bipartite([tmp_path], nome))
