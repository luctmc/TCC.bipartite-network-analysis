# Specs da Frente B — Detecção de Comunidades  `[B]` Gabriel

Louvain, Girvan-Newman, modularidade Q à mão, comparação e
caracterização.

**Produz** `communities/` e `metrics/communities.csv`. **Consome**
`projections/` e `bipartite/`; lê `outcomes.csv` apenas em
`evaluate.py`.

| ID | Spec | Consome | Cumpre | Artigo |
|---|---|---|---|---|
| [B-01](B-01-louvain.md) | Louvain determinístico | Projection (fixture) | Partition | — |
| [B-02](B-02-girvan-newman.md) | Girvan-Newman com orçamento | Projection (fixture) | Partition | decisão metodológica (ADR-0006) |
| [B-03](B-03-modularidade.md) | Q implementada à mão | Projection, Partition | — | **algoritmo implementado à mão** |
| [B-04](B-04-comparacao.md) | Comparação Louvain × GN × ponderação | Partition | `metrics/communities.csv` | **tabela principal do cap. 3** |
| [B-05](B-05-caracterizacao.md) | Caracterização por disciplina | Partition, Bipartite (fixture) | `profile.csv` | **saída obrigatória** |
| [B-06](B-06-validacao.md) | Validação a posteriori | Partition, Outcomes | — | tabela de validação |
| [B-07](B-07-figuras.md) | Figuras de comunidades | Partition, Projection | — | figuras |

## Ordem sugerida

**Onda 1:** B-01, B-03 · **Onda 2:** B-02, B-04 · **Onda 3:** B-05, B-06
· **Onda 4:** B-07.

## Por que nenhuma delas espera pela Frente A

`data/fixtures/synthetic_v1/projections/` traz as quatro projeções, e
`tiny_v1` traz o caso conferível à mão. As sete specs fecham inteiras
sobre fixtures.

Quando a Frente A entregar o OULAD (spec A-06), muda **só o argumento**:

```bash
python -m edugraph community louvain --root data/processed --dataset oulad_bbb_2013j ...
```

## Duas coisas para não esquecer

**Densificar os ids de comunidade.** O validador exige `0..k-1`; as
bibliotecas não garantem. `modularity.densify` (B-03) resolve, e B-01 e
B-02 devem usá-lo.

**Estouro de orçamento não levanta exceção.** Devolve
`status="timeout"`. O contrato proíbe o contrário, porque é o que
transforma a limitação do Girvan-Newman em resultado do capítulo 3.
