# [B-02] Girvan-Newman com orçamento de tempo

**Frente:** B
**Dono:** Gabriel
**Status:** não iniciada

## Objetivo

Implementar Girvan-Newman com orçamento de tempo, critério de parada e
`status`, de modo que um estouro seja **resultado reportável** e não
falha de execução.

## Contexto

**Cumpre:** `Partition`.
**Consome:** `ProjectionBundle`.

O algoritmo recalcula a intermediação de todas as arestas a cada
remoção: O(m²n). O starter kit mediu **645×** o tempo do Louvain sobre
120 nós. Sobre o OULAD completo, não termina.

Decisão registrada na ADR-0006. O briefing §8 é explícito: tratar a
limitação como resultado.

## Dependências

- Projeções da Frente A.
- **Neutralizada por:** as fixtures.
- A-06 (amostragem) ajuda no OULAD, mas não bloqueia: `sample_nodes`
  pode ser implementado aqui de forma simples enquanto a A-06 não fecha.

## Escopo

### Incluído

- `GirvanNewmanAlgorithm.run` com `time_budget_s`,
  `target_communities`, `sample_nodes` e `seed`.
- Consumir `nx.community.girvan_newman` como iterador, checando o relógio
  **a cada corte** — não dá para interromper depois que o gerador entrou
  numa iteração longa.
- Guardar a melhor partição por Q vista até o momento.
- Ao estourar: `status="timeout"`, melhor partição, e o número de cortes
  em `params`. **Não levantar exceção** — o contrato proíbe.
- Se nem o primeiro corte couber: `status="skipped"`, partição trivial,
  Q = 0.
- Comando `edugraph community girvan-newman --time-budget N`.

### Fora de escopo

- Paralelizar o cálculo de intermediação.
- Implementar Brandes à mão (ADR-0010 decidiu que não paga).

## Critérios de aceite

- [ ] Dado `synthetic_v1` e `time_budget_s=0.01`, quando rodar, então
      devolve `status` em {`timeout`, `skipped`} **sem levantar exceção**
      e com `membership` não vazio.
- [ ] Dado `tiny_v1` e orçamento folgado com `target_communities=2`,
      então `status="ok"`, S4 e S5 juntos e separados de S1.
- [ ] Dado `target_communities=None`, então para no melhor Q do
      dendrograma.
- [ ] `validate_partition` passa nos três status.
- [ ] O tempo relativo ao Louvain sobre a mesma projeção está medido — é
      o número que vai para o artigo.

## Testes exigidos

- **Contrato:** artefato com `status="timeout"` passa nos validadores
  como qualquer outro.
- **Unitários** (já escritos como `xfail`): orçamento estourado devolve
  timeout; separação da ponte em `tiny_v1`.
- **Lento:** execução completa sobre uma coorte do OULAD.

## Arquivos criados ou alterados

- `src/edugraph/community/girvan_newman.py`.
- `src/edugraph/community/cli.py` — `cmd_girvan_newman`.
- `tests/community/test_louvain.py` — remover os `xfail` da B-02.

## Impacto no artigo

**Decisão metodológica** (ADR-0006) e a coluna `status` da tabela
principal do capítulo 3. O tempo relativo ao Louvain é um dos números
mais citáveis do trabalho.
