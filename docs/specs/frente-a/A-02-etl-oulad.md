# [A-02] ETL do OULAD: download, esquema e tabela normalizada

**Frente:** A
**Dono:** Pedro
**Status:** concluída contra `oulad_mini` (18/09/2026); rodada na base completa pendente do download

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

- [x] Dado `tests/data/oulad_mini/`, quando rodar `normalize`, então a
      tabela tem as colunas de `NORMALIZED_COLUMNS` e nenhuma duplicata
      de (aluno, módulo, apresentação).
- [x] Dada uma tabela sem uma coluna esperada, quando ler, então falha
      com mensagem que nomeia a tabela e a coluna.
- [x] Dado o OULAD completo, quando rodar com `cache_dir`, então a
      segunda execução não relê `studentVle.csv`. *Mecanismo pronto e
      testado sobre `oulad_mini` (o teste remove o `studentVle.csv` entre
      as duas chamadas e a segunda ainda responde do cache; alterar a
      fonte expira o cache). A confirmação na base completa é parte da
      rodada manual.*
- [ ] Dado o OULAD completo, quando rodar, então o pico de memória cabe
      num notebook de 8 GB — **medir e registrar**. *Pendente do download
      (passo manual). `studentVle` é lida em blocos de 1 milhão de linhas
      com `usecols`/`dtype`; o pico esperado é o de um bloco (~40 MB)
      mais a tabela final. Medir com `python -m edugraph data etl` e
      anotar aqui.*
- [x] A nota média por matrícula é ponderada pelo `weight` da avaliação,
      e a escolha está registrada em `docs/artigo/`.
- [x] `to_outcomes` produz um desfecho por aluno, com a regra de
      desempate documentada.

## Testes exigidos

- **Contrato:** `outcomes.csv` gerado passa em `validate_outcomes`.
- **Unitários** (`tests/data/test_bipartite.py`, já esboçados): esquema
  de `oulad_mini` bate com `SCHEMAS`; `normalize` produz a tabela sem
  duplicatas; matrícula cancelada vira `Withdrawn`; avaliação sem data
  não quebra a leitura.
- **Lento** (`@pytest.mark.slow` + `@pytest.mark.oulad`): rodada sobre a
  base completa — *a escrever junto com a rodada manual, quando houver
  números de referência para afirmar.*
- **Escritos:** `tests/data/test_etl.py`, 17 testes sobre `oulad_mini` —
  esquema das sete tabelas, atributos demográficos não carregados,
  mensagens de erro, média ponderada (e simples quando Σpeso = 0),
  cliques, leitura em blocos, descarte sem evidência, cache e expiração,
  tabela por avaliação, regra de desfecho, `verify`/`download` sem rede,
  comando `data etl`.

## Arquivos criados ou alterados

- `src/edugraph/data/oulad/download.py`, `schema.py`, `etl.py`.
- `src/edugraph/data/cli.py` — `cmd_etl`.
- `scripts/download_oulad.py` (já existia; usa `download.py`).
- `src/edugraph/data/pipeline.py` — fonte `oulad` escolhe a tabela pelo grão
  (`assessment` → tabela por avaliação).
- `OULAD_SHA256` em `download.py` fica **vazio até o primeiro download real**;
  `download()` imprime o hash para preencher.
- `tests/data/test_bipartite.py`.

## Impacto no artigo

Estatísticas descritivas do dataset (seção de dados) e duas decisões
metodológicas a registrar: a regra de agregação de matrículas repetidas e
a ponderação da nota média.
