# Decisões metodológicas — o que precisa estar no texto

O briefing (§9) trata rastreabilidade como requisito funcional: cada
escolha não-óbvia precisa estar registrada, porque vira parágrafo de
justificativa e **pergunta de banca**.

Este documento é a lista de coisas que o artigo precisa dizer, e onde
cada uma está resolvida no repositório. Ele é atualizado conforme as
specs fecham.

## Já decididas

### A restrição de não usar IA/ML

**O que dizer.** Nenhum componente usa aprendizado de máquina. Louvain e
Girvan-Newman são otimização combinatória e remoção iterativa de arestas
sobre a estrutura do grafo: não há treino, não há rótulo de entrada, e o
resultado é rastreável até as arestas.

NMI, pureza e correlação de Spearman, usados na validação, são medidas de
teoria da informação e estatística descritiva **entre partições e
categorias já conhecidas** — nenhuma delas treina nada.

**Onde está garantido.** ADR-0008; `tests/contract/test_no_ml.py` varre o
código e as dependências declaradas.

### Rótulos históricos fora do grafo

**O que dizer.** O desfecho de cada matrícula entra **apenas** na
validação a posteriori. Ele vive em `outcomes.csv`, separado do grafo, e
só módulos `evaluate.py` podem lê-lo.

**Onde está garantido.** ADR-0008;
`tests/contract/test_outcomes_isolation.py`.

### A ressalva do critério `final_result_pass`

**O que dizer — e é preciso dizer.** Uma das configurações de aresta
(`final_result_pass`) usa o desfecho para decidir se a aresta existe.
Isso não é um algoritmo inferindo a partir do rótulo: é uma **definição
declarada de aresta**, registrada em `BipartiteSpec` e visível no
`meta.json` do artefato.

A distinção é sutil, e a banca vai perguntar. Se o grupo preferir não se
expor à discussão, a alternativa é usar só `score_threshold` e
`vle_activity` e citar `final_result_pass` como configuração considerada
e descartada — o que também é uma resposta defensável.

**Onde está.** ADR-0007.

### Granularidade do nó disciplina (decisão D1)

**O que dizer.** O OULAD tem só 7 módulos. Com V = módulo, a projeção
disciplina↔disciplina degenera: qualquer par de disciplinas compartilha
algum aluno, o grafo vira completo, toda intermediação é zero e não há
gargalo a identificar.

**Isto foi verificado empiricamente, antes do OULAD.** Na fixture
`synthetic_v1`, `discipline_simple` tem 7 nós e 21 arestas — K₇ exato.
Registrado em `data/fixtures/synthetic_v1/REFERENCE.md`.

A saída é granularidade mais fina: `module_presentation` (22 nós) como
padrão, com `module` (7) como comparação, e `assessment` para as análises
por coorte. A comparação entre granularidades **é resultado**, não
detalhe de implementação.

**A base real, medida em 18/09/2026 — e a previsão estava meio errada.**
Com V = módulo, `discipline_simple` tem **12 de 21 arestas (57%)**, não o
grafo completo que a D1 previa: 91,8% dos alunos do OULAD cursam **um
único módulo**, e essa esparsidade impede a completude. Com V =
`module_presentation`, são **93 de 231 (40%)**. Em nenhuma das duas a
projeção disciplina↔disciplina degenera — a intermediação discrimina, e é
a configuração recomendada para a spec C-03.

O problema real de V = módulo é **do outro lado**: a projeção aluno↔aluno
daria ~52 milhões de pares (15,9 milhões com `module_presentation`), e
não cabe em memória. A decisão D1 acertou o diagnóstico — V = módulo é
inadequado — pela razão oposta à que supunha.

**Segundo achado, da spec A-01: a degeneração depende também da
esparsidade.** `synthetic_v2` tem os mesmos 7 módulos e a mesma seed de
`synthetic_v1`, mas 70% dos alunos reduzidos a uma única matrícula — o
perfil do OULAD. Nela, `discipline_simple` tem **16 de 21 arestas**: não
é mais completa, e a intermediação passa a discriminar. Isso muda o que
o texto deve dizer: com V = módulo, a projeção disciplina↔disciplina é
completa quando os alunos cursam muitas disciplinas (`synthetic_v1`) e
deixa de ser quando cursam poucas (`synthetic_v2`, OULAD). No OULAD real
as duas forças atuam: poucos módulos *e* poucas matrículas por aluno. O
número real só a A-02/A-06 dirão.

