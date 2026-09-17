# [B-01] Louvain sobre `ProjectionBundle`

**Frente:** B
**Dono:** Gabriel
**Status:** não iniciada

## Objetivo

Particionar uma projeção em comunidades por otimização de modularidade,
de forma determinística e com os parâmetros registrados no artefato.

## Contexto

**Cumpre:** `Partition`.
**Consome:** `ProjectionBundle`.

Louvain (Blondel et al., 2008) é otimização combinatória sobre a
estrutura do grafo — **não é aprendizado de máquina**: não há treino, não
há rótulo, e o resultado é rastreável até as arestas. É o que a restrição
do briefing §2 exige.

Ver `docs/contratos/partition.md`.

## Dependências

- Projeções da Frente A.
- **Neutralizada por:** `data/fixtures/synthetic_v1/projections/*` e
  `tiny_v1` já existem. Esta spec fecha inteira sem a Frente A.

## Escopo

### Incluído

- `LouvainAlgorithm.run` com `seed`, `resolution` e `implementation`.
- **Densificar os ids** de comunidade para `0..k-1` — o validador exige e
  a biblioteca não garante. A renumeração é determinística: pela ordem do
  menor id de nó de cada comunidade.
- Medir `runtime_s` com `time.perf_counter`.
- Calcular Q com a implementação da B-03 (não a da biblioteca).
- Comparar `python-louvain` com `nx.community.louvain_communities` e
  registrar a diferença.
- Comando `edugraph community louvain`.

### Fora de escopo

- Girvan-Newman (B-02), caracterização (B-05), validação (B-06).

## Critérios de aceite

- [ ] Dado `tiny_v1`/`student_simple`, quando rodar, então S4 e S5 ficam
      juntos, S1/S2/S6 ficam juntos, e os dois grupos são distintos.
- [ ] Dado `synthetic_v1`/`student_simple`, então Q ∈ [0,40, 0,55] e há
      pelo menos 3 comunidades com 10 ou mais alunos.
- [ ] Dada a mesma seed, duas execuções dão a **mesma** partição.
- [ ] Os ids de comunidade são densos `0..k-1`.
- [ ] `validate_partition` passa, inclusive no cruzamento com a projeção.
- [ ] `params` registra `seed`, `resolution` e `implementation`.
- [ ] A comparação entre as duas bibliotecas está registrada.

## Testes exigidos

- **Contrato:** artefatos passam em `validate_dataset`; `membership`
  cobre exatamente os nós da projeção.
- **Unitários** (`tests/community/test_louvain.py`, já escritos como
  `xfail`): recuperação em `tiny_v1`; faixa de Q em `synthetic_v1`;
  determinismo; ids densos.

## Arquivos criados ou alterados

- `src/edugraph/community/louvain.py`.
- `src/edugraph/community/cli.py` — `cmd_louvain`.
- `src/edugraph/community/stage.py`.
- `tests/community/test_louvain.py` — remover os `xfail`.

## Impacto no artigo

Nenhum isoladamente — alimenta B-04 (tabela principal), B-05
(caracterização) e B-06 (validação).
