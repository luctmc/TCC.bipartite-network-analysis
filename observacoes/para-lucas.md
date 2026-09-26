# Observações para o Lucas — Frente C

Ver as regras em [`README.md`](README.md).

## Abertas

### C-OBS-01 · Decidir se os relatórios internos entram no repositório

- **De:** revisão final (Claude, sessão do Lucas) · **Data:** 26/09/2026
- **Onde:** `results/relatorio-interno-oulad_module_presentation.md` e
  `results/relatorio-interno-oulad_vle_bbb_2013j.md` (fora do git)
- **O quê:** são a saída obrigatória da C-07 e se regeneram idênticos com
  `python -m edugraph centrality report --root data/processed --dataset <ds>`.
  Trazem só agregados de dados públicos, mas cada um diz "uso exclusivamente
  interno", e o repositório é público.
- **Como resolver:** decidir com o grupo; se entrarem, fazer o commit dos
  dois arquivos.

### C-OBS-02 · Figura 9: capturas da interface

- **De:** revisão final (Claude, sessão do Lucas) · **Data:** 26/09/2026
- **Onde:** `docs/artigo/indice-figuras.md` (figura 9, "pendente")
- **O quê:** a C-05 prevê capturas de tela da interface para o capítulo 3,
  com o prefixo `ui-` em `results/figures/`. Nenhuma foi gerada.
- **Como resolver:** capturar as telas do roteiro do `frontend/README.md` e
  regenerar o índice com `python -m edugraph figures --index`.

## Resolvidas

Nenhuma ainda.