**Onde está.** ADR-0007; `configs/`;
`data/fixtures/synthetic_v2/REFERENCE.md`.

### Girvan-Newman e o orçamento de tempo

**O que dizer.** O algoritmo é O(m²n) e não termina sobre a base
completa. O trabalho o executa com orçamento de tempo declarado e
reporta, para cada configuração, se ela terminou (`status`). O custo
relativo ao Louvain é um resultado medido, não uma citação de notação
assintótica.

**Onde está.** ADR-0006; coluna `status` em `metrics/communities.csv`.

### Determinismo

**O que dizer.** Toda execução estocástica tem semente fixa, gravada no
artefato. Mesma configuração, mesmo resultado.

**A ressalva honesta:** um resultado que só vale para a seed 42 não é
resultado. Os testes usam faixas, não igualdade exata, e onde a
estabilidade importa (os valores de `tiny_v1`) os esperados foram
derivados no papel, não copiados da biblioteca.

**Onde está.** ADR-0011.

### Implementações à mão

**O que dizer.** Três algoritmos foram implementados sem usar a
biblioteca, e cada um é comparado numericamente com a implementação do
NetworkX: as projeções (A-04/A-05), a modularidade Q (B-03) e a
centralidade de autovetor por iteração de potência (C-02).

Brandes (intermediação) e Louvain **não** foram implementados à mão, e a
razão é registrável: custo alto e retorno didático baixo perto das outras
três.

**Onde está.** ADR-0010.

### Nós isolados removidos do bipartido

**O que dizer.** Alunos que não satisfazem o critério de aresta em
disciplina nenhuma viram nós de grau zero e são removidos. Em
`synthetic_v1`, o gerador produz 120 alunos e o bipartido tem 98.

**Consequência a reportar:** o starter kit relata ~25 comunidades; a
fixture tem 3. As ~22 extras eram esses nós isolados, cada um virando
comunidade de tamanho 1. Ao reportar `k` no artigo, **dizer quantas
comunidades são unitárias** — um `k` alto de singletons diz algo muito
diferente de um `k` alto de grupos reais.

### Agregação por (aluno, disciplina) — decidida na A-03

**O que dizer.** Quando um aluno tem mais de uma matrícula na mesma
disciplina (repetiu o módulo em outra apresentação e a granularidade é
`module`), as linhas são agregadas assim: **média** da nota, **soma** dos
cliques no AVA, e aprovado se **alguma** das matrículas foi `Pass` ou
`Distinction`. O peso da aresta é a grandeza que o critério de aresta
olhou — nota média, cliques ou 1,0 — e as projeções o ignoram: usam só a
existência da aresta.

**Onde está.** `edugraph.data.bipartite.normalize_table`;
`meta.stats["n_isolated_removed"]` registra quantos alunos saíram por não
satisfazer o critério em disciplina nenhuma (22 dos 120 em `synthetic_v1`).

### A referência NetworkX para a alocação de recursos — decidida na A-05

**O que dizer.** A projeção simples é comparada com
`nx.bipartite.weighted_projected_graph`, que é exatamente a contagem de
vizinhos em comum. Para a alocação de recursos **não existe função
pronta no NetworkX**: `collaboration_weighted_projected_graph` é a
ponderação de Newman (2001), em que cada vizinho comum contribui
`1/(grau − 1)`, e **não** a de Zhou et al. (2007), que contribui
`1/grau`. Em `tiny_v1` a disciplina DA (grau 4) contribui 1/3 por Newman
e 1/4 por Zhou — as duas divergem em toda aresta, e um teste garante que
isso continua sendo verdade.

