# `frontend/` — visualização interativa  `[C]`

React + Vite + Cytoscape.js (decisão **D3**, registrada na ADR-0005).
Consome a API somente leitura do FastAPI e é compilado para
`src/edugraph/api/static/`, de onde o próprio FastAPI o serve em `/`.

## Requisitos

**Node.js 18 ou superior** (Vite 5 não roda em versões anteriores).
Confira com `node --version`; se estiver abaixo, instale o LTS atual —
versões anteriores à 18 estão sem suporte de segurança.

## Comandos

```bash
cd frontend
npm install

npm run dev        # servidor de desenvolvimento em :5173, com proxy para :8000
npm run build      # compila para ../src/edugraph/api/static/
npm run typecheck  # tsc sem emitir
```

Em desenvolvimento, suba os dois:

```bash
python -m edugraph api serve --root data/fixtures   # terminal 1
npm run dev                                          # terminal 2
```

O Vite encaminha `/health`, `/datasets` e `/openapi.json` para a API, de
modo que o front usa caminhos relativos nos dois modos e não precisa
saber onde está rodando.

## O que já existe, e o que é a spec C-05

Esta pasta é **esqueleto**, como o resto do repositório: a implementação
da visualização é a spec C-05.

**Pronto (dia 0)**

- Cliente da API tipado (`src/api.ts`, `src/types.ts`), espelhando os
  schemas pydantic de `edugraph/api/schemas.py`.
- Seletores de dataset e de projeção montados a partir de `/datasets` —
  nenhum nome de dataset fica embutido no código, então o OULAD aparece
  sozinho quando a Frente A o gravar em `data/processed`.
- Ciclo de vida do Cytoscape dentro do React sem vazamento, layout fcose
  e estilo base (`src/components/GraphView.tsx`).
- Tema escuro e transições entre estados (`framer-motion`), pensados para
  projetor.
- Estado explícito para rota ainda não implementada: enquanto a C-04 não
  fecha, a interface diz "aguardando C-04" em vez de mostrar erro.

**Spec C-05 (marcado com `TODO C-05` no código)**

- Cor por comunidade, com escala qualitativa acessível.
- Tamanho do nó por centralidade, com seletor de métrica.
- Painel do nó selecionado (vizinhos, comunidade, scores).
- Transições entre projeções preservando a posição dos nós comuns.

## Limite de escala

`MAX_EDGES_CONFORTAVEL` em `GraphView.tsx` é 3.000. Acima disso o
navegador engasga e a figura deixa de comunicar. O corte é
responsabilidade da API (spec C-04, com `min_weight` da spec A-06); o
componente confia no que recebe, mas avisa quando o número passa.
