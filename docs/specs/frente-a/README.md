# Specs da Frente A — Dados e Modelagem  `[A]` Pedro

ETL do OULAD, gerador sintético, grafo bipartido e as duas projeções.

**Produz** `bipartite/`, `projections/`, `outcomes.csv` e
`metrics/projections.csv`. **Consome** apenas CSV bruto.

| ID | Spec | Consome | Cumpre | Artigo |
|---|---|---|---|---|
| [A-01](A-01-gerador-sintetico.md) | Gerador sintético determinístico | — | Bipartite, Outcomes | decisão metodológica (base secundária) |
| [A-02](A-02-etl-oulad.md) | ETL do OULAD | CSV bruto | tabela normalizada | estatísticas do dataset |
| [A-03](A-03-bipartido-parametrizavel.md) | Bipartido parametrizável | tabela normalizada | Bipartite | critério de aresta (ADR-0007) |
| [A-04](A-04-projecoes-manuais.md) | Projeções à mão | Bipartite | Projection | **algoritmo implementado à mão** |
| [A-05](A-05-comparacao-projecao.md) | Manual × NetworkX | Bipartite | `metrics/projections.csv` | tabela + figura |
| [A-06](A-06-escala.md) | Escala e rodada do OULAD | tabela normalizada | Bipartite, Projection | limitação reportada |
| [A-07](A-07-estatisticas-bipartido.md) | Estatísticas e figura | Bipartite | — | figura + tabela |

## Ordem sugerida

**Onda 1:** A-01, A-02 · **Onda 2:** A-03, A-04 · **Onda 3:** A-05, A-06
· **Onda 4:** A-07.

A-06 é a que **destrava as outras frentes de verdade**: quando
`data/processed` existir, B e C trocam `--root` e param de usar fixtures.

## Estado (18/09/2026)

| Spec | Estado | O que falta |
|---|---|---|
| A-01 | concluída | — |
| A-02 | concluída contra `oulad_mini` | rodada na base completa; medir memória; preencher `OULAD_SHA256` |
| A-03 | concluída | — |
| A-04 | concluída | medir tempo sobre uma coorte real |
| A-05 | concluída | — |
| A-06 | em andamento | rodada completa → `data/processed`; tempo e memória; escolher `min_weight`/`sample_students`/`k_core` nos TOML |
| A-07 | concluída sobre as fixtures | figura e tabela finais saem da rodada do OULAD |

Tudo o que falta depende de **um passo manual**: baixar o OULAD
(`python scripts/download_oulad.py`, ou pela página do dataset) para
`data/raw/oulad/`. Depois disso, em ordem:

```bash
python -m edugraph data etl                                        # A-02: normaliza e mede
python -m edugraph run configs/oulad_cohort_bbb_2013j.toml --only data   # A-06: uma coorte
python -m edugraph run configs/oulad_module_presentation.toml --only data
python -m edugraph validate --root data/processed
pytest --artifacts-root data/processed                             # a mesma suíte, sobre o real
python -m edugraph data compare --dataset oulad_bbb_2013j --figures results/figures  # A-05
python -m edugraph data report  --dataset oulad_bbb_2013j          # A-07
```

Anotar tempo e pico de memória nas specs A-02 e A-06 e em
`docs/artigo/decisoes-metodologicas.md`, e só então fixar os valores de
escala nos TOML.

`tests/data/oulad_mini/` continua sendo a fixture do ETL: sete tabelas em
miniatura com o esquema real.