A referência usada é `generic_weighted_projected_graph` com a fórmula de
Zhou fornecida por nós: a biblioteca faz a projeção (interseção de
vizinhanças, nós, atributos) e nós damos só o peso. É a comparação mais
independente possível, e o texto deve dizer isso em vez de afirmar que
"o NetworkX implementa a alocação de recursos".

**Resultado.** Nas quatro projeções de `synthetic_v1` (98 nós, 1.971
arestas), a implementação à mão e a referência concordam com diferença
máxima abaixo de 1e-9. Tabela em `metrics/projections.csv`.

**Na base real** (coorte BBB_2013J, 1.706 alunos, **1.449.841 arestas**),
as duas continuam concordando (diferença máxima 1,7e-18) e a
implementação à mão é **mais rápida**: 5,2 s contra 9,5 s do NetworkX na
projeção simples, e 5,2 s contra 22,5 s na alocação de recursos — porque
a referência precisa chamar a função de peso por par, enquanto a nossa
acumula num único percurso. É um número citável: a implementação didática
não custa desempenho.

**Onde está.** `edugraph.data.projection.networkx_ref`; ADR-0010.

### As três regras do ETL do OULAD — decididas na A-02

**O que dizer.**

1. **Nota da matrícula = média ponderada pelo `weight` da avaliação.**
   No OULAD as avaliações contínuas (TMA/CMA) somam 100 e o exame vale
   100 à parte; a média simples daria peso igual a um teste de 5% e ao
   exame. Quando todos os pesos das avaliações entregues são zero (só
   CMAs sem peso), a nota é a média simples, e a linha fica marcada
   (`score_weighted = false`) para que o texto possa dizer quantas são.
2. **Matrícula sem nota e sem clique no AVA é descartada.** Não há
   evidência de participação; ela não geraria aresta em critério nenhum.
   Reportar quantas foram descartadas.
3. **Um desfecho por aluno = o da apresentação mais recente**; empate na
   mesma apresentação, o módulo de código maior. É o "estado final" do
   aluno na base. A regra de desempate é arbitrária e por isso está
   escrita; alternativas (qualquer aprovação; o pior desfecho) mudariam
   a tabela de validação da B-06 e devem ser citadas como sensibilidade.

**O que o ETL não lê, de propósito.** Gênero, região, faixa etária,
escolaridade, IMD e deficiência de `studentInfo` não entram em
`usecols`. A forma mais segura de não vazar um atributo demográfico para
o grafo (ADR-0008) é não carregá-lo.

**Onde está.** `edugraph.data.oulad.etl` (docstring do módulo);
`edugraph.data.oulad.schema.SCHEMAS`; testes em `tests/data/test_etl.py`
sobre `oulad_mini`.

### Reduções de escala — decididas na A-06, números pendentes do OULAD

**O que dizer.** O Girvan-Newman é O(m²n) e a projeção aluno↔aluno de
uma coorte real chega a milhões de arestas. O trabalho usa quatro
reduções, sempre declaradas e sempre gravadas no artefato
(`meta.stats["reductions"]`, com parâmetros e contagens) — o texto pode
dizer, para cada tabela, exatamente sobre que recorte ela foi calculada:

1. **Coorte** (`BipartiteSpec.cohort` ou `edugraph data cohort`): uma
   apresentação de módulo. É a redução preferida, porque recorta por uma
   unidade com sentido pedagógico — uma turma — e não por conveniência.
2. **Corte por peso mínimo** (`ProjectionSpec.min_weight`): remove
   arestas fracas da projeção; não muda o conjunto de nós; o validador
   confere que foi aplicado.
3. **Amostra de alunos** com semente fixa (`sample_students`): muda quem
   está no grafo; reproduzível pela semente registrada.
4. **Núcleo-k** da projeção (`k_core`): muda a topologia de propósito;
   a partição ou centralidade calculada depois vale só para o núcleo, e
   o número de nós removidos é reportado.

**O que ainda falta e depende do download do OULAD (passo manual):** o
tamanho real de cada coorte, o tempo e o pico de memória da rodada
completa, e a escolha dos valores de `min_weight`, `sample_students` e
`k_core` para as configurações de `configs/`. Esses números viram a
seção de limitações do artigo, e a spec A-06 fica aberta até lá.

