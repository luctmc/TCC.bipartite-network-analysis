# [C-05] Front-end: grafo interativo com cor por comunidade

**Frente:** C
**Dono:** Lucas
**Status:** não iniciada

## Objetivo

Entregar a visualização interativa: grafo com cor por comunidade, tamanho
por centralidade e filtros por projeção.

## Contexto

**Cumpre:** a visualização.
**Consome:** a API (C-04).

React + Vite + Cytoscape.js (decisão **D3**, ADR-0005). O grupo escolheu
esta stack em vez da página estática recomendada no plano porque a defesa
é uma apresentação, e transições controladas melhoram a legibilidade do
que está sendo mostrado na banca.

**Requisito de máquina:** Node.js 18+.

## Dependências

- C-04, para as rotas de dados.
- **Neutralizada por:** o esqueleto do dia 0 já conecta em `/health` e
  `/datasets`, monta os seletores e trata o 501 da rota de projeção com
  um estado explícito ("aguardando C-04"). Dá para adiantar layout,
  estilo e interações com dados de exemplo.

## Escopo

### Incluído

- Cor por comunidade, com **escala qualitativa acessível** — precisa
  distinguir também em escala de cinza, porque as capturas podem ser
  impressas.
- Tamanho do nó por centralidade, com seletor de métrica.
- Seletor de partição (`communities/` disponíveis no dataset).
- Painel do nó selecionado: vizinhos, comunidade, scores das três
  métricas.
- Transição entre projeções preservando a posição dos nós comuns.
- Aviso quando o grafo passa de `MAX_EDGES_CONFORTAVEL` (3.000).

### Fora de escopo

- Edição de dados: a API é somente leitura.
- Exportação de figura pelo front — as figuras do artigo saem de
  `reporting/figures.py`, que garante estilo e resolução consistentes.
  Capturas de tela da interface são material **complementar**, não
  substituto.

## Critérios de aceite

- [ ] Dado `synthetic_v1`, quando abrir, então o grafo aparece com os
      nós coloridos pela partição escolhida.
- [ ] Dado um seletor de métrica, quando trocar, então o tamanho dos nós
      muda com transição, sem recarregar a página.
- [ ] Dado um nó clicado, então o painel mostra comunidade, grau,
      intermediação e autovetor daquele nó.
- [ ] Dado um grafo acima do limite, então o aviso aparece e a interface
      continua utilizável.
- [ ] `npm run build` gera `src/edugraph/api/static/` e
      `python -m edugraph api serve` passa a servir a interface em `/`.
- [ ] `npm run typecheck` passa — o front é tipado contra os schemas da
      API.
- [ ] As cores distinguem comunidades em escala de cinza.

## Testes exigidos

- **Manual, documentado:** roteiro de verificação em `frontend/README.md`
  (abrir, trocar dataset, trocar projeção, clicar num nó).
- **Automatizado:** `npm run typecheck` na CI do front, se o grupo
  decidir criá-la. Teste de interface com navegador **não paga** o custo
  num TCC de três pessoas — registrar essa decisão é melhor do que
  fingir que ela não foi tomada.

## Arquivos criados ou alterados

- `frontend/src/components/GraphView.tsx` — os `TODO C-05`.
- `frontend/src/App.tsx` — seletores de partição e métrica.
- `frontend/src/components/NodePanel.tsx` (novo).
- `frontend/README.md` — roteiro de verificação.

## Impacto no artigo

**Capturas de tela do capítulo 3.** A escolha da stack vale uma frase na
seção de ferramentas — visualização é meio, não resultado.
