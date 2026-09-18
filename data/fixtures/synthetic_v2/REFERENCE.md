# `synthetic_v2` — números de referência

Recalculados na geração da fixture por `scripts/make_fixtures.py`.
Os testes comparam **faixas**, não igualdade exata: Louvain é
estocástico e uma troca de versão da biblioteca move o quarto
decimal sem que nada esteja errado.

## Bipartido

- 81 alunos
- 7 disciplinas
- 105 arestas (critério: nota média ≥ 60)

## Projeções

| projeção | nós | arestas |
|---|---:|---:|
| `student_simple` | 81 | 728 |
| `student_resource_allocation` | 81 | 728 |
| `discipline_simple` | 7 | 16 |
| `discipline_resource_allocation` | 7 | 16 |

## Louvain de referência

Gerado pela biblioteca (`python-louvain`, seed 42) e marcado com
`producer="reference"` no `meta.json`. **Não é saída da Frente B** —
existe para destravar a Frente C no dia 0.

| projeção | Q | comunidades | maior |
|---|---:|---:|---:|
| `student_simple` | 0.5392 | 5 | 24 |
| `student_resource_allocation` | 0.5345 | 5 | 24 |
| `discipline_simple` | 0.2294 | 3 | 3 |
| `discipline_resource_allocation` | 0.2686 | 3 | 3 |

## Centralidade de referência (top 3)

### `student_simple`

| métrica | 1º | 2º | 3º |
|---|---|---|---|
| degree | `S100006` (0.625) | `S100111` (0.5) | `S100105` (0.4625) |
| betweenness | `S100006` (0.2211) | `S100111` (0.128) | `S100105` (0.0896) |
| eigenvector | `S100111` (0.2442) | `S100078` (0.2376) | `S100006` (0.2161) |

### `student_resource_allocation`

| métrica | 1º | 2º | 3º |
|---|---|---|---|
| degree | `S100006` (0.625) | `S100111` (0.5) | `S100105` (0.4625) |
| betweenness | `S100006` (0.2211) | `S100111` (0.128) | `S100105` (0.0896) |
| eigenvector | `S100006` (0.2702) | `S100078` (0.2443) | `S100111` (0.2313) |

### `discipline_simple`

| métrica | 1º | 2º | 3º |
|---|---|---|---|
| degree | `DBBB` (0.8333) | `DCCC` (0.8333) | `DDDD` (0.8333) |
| betweenness | `DBBB` (0.0778) | `DDDD` (0.0778) | `DCCC` (0.0522) |
| eigenvector | `DEEE` (0.5045) | `DDDD` (0.4855) | `DGGG` (0.3657) |

### `discipline_resource_allocation`

| métrica | 1º | 2º | 3º |
|---|---|---|---|
| degree | `DBBB` (0.8333) | `DCCC` (0.8333) | `DDDD` (0.8333) |
| betweenness | `DBBB` (0.0778) | `DDDD` (0.0778) | `DCCC` (0.0522) |
| eigenvector | `DEEE` (0.5358) | `DDDD` (0.534) | `DGGG` (0.3714) |

## Esparsidade tipo OULAD

Gerada com `sparsity = 0.7`: com essa probabilidade, cada
aluno fica com **uma** matrícula só. É a forma sintética do que a
decisão D1 aponta no OULAD, onde a maior parte dos alunos aparece
em uma única matrícula.

| medida | valor |
|---|---:|
| matrículas por aluno (mediana) | 1 |
| matrículas por aluno (média) | 1.517 |
| alunos com uma só matrícula | 68% |

Em `synthetic_v1` a mediana é 2, a média 2,5, e nenhum aluno tem só uma.

## O efeito da esparsidade na projeção disciplina↔disciplina

`discipline_simple` tem 7 nós e 16 arestas; K7 teria 21. **Deixou de ser completo**: a esparsidade removeu pares de disciplinas sem aluno em comum, e a intermediação passa a discriminar. Compare com `synthetic_v1`, onde é K₇.

## Recuperação das áreas plantadas

Pureza da partição Louvain de referência contra o grupo plantado
(fração de alunos na maioria plantada da sua comunidade):

| projeção | pureza |
|---|---:|
| `student_simple` | 0.864 |
| `student_resource_allocation` | 0.840 |

É o número que a spec B-06 vai medir com NMI. Se a pureza aqui for
baixa, isso não é bug: é o achado de que, com pouca evidência por
aluno, a estrutura plantada deixa de ser recuperável — e vai para
o texto do artigo como limitação do método.
