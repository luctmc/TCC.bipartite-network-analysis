# [A-03] Grafo bipartido parametrizável por `BipartiteSpec`

**Frente:** A
**Dono:** Pedro
**Status:** não iniciada

## Objetivo

Construir G = (U ∪ V, E) a partir da tabela normalizada, com
granularidade, critério de aresta, limiar e coorte como **parâmetros**.

## Contexto

**Cumpre:** `BipartiteBundle`.
**Consome:** a tabela normalizada (A-01 ou A-02).

É a materialização da ADR-0007 e da decisão D1. O briefing §8 exige que o
critério de aresta seja parametrizável, porque o grupo vai comparar mais
de uma configuração no capítulo de Resultados.

Ver `docs/contratos/bipartite.md`.

## Dependências

- A-01 ou A-02 para ter tabela de entrada.
- **Não depende de nenhuma outra frente.**

## Escopo

### Incluído

- `build_bipartite(table, spec)` cobrindo as três granularidades
  (`module`, `module_presentation`, `assessment`) e os três critérios
  (`score_threshold`, `final_result_pass`, `vle_activity`).
- `normalize_table` — agregação por (aluno, disciplina), separada para
  ser testável sozinha.
- Filtro por `spec.cohort`.
- Remoção de nós isolados, com o número em `meta.stats`.
- Ids com prefixo `S`/`D`; nós **apenas** com `kind` e `label`.

### Fora de escopo

- Projeções — são a A-04.
- Estratégias de escala além do `cohort` — são a A-06.

## Critérios de aceite

- [ ] Dada uma tabela com notas 82 e 41 e `threshold=60`, quando
      construir com `score_threshold`, então existe aresta para o
      primeiro aluno e não para o segundo.
- [ ] Dada a mesma tabela, quando construir com `granularity="module"`,
      então o nó é `DAAA`; com `module_presentation`, `DAAA_2024J`.
- [ ] Dado `cohort="BBB_2013J"`, quando construir, então só matrículas
      daquela apresentação entram.
- [ ] Dado qualquer `spec`, quando construir, então nenhum nó tem
      atributo além de `kind` e `label` (ADR-0008).
- [ ] Dado o resultado, quando validar, então `validate_bipartite` passa.
- [ ] Sobre as mesmas entradas de `tiny_v1` e `synthetic_v1`, o grafo
      produzido é **idêntico** ao das fixtures — é o que prova que a
      implementação de referência do dia 0 pode ser aposentada.

## Testes exigidos

- **Contrato:** artefatos gerados passam em `validate_dataset`;
  `nodes.csv` sem coluna proibida.
- **Unitários** (`tests/data/test_bipartite.py`, já escritos como
  `xfail`): limiar decide a aresta; granularidade muda o nó; critério de
  aprovação ignora a nota; nós sem rótulo.
- Acrescentar: comparação com as fixtures.

## Arquivos criados ou alterados

- `src/edugraph/data/bipartite.py`.
- `src/edugraph/data/cli.py` — `cmd_bipartite`.
- `src/edugraph/data/stage.py` — parte do estágio `data`.
- `tests/data/test_bipartite.py` — remover os `xfail`.

## Impacto no artigo

A escolha do critério de aresta é parágrafo de justificativa da
Fundamentação (ADR-0007); a comparação entre critérios é tabela do
capítulo 3. A contagem de nós isolados removidos precisa ser reportada.
