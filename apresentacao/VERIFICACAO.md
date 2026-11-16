# Relatório de verificação da apresentação

Revisão de 16/11/2026, numa cópia limpa do repositório no commit `2ff819b`
(Linux, Python 3.13, Node 22.23, Chromium do Playwright), com o sistema
servido sobre `data/fixtures`.

## 1. Estrutura de TCC

A apresentação segue a estrutura da defesa e do artigo: sumário;
**1 Introdução** (contextualização, problema de pesquisa, justificativa,
objetivo geral e específicos); **2 Fundamentação teórica** (bipartido,
projeção, comunidades e modularidade, Louvain × Girvan–Newman,
centralidade); **3 Metodologia** (caracterização, bases, critérios de
avaliação, etapas); **4 Desenvolvimento** (como o trabalho foi conduzido,
arquitetura, o sistema, dados da demonstração, demonstração ao vivo);
**5 Resultados e discussão**; **6 Considerações finais** (conclusões,
limitações e trabalhos futuros); referências; encerramento. São 34 slides
principais (com seis aberturas de capítulo) para 15–20 min e 15 de
apêndice técnico para as perguntas.

ABNT: citações autor-data pela NBR 10520:2023 (sobrenome em maiúsculas e
minúsculas dentro dos parênteses, “;” entre autores, *et al.* acima de
três) e referências pela NBR 6023:2018. Slides não têm norma ABNT própria
de formatação; a norma vale para citar e referenciar.

**A conferir pelo grupo:** (1) o enunciado do problema de pesquisa foi
derivado do objetivo da Introdução aprovada (`docs/briefing.md`, seção 1);
(2) a caracterização “aplicada, quantitativa, experimental computacional”
descreve o que o repositório faz; (3) a lista de referências deve bater com
a do artigo. As três estão marcadas nas notas dos slides.

## 2. Conferência do conteúdo contra o código

Cada afirmação dos slides principais foi conferida na fonte indicada.

