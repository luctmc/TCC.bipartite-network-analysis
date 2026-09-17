# [B-07] Figuras de comunidades

**Frente:** B
**Dono:** Gabriel
**Status:** não iniciada

## Objetivo

Gerar as figuras de comunidades do capítulo 3: o grafo com cor por
comunidade e a distribuição de tamanhos.

## Contexto

**Cumpre:** `results/figures/`.
**Consome:** `Partition`, `ProjectionBundle`.

Briefing §9: refazer uma figura na semana da entrega tem que ser um
comando.

## Dependências

- B-01 e B-02, para ter partições.
- **Neutralizada por:** as partições de referência das fixtures.

## Escopo

### Incluído

- `figure_communities(partition, projection, out, layout)` — cor por
  comunidade.
- **Em grafos grandes, agregar**: um nó por comunidade, área proporcional
  ao tamanho, aresta proporcional ao número de ligações entre
  comunidades. Desenhar dois mil pontos não comunica nada.
- `figure_size_distribution(partitions, out)` — um painel por algoritmo.
- Figura de Q × tempo por algoritmo (alimenta a B-04).
- Estilo comum de `reporting.figures.STYLE`; PNG e SVG.

### Fora de escopo

- Visualização interativa — é a C-05.
- Escolher paleta própria: usar uma escala qualitativa acessível e
  registrar qual.

## Critérios de aceite

- [ ] Dada uma partição de `synthetic_v1`, quando gerar, então saem PNG e
      SVG em `results/figures/`.
- [ ] Dado um grafo com mais de 500 nós, então a figura é agregada e a
      legenda diz isso.
- [ ] Rodar duas vezes produz a mesma figura (layout com seed fixa).
- [ ] As cores distinguem as comunidades também em escala de cinza — o
      artigo pode ser impresso em preto e branco.
- [ ] `docs/artigo/indice-figuras.md` é regenerado e inclui as novas.

## Testes exigidos

- **Unitários:** os dois arquivos são escritos; `community_sizes` sobre
  `tiny_v1` bate com valores à mão.
- Sem teste de aparência.

## Arquivos criados ou alterados

- `src/edugraph/community/report.py`.
- `tests/community/test_figuras.py` (novo).

## Impacto no artigo

**Duas figuras do capítulo 3**: grafo com comunidades e distribuição de
tamanhos.
