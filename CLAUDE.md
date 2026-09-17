# Regras deste repositório

TCC Grupo 16 — UniAnchieta. Análise topológica de redes educacionais
bipartidas. Leia [`docs/README.md`](docs/README.md) para o mapa completo.

## As três regras que não se negociam

### 1. Sem IA, sem aprendizado de máquina

Nenhum componente pode usar ML, embeddings de grafo ou qualquer modelo
treinado com dados rotulados. Está fora de escopo, sem exceção:
`sklearn`, `tensorflow`, `torch`, `node2vec`, k-means, DBSCAN,
classificadores de qualquer natureza.

Foi exigência explícita do orientador e é o diferencial declarado do
trabalho. **Em caso de dúvida, escolha a alternativa clássica de Teoria
dos Grafos.**

Verificado por `tests/contract/test_no_ml.py`.

### 2. Rótulos históricos ficam fora do grafo

O desfecho da matrícula (`final_result`), notas e atributos demográficos
vivem em `bipartite/outcomes.csv`, **separados** de `nodes.csv`, e só
podem ser lidos por módulos chamados `evaluate.py`.

`nodes.csv` tem exatamente três colunas: `id`, `kind`, `label`.

Verificado por `tests/contract/test_outcomes_isolation.py`. ADR-0008.

### 3. Nenhuma frente importa outra

`edugraph.data`, `edugraph.community`, `edugraph.centrality` e
`edugraph.api` **não se importam**. Elas se comunicam por artefatos em
disco, através de `edugraph.contracts`.

Só dois arquivos são isentos: `edugraph/__main__.py` e
`edugraph/contracts/registry.py`. Acrescentar um terceiro exige ADR.

Verificado por `tests/contract/test_import_boundaries.py`. ADR-0003.

## Contratos congelados

`src/edugraph/contracts/` entrou em `main` no dia 0 e **não muda sem ADR
e aprovação dos três**. Mudar layout, nome de coluna ou semântica de
campo exige, além disso, subir `SCHEMA_VERSION`.

Antes de propor mudança de contrato, confira se o que você precisa não
cabe em `params` ou em `meta.stats` — os dois são dicionários livres e
existem para isso. A pergunta que decide: *outra frente precisa saber
disso?* Se não precisa, não é contrato.

## Fixtures são imutáveis

`data/fixtures/` é versionado e **nunca muda**. Quem precisar de outra
cria uma versão nova (`synthetic_v2`).

`scripts/make_fixtures.py` recusa sobrescrever sem `--force`, e a
regeneração é byte a byte idêntica (metadados congelados, ADR-0011). Um
diff em `data/fixtures/` significa que algo mudou de verdade.

## Comandos

```bash
pip install -e ".[dev]"

python -m edugraph validate --root data/fixtures
python -m edugraph api serve --root data/processed --root data/fixtures
python -m edugraph run configs/synthetic_v1.toml --dry-run
python scripts/make_fixtures.py

pytest                                    # sobre as fixtures
pytest --artifacts-root data/processed    # sobre o OULAD
pytest -m "not slow"                      # o que a CI roda

ruff check . && ruff format --check . && mypy src/edugraph/contracts
```

**Nada de `make`:** o grupo trabalha em Windows. Todo comando é
`python -m edugraph`.

## Convenções de código

- **Idioma (decisão D2):** código, nomes de coluna e chaves JSON em
  **inglês**, sem acentos, coerentes com NetworkX e pandas. Docstrings,
  comentários, documentação, specs, ADRs, commits e artigo em
  **português**.
- Só `pathlib`; nunca concatenação de caminho com `/` literal.
- **UTF-8 explícito** em toda leitura e escrita. Console: chamar
  `edugraph.console.configure()` nos pontos de entrada — o Windows usa
  `cp1252` por padrão e imprimir um acento levanta exceção.
- Toda escrita de artefato passa por `contracts.io`. Nenhum módulo de
  frente abre um CSV de artefato por conta própria.
- Todo algoritmo estocástico recebe `seed` explícita, gravada em
  `params`.
- Stub de spec ainda aberta levanta
  `NotImplementedError("A-04: ver docs/specs/...")` — **com o id da
  spec**, sempre.

## Testes

- Nomes em português, descrevendo o comportamento:
  `test_orcamento_estourado_devolve_timeout_e_nao_excecao`.
- `xfail` de spec aberta usa
  `@pytest.mark.xfail(reason="A-04 não implementada", raises=NotImplementedError, strict=True)`.
  `strict=True` é proposital: quando a spec fecha e o teste passa, a CI
  quebra — é o aviso de remover o marcador.
- Teste que depende de um dataset declara `@pytest.mark.dataset("nome")`
  e é pulado, não quebrado, quando ele não existe.
- Escrita só em `tmp_path`. Nenhum teste escreve em `data/fixtures`.
- Valores esperados de `tiny_v1` foram **derivados no papel** (ver
  `docs/testes/estrategia.md`). Não substitua por saída da biblioteca:
  isso transformaria a verificação em tautologia.

## Git

- `main` protegida, só por PR com CI verde.
- Uma spec, um branch, um PR: `a/A-04-projecao-manual`.
- Commits em português com o id da spec:
  `B-03: modularidade à mão e comparação com NetworkX`.
- PR que toca `contracts/`, `tests/contract/`, `data/fixtures/`,
  `__main__.py`, `pyproject.toml` ou `requirements*.txt` precisa da
  aprovação dos outros dois.

## Ao escrever para o artigo

Toda escolha não-óbvia vira parágrafo de justificativa e pergunta de
banca. Se você tomou uma decisão que pode surpreender outra pessoa do
grupo, ela vai para uma ADR ou para
`docs/artigo/decisoes-metodologicas.md` — no mesmo PR.
