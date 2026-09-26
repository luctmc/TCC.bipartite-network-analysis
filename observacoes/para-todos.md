# Observações para o grupo

Ver as regras em [`README.md`](README.md). Aqui entra o que envolve mais de
uma frente ou precisa de decisão conjunta.

## Abertas

### T-OBS-01 · `oulad_bbb_2013j` sem comunidades e sem centralidades

- **De:** Lucas (Frente C) · **Data:** 26/09/2026
- **Onde:** `data/processed/oulad_bbb_2013j` (fora do git)
- **O quê:** o dataset da coorte por avaliação (1.706 alunos) foi gerado pela
  Frente A, mas nenhuma frente rodou comunidades nem centralidades nele. No
  front, ele aparece sem cor e sem tamanho. Segundo o README da Frente C, é o
  grafo menor pensado para a comparação Louvain × Girvan-Newman.
- **Como resolver:** a Frente B decide se roda as comunidades
  (`run configs/oulad_cohort_bbb_2013j.toml --only community --root data/processed`)
  e a Frente C roda as centralidades em seguida
  (`--only centrality`). Ou o grupo decide que ele fica de fora.

## Resolvidas

Nenhuma ainda.
