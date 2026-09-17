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

## O que já existe no dia 0

`edugraph/data/synthetic.py` **funciona** — é dele que saem as fixtures.
Tudo o mais é stub com `NotImplementedError` carregando o id da spec.

`tests/data/oulad_mini/` traz as sete tabelas do OULAD em miniatura, com
o esquema real, para que a A-02 não espere pelo download.
