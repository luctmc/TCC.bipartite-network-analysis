# [A-06] Estratégia de escala e rodada completa do OULAD

**Frente:** A
**Dono:** Pedro
**Status:** em andamento — reduções prontas e testadas (18/09/2026); rodada completa pendente do download do OULAD

## Objetivo

Viabilizar o processamento do OULAD com reduções declaradas e
auditáveis, e gerar `data/processed` para as três frentes.

## Contexto

**Cumpre:** `BipartiteBundle` e `ProjectionBundle` em escala real.
**Consome:** a tabela normalizada.

O briefing §8 avisa: a projeção aluno↔aluno de uma coorte com dois mil
alunos chega a milhões de arestas, e o Girvan-Newman é O(m²n). A
limitação é **resultado a reportar**, não falha a esconder.

## Dependências

- A-02 (OULAD normalizado), A-03 e A-04.
- Esta é a spec que **fecha** as dependências de B e C: quando
  `data/processed` existir, eles só trocam `--root`.

## Escopo

### Incluído

- `filter_cohort` — recorte por apresentação. É a redução preferida:
  recorta por unidade com sentido pedagógico.
- `sample_students` — amostra com seed, registrada no `meta.json`.
- `k_core` — núcleo-k sobre a projeção, reportando quantos nós saíram.
- `prune_by_weight` — corte por peso mínimo, registrado em
  `ProjectionSpec.min_weight` e conferido pelo validador.
- Rodada completa gerando `data/processed`.

### Fora de escopo

- Paralelismo, Dask, computação distribuída — briefing §13.

## Critérios de aceite

- [x] Dado `cohort="BBB_2013J"`, quando filtrar, então só aquela
      apresentação sobra e o número de nós removidos vai para
      `meta.stats`.
- [x] Dada a mesma seed, quando amostrar duas vezes, então a amostra é
      idêntica.
- [x] Dado `min_weight=2.0`, quando podar, então `validate_projection`
      confere que nenhuma aresta abaixo do corte sobreviveu.
- [ ] Dada a rodada completa, quando terminar, então `data/processed`
      passa em `edugraph validate` e `pytest --artifacts-root data/processed`
      fica verde. *Pendente: exige o OULAD baixado (passo
      manual). O comando é `python -m edugraph run
      configs/oulad_cohort_bbb_2013j.toml --only data`.*
- [x] Cada redução aplicada está registrada no `meta.json` do artefato —
      **nenhuma redução silenciosa**.
- [ ] Tempo e pico de memória da rodada completa estão medidos e
      registrados. *Pendente do mesmo download. Anotar aqui e em
      `docs/artigo/decisoes-metodologicas.md`; depois escolher
      `min_weight`, `sample_students` e `k_core` nos TOML.*

## Testes exigidos

- **Contrato:** a suíte inteira roda com `--artifacts-root data/processed`.
- **Unitários:** `tests/data/test_scale.py`, 15 testes — coorte por
  apresentação e por período, erro orientado quando a granularidade não
  carrega apresentação, corte por peso auditável pelo validador, amostra
  determinística e seus limites, núcleo-k, reduções encadeadas no
  histórico, pipeline lendo `[source]` e os comandos `data sample`,
  `data cohort` e `data project --k-core`.
- **Lentos** (`slow` + `oulad`): a rodada completa.

## Arquivos criados ou alterados

- `src/edugraph/data/scale.py`.
- `configs/oulad_module_presentation.toml`,
  `configs/oulad_cohort_bbb_2013j.toml` — ajustar após medir.
- `tests/data/test_scale.py` (novo).
- `src/edugraph/data/pipeline.py` — `sample_students`/`sample_seed`/`k_core`
  lidos de `[source]` (RunConfig é contrato congelado; a decisão de
  escala é sobre a fonte).
- `src/edugraph/data/cli.py` — `data sample`, `data cohort`, `data project --k-core`.

## Impacto no artigo

**Limitação reportada como resultado** (seção de limitações): o que não
coube, por quê, e o que foi feito no lugar. Mais a tabela de tamanhos por
recorte.