**Onde está.** `edugraph.data.scale`; `[source]` dos TOML de `configs/`.

### Q precisa de linha de base — o achado da A-08

**O que dizer, e é o mais importante desta rodada.** A modularidade
encontra "comunidades" em qualquer grafo esparso, inclusive em grafos sem
estrutura nenhuma (Guimerà et al., 2004). Por isso o trabalho compara todo
Q com o de **réplicas nulas**: os mesmos alunos, as mesmas disciplinas, os
mesmos graus, mas quem cursou o quê é sorteado.

Medido em 18/09/2026, projeção aluno↔aluno, Louvain com seed 42:

| dataset | Q real | Q nulo | veredito |
|---|---:|---|---|
| `synthetic_v1` | 0,4666 | 0,2079 ± 0,0168 (z = +15,4) | estrutura real |
| `synthetic_v2` | 0,5392 | 0,4611 ± 0,0202 (z = +3,9) | estrutura real, sinal fraco |
| OULAD `module_presentation` (amostra de 3.000) | 0,7728 | 0,7807 / 0,7816 | **indistinguível do acaso** |

Três coisas seguem disso, e todas vão para o texto:

1. **O método funciona.** No sintético, o Q real fica 15 desvios acima do
   nulo. Louvain recupera estrutura plantada — é o que valida o método e
   o que a Conclusão precisa para responder ao objetivo declarado.
2. **O OULAD não sustenta a afirmação.** O Q de 0,77 é *menor* que o das
   réplicas embaralhadas. Escrever "encontramos 15 comunidades de perfis
   de alunos" seria falso. O resultado negativo é o resultado.
3. **A esparsidade infla Q.** O Q nulo de `synthetic_v2` (0,46) é o dobro
   do de `synthetic_v1` (0,21), só por ter 70% dos alunos com uma
   matrícula. É o mesmo mecanismo que produz o 0,78 do OULAD, e explica
   *por que* a base real não discrimina: com grau mediano 1, quase não há
   informação relacional entre alunos.

**O que isso não quer dizer.** Não quer dizer que o OULAD não tenha
estrutura nenhuma — quer dizer que *esta* projeção, *nesta* granularidade,
não tem. Outras configurações (coorte, avaliação, critério de aresta) são
exatamente o que as tabelas comparativas do capítulo 3 existem para
explorar, e cada uma precisa da sua linha de base nula.

**Onde está.** Spec A-08; `edugraph.data.nullmodel`; a comparação é da
spec B-06.

### O critério de aresta muda de matrícula para interação no AVA

**O que dizer.** A seção anterior mostra que o critério "cursou o módulo"
não carrega informação relacional suficiente: 91,8% dos alunos do OULAD
cursam um único módulo, e a projeção aluno↔aluno resultante não se
distingue do acaso. O trabalho **troca o critério de aresta** para a
interação com recursos do ambiente virtual de aprendizagem.

Isto **não é mudança de tema nem de escopo**. O critério de aresta é
parâmetro desde o dia 0: o briefing §8 já listava "participação no AVA"
entre os critérios candidatos, a ADR-0007 o tornou configurável, e
`EdgeCriterion` já contém `vle_activity`. A fundamentação do tema
descreve o bipartido como **"Aluno → Comportamento"** e o peso da aresta
como "interseção de atributos compartilhados" — que é exatamente esta
configuração, e não a de matrícula.

**Por que funciona.** O grau muda de ordem de grandeza:

| nó do lado V | grau mediano do aluno |
|---|---:|
| módulo | 1 |
| módulo × apresentação | 1 |
| recurso do AVA | 40 |
| tipo de atividade | 7 |

Medido em três coortes independentes, projeção por alocação de recursos,
três sementes do Louvain cada:

| coorte | alunos × recursos | Q real | Q nulo | razão |
|---|---|---:|---:|---:|
| BBB 2013J | 1.870 × 320 | 0,0825 | 0,0158 | 5,2× |
| FFF 2013J | 2.098 × 526 | 0,0742 | 0,0081 | 9,2× |
| DDD 2014J | 1.647 × 361 | 0,0511 | 0,0073 | 7,0× |

