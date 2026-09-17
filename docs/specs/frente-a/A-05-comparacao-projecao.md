# [A-05] Projeção de referência via NetworkX e comparação

**Frente:** A
**Dono:** Pedro
**Status:** não iniciada

## Objetivo

Comparar a implementação à mão com a do NetworkX: igualdade numérica,
tempo e distribuição de pesos.

## Contexto

**Cumpre:** `metrics/projections.csv`.
**Consome:** `BipartiteBundle`, `ProjectionBundle`.

A comparação é o que sustenta a afirmação de domínio do algoritmo
(ADR-0010) e é, de quebra, o melhor teste possível da A-04: uma
divergência acima da tolerância aponta bug real.

## Dependências

- A-04, para ter o que comparar.

## Escopo

### Incluído

- `NetworkXSimpleProjection` e `NetworkXResourceAllocationProjection`.
- `compare()` → uma linha de `metrics/projections.csv`.
- `weight_distribution()` → histograma para a figura.
- **Verificar qual função do NetworkX corresponde de fato à alocação de
  recursos de Zhou et al.** As funções prontas não são todas
  equivalentes; se nenhuma corresponder exatamente, **documentar a
  diferença** em vez de forçar a comparação.

### Fora de escopo

- Otimizar a implementação à mão para ganhar do NetworkX. O objetivo é
  demonstrar correção, não competir em desempenho — e reportar que a
  biblioteca é mais rápida é resultado honesto.

## Critérios de aceite

- [ ] Dadas as duas implementações sobre `tiny_v1`, quando comparar,
      então `max_abs_diff < 1e-9` e `equal_within_tolerance` é verdadeiro.
- [ ] Dadas as duas sobre `synthetic_v1`, idem.
- [ ] Dada uma aresta presente em uma e ausente na outra, quando
      comparar, então a diferença é `inf` — **não pode ser silenciada**.
- [ ] `metrics/projections.csv` tem as colunas de `METRICS_COLUMNS` e é
      idempotente por `(dataset, projection_id)`.
- [ ] Se `collaboration_weighted_projected_graph` não for equivalente à
      alocação de recursos, isso está escrito em
      `docs/artigo/decisoes-metodologicas.md`.

## Testes exigidos

- **Unitários:** `test_manual_e_networkx_batem_ate_1e9` (já escrito como
  `xfail`); aresta faltante gera diferença infinita.
- **Contrato:** `metrics/projections.csv` é idempotente.

## Arquivos criados ou alterados

- `src/edugraph/data/projection/networkx_ref.py`, `compare.py`.
- `src/edugraph/data/report.py` — `figure_weight_distributions`.
- `tests/data/test_projections.py`.

## Impacto no artigo

**Tabela** de validação (manual × NetworkX: diferença máxima, tempos) e
**figura** comparando as distribuições de peso das duas ponderações —
que é onde o efeito de Zhou et al. fica visível.
