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

- **Atualização:** auditoria de 20/10/2026 confirmou que os três TOMLs
  OULAD (`configs/oulad_cohort_bbb_2013j.toml:11`,
  `configs/oulad_module_presentation.toml:14` e
  `configs/oulad_vle_bbb_2013j.toml:18`) já têm
  `stages = ["data", "community", "centrality"]`: a falta registrada é
  só de execução, não de configuração. A execução real não é verificável
  nesta máquina, sem dados brutos OULAD nem `data/processed`.

### T-OBS-02 · Pipeline mistura rodadas quando a raiz antiga precede a saída

- **De:** auditoria AUD-01 · **Data:** 20/10/2026
- **Onde:** `src/edugraph/__main__.py:128`,
  `src/edugraph/__main__.py:141`,
  `src/edugraph/community/stage.py:63` e
  `src/edugraph/centrality/stage.py:110`.
- **O quê:** com `--root` diferente de `--out` e o mesmo dataset nas duas
  raízes, A grava uma nova rodada em `--out`, mas B e C resolvem artefatos
  por `[*roots, out]` e leem primeiro a raiz antiga. Na AUD-01b, uma cópia
  temporária do TOML sintético com dataset `tiny_v1`, só Louvain e degree,
  executada por `python -m edugraph run <config-temporária> --root
  <cópia-das-fixtures> --out <saída-temporária>` terminou com exit 0.
  Porém, `python -m edugraph validate --root <saída-temporária>` falhou
  (exit 1): `membership cobre 3 nós, mas a projeção
  'discipline_resource_allocation' tem 7`. A reprodução isolando os
  estágios A e C também mostrou `A output nodes=98; C output scores=6;
  same nodes=False`. O pipeline com leitura e escrita na mesma raiz passou;
  a quebra exige a colisão entre raiz antiga e saída distinta.
- **Como resolver:** o runner deve promover a saída da etapa executada à
  primeira raiz das etapas seguintes, preservando a precedência esperada
  de execuções isoladas; acrescentar teste de colisão de dataset entre
  entrada antiga e saída regenerada. O runner é arquivo compartilhado:
  a alteração exige aprovação dos três. B e C devem revisar em conjunto
  a resolução de raízes; não mudar o contrato congelado para contornar
  o problema.

## Resolvidas

### T-OBS-03 · Informativo: CI do frontend executa lint e testes

- **De:** correção FIX-C2, sessão do Lucas · **Data:** 20/10/2026
- **Onde:** `.github/workflows/ci.yml:96` e `frontend/package.json:14`.
- **O quê:** o job do frontend usa o lockfile como chave de cache e
  instala por `npm ci`; além de tipos e build, passa a executar
  `npm run lint` e `npm test`. A sequência local
  `npm ci && npm run lint && npm test && npm run build` passou, com
  seis testes do cliente. O caráter informativo do job foi preservado.
- **Como resolver:** aviso ao grupo; manter o lockfile e os testes do
  frontend atualizados nas próximas alterações.
- **Resolvida:** 20/10/2026 por Lucas, branch c/pendencias-frente-c —
  CI atualizada e comandos verificados localmente; item informativo.
