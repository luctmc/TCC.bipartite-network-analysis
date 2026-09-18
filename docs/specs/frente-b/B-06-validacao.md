# [B-06] Validação a posteriori das comunidades

**Frente:** B
**Dono:** Gabriel
**Status:** não iniciada

## Objetivo

Verificar se a estrutura descoberta **apenas pela topologia** guarda
relação com o grupo plantado (sintético) e com o desfecho histórico.

## Contexto

**Cumpre:** tabela de validação para o artigo.
**Consome:** `Partition`, `Outcomes`.

**Este é o único módulo da Frente B autorizado a ler `outcomes.csv`**
(ADR-0008). Um teste de contrato falha se `load_outcomes` for chamada de
qualquer outro lugar.

O que se mede **não é acurácia de um modelo** — não há modelo. NMI,
pureza e distribuição de desfechos são medidas entre partições e
categorias já conhecidas.

## Dependências

- B-01, para ter partições.
- `outcomes.csv`, que já existe nas fixtures **com o grupo plantado**.

> **Nota da Frente A (18/09/2026) — leia antes de reportar qualquer Q.**
> A spec **A-08** acrescentou réplicas do **modelo nulo**: o mesmo grafo
> com os mesmos graus e a estrutura embaralhada. Elas já estão em
> `data/processed` (`oulad_module_presentation_null0..2`) e saem de
> `edugraph data null --dataset X --replicas N`.
>
> Isso importa porque a modularidade encontra "comunidades" em qualquer
> grafo esparso. Medido: em `synthetic_v1` o Q real (0,4666) fica 15
> desvios acima do nulo (0,208 ± 0,017) — o método funciona; no OULAD
> `module_presentation` o Q real (0,7728) é **menor** que o das réplicas
> (0,781) — ali não há estrutura a reportar.
>
> **Atualização (A-09, mesmo dia).** O diagnóstico acima levou à troca do
> critério de aresta. Existe agora `oulad_vle_bbb_2013j`, em que o nó do
> lado V é o recurso do AVA e o grau mediano do aluno é 33 em vez de 1.
> Nele o Q real fica ~5× acima do nulo, com 4 comunidades de tamanhos
> 941, 480, 322 e 127. **É o dataset a usar para comunidades de alunos.**
> As réplicas nulas dele são `oulad_vle_bbb_2013j_null0..4`.
>
> A comparação é **desta spec**, não da A-08 (a Frente A só gera o
> artefato). `edugraph.data.nullmodel.is_null(bundle)` distingue uma
> réplica de um dataset real sem depender do nome. Sugestão de critério:
> reportar o z-score de Q contra ≥ 5 réplicas, e tratar z < 3 como
> "indistinguível do acaso". Gabriel decide o critério final — isto é
> apontamento, não alteração de escopo.

## Escopo

### Incluído

- `normalized_mutual_information(partition, planted_group)`.
- `purity(partition, planted_group)`.
- `outcome_profile(partition, outcomes)` — distribuição dos quatro
  desfechos por comunidade, em absoluto e relativo à base.
- Comando `edugraph community evaluate`.
- Tratar `planted_group is None` (caso OULAD) sem quebrar: só
  `outcome_profile` se aplica.

### Fora de escopo

- Qualquer uso do desfecho como entrada de algoritmo — é a restrição
  inegociável.
- Teste de significância estatística: fora do escopo do artigo e exigiria
  discussão metodológica que não cabe em 18 páginas.

## Critérios de aceite

- [ ] Dada a partição de referência de `synthetic_v1` e o grupo plantado,
      então NMI ≥ 0,8.
- [ ] Dada uma partição idêntica ao grupo plantado, então NMI = 1 e
      pureza = 1.
- [ ] Dado o OULAD (sem `planted_group`), então `outcome_profile`
      funciona e NMI é pulado sem erro.
- [ ] `outcome_profile` tem uma linha por comunidade, com a taxa de cada
      desfecho **e** a taxa da base para comparação.
- [ ] Se uma comunidade concentra `Withdrawn` acima da base, isso é
      visível na tabela sem cálculo adicional.

## Testes exigidos

- **Contrato:** `test_outcomes_isolation` confirma que só este módulo (e
  o `evaluate.py` da Frente C) lê os rótulos.
- **Unitários** (já escritos como `xfail`): NMI contra o grupo plantado;
  cobertura de todas as comunidades no perfil de desfecho.

## Arquivos criados ou alterados

- `src/edugraph/community/evaluate.py`.
- `src/edugraph/community/cli.py` — `cmd_evaluate`.
- `tests/community/test_caracterizacao.py`.

## Impacto no artigo

**Tabela de validação.** E, se a relação **não** aparecer, isso também é
resultado: o artigo reporta que a estrutura topológica e o desfecho
histórico são dimensões independentes. Registrar a interpretação em
`docs/artigo/decisoes-metodologicas.md`.
