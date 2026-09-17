# [B-04] Comparação Louvain × Girvan-Newman × ponderação

**Frente:** B
**Dono:** Gabriel
**Status:** não iniciada

## Objetivo

Produzir `metrics/communities.csv`: a **tabela principal do capítulo 3**.

## Contexto

**Cumpre:** `metrics/communities.csv`.
**Consome:** `Partition`.

O briefing §9 pede comparações, não só resultados. A arquitetura torna
trivial rodar as variantes: cada uma é uma linha desta tabela.

Ver `docs/contratos/metrics.md`.

## Dependências

- B-01 e B-02, para ter partições a comparar.

## Escopo

### Incluído

- `to_metrics_row()` e `compare()` no formato de `METRICS_COLUMNS`.
- **Incluir as linhas com `status="timeout"`.** Uma execução que não
  coube no orçamento é dado do artigo; omiti-la seria esconder o
  resultado que o briefing §8 manda reportar.
- `agreement()` — NMI e índice de Rand ajustado entre duas partições do
  mesmo grafo. São medidas de teoria da informação entre partições
  conhecidas, não aprendizado de máquina.
- Comando `edugraph community compare --dataset X`.

### Fora de escopo

- Validação contra o desfecho — é a B-06.
- Figuras — são a B-07.

## Critérios de aceite

- [ ] Dadas as partições de `synthetic_v1`, quando comparar, então a
      tabela tem uma linha por (projeção, algoritmo), com as colunas de
      `METRICS_COLUMNS`.
- [ ] Rodar duas vezes **atualiza** as linhas em vez de duplicá-las.
- [ ] Uma partição com `status="timeout"` aparece na tabela, com o
      status visível.
- [ ] `agreement()` entre uma partição e ela mesma dá NMI = 1.
- [ ] A tabela permite responder, sem cálculo adicional: qual algoritmo
      deu maior Q, qual foi mais rápido, e quanto.
- [ ] A comparação entre as duas **ponderações** aparece — não só entre
      os dois algoritmos.

## Testes exigidos

- **Contrato:** idempotência por `(dataset, projection_id, algorithm)`;
  mudar as colunas levanta `ContractError`.
- **Unitários:** NMI de uma partição consigo mesma é 1; linha com timeout
  entra na tabela.

## Arquivos criados ou alterados

- `src/edugraph/community/compare.py`.
- `src/edugraph/community/cli.py` — `cmd_compare`.
- `tests/community/test_comparacao.py` (novo).

## Impacto no artigo

**A tabela principal do capítulo 3**, mais a figura de Q × tempo por
algoritmo (B-07).
