# [A-07] Estatísticas descritivas e figura do bipartido

**Frente:** A
**Dono:** Pedro
**Status:** não iniciada

## Objetivo

Produzir a tabela de estatísticas descritivas e a figura do grafo
bipartido que abrem a seção de dados do capítulo 3.

## Contexto

**Cumpre:** `results/tables/` e `results/figures/`.
**Consome:** `BipartiteBundle`.

Requisito que vem do artigo, não do software (briefing §9): refazer uma
figura na semana da entrega tem que ser um comando, não arqueologia.

## Dependências

- A-03, para ter um bipartido.
- **Neutralizada por:** as fixtures já têm bipartidos; dá para fechar a
  spec sobre elas e só trocar `--root` depois.

## Escopo

### Incluído

- `describe()` / `table_dataset_stats()`: nº de alunos, de disciplinas,
  de arestas, densidade, grau médio de cada lado, distribuição de grau.
- `figure_bipartite()`: os dois lados em colunas. Em grafos grandes,
  **amostrar ou agregar e dizer na legenda o que foi feito** — desenhar
  28 mil nós não comunica nada.
- Comando `edugraph data report --dataset X`.
- Geração do índice de figuras (`edugraph figures --index`), arquivo
  **gerado**, nunca editado à mão.

### Fora de escopo

- Figuras de comunidades (B-07) e de centralidade (C-07).

## Critérios de aceite

- [ ] Dado `synthetic_v1`, quando rodar `describe`, então a tabela traz
      98 alunos, 7 disciplinas e 197 arestas.
- [ ] Dado qualquer dataset, quando gerar a figura, então saem PNG e SVG
      em `results/figures/`, com o estilo de `reporting.figures.STYLE`.
- [ ] Dado um grafo com mais de mil nós, quando gerar a figura, então a
      redução aplicada aparece na legenda.
- [ ] Rodar duas vezes produz a mesma figura.
- [ ] `docs/artigo/indice-figuras.md` é gerado, não editado.

## Testes exigidos

- **Unitários:** `describe` sobre `tiny_v1` bate com valores à mão (6
  alunos, 3 disciplinas, 10 arestas); a figura é escrita nos dois
  formatos.
- Sem teste de aparência — comparação de imagem é frágil e não paga.

## Arquivos criados ou alterados

- `src/edugraph/data/report.py`.
- `src/edugraph/reporting/figures.py` — `build_index`.
- `src/edugraph/data/cli.py` — `cmd_report`.
- `tests/data/test_report.py` (novo).

## Impacto no artigo

**Figura 2** (grafo bipartido) e a **tabela de estatísticas do dataset**,
ambas do capítulo 3.
