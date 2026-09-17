# [A-01] Gerador sintético determinístico com comunidades plantadas

**Frente:** A
**Dono:** Pedro
**Status:** não iniciada

## Objetivo

Estender o gerador sintético do dia 0 para produzir datasets com número
de grupos configurável e com a esparsidade do OULAD, e gravar o resultado
como artefatos de contrato.

## Contexto

**Cumpre:** `BipartiteBundle`, `Outcomes`.
**Consome:** nada — é a origem do pipeline.

A base secundária declarada no briefing §8: comunidades plantadas de
propósito servem de *ground truth* para verificar se Louvain e
Girvan-Newman recuperam estrutura conhecida.

`edugraph/data/synthetic.py` **já funciona** para os parâmetros do
starter kit (seed 42, três grupos de 40, 30% em risco) — é dele que sai
`data/fixtures/synthetic_v1`. Esta spec acrescenta o que falta.

Ver `docs/contratos/bipartite.md` e `docs/contratos/outcomes.md`.

## Dependências

- Nenhuma de outra frente.
- Depende de A-03 (construção do bipartido) para gravar artefatos; até
  lá, é possível fechar o gerador e testá-lo só pelas matrículas.

## Escopo

### Incluído

- `SyntheticSpec.sparsity`: remoção determinística de matrículas para
  imitar o OULAD, onde a maior parte dos alunos aparece em uma única
  matrícula.
- Número de grupos e de módulos por grupo configuráveis.
- Uma fixture nova `synthetic_v2`, com esparsidade realista, gerada por
  `scripts/make_fixtures.py`.
- Comando `edugraph data synthetic --seed N --out DIR`.

### Fora de escopo

- Qualquer modelo generativo aprendido a partir do OULAD real — violaria
  a restrição do briefing §2.
- Alterar `synthetic_v1`: fixtures são imutáveis (ADR-0011).

## Critérios de aceite

- [ ] Dado `SyntheticSpec(seed=42)`, quando gerar duas vezes, então as
      matrículas são idênticas.
- [ ] Dado `sparsity=0.5`, quando gerar, então a mediana de matrículas
      por aluno cai para 1 e o desvio da distribuição se aproxima do
      OULAD (documentar a comparação).
- [ ] Dado `sparsity` alto, quando gerar, então o grupo plantado continua
      recuperável — se a esparsidade destruir a estrutura, isso é achado
      e vai para o texto.
- [ ] Dado `--seed 7 --out data/processed`, quando rodar o comando, então
      o dataset é gravado e passa em `edugraph validate`.
- [ ] `synthetic_v2` existe, é imutável e tem `REFERENCE.md`.

## Testes exigidos

- **Contrato:** `synthetic_v2` passa em `validate_dataset`.
- **Unitários** (`tests/data/test_synthetic.py`, já existentes e a
  estender): determinismo; seeds diferentes geram dados diferentes;
  tamanhos de grupo; faixa de matrículas por aluno; existência de ruído;
  vocabulário de `final_result`.
- Remover o `test_esparsidade_ainda_nao_implementada`, que hoje verifica
  o `NotImplementedError`.

## Arquivos criados ou alterados

- `src/edugraph/data/synthetic.py` — implementar `sparsity`; generalizar
  grupos.
- `src/edugraph/data/cli.py` — `cmd_synthetic`.
- `scripts/make_fixtures.py` — `make_synthetic_v2`.
- `tests/data/test_synthetic.py`.

## Impacto no artigo

A esparsidade realista é o que permite mostrar, **antes do OULAD**, o
efeito da decisão D1 sobre a projeção. Rende uma figura comparando a
distribuição de matrículas por aluno em `synthetic_v1`, `synthetic_v2` e
OULAD, e um parágrafo na seção de dados.
