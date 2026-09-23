"""Estágio ``community`` do comando ``run``  ``[B]``.

O estágio é o caminho que a rodada final do artigo usa: um TOML de
``configs/`` descreve a configuração, e ``python -m edugraph run`` produz
partições, perfis e a tabela comparativa de uma vez.

Os testes rodam sobre as fixtures, como o resto da frente, e escrevem
sempre em ``tmp_path``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from edugraph.community.stage import CommunityStage
from edugraph.contracts import io
from edugraph.contracts.errors import ContractError
from edugraph.contracts.types import BipartiteSpec, ProjectionSpec, RunConfig

pytestmark = pytest.mark.dataset("synthetic_v1")

FIXTURES = Path("data/fixtures")


def _config(**community: object) -> RunConfig:
    return RunConfig(
        name="teste",
        bipartite=BipartiteSpec(dataset="synthetic_v1"),
        projections=[ProjectionSpec(side="student", weighting="simple")],
        community=dict(community),
        stages=["community"],
    )


def test_estagio_grava_particao_perfil_e_tabela(tmp_path: Path) -> None:
    written = CommunityStage().run([FIXTURES], tmp_path, _config(algorithms=["louvain"]))

    assert any(p.name == "profile.csv" for p in written)
    assert any(p.name == "communities.csv" for p in written)

    partition = io.load_partition([tmp_path], "synthetic_v1", "louvain__student_simple")
    assert partition.status == "ok"
    assert partition.meta.producer == "B-01"

    rows = io.load_metrics([tmp_path], "synthetic_v1", "communities")
    assert len(rows) == 1
    assert rows[0]["algorithm"] == "louvain"


def test_estagio_repassa_os_parametros_do_toml(tmp_path: Path) -> None:
    """``[community.louvain] seed = 7`` precisa chegar ao algoritmo."""
    config = _config(algorithms=["louvain"], louvain={"seed": 7, "resolution": 1.5})
    CommunityStage().run([FIXTURES], tmp_path, config)

    partition = io.load_partition([tmp_path], "synthetic_v1", "louvain__student_simple")
    assert partition.params["seed"] == 7
    assert partition.params["resolution"] == 1.5


def test_parametro_desconhecido_no_toml_quebra_cedo(tmp_path: Path) -> None:
    """Melhor falhar na configuração do que gerar uma tabela com o parâmetro errado."""
    config = _config(algorithms=["louvain"], louvain={"seeed": 7})
    with pytest.raises(ContractError, match="seeed"):
        CommunityStage().run([FIXTURES], tmp_path, config)


def test_orcamento_estourado_nao_derruba_o_estagio(tmp_path: Path) -> None:
    """A partição sai com o status visível e a tabela é gravada assim mesmo."""
    config = _config(algorithms=["girvan_newman"], girvan_newman={"time_budget_s": 0.0})
    CommunityStage().run([FIXTURES], tmp_path, config)

    partition = io.load_partition([tmp_path], "synthetic_v1", "girvan_newman__student_simple")
    assert partition.status == "skipped"

    rows = io.load_metrics([tmp_path], "synthetic_v1", "communities")
    assert rows[0]["status"] == "skipped"


def test_sem_projecao_declarada_usa_as_do_disco(tmp_path: Path) -> None:
    config = RunConfig(
        name="teste",
        bipartite=BipartiteSpec(dataset="synthetic_v1"),
        community={"algorithms": ["louvain"]},
        stages=["community"],
    )
    CommunityStage().run([FIXTURES], tmp_path, config)

    rows = io.load_metrics([tmp_path], "synthetic_v1", "communities")
    assert {row["projection_id"] for row in rows} == {
        "student_simple",
        "student_resource_allocation",
        "discipline_simple",
        "discipline_resource_allocation",
    }


def test_dataset_sem_projecao_nenhuma_e_erro_de_contrato(tmp_path: Path) -> None:
    config = RunConfig(
        name="teste",
        bipartite=BipartiteSpec(dataset="nao_existe"),
        community={"algorithms": ["louvain"]},
        stages=["community"],
    )
    with pytest.raises(ContractError, match="nenhuma projeção"):
        CommunityStage().run([FIXTURES], tmp_path, config)


def test_run_only_community_pela_cli(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """O caminho de ponta a ponta: um TOML e um comando."""
    from edugraph.__main__ import main

    config = tmp_path / "teste.toml"
    config.write_text(
        "\n".join(
            [
                'name = "teste"',
                'stages = ["community"]',
                "[bipartite]",
                'dataset = "synthetic_v1"',
                "[[projections]]",
                'side = "student"',
                'weighting = "simple"',
                "[community]",
                'algorithms = ["louvain"]',
                "[community.louvain]",
                "seed = 42",
            ]
        ),
        encoding="utf-8",
    )

    code = main(["run", str(config), "--root", str(FIXTURES), "--out", str(tmp_path),
                 "--only", "community"])  # fmt: skip

    assert code == 0
    assert "community" in capsys.readouterr().out
    assert (tmp_path / "synthetic_v1" / "metrics" / "communities.csv").exists()
