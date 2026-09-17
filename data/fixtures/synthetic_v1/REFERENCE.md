# `synthetic_v1` — números de referência

Recalculados na geração da fixture por `scripts/make_fixtures.py`.
Os testes comparam **faixas**, não igualdade exata: Louvain é
estocástico e uma troca de versão da biblioteca move o quarto
decimal sem que nada esteja errado.

## Bipartido

- 98 alunos
- 7 disciplinas
- 197 arestas (critério: nota média ≥ 60)

## Projeções

| projeção | nós | arestas |
|---|---:|---:|
| `student_simple` | 98 | 1971 |
| `student_resource_allocation` | 98 | 1971 |
| `discipline_simple` | 7 | 21 |
| `discipline_resource_allocation` | 7 | 21 |

## Louvain de referência

Gerado pela biblioteca (`python-louvain`, seed 42) e marcado com
`producer="reference"` no `meta.json`. **Não é saída da Frente B** —
existe para destravar a Frente C no dia 0.

| projeção | Q | comunidades | maior |
|---|---:|---:|---:|
| `student_simple` | 0.4666 | 3 | 39 |
| `student_resource_allocation` | 0.4596 | 3 | 38 |
| `discipline_simple` | 0.3143 | 3 | 3 |
| `discipline_resource_allocation` | 0.3715 | 3 | 3 |

## Centralidade de referência (top 3)

### `student_simple`

| métrica | 1º | 2º | 3º |
|---|---|---|---|
| degree | `S100055` (0.7113) | `S100012` (0.701) | `S100029` (0.6804) |
| betweenness | `S100055` (0.0756) | `S100084` (0.0612) | `S100079` (0.0492) |
| eigenvector | `S100012` (0.1848) | `S100016` (0.1842) | `S100039` (0.1842) |

### `student_resource_allocation`

| métrica | 1º | 2º | 3º |
|---|---|---|---|
| degree | `S100055` (0.7113) | `S100012` (0.701) | `S100029` (0.6804) |
| betweenness | `S100055` (0.0756) | `S100084` (0.0612) | `S100079` (0.0492) |
| eigenvector | `S100016` (0.2238) | `S100039` (0.2238) | `S100012` (0.2025) |

### `discipline_simple`

| métrica | 1º | 2º | 3º |
|---|---|---|---|
| degree | `DAAA` (1.0) | `DBBB` (1.0) | `DCCC` (1.0) |
| betweenness | `DAAA` (0.0) | `DBBB` (0.0) | `DCCC` (0.0) |
| eigenvector | `DCCC` (0.4498) | `DBBB` (0.4494) | `DAAA` (0.4335) |

### `discipline_resource_allocation`

| métrica | 1º | 2º | 3º |
|---|---|---|---|
| degree | `DAAA` (1.0) | `DBBB` (1.0) | `DCCC` (1.0) |
| betweenness | `DAAA` (0.0) | `DBBB` (0.0) | `DCCC` (0.0) |
| eigenvector | `DCCC` (0.3904) | `DBBB` (0.387) | `DFFF` (0.3808) |

## Comparação com o starter kit

O starter kit reporta, sobre o mesmo gerador com seed 42:
120 alunos, 7 disciplinas, 197 arestas, Louvain com Q ~ 0,47 e
~25 comunidades. O número de arestas e o Q batem; o número de
comunidades, não, e a diferença é explicada:

- **98 alunos, não 120.** Os 22 que ficaram sem nenhuma nota ≥ 60
  viram nós isolados e são removidos pelo contrato — um aluno sem
  aresta não participa de projeção nenhuma.
- **3 comunidades, não ~25.** As ~22 comunidades extras do starter
  kit eram exatamente esses nós isolados, cada um virando uma
  comunidade de tamanho 1. As três comunidades grandes são as três
  áreas plantadas pelo gerador, que é o resultado esperado.
- **Q com peso.** A modularidade acima usa `weight`; sem peso o
  valor muda no terceiro decimal.

O starter kit foi removido do repositório depois de cumprir esse
papel; `reference/README.md` registra o que ele mediu e como
recuperá-lo do histórico do git.

## Projeção disciplina↔disciplina: o caso degenerado da decisão D1

`discipline_simple` tem **7 nós e 21 arestas** — é o grafo completo
K₇. Toda intermediação é 0 e todo grau normalizado é 1: com sete
disciplinas e alunos cursando de 2 a 4 delas, qualquer par de
disciplinas compartilha algum aluno.

Isto **confirma empiricamente a decisão D1** do plano de
arquitetura, antes mesmo do OULAD: com V = módulo, a projeção
disciplina↔disciplina não discrimina nada, e a identificação de
disciplinas críticas (spec C-03, saída obrigatória) precisa de uma
granularidade mais fina — `module_presentation` (22 nós) ou
`assessment`. Só o **peso** das arestas distingue os pares, e é por
isso que o autovetor ponderado acima ainda ordena as disciplinas
enquanto grau e intermediação empatam tudo.

Consequência prática para a spec C-01: **nenhum teste deve afirmar
que uma disciplina específica lidera a intermediação em
`synthetic_v1`** — nesta fixture, todas empatam em zero. O teste
correto verifica o empate e a degeneração.
