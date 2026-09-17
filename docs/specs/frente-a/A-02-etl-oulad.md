# [A-02] ETL do OULAD: download, esquema e tabela normalizada

**Frente:** A
**Dono:** Pedro
**Status:** não iniciada

## Objetivo

Transformar as sete tabelas do OULAD numa tabela normalizada com uma
linha por (aluno, disciplina, apresentação), com nota média, cliques no
AVA e desfecho.

## Contexto

**Cumpre:** a tabela normalizada (contrato interno da Frente A) e
`Outcomes`.
**Consome:** os sete CSV brutos.

Open University Learning Analytics Dataset (Kuzilek; Hlosta; Zdrahal,
2017), ~32 mil estudantes. `studentVle.csv` tem ~10,6 milhões de linhas.

**Pode ser dividida em duas specs** se ficar grande: (a) download +
esquema, (b) normalização.

## Dependências

- **Download do OULAD** (~450 MB), passo manual documentado no README.
- **Neutralizada por:** `tests/data/oulad_mini/` — sete arquivos
  minúsculos com o esquema real, já no repositório. O desenvolvimento
  inteiro acontece contra eles; a base completa só é necessária na
  rodada final.

## Escopo

### Incluído

- `download.py`: baixar, conferir SHA-256, extrair, não sobrescrever
  download válido sem `--force`.
- `schema.py`: completar `SCHEMAS` conferindo contra o dicionário de
  dados publicado; `validate_schema` falha cedo e com mensagem clara.
- `etl.py`: junções, agregação e a tabela normalizada; cache em
  `data/interim`.
- Decidir e **registrar** a regra para aluno com mais de uma matrícula no
  mesmo módulo.
- Leitura com `usecols` e `dtype` explícitos.

### Fora de escopo

- Construção do grafo — é a A-03.
- Imputação de dados faltantes por qualquer método aprendido.

## Critérios de aceite

- [ ] Dado `tests/data/oulad_mini/`, quando rodar `normalize`, então a
      tabela tem as colunas de `NORMALIZED_COLUMNS` e nenhuma duplicata
      de (aluno, módulo, apresentação).
- [ ] Dada uma tabela sem uma coluna esperada, quando ler, então falha
      com mensagem que nomeia a tabela e a coluna.
- [ ] Dado o OULAD completo, quando rodar com `cache_dir`, então a
      segunda execução não relê `studentVle.csv`.
- [ ] Dado o OULAD completo, quando rodar, então o pico de memória cabe
      num notebook de 8 GB — **medir e registrar**.
- [ ] A nota média por matrícula é ponderada pelo `weight` da avaliação,
      e a escolha está registrada em `docs/artigo/`.
- [ ] `to_outcomes` produz um desfecho por aluno, com a regra de
      desempate documentada.

## Testes exigidos

- **Contrato:** `outcomes.csv` gerado passa em `validate_outcomes`.
- **Unitários** (`tests/data/test_bipartite.py`, já esboçados): esquema
  de `oulad_mini` bate com `SCHEMAS`; `normalize` produz a tabela sem
  duplicatas; matrícula cancelada vira `Withdrawn`; avaliação sem data
  não quebra a leitura.
- **Lento** (`@pytest.mark.slow` + `@pytest.mark.oulad`): rodada sobre a
  base completa.

## Arquivos criados ou alterados

- `src/edugraph/data/oulad/download.py`, `schema.py`, `etl.py`.
- `src/edugraph/data/cli.py` — `cmd_etl`.
- `scripts/download_oulad.py`.
- `tests/data/test_bipartite.py`.

## Impacto no artigo

Estatísticas descritivas do dataset (seção de dados) e duas decisões
metodológicas a registrar: a regra de agregação de matrículas repetidas e
a ponderação da nota média.