As partições não são degeneradas: há sempre uma comunidade maior (50% a
69% dos alunos) e duas ou três menores com tamanho caracterizável. O Q é
estável entre sementes (variação na quarta casa decimal). Em DDD 2014J o
número de comunidades oscila entre 3 e 4 conforme a semente, sem alterar
o Q — limitação conhecida do Louvain, registrada como tal.

**Achado de método, e vale por si.** A escolha da ponderação decide se o
sinal aparece. Sob extração de espinha (mantendo só as arestas mais
pesadas), a **contagem simples inverte de lado** e o Q real cai *abaixo*
do nulo em todos os limiares testados; a **alocação de recursos** (Zhou
et al., 2007) se mantém acima em todos. A causa é interpretável: a
contagem simples premia volume de cliques, então as arestas mais pesadas
passam a ligar os alunos mais ativos entre si — efeito de volume, não de
afinidade. A alocação de recursos normaliza pelo grau e desfaz o viés.
Como o briefing exige as duas projeções implementadas à mão, o contraste
é resultado próprio do trabalho.

**O que a configuração antiga continua servindo.** O bipartido por módulo
**não sai do trabalho**. A projeção disciplina↔disciplina dele funciona
(93 de 231 arestas com `module_presentation`, intermediação discrimina) e
continua sendo a base da spec C-03, disciplinas críticas. As duas
configurações convivem em `configs/`, que é precisamente o que a ADR-0007
existe para permitir: uma serve à Frente B, outra à Frente C.

**Ressalvas que o texto precisa carregar.** O Q absoluto é baixo (0,05 a
0,08) — a estrutura é estatisticamente inequívoca, mas fraca. A projeção
fica quase completa (densidade 0,9996), então o sinal está nos **pesos**,
não na presença da aresta. Aplicar limiar fragmenta o grafo em centenas
de componentes de nó isolado, então o recorte honesto é a projeção cheia.

**Onde está.** ADR-0007; spec A-09; `docs/orientador/nota-01-criterio-de-aresta.md`.

### O papel do gerador sintético — e o que ele não deve fazer

**Não se misturam dados sintéticos com dados reais.** Não há aumento de
dados, não há preenchimento de lacunas, não há arestas geradas entrando no
grafo do OULAD. Qualquer número saído de um grafo misto seria ficção, e a
restrição da seção 2 do briefing deixaria de ser verificável.

O gerador agrega de três formas, todas separadas dos dados reais:

1. **Ground truth que o OULAD não tem.** A base real não traz comunidades
   conhecidas. Sem o sintético, não há como afirmar que o método recupera
   estrutura — só que ele produz um número.
2. **Linha de base nula** (A-08), que é o gerador calibrado no real *sem*
   estrutura plantada. É o que transforma um Q num resultado.
3. **Calibração da dificuldade.** `synthetic_v2` mostrou, antes do
   download, que a esparsidade derruba a detectabilidade — o que o OULAD
   depois confirmou.

**Onde está.** Specs A-01 e A-08.

## A decidir nas specs

| Pendência | Spec | Por que importa |
|---|---|---|
| `weight_mode` da intermediação (`none`/`inverse`/`raw`) | C-01 | **muda o ranking**; em NetworkX peso é distância, não afinidade |
| Interpretação do resultado da validação a posteriori | B-06, C-06 | se a relação não aparecer, é achado a reportar, não fracasso |

## O que o artigo não deve afirmar

- Que as comunidades **predizem** evasão. Elas não predizem nada: são
  descrição estrutural, e a relação com o desfecho é verificada depois.
- Que uma disciplina de alta intermediação é "difícil". Ela é
  estruturalmente central; se também é difícil, isso é a pergunta da
  C-06, não a premissa.
- Que os resultados generalizam para outras instituições. O OULAD é uma
  universidade aberta britânica, com perfil de aluno e de currículo
  particulares.
