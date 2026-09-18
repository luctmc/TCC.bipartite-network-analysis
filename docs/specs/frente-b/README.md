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

## O que a Frente A entrega — leia antes de escolher o `--root`

Em `data/processed`, prontos para `--root`. **A escolha do dataset não é
indiferente**, e a razão está na spec A-08:

| dataset | o que é | para quê |
|---|---|---|
| `oulad_vle_bbb_2013j` | coorte BBB 2013J pelo **AVA**: 1.870 alunos × 320 recursos, projeção aluno↔aluno com 1,75 M arestas | **comunidades de alunos** — é o único com sinal |
| `oulad_vle_bbb_2013j_null0..4` | réplicas nulas do anterior | a linha de base da B-06 |
| `oulad_module_presentation` | base inteira por módulo×apresentação, 22.425 alunos, 22 disciplinas | **projeção de disciplina** e disciplinas críticas (C-03) |
| `oulad_module_presentation_null0..2` | réplicas nulas do anterior | linha de base |
| `oulad_bbb_2013j` | coorte por avaliação, 1.706 alunos | comparação Louvain × Girvan-Newman (grafo menor) |

**O aviso que evita concluir o contrário do certo.** Na projeção
aluno↔aluno de `oulad_module_presentation`, o Q real (0,7728) é **menor**
que o das réplicas embaralhadas (0,781): ali não há estrutura de
comunidade, e o Q alto é artefato da esparsidade. Quem quiser comunidades
de alunos usa `oulad_vle_bbb_2013j`, onde o Q real fica 5 vezes acima do
nulo.

Nada muda no código de quem consome: `kind`, `nodes.csv` e o layout são
idênticos nos dois. Muda só o que o nó do lado V significa — recurso do
AVA em vez de disciplina (ADR-0012).
