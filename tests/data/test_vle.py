"""Granularidades do comportamento  ``[A]`` — spec A-09.

O bipartido deixa de ser aluno × disciplina e passa a ser
aluno × recurso do AVA. É a troca que a A-08 tornou necessária: com o nó
de V sendo o módulo, 91,8% dos alunos do OULAD têm grau 1 e a projeção
aluno↔aluno não se distingue do acaso.

Tudo aqui roda sobre ``tests/data/oulad_mini/``. Os valores esperados
foram **derivados à mão** das duas tabelas, como manda
``docs/testes/estrategia.md`` — não são saída da biblioteca.

``studentVle.csv`` da fixture, com o tipo vindo de ``vle.csv``:

=====  ====  ======  =======  ===========  =======
aluno  mód.  apres.  recurso  tipo         cliques
=====  ====  ======  =======  ===========  =======
11391  AAA   2013J   546712   oucontent    1
11391  AAA   2013J   546943   resource     4
11391  BBB   2013J   877376   homepage     9
23629  BBB   2013J   877376   homepage     2
28400  AAA   2013J   546943   resource     3
30268  AAA   2013J   546943   resource     1
31604  AAA   2014J   546998   forumng      7
=====  ====  ======  =======  ===========  =======

Sete pares (aluno, recurso), cinco alunos, quatro recursos, quatro tipos.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import BipartiteSpec
from edugraph.data.bipartite import build_bipartite, describe
from edugraph.data.oulad import etl

OULAD_MINI = Path(__file__).parent / "oulad_mini"

#: Grau de cada aluno no bipartido por recurso, contado à mão da tabela acima.
GRAUS_POR_RECURSO = {"S11391": 3, "S23629": 1, "S28400": 1, "S30268": 1, "S31604": 1}


# ---------------------------------------------------------------------
# ETL
# ---------------------------------------------------------------------


def test_normalize_vle_devolve_uma_linha_por_aluno_e_recurso() -> None:
    table = etl.normalize_vle(OULAD_MINI)
    assert len(table) == 7
    assert list(table.columns) == list(etl.VLE_COLUMNS)
    assert not table.duplicated(subset=etl.VLE_KEY).any()


def test_normalize_vle_traz_o_tipo_de_atividade_de_cada_recurso() -> None:
    table = etl.normalize_vle(OULAD_MINI)
    tipos = dict(zip(table["id_site"], table["activity_type"], strict=True))
    assert tipos[546943] == "resource"
    assert tipos[546712] == "oucontent"
    assert tipos[546998] == "forumng"
    assert tipos[877376] == "homepage"


def test_normalize_vle_soma_os_cliques_do_mesmo_par() -> None:
    """Uma linha por dia no bruto vira uma linha por (aluno, recurso)."""
    table = etl.normalize_vle(OULAD_MINI)
    linha = table[(table.id_student == 11391) & (table.id_site == 546943)]
    assert len(linha) == 1
    assert int(linha["sum_click"].iloc[0]) == 4


def test_normalize_vle_deixa_score_media_nula_de_proposito() -> None:
    """O OULAD não tem nota por recurso; a coluna existe só para a forma.

    Manter ``score_media`` (nula) é o que deixa a tabela do AVA com a
    mesma forma das outras duas, para quem consome não precisar saber de
    qual ETL ela veio.
    """
    table = etl.normalize_vle(OULAD_MINI)
    assert "score_media" in table.columns
    assert table["score_media"].isna().all()


def test_normalize_vle_com_coorte_recorta_na_leitura() -> None:
    """A coorte entra no ETL, não depois: studentVle tem 10,6 M linhas."""
    table = etl.normalize_vle(OULAD_MINI, cohort="AAA_2013J")
    assert len(table) == 4
    assert set(table["code_module"]) == {"AAA"}
    assert set(table["code_presentation"]) == {"2013J"}


def test_normalize_vle_com_coorte_inexistente_devolve_tabela_vazia() -> None:
    table = etl.normalize_vle(OULAD_MINI, cohort="ZZZ_1999J")
    assert len(table) == 0
    assert list(table.columns) == list(etl.VLE_COLUMNS)


# ---------------------------------------------------------------------
# Bipartido
# ---------------------------------------------------------------------


def test_granularidade_vle_site_usa_o_recurso_como_no_de_v() -> None:
    table = etl.normalize_vle(OULAD_MINI)
    spec = BipartiteSpec(dataset="mini", granularity="vle_site", edge_criterion="vle_activity")
    bundle = build_bipartite(table, spec)

    assert bundle.disciplines == {"D546712", "D546943", "D546998", "D877376"}
    assert len(bundle.students) == 5
    assert bundle.graph.number_of_edges() == 7
    for student, grau in GRAUS_POR_RECURSO.items():
        assert bundle.graph.degree(student) == grau, student


def test_o_lado_v_continua_marcado_como_discipline() -> None:
    """``kind`` marca o lado do bipartido, não a natureza do nó.

    É o que permite as Frentes B e C consumirem o artefato do AVA sem
    mudar uma linha — ver ADR-0012.
    """
    table = etl.normalize_vle(OULAD_MINI)
    spec = BipartiteSpec(dataset="mini", granularity="vle_site", edge_criterion="vle_activity")
    bundle = build_bipartite(table, spec)
    assert all(bundle.graph.nodes[n]["kind"] == "discipline" for n in bundle.disciplines)
    assert all(bundle.graph.nodes[n]["kind"] == "student" for n in bundle.students)


def test_peso_da_aresta_no_ava_e_a_soma_de_cliques() -> None:
    table = etl.normalize_vle(OULAD_MINI)
    spec = BipartiteSpec(dataset="mini", granularity="vle_site", edge_criterion="vle_activity")
    bundle = build_bipartite(table, spec)
    assert bundle.graph["S11391"]["D877376"]["weight"] == pytest.approx(9.0)
    assert bundle.graph["S23629"]["D877376"]["weight"] == pytest.approx(2.0)


def test_granularidade_por_tipo_agrega_recursos_do_mesmo_tipo() -> None:
    """Dois recursos do mesmo tipo viram **uma** aresta, com os cliques somados.

    A fixture não tem esse caso, então a tabela é montada aqui: um aluno
    com dois recursos ``resource`` precisa virar grau 1, não 2.
    """
    table = pd.DataFrame(
        {
            "id_student": [1, 1, 1],
            "code_module": ["AAA", "AAA", "AAA"],
            "code_presentation": ["2013J", "2013J", "2013J"],
            "id_site": [10, 11, 12],
            "activity_type": ["resource", "resource", "forumng"],
            "sum_click": [3, 4, 5],
            "score_media": [pd.NA, pd.NA, pd.NA],
        }
    )
    spec = BipartiteSpec(
        dataset="mini", granularity="vle_activity_type", edge_criterion="vle_activity"
    )
    bundle = build_bipartite(table, spec)

    assert bundle.disciplines == {"Dresource", "Dforumng"}
    assert bundle.graph.degree("S1") == 2
    assert bundle.graph["S1"]["Dresource"]["weight"] == pytest.approx(7.0)


def test_limiar_de_cliques_corta_a_aresta_fraca() -> None:
    table = etl.normalize_vle(OULAD_MINI)
    spec = BipartiteSpec(
        dataset="mini", granularity="vle_site", edge_criterion="vle_activity", threshold=3.0
    )
    bundle = build_bipartite(table, spec)
    # Sobram os pares com >= 3 cliques: 11391-546943 (4), 11391-877376 (9),
    # 28400-546943 (3) e 31604-546998 (7).
    assert bundle.graph.number_of_edges() == 4
    assert "S30268" not in bundle.students


def test_nota_como_criterio_sobre_o_ava_falha_nomeando_a_causa() -> None:
    """A combinação daria grafo vazio em silêncio; tem que explodir cedo."""
    table = etl.normalize_vle(OULAD_MINI)
    spec = BipartiteSpec(dataset="mini", granularity="vle_site", edge_criterion="score_threshold")
    with pytest.raises(ContractError, match="não registra nota por recurso"):
        build_bipartite(table, spec)


def test_ava_como_criterio_sobre_avaliacao_falha_nomeando_a_causa() -> None:
    table = etl.normalize_assessments(OULAD_MINI)
    spec = BipartiteSpec(dataset="mini", granularity="assessment", edge_criterion="vle_activity")
    with pytest.raises(ContractError, match="não é registrado por avaliação"):
        build_bipartite(table, spec)


def test_granularidade_do_ava_exige_a_coluna_do_recurso() -> None:
    """Passar a tabela por matrícula com granularidade do AVA tem que falhar."""
    table = etl.normalize(OULAD_MINI)
    spec = BipartiteSpec(dataset="mini", granularity="vle_site", edge_criterion="vle_activity")
    with pytest.raises(ContractError, match="id_site"):
        build_bipartite(table, spec)


# ---------------------------------------------------------------------
# O motivo de tudo isto existir
# ---------------------------------------------------------------------


def test_o_ava_da_ao_aluno_grau_maior_que_a_matricula() -> None:
    """O achado que justifica a spec, na escala da fixture.

    Na base real a mediana passa de 1 para 40. Aqui o número é pequeno,
    mas a direção é a mesma e é o que o teste protege: se alguém voltar o
    nó de V para o módulo, este teste cai.
    """
    por_matricula = build_bipartite(
        etl.normalize(OULAD_MINI),
        BipartiteSpec(dataset="mini", granularity="module", edge_criterion="vle_activity"),
    )
    por_recurso = build_bipartite(
        etl.normalize_vle(OULAD_MINI),
        BipartiteSpec(dataset="mini", granularity="vle_site", edge_criterion="vle_activity"),
    )
    assert (
        describe(por_recurso)["mean_degree_student"]
        > describe(por_matricula)["mean_degree_student"]
    )
