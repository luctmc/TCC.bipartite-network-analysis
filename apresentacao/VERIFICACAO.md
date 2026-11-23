# Relatório de verificação da apresentação

## 0. Ajuste “contexto primeiro” (22/11/2026)

Aplicação do [`PLANO-AJUSTE.md`](PLANO-AJUSTE.md) sobre `main` (`757bb69`),
com o sistema rodado pela `.venv` do projeto e a apresentação aberta no
Chromium do Playwright, a partir do disco (`file://`).

**Estrutura (versão para 15–20 min):** 33 slides principais (6 aberturas
de capítulo) e 26 de apêndice. Do plano, ficaram na fala: `aluno-some`
(opcional), `evasao-inep`, `contexto` reescrito, `ligacao` (com a força da
ligação), `comunidades-ctx` (com os papéis), `atencao-talento`, `solucao`
e `grafo` (com o bipartido). Foram para o apêndice, sem perder conteúdo:
`por-que-comunidade`, `escore-z`, `dicionario`, `bipartido`,
`girvan-newman`, `pipeline`, `sinteticos`, `arquitetura`, `clique`,
`interface` e `desenvolvimento-processo`. `val-sintetico` é opcional
(`--curta`, 31 slides).

**Tempo:** a fala do `ENREDO.md` tem 1.610 palavras, das quais ≈ 1.500
fora a demonstração (`aplicar_enredo.py --contar`): ≈ 11 min a 140
palavras por minuto. Somando os avanços, a espera das animações e ≈ 3 min
de demonstração, a estimativa é **≈ 17 min** (≈ 16 com `--curta`). É
estimativa de papel: o tempo real só o ensaio mede. As notas do
apresentador saem do `ENREDO.md` por `aplicar_enredo.py` (rodar duas
vezes dá o mesmo arquivo).

| Afirmação nova | Como foi conferida | Resultado |
|---|---|---|
| Notas dos seis alunos; média da turma 74 (73,7); 1,67 disciplina por aluno; Carla 68,7 | `gerar_dados.py` → `contexto.alunos`/`turma`, das matrículas de `tiny_v1` | ok |
| Felipe “Risco alto”, risco 0,642, “nota média 66, abaixo da turma (74)” · “pouco ligado ao próprio grupo” | `run_lab(source="tiny_v1", students=6)`; texto lido de `dados.js`, não digitado | ok |
| Diego 0,463 e Elisa 0,483 “Em atenção” | idem; o texto que o sistema escreve para eles **não** é mostrado (T-OBS-06) | ok |
| Carla = “ponte”; os outros cinco “periféricos”; Felipe com o menor vínculo (z = −1,73) | `insight.roles` | ok |
| Turma padrão: 43 alunos, *Q* = 0,528, 3 grupos; 8 risco alto, 4 em atenção, 12 talentos | `run_lab(demo, 45, semente 12, mistura 0,2)` | ok |
| Alice T. (apoio) e Larissa J. (liga grupos): textos | idem; regra fixa: 1º talento com selo `apoio`, 1º com `polimata` | ok |
| 1º da lista de atenção na demonstração: Carla N., “nota média 52…” | idem (`signals.attention[0]`) | ok — é outra pessoa; o aviso está na fala de `sinteticos` e da demo |
| NMI = 1,00 contra as áreas plantadas, na turma padrão | calculado à mão sobre `result.membership` e `reveal.planted.node_area` | ok |
| Louvain ≈ 1 ms × Girvan–Newman ≈ 0,4 s, na turma padrão | `result.runtime_s`: 0,0008 s e 0,386 s (22/11/2026; varia com a máquina) | ok; a tabela do slide passou de “≈ 0,5 s” a “≈ 0,4 s” |
| Pesos 35/35/30, cortes 0,25 e 0,50, talento z ≥ 1 / 1,5, disciplina com ≥ 6 alunos | `src/edugraph/lab/signals.py:45-60` | ok |
| Teste contra o acaso: ≥ 5 réplicas, z ≥ 3 | spec B-06 (`Z_THRESHOLD = 3.0`) | ok |
| Inep: 13% / 29% / 40% / 60%; 39% concluíram, 1% cursando; 65% × 59% | relatório do Inep, Gráf. 15 e 18 (p. 33 e 36), conferido pelo grupo em 20/11/2026 (NARRATIVA, seção 2) | **conferido no relatório, não gerado**; aqui não foi possível abrir o PDF (o site recusa acesso automático). Uma reportagem do Correio Braziliense (23/09/2025) traz os mesmos 65% para o ensino a distância |
| 69% × 7% e 197 / 94% / 43% (Open University) | `docs/orientador/estudo-apresentacao-11-2026.md`, seção 5 | exige o ZIP de resultados do OULAD; não se reproduz só com o repositório |

**Ilustrativo, e avisado na tela:** os nomes e cursos dos seis alunos, a
linha do tempo do slide `aluno-some`, o desenho do motivo 2 de
`por-que-comunidade`, as duas turmas (300 × 15) do slide `forca`, o metrô
genérico do slide `grafo` e o exemplo de conta (média 70, passo 10) do
slide `escore-z`.

**Varreduras do plano (seção 8):** nenhum “exigência do orientador” no
`index.html`; “prevê” só em frase negativa; nenhum “aluno 1…6”,
“disciplina A/B/C” ou “3–4” fora das linhas de fonte; nomes de integrantes
só na capa e no encerramento; siglas (ADS, Inep, OULAD, NMI, AVA) por
extenso na primeira vez ou trocadas por palavras.

**Técnica:** os 59 slides percorridos em todos os passos (com e sem
“reduzir movimento”) sem erro de JavaScript no console (o único aviso é o
da verificação de saúde quando o sistema está desligado, esperado);
`gerar_dados.py` determinístico (duas execuções, mesmo MD5); `ruff check`
e `ruff format --check` limpos.

**Desvios do plano, decididos na aplicação:**

- **Referência do Inep:** o plano a punha entre HAGBERG e KUZILEK, mas pela
  NBR 6023 a entrada começa por “BRASIL.”; ficou logo depois de BRANDES.
- **“Notas finais ficam fora do mapa”** virou “o desfecho do aluno
  (aprovou, reprovou, desistiu) fica fora do mapa”: a nota de cada
  disciplina entra como força da matrícula, e o slide mostra “nota média
  66”. Dita do outro jeito, a banca veria uma contradição.
- **Modularidade:** a regra “acima de 0,3” passou a ser dita como regra
  prática, com a ressalva de que quem decide é o teste contra o acaso (na
  base real, *Q* = 0,77 falha e *Q* = 0,08 passa).
- **Papéis:** a centralidade diz que “espalhar-se para outros grupos” é
  comparado com os colegas do próprio grupo; é o que faz Diego e Elisa,
  com metade das ligações para fora, serem “periféricos”.
- **Demonstração:** a nota pede para **não** revelar sinais × desfecho na
  turma inventada: o gerador sorteia nota e desfecho do mesmo perfil de
  risco (`data/synthetic.py:186-190`), então a coincidência é de
  construção.
- **Solução:** “73% de chance de evadir” virou “tantos por cento”, para
  ninguém tomar o número como resultado.

---

## Revisão anterior (16/11/2026)

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