| Afirmação | Fonte conferida | Situação |
|---|---|---|
| `nodes.csv` com 3 colunas; desfecho só em `outcomes.csv`, lido por `evaluate.py` | fixtures, `tests/contract/test_outcomes_isolation.py` | ok |
| `test_no_ml.py` barra sklearn, torch, tensorflow (e outras 14) | `tests/contract/test_no_ml.py` | ok |
| Q pela forma fechada, γ = 1 | `community/modularity.py` | ok |
| Louvain registrado usa python-louvain; o do laboratório tem rastro e é conferido | `community/louvain.py`, `POST /lab/run` (`same_partition: true`) | ok |
| Turma: 43 alunos, 8 disciplinas, 93 matrículas, 337 ligações; Louvain Q 0,528, 41 movimentos, 3 grupos, pureza 1,00; GN Q 0,488, 3 grupos, pureza 0,93 | `POST /lab/run` (semente 12, 45 alunos, mistura 20%) | ok |
| Mistura 50%: GN fragmenta em 7 grupos, Louvain mantém 3 | `POST /lab/run` | ok |
| Cada aluno cursa 2 ou 3 disciplinas da área; 30% “em risco” com notas menores; matrícula vale com média ≥ 50 | `data/synthetic.py` (`randint(2, min(4, …))`, `risk_rate = 0.30`), `lab/demo.py` (`THRESHOLD = 50`) | ok |
| Limites do laboratório: 24–75 alunos, 4.000 ligações, 1.500 no GN, até 60 s | `lab/demo.py`, `lab/service.py`, `api/lab_routes.py` | ok |
| Exemplo da fundamentação: 6 alunos, 3 disciplinas, 10 matrículas (notas 61–90); pesos simples 2/1 e por alocação 0,58/0,33/0,25 | `data/fixtures/tiny_v1` (`bipartite/`, `expected/`) | ok — lido de `js/dados.js` |
| Louvain no exemplo: 4 movimentos (4→5, 2→1, 3→1, 6→1), *Q* −0,132 → 0,111, 2 grupos | `edugraph.lab.trace.louvain_trace(seed=42)` sobre `tiny_v1/student_simple` | ok — rastro real |
| Girvan–Newman no exemplo: 1ª ponte 3–4, depois 3–5; melhor corte k = 2, *Q* 0,111 | `girvan_newman_trace` sobre o mesmo grafo | ok — rastro real |
| Centralidades do exemplo: grau 3 = 1,00; intermediação só o 3 = 0,60; autovetor 0,56/0,52/0,33/0,15 | `tiny_v1/expected/student_simple.centrality.csv` e implementações da Frente C | ok |
| Rede da capa: 98 alunos, 1.971 ligações (438 no esqueleto k = 5), comunidades de 39/30/29, *Q* 0,4666 | `GET /datasets/synthetic_v1/projections/student_simple` e `louvain__student_simple/meta.json` | ok |
| Réplicas nulas: *Q* = 0,2198 · 0,2159 · 0,2280 · 0,1876 · 0,1883; média 0,2079 ± 0,0168; z = +15,4; réplica 1 com 2.360 ligações | `null_replicas(synthetic_v1, n=5, seed=0)` + `SimpleProjection` + Louvain (semente 42), em `gerar_dados.py` | ok — reproduzido |
| Caminho de um clique: API → `lab` → registro (`PROJECTIONS`, `COMMUNITIES`, `CENTRALITIES`); resposta em ≈ 0,13 s | `api/lab_routes.py`, `lab/service.py`; `timing.total_s` de `POST /lab/run` | ok (tempo depende da máquina) |
| Equipe e RA: Gabriel Luís Lopes (2300873), Pedro Alexandre dos Santos Chaves (2301503), Lucas Timponi Mercadante Castro (2304913) | nomes: `README.md`, `pyproject.toml`; RA informados pelo grupo | ok |
| Arestas do bipartido em `source, target, weight` | `data/fixtures/*/bipartite/edges.csv` | **corrigido** (antes dizia `student, discipline`) |
| Q 0,467 real × 0,208 ± 0,017 nulo, z ≈ +15 | **reproduzido**: 5 réplicas de `null_replicas(seed=0)`, Louvain semente 42, desvio populacional → 0,4666 × 0,2079 ± 0,0168, z = +15,4 | ok (ver B-OBS-03) |
| NMI 0,819, pureza 0,949; GN 34,4 s × 0,024 s (1.453×); v2: pureza 0,864, NMI 0,495 | `docs/artigo/decisoes-metodologicas.md` (B-01 a B-07) | documentado, não reexecutado |
| OULAD: Q 0,773 × 0,781 (amostra de 3.000); AVA 0,083/0,074/0,051 × 0,016/0,008/0,007 | idem (A-08 e critério do AVA) | documentado; exige `data/processed/` |
| Quartis do autovetor 89,3 / 52,6 / 18,4 / 10,5%, base 42,7% | `results/tables/tab8b-desfecho-faixa-oulad_vle_bbb_2013j-eigenvector.csv` | ok |
| «Pouco engajados» 69% × 7% | `docs/orientador/estudo-apresentacao-11-2026.md`, seção 5 | documentado; exige o ZIP do OULAD |
| Spearman 0,84 / 0,53 / 0,21; só na intermediação: FFF_2014B, FFF_2013J, BBB_2014J | `results/tables/tab7-discordancia-*.csv` | ok |
| Linha do tempo (17/09 → 04/11/2026), 16 PRs, 23 specs, 14 ADRs | `git log`, `docs/specs/`, `docs/adr/` | ok |
| 428 testes Python (1 pulado) e 32 da interface | `pytest`, `npm test` | ok |

## 3. Mudanças no sistema

- **Tour** (`frontend/src/tour/Tour.tsx`, `frontend/src/styles.css`):
  véu mais claro com anel e halo no alvo, balão com marca, “Passo n de 9”,
  barra de progresso, títulos maiores, botões em pílula e entrada suave a
  cada passo. Textos, passos, teclado e lógica não mudaram.
- **C-OBS-15 resolvida:** a etapa ativa do laboratório não perde mais o
  rótulo sob o mouse (`:not(.ativa)` no hover).
- **C-OBS-16 resolvida:** `npm test` passou a ser `node --test`, que acha
  os testes no Node 20 e no 22.

## 4. O que foi testado

| Verificação | Resultado |
|---|---|
| `pytest -m "not slow"` · `ruff check .` · `ruff format --check .` | 427 passaram, 1 pulado; sem erros (inclui `apresentacao/`) |
| `npm run typecheck` · `npm run lint` · `npm test` · `npm run build` | sem erros; 32 testes passaram |
| Render de todos os slides em 1920 × 1080, no passo final | sem sobreposição nem corte |
| Navegação, passos, visão geral, notas, apêndice, versão curta | corretos |
| Demonstração ao vivo: entrar, avançar o tour, sair | ok; tour novo visível na janela |
| Reserva com o sistema desligado | capturas rotuladas; a legenda da figura também avisa |
| Modo apresentador com e sem a janela da plateia | ok |
| Desempenho das animações (Chromium headless, 1920 × 1080) | 60 quadros/s na abertura e nas três sequências; pior quadro ≤ 33 ms |
| Transições (ida e volta, capítulos) | conferidas em captura durante a transição |
| Console do navegador | nenhum erro |

## 5. O que não foi testado

- Projetor real, Safari e Firefox, e o `servir.py` subindo a API no Windows.
- Números do OULAD inteiro: vêm dos documentos do grupo, porque
  `data/processed/` não está no repositório.
