# Layout em disco e resolução de raízes

O mesmo layout vale para `data/fixtures` e `data/processed`. **Trocar de
fonte é trocar a raiz** — é essa propriedade que permite às Frentes B e C
trabalharem no dia 0 sobre fixtures e, mais tarde, sobre o OULAD, sem
mudar uma linha de código.

## A árvore

```
<root>/<dataset>/
├── bipartite/
│   ├── nodes.csv          # id,kind,label          <- nunca contém rótulo
│   ├── edges.csv          # source,target,weight
│   ├── outcomes.csv       # student_id,final_result[,planted_group]
│   └── meta.json          # schema_version,kind,spec,stats,producer,created_at
├── projections/<projection_id>/
│   ├── nodes.csv          # student_simple · student_resource_allocation
│   ├── edges.csv          # discipline_simple · discipline_resource_allocation
│   └── meta.json          # + spec e source
├── communities/<algorithm>__<projection_id>/
│   ├── membership.csv     # node_id,community
│   ├── profile.csv        # community,size,top_disciplines,…   (spec B-05)
│   └── meta.json          # modularity,n_communities,runtime_s,status,params
├── centrality/<projection_id>/
│   ├── degree.csv · betweenness.csv · eigenvector.csv    # node_id,score
│   └── <metric>.meta.json
└── metrics/
    ├── communities.csv
    ├── centrality_top.csv
    └── projections.csv
```

## Como os ids são formados

| Id | Forma | Exemplo |
|---|---|---|
| nó aluno | `S` + id do aluno | `S100055` |
| nó disciplina | `D` + código | `DAAA`, `DAAA_2013J` |
| `projection_id` | `<side>_<weighting>` | `discipline_resource_allocation` |
| id de partição | `<algorithm>__<projection_id>` | `louvain__student_simple` |

O prefixo `S`/`D` não é enfeite: ele torna o lado do nó legível no CSV e
permite detectar mistura de lados só olhando o arquivo. O validador
confere que ele bate com o `kind`.

## Várias raízes, consultadas em ordem

```bash
python -m edugraph community louvain --root data/processed --root data/fixtures ...
```

A primeira raiz que contiver o artefato vence. Assim `data/processed`
sobrepõe `data/fixtures` **sem copiar nada**: o que a Frente A já gerou é
usado, e o que ela ainda não gerou cai na fixture.

Alternativa à linha de comando, útil em scripts e na CI:

```bash
export EDUGRAPH_ROOTS="data/processed:data/fixtures"   # ';' no Windows
```

Sem nenhum dos dois, o padrão é `data/processed` e depois
`data/fixtures`.

**A escrita nunca usa a lista** — vai sempre para uma raiz única, passada
em `--out`, e o padrão é `data/processed`. `data/fixtures` só é escrito
por `scripts/make_fixtures.py`.

## Quando um artefato não é encontrado

`ArtifactNotFoundError` lista **todas** as raízes consultadas, com o
caminho completo procurado em cada uma. O engano mais comum em
desenvolvimento é esquecer o `--root`, e a mensagem existe para que isso
leve segundos e não meia hora.

## Fixtures são imutáveis

`data/fixtures/` é versionado em git e **nunca muda**. Quem precisar de
outra fixture cria uma versão nova (`synthetic_v2`); as anteriores
continuam existindo para os testes que dependem delas.

`scripts/make_fixtures.py` se recusa a sobrescrever sem `--force`, e os
metadados são congelados (`created_at` fixo, `runtime_s = 0`) para que
uma regeneração produza os mesmos bytes — ver ADR-0011. Um diff em
`data/fixtures/` significa que algo mudou de verdade.

## Escrita canônica

Toda escrita passa por `contracts.io`, que garante:

- nós e arestas **ordenados**; extremos de aresta em ordem lexicográfica;
- floats no `repr` mais curto que retorna exatamente ao mesmo binário;
- quebra de linha `\n` e UTF-8 explícito, independentemente do sistema;
- `meta.json` com chaves ordenadas e indentação fixa.

Consequência prática: `escrever → ler → escrever` é uma identidade byte a
byte, verificada em `tests/contract/test_roundtrip.py`.
