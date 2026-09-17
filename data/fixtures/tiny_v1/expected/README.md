# Valores esperados de `tiny_v1`

Derivados no papel a partir de `TINY_ENROLLMENTS`, em `scripts/make_fixtures.py`. Não são cópia da saída do NetworkX — é isso que faz dos testes que os consomem uma verificação, e não uma tautologia.

| Arquivo | O que contém |
|---|---|
| `student_simple.csv` | pesos da projeção aluno↔aluno simples |
| `student_resource_allocation.csv` | idem, alocação de recursos |
| `discipline_simple.csv` | pesos da projeção disciplina↔disciplina |
| `discipline_resource_allocation.csv` | idem, alocação de recursos |
| `student_simple.centrality.csv` | grau e intermediação (sem peso) |
| `discipline_simple.eigenvector.csv` | autovetor, forma fechada |

A derivação de cada um está comentada em `_write_tiny_expected` e explicada em `docs/testes/estrategia.md`.
