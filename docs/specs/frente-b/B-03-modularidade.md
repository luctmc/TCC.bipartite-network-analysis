# [B-03] Modularidade Q implementada à mão

**Frente:** B
**Dono:** Gabriel
**Status:** não iniciada

## Objetivo

Implementar a modularidade Q sem usar `nx.community.modularity`, e
comparar as duas.

## Contexto

**Cumpre:** nada em disco — alimenta `Partition.modularity`.
**Consome:** `ProjectionBundle`, `Partition`.

Segunda implementação à mão do projeto (ADR-0010), ao lado da projeção
(A) e da iteração de potência (C).

Q = (1/2m) Σᵢⱼ (Aᵢⱼ − kᵢkⱼ/2m) δ(cᵢ, cⱼ). Em grafo ponderado, Aᵢⱼ é o
peso, kᵢ a força do nó e m metade da soma de todos os pesos.

## Dependências

- Nenhuma de outra frente: as fixtures trazem projeções **e** partições
  de referência.

## Escopo

### Incluído

- `modularity(graph, membership, weight, resolution)`.
- **Usar a forma fechada por comunidade**, `Q = Σ_c (m_c/m − γ(K_c/2m)²)`,
  que é O(m). A forma ingênua O(n²) pode ficar nos testes, sobre
  `tiny_v1`, como verificação cruzada.
- `compare_with_networkx()` — os dois valores e a diferença.
- `densify()` — renumeração determinística para `0..k-1`, usada pela
  B-01 e pela B-02.

### Fora de escopo

- Modularidade para grafos bipartidos (Barber) — o trabalho calcula Q
  sobre as **projeções**, não sobre o bipartido.
- Modularidade dirigida.

## Critérios de aceite

- [ ] Dada a partição trivial (tudo numa comunidade), então Q = 0.
- [ ] Dada a partição de referência de `synthetic_v1`, então o Q à mão
      difere do NetworkX em menos de 1e-9.
- [ ] Dado o mesmo grafo com e sem peso, então os valores diferem e
      ambos estão em [−0,5, 1].
- [ ] Dada uma partição com ids esparsos, então `densify` devolve
      `0..k-1` preservando os agrupamentos, de forma determinística.
- [ ] Dado um grafo de 100 mil arestas, então o cálculo termina em tempo
      linear — **medir**, para provar que a forma fechada foi usada.

## Testes exigidos

- **Unitários** (já escritos como `xfail`): Q da partição trivial é zero;
  Q à mão bate com o NetworkX.
- Acrescentar: forma fechada = forma ingênua sobre `tiny_v1`;
  determinismo de `densify`.

## Arquivos criados ou alterados

- `src/edugraph/community/modularity.py`.
- `tests/community/test_modularidade.py` (novo, ou estender
  `test_louvain.py`).

## Impacto no artigo

**Algoritmo implementado à mão** — descrição do método na Fundamentação e
tabela de validação contra o NetworkX.
