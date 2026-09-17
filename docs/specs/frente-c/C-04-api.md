# [C-04] API FastAPI somente leitura

**Frente:** C
**Dono:** Lucas
**Status:** não iniciada

## Objetivo

Servir os artefatos em disco como JSON, para o front-end e para o uso
interno da instituição.

## Contexto

**Cumpre:** a API.
**Consome:** todos os bundles.

A API **não calcula nada** (ADR-0004): o cálculo acontece pela CLI. Se
calculasse, importaria `community` e `centrality`, e a fronteira da
ADR-0003 cairia no primeiro endpoint.

Ver `docs/contratos/` e `src/edugraph/api/schemas.py`.

## Dependências

- Nenhuma: a API sobe sobre `data/fixtures` desde o dia 0.
- **`/health` e `/datasets` já estão prontos** e testados.

## Escopo

### Incluído

- `GET /datasets/{dataset}/projections/{projection_id}` — com
  `?partition=` e `?metrics=` para embutir comunidade e centralidades,
  evitando uma segunda ida ao servidor.
- `GET /datasets/{dataset}/bipartite`
- `GET /datasets/{dataset}/communities/{artifact_id}`
- `GET /datasets/{dataset}/centrality/{projection_id}/{metric}`
- `GET /datasets/{dataset}/metrics/{name}`
- **Limite de arestas por resposta**, com o corte declarado no corpo, para
  que a interface possa avisar. Um grafo de um milhão de arestas não
  renderiza e não deve sequer ser transferido.
- 404 com a lista de raízes consultadas — o engano mais comum é esquecer
  o `--root`.

### Fora de escopo

- Qualquer `POST`. Um `POST /runs` pode ser acrescentado depois sem mudar
  os contratos, mas não entra no escopo inicial (ADR-0004).
- Autenticação: o sistema é de uso interno e não expõe dados a terceiros
  (briefing §6.2). Se um dia for exposto, isso vira spec própria.

## Critérios de aceite

- [ ] Dada a fixture, cada rota responde 200 e o corpo valida contra o
      schema pydantic.
- [ ] Dado um dataset inexistente, então 404 com a mensagem do contrato,
      citando as raízes consultadas.
- [ ] Dada uma projeção com mais arestas que o limite, então a resposta
      traz o subconjunto **e** diz que cortou.
- [ ] `?partition=louvain__student_simple` embute o `membership` na
      mesma resposta.
- [ ] A API **não importa** `edugraph.community` nem `edugraph.data` — o
      teste de fronteira continua verde.
- [ ] `edugraph api openapi` gera o esquema que tipa o front.

## Testes exigidos

- **Contrato:** `test_import_boundaries` continua verde.
- **API** (`tests/api/test_api.py`, já escritos como `xfail`): cada rota
  200 sobre a fixture; 404 para inexistente.
- Acrescentar: corte de arestas; embutir partição.

## Arquivos criados ou alterados

- `src/edugraph/api/routes.py` — as cinco rotas.
- `src/edugraph/api/schemas.py` — ajustar se preciso (com o front junto).
- `tests/api/test_api.py` — remover os `xfail`.

## Impacto no artigo

Nenhum diretamente. Habilita a C-05, de onde saem as capturas do capítulo
3.
