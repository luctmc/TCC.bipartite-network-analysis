# Roteiro da defesa — edugraph

Gerado de `index.html` por `gerar_roteiro.py`: **não edite à mão** — edite as
notas (`<aside class="notas">`) de cada slide e rode o script de novo.

34 slides principais e 15 de apêndice.
Marcas: **Fala** é o que dizer; **Ação** é o que fazer (avançar, clicar);
**Se perguntarem** antecipa perguntas da banca.


## Abertura e sumário

### 01 · Abertura

**Ação:** abra nesta tela e espere a animação terminar (≈ 5 s): a marca do edugraph se desfaz na rede real do trabalho.

**Fala:** Boa noite, professores. Somos o Grupo 16 — Gabriel, Pedro e eu, Lucas — e apresentamos o Trabalho de Conclusão de Curso *Análise Topológica e Detecção de Comunidades em Redes Complexas*, orientado pelo professor Clayton Valdo.

A rede que acabou de se formar já é um resultado do trabalho: 98 alunos, ligados pelas disciplinas que têm em comum, e os três grupos que o algoritmo encontrou sozinho. Ao longo da apresentação, vamos mostrar como ela foi construída e o que ela permite concluir.

### 02 · Sumário

**Fala:** A apresentação segue a estrutura do artigo. Começo pela introdução — o contexto, o problema e os objetivos. Depois, a fundamentação teórica, com os quatro conceitos de que o trabalho depende. Em seguida, a metodologia, o desenvolvimento do sistema — com uma demonstração ao vivo — e os resultados. Fecho com as considerações finais.


## 1 · Introdução

### 03 · 1 · Introdução

**Fala:** Começo pela introdução: o contexto, o problema e os objetivos.

### 04 · Contextualização

**Fala:** Toda instituição de ensino registra quem se matriculou em quê, com que nota, e — no ensino a distância — o que cada aluno acessou no ambiente virtual.

**Ação:** avance os três cartões.

Esses registros existem, inclusive em bases públicas, como o OULAD, da Open University. E eles são, por natureza, relações: aluno com disciplina, aluno com recurso. A Ciência de Redes tem ferramentas clássicas para isso: encontrar comunidades e medir quem é central.

Só que, na prática, esses dados costumam ser lidos como planilha — que esconde as relações — ou entregues a modelos preditivos, que podem acertar sem explicar por quê. É desse contraste que nasce o problema da pesquisa.

### 05 · Problema de pesquisa e justificativa

**Fala:** A pergunta que orienta o trabalho é esta: dá para extrair padrões estruturais de dados educacionais — grupos de alunos semelhantes e gargalos no currículo — usando apenas Teoria dos Grafos, sem inteligência artificial, de um jeito que se possa interpretar e verificar?

**Ação:** avance as três justificativas.

Ela se justifica por três razões: para a **gestão pedagógica**, que precisa de grupos que consiga explicar; pela **transparência**, já que tudo é rastreável até as ligações do grafo; e pela **pesquisa**, porque testa se a Ciência de Redes clássica é uma alternativa real aos modelos opacos.

**Observação para o grupo:** esta formulação foi derivada do objetivo da Introdução aprovada (`docs/briefing.md`, seção 1). Se o artigo enuncia o problema com outras palavras, use as do artigo.

### 06 · Objetivos

**Fala:** O objetivo geral está na Introdução já aprovada: projetar e implementar um sistema de análise estrutural que extraia padrões de bases educacionais usando apenas Teoria dos Grafos, sem IA.

**Ação:** avance os quatro objetivos específicos.

Ele se desdobra em quatro objetivos específicos: **modelar** os dados como grafo bipartido; **projetar** esse grafo para medir a força da relação entre alunos; **agrupar** perfis com Louvain e Girvan–Newman; e **medir** centralidade para achar gargalos.

**Ação:** avance a faixa verde.

E a restrição de não usar IA, que foi exigência do orientador, não ficou só no papel: dois testes automáticos quebram a integração contínua se alguém importar uma biblioteca de aprendizado de máquina ou ler o desfecho dos alunos fora da validação.

**Se perguntarem** “NMI e pureza não são de aprendizado de máquina?”: são medidas entre dois agrupamentos já prontos; não treinam nada e foram implementadas à mão.


## 2 · Fundamentação teórica

### 07 · 2 · Fundamentação teórica

**Fala:** Para a fundamentação, vou usar um único exemplo do início ao fim: a fixture `tiny_v1` do repositório — seis alunos e três disciplinas —, o caso de teste que o grupo resolveu no papel para conferir o sistema. Todos os números dos próximos slides são dela.

### 08 · Grafo bipartido

**Fala:** O primeiro conceito é o **grafo bipartido**: dois tipos de ponto — alunos e disciplinas — e uma linha para cada matrícula. Este é o caso de teste do repositório: seis alunos, três disciplinas, dez matrículas.

**Ação:** avance — as matrículas aparecem.

Repare que aluno não se liga diretamente a aluno: a relação entre dois alunos passa pelas disciplinas.

**Ação:** avance — o destaque.

Guardem dois detalhes: o aluno 3 é o único que cursa as três disciplinas; e a disciplina A é a mais cheia, com quatro alunos.

### 09 · Projeção ponderada

**Fala:** A **projeção** tira as disciplinas do desenho e liga diretamente os alunos que têm algo em comum.

**Ação:** avance — a rede se transforma.

No peso simples, contamos as disciplinas em comum: 1 e 2 dividem A e B, peso 2; o aluno 6 só divide A com eles, peso 1.

**Ação:** avance — alocação de recursos.

Na alocação de recursos, de Zhou e colegas, cada disciplina vale um sobre o número de alunos dela. A, com quatro alunos, vale um quarto; B e C, um terço. Por isso as ligações que vêm só de A encolhem para 0,25. Esses valores são os que o grupo conferiu no papel e que os testes exigem do sistema.

### 10 · Comunidades e modularidade

**Fala:** O terceiro conceito é a **comunidade**: um grupo muito ligado por dentro e pouco ligado ao resto. Esta rede é real: os 98 alunos do conjunto sintético de teste, e as cores são os grupos que o Louvain encontrou.

**Ação:** avance — modularidade.

Para dar nota a uma divisão usamos a **modularidade Q**: quanto das ligações fica dentro dos grupos, descontado o que ficaria por acaso.

**Ação:** avance — a escala. Perto de zero, a divisão não é melhor que sortear; acima de 0,3, os grupos são bem definidos. Esta rede tem 0,4666.

**Ação:** avance — o cuidado. Em redes esparsas até um grafo sorteado tem Q alto; por isso comparamos todo Q com redes embaralhadas. Isso vai decidir um resultado importante mais adiante.

### 11 · Louvain

**Fala:** O primeiro algoritmo é o **Louvain**. Pensem numa festa: cada pessoa começa sozinha numa mesa e, uma de cada vez, muda para a mesa vizinha em que a divisão melhora mais.

**Ação:** avance quatro vezes — um movimento por clique.

Primeiro o aluno 4 se junta ao 5; depois o 2 ao 1; o 3 e o 6 vêm em seguida. A cada movimento o Q sobe, até 0,11. Ninguém mais quer mudar: dois grupos.

**Ação:** avance — em escala. Na turma da demonstração, são 41 movimentos, Q de 0,53, em um milésimo de segundo. Esse é o rastro real que o sistema anima — vocês vão ver ao vivo.

### 12 · Girvan–Newman

**Fala:** O segundo algoritmo faz o caminho inverso: o **Girvan–Newman** começa com a rede inteira e vai cortando.

**Ação:** avance — a ponte em vermelho. Ele calcula por qual ligação passam mais caminhos entre todos os pares de alunos: aqui, a 3–4.

**Ação:** avance — a rede se parte. Apaga, recalcula e apaga a 3–5: a rede se divide nos mesmos dois grupos do Louvain.

**Ação:** avance — a curva. Ele continua cortando até o fim e anota o Q de cada corte; o melhor é o primeiro, com dois grupos.

**Ação:** avance — a tabela. Na turma da demonstração os dois chegam aos mesmos três grupos, mas o Girvan–Newman leva centenas de vezes mais tempo, porque recalcula as pontes a cada corte.

**Fonte:** `girvan_newman_trace` sobre `tiny_v1`; tabela por `POST /lab/run` (semente 12).

### 13 · Centralidade

**Fala:** O último conceito é a **centralidade**: quão importante é um aluno na rede. Só que “importante” tem mais de um sentido. O tamanho de cada ponto é o valor da métrica; os valores estão na tabela.

**Ação:** avance três vezes. **Grau**: o 3 se liga a todos. **Intermediação**: só o 3 é ponte — tire o 3 e os alunos 4 e 5 ficam isolados; é o que o objetivo chama de gargalo. **Autovetor**: 1, 2 e 3 quase empatam, porque estão no bloco mais denso.

Mesmo exemplo, três leituras diferentes — e é por isso que, nos resultados, as métricas vão discordar nas disciplinas reais.

**Fonte:** grau e intermediação em `tiny_v1/expected/student_simple.centrality.csv` (derivados no papel); autovetor pela implementação da Frente C.


## 3 · Metodologia

### 14 · 3 · Metodologia

**Fala:** Com os conceitos no lugar, a metodologia: que tipo de pesquisa é, com que dados, e como cada resultado foi avaliado.

### 15 · Caracterização da pesquisa

**Fala:** Metodologicamente, é uma pesquisa **aplicada**, porque produz um sistema; **quantitativa**, porque tudo é avaliado por métricas; e feita por **experimentos computacionais**: cada configuração é um arquivo, com semente fixa, e a mesma execução dá o mesmo resultado.

Usamos duas bases: a **OULAD**, real e pública, e um **gerador sintético** que planta grupos — ou seja, uma base em que sabemos a resposta certa.

**Ação:** avance a tabela.

Cada pergunta de avaliação tem um critério explícito. Para saber se existe estrutura, comparamos o Q com redes sorteadas de mesmo grau e exigimos três desvios acima delas. Para saber se os grupos são os certos, usamos NMI e pureza no sintético. Medimos o custo, cruzamos com o desempenho só no fim e comparamos as implementações à mão com a biblioteca.

**Observação para o grupo:** a classificação (aplicada, quantitativa, experimental) descreve o que o repositório faz; se o artigo usar outra terminologia, alinhe.

### 16 · O método em sequência

**Ação:** a sequência começa sozinha (16 s). K pausa e retoma; J e L voltam e avançam 2 s.

**Fala:** Este é o método inteiro em uma sequência, com o mesmo exemplo de seis alunos. Começa numa planilha de matrículas; cada matrícula vira uma ligação do grafo bipartido; a projeção liga os alunos que dividem disciplinas; o Louvain forma os grupos; e a centralidade aponta o aluno que faz ponte. À direita, as etapas acendem junto com a animação.

As etapas 6 e 7 — a validação, em que o desfecho dos alunos entra só no fim, e a API com a interface — completam o caminho. Cada etapa grava um arquivo que a próxima lê, e um comando roda tudo a partir de um arquivo de configuração: `python -m edugraph run configs/synthetic_v1.toml`.

**Fonte:** fixture `tiny_v1` e rastro real de `edugraph.lab.trace`; a frase final cita os 22.425 alunos de `oulad_module_presentation`.


## 4 · Desenvolvimento

### 17 · 4 · Desenvolvimento

**Fala:** Agora o que foi construído: como o trabalho foi conduzido, a arquitetura do sistema e uma demonstração ao vivo.

### 18 · Como o trabalho foi conduzido

**Fala:** O desenvolvimento durou cerca de sete semanas, com as três frentes trabalhando ao mesmo tempo.

**Ação:** avance a linha do tempo.

No dia zero entraram a arquitetura, os contratos dos dados e fixtures completas — o que permitiu que as frentes não esperassem umas pelas outras. Logo depois vieram os dados, os algoritmos de comunidade, a centralidade e a aplicação. Em outubro, uma auditoria e o redesenho da interface; no começo de novembro, o laboratório ao vivo e a revisão de entrega.

**Ação:** avance os números.

Tudo foi guiado por 23 especificações, com 14 decisões de arquitetura registradas, entrando na branch principal só por pull request com a integração contínua verde.

**Fonte:** histórico do git (109 commits entre 17/09 e 04/11/2026); `docs/specs/`, `docs/adr/`.

### 19 · Arquitetura

**Fala:** A decisão central de arquitetura: as três frentes não se importam no código; elas se comunicam por arquivos em disco, num formato fixo.

**Ação:** avance os quatro passos.

Cada frente é um pacote Python. Os contratos dos dados e fixtures completas entraram no primeiro dia, então ninguém esperou ninguém. A regra é verificada por um teste que falha se aparecer import cruzado. E trocar os dados sintéticos pelo OULAD é trocar um argumento, sem mudar código.

**Se perguntarem** sobre tecnologias: Python com NetworkX nos algoritmos, FastAPI na API, React com Cytoscape.js na interface — detalhes no apêndice (tecla A).

### 20 · Por dentro de um clique

**Ação:** a sequência começa sozinha (15 s); K pausa.

**Fala:** Antes de mostrar o sistema, vale ver o que acontece por trás de um clique. O navegador envia o pedido; a API confere os limites e chama o pacote `lab`. O `lab` não importa as frentes: chama cada uma pelo registro. A Frente A gera a turma e faz a projeção; a Frente B roda o Louvain guardando cada movimento — e a biblioteca oficial confere o resultado; a Frente C calcula as centralidades. Tudo volta numa única resposta, em cerca de 0,13 s, e o navegador transforma o rastro em animação. Ou seja: o que vocês vão ver na demonstração é exatamente o que o algoritmo fez.

**Fontes:** `api/lab_routes.py`, `lab/service.py` (`PROJECTIONS`, `COMMUNITIES`, `CENTRALITIES`); números de `POST /lab/run` com os valores padrão (16/11/2026; o tempo varia com a máquina).

### 21 · A interface

**Fala:** Para quem usa, o sistema tem duas telas: o **Laboratório ao vivo**, que monta uma rede na hora e anima o que o algoritmo fez, e o **Explorar resultados**, com os resultados já calculados sobre as bases completas. A identidade visual é a de uma página de periódico, com cores legíveis para quem tem daltonismo e uma forma para cada grupo.

### 22 · Os dados sintéticos

**Fala:** A demonstração usa uma turma **fictícia** de Computação, gerada na hora: três áreas, oito disciplinas. Cada aluno cursa duas ou três disciplinas da sua área e, com a chance chamada **mistura**, uma de fora.

O ponto importante: a área verdadeira de cada aluno fica **fora do grafo**. No fim, revelamos a resposta e medimos o acerto — algo que a base real não permite.

### 23 · Demonstração ao vivo

**Antes:** a barra da janela deve dizer “Ao vivo · sistema conectado”. Se não, use as capturas e diga que são capturas.

**Ação 1 — Enter.** Faça o tour com a seta → (≈ 1 min), lendo só os títulos.

**Ação 2 — ▶ com Louvain.** “Matrículas: 43 alunos e 8 disciplinas. Projeção: 337 ligações, as grossas dentro das áreas. Algoritmo: o Q sobe ao vivo até 0,53. Resultado: três grupos com nome.”

**Ação 3 — Revelar** as áreas plantadas: “o algoritmo não sabia das áreas e acertou 100% dos alunos.”

**Ação 4 (se houver tempo) — Girvan–Newman:** as pontes somem em vermelho; mesmos grupos, Q 0,49, muito mais lento.

**Voltar:** botão “Voltar à apresentação” no topo. Orçamento: 4 minutos.


## 5 · Resultados e discussão

### 24 · 5 · Resultados e discussão

**Fala:** Os resultados. Primeiro nos dados sintéticos, onde sabemos a resposta certa; depois na base real, onde a resposta honesta às vezes é “não há estrutura”.

### 25 · O teste contra o acaso

**Ação:** a sequência começa sozinha (15 s); K pausa.

**Fala:** Este é o teste que sustenta todos os resultados. À esquerda, a rede real do conjunto sintético, com Q de 0,467. O modelo nulo sorteia de novo quem cursou o quê, mas mantém quantas disciplinas cada aluno e cada disciplina têm. Vejam as cores se misturarem: a estrutura some — e, mesmo assim, o Louvain encontra Q de 0,22. Esse é o Q do acaso.

Repetindo cinco vezes, o acaso fica entre 0,19 e 0,23, com média de 0,208. O Q real está 15,4 desvios acima. Por isso afirmamos que aqui há estrutura — e é esse mesmo teste que, no OULAD, vai dizer o contrário.

**Fonte:** `null_replicas(synthetic_v1, n=5, seed=0)`, projeção simples, Louvain com semente 42 (`gerar_dados.py`); desvio populacional. A réplica desenhada é a nº 1. As cores dos alunos são as da rede real, mantidas para mostrar a mistura.

### 26 · Validação no sintético

**Fala:** Com o teste do acaso feito, a segunda pergunta: os grupos encontrados são os certos? No sintético sabemos a resposta, porque as áreas foram plantadas pelo gerador.

**Ação:** avance — os números. O Louvain encontra três comunidades, de 39, 30 e 29 alunos, e elas coincidem com as áreas plantadas: NMI de 0,82 e pureza de 0,95, mesmo com 35% de ruído.

**Ação:** avance — os tempos. Na mesma rede, o Girvan–Newman levou 34,4 s contra 0,024 s do Louvain — 1.453 vezes mais lento — e chegou à mesma estrutura (NMI 0,774 entre as duas partições). O achado é da estrutura dos dados, não de um algoritmo.

**Ação:** avance — o cartão laranja. Quando 70% dos alunos ficam com uma única matrícula, a pureza quase não cai, mas o NMI cai pela metade: a esparsidade apaga a informação. É o mesmo mecanismo que aparece no OULAD.

**Para leigos:** NMI mede, de 0 a 1, o quanto dois agrupamentos concordam; pureza é a fração de alunos que caiu no grupo certo.

### 27 · Base real: OULAD

**Fala:** Na base real, o resultado tem duas partes — e a primeira é negativa.

**Ação:** avance — painel da esquerda.

Ligando aluno à disciplina cursada, o Q é 0,77 — mas redes sorteadas dão 0,78. É indistinguível do acaso: 91,8% dos alunos cursam um módulo só, e não há informação entre eles. Dizer que achamos comunidades seria falso.

**Ação:** avance — painel da direita.

Trocando o critério para a interação com o ambiente virtual, a estrutura aparece: Q baixo, mas de 5 a 9 vezes o do acaso, em três turmas.

**Ação:** avance — achado de método. E a ponderação decide se o sinal aparece: a alocação de recursos se mantém acima do acaso; a simples, não.

### 28 · O desfecho revelado

**Fala:** Agora o que o grafo nunca viu: o desfecho dos alunos.

**Ação:** avance — gráfico.

Dividimos os 1.870 alunos em quatro faixas de centralidade e só depois cruzamos com o desfecho. No quarto menos central, 89% não concluíram; no mais central, 10,5%. A turma toda tem 42,7%.

**Ação:** avance — comunidades. O grupo “Pouco engajados” concentra 69% de reprovados e desistentes, contra 7%.

**Ação:** avance — cartão vermelho. Mas isto **não é previsão**: quem desiste para de acessar, então parte do sinal é mecânica. Para falar em antecipação, seria preciso usar só as primeiras semanas.

### 29 · Disciplinas críticas

**Fala:** Por fim, os gargalos do currículo: a rede de 22 ofertas de módulo do OULAD.

**Ação:** avance tabela e correlações.

As três métricas apontam disciplinas diferentes. Grau e autovetor quase concordam; intermediação e autovetor, não — ser ponte e estar num bloco central são coisas diferentes.

**Ação:** avance — validação. As disciplinas-ponte têm só 1,2 ponto acima da taxa de não conclusão da base: um gargalo estrutural é um ponto de passagem, não uma disciplina difícil.


## 6 · Considerações finais

### 30 · 6 · Considerações finais

**Fala:** Para fechar, as considerações finais.

### 31 · Conclusão

**Fala:** Voltando à pergunta de pesquisa: sim, é possível — com uma ressalva honesta.

**Ação:** avance os quatro itens.

Modelamos e projetamos os dados com implementações próprias, conferidas com a biblioteca. No sintético, o método recupera a estrutura plantada. As métricas de centralidade discordam de forma informativa. E na base real o sinal está no **comportamento**, não na matrícula — e o método soube dizer quando não havia estrutura.

Essa é a contribuição: Teoria dos Grafos, sem IA, produz resultados interpretáveis e rastreáveis.

### 32 · Limitações e trabalhos futuros

**Fala:** Preferimos mostrar os limites antes de sermos perguntados — e cada um aponta um próximo passo.

**Ação:** avance linha por linha.

O principal: o resultado **não é previsão** de evasão, porque quem desiste para de acessar; o teste certo é medir a centralidade só com as primeiras semanas. O sinal real é fraco em valor absoluto. O Girvan–Newman não escala para a base inteira. O limiar de nota deixa de fora justamente quem mais reprova. E o sistema foi feito para uso local, sem autenticação.

**Detalhes** no apêndice e em `observacoes/` (por exemplo, T-OBS-02 no executor do pipeline).


## Referências e encerramento

### 33 · Referências

**Fala:** Estas são as referências citadas na apresentação, no formato da ABNT NBR 6023:2018; as citações nos slides seguem a NBR 10520:2023, no sistema autor-data.

**Observação para o grupo:** confira a lista contra a seção de referências do artigo — a apresentação deve citar só o que o artigo cita.

### 34 · Obrigado · Perguntas

**Fala:** Agradecemos a atenção da banca e ao nosso orientador. Ficamos à disposição para as perguntas.

**Durante as perguntas:** A abre o apêndice técnico; O mostra todos os slides; D volta à demonstração.

**Perguntas prováveis:** o critério de aresta que usa o desfecho (ADR-0007); por que Louvain e Brandes não foram implementados à mão (ADR-0010); se o “risco de evasão” é aprendizado de máquina (não — apêndice A3); por que a intermediação ignora o peso (apêndice A2).


## Apêndice técnico

### A1 · Tecnologias e porquês

**Fala:** Cada tecnologia foi escolhida por um motivo, e cada motivo está registrado numa ADR — um registro de decisão de arquitetura. São quatorze no repositório.

**Ação:** avance linha por linha.

Para os **algoritmos**, Python com NetworkX, que é a referência acadêmica de grafos; as partes que implementamos à mão são comparadas numericamente com ela. Para o **armazenamento**, arquivos CSV com um `meta.json` que diz quem gerou o artefato, com que parâmetros e quando — não há banco de dados, e isso foi deliberado: os artefatos são legíveis, versionáveis e podem ser comparados byte a byte. A **API** usa FastAPI. A **interface**, React com TypeScript e Vite; o grafo é desenhado com Cytoscape.js, que usa canvas e aguenta milhares de arestas. Na **qualidade**, testes, lint e checagem de tipos rodam a cada pull request, em duas versões do Python.

**Se perguntarem** “por que não um banco de dados?”: os dados são lidos inteiros por algoritmos de grafo, não consultados por linha; arquivos com escrita canônica permitem provar reprodutibilidade (diff vazio). Um banco foi analisado e ficou como trabalho futuro em `docs/entrega.md`.

### A2 · Dados e contratos

**Fala:** Este é o modelo de dados na prática. Cada etapa do pipeline é uma pasta, sempre no mesmo lugar.

**Ação:** avance as camadas da árvore.

No **bipartido**, os nós — com só três colunas: identificador, tipo e rótulo —, as arestas com peso e, separado, o arquivo de desfechos. Depois vêm as **projeções**, as **comunidades**, com a pertença de cada nó a um grupo, e as **centralidades**, uma por métrica.

Toda pasta tem um `meta.json` que diz qual versão do formato, qual especificação gerou, com que parâmetros e quem produziu. É isso que permite responder, para qualquer número do artigo, “de onde veio isto?”.

E há um comando que valida tudo: confere as colunas e a coerência entre as camadas.

**Nível técnico:** a escrita é canônica — nós e arestas ordenados, floats no menor `repr` que retorna ao mesmo valor, UTF-8 e `\n` explícitos. Por isso as fixtures se regeneram byte a byte, e a CI confere isso num job próprio.

### A3 · Laboratório ao vivo: o fluxo

**Fala:** Este slide mostra como os componentes conversam quando alguém aperta ▶ no laboratório.

**Ação:** avance mensagem por mensagem.

O navegador envia um `POST /lab/run` com as escolhas da tela: tamanho da turma, mistura entre áreas, o que projetar, qual algoritmo. A API valida os limites e chama o pacote `lab`.

O `lab` gera a turma fictícia com o mesmo gerador sintético do trabalho, monta o bipartido e a projeção e roda o algoritmo **guardando o rastro**: cada movimento do Louvain ou cada corte do Girvan–Newman. Depois produz a leitura em português: nome dos grupos, papel de cada aluno, sinais de atenção.

Tudo volta num único JSON. No navegador, uma função pura transforma esse rastro em quadros de animação, e o canvas apenas liga e desliga estilos. Ou seja: **a animação não é encenação** — ela reproduz o que o algoritmo fez de fato.

Para proteger o servidor há limites de tamanho e de tempo; o cálculo pesado, sobre a base real inteira, continua só pela linha de comando.

**Se perguntarem** “o Louvain da tela é o mesmo do artigo?”: não é o mesmo código — a biblioteca python-louvain não expõe os movimentos. Por isso um teste exige que o Q da nossa versão fique a menos de 0,02 da biblioteca, e a própria tela mostra os dois Q lado a lado. Na turma padrão, a partição é idêntica.

### A4 · Verificação e reprodutibilidade

**Fala:** Uma pergunta natural é: como sabemos que os resultados estão certos? A resposta tem duas partes.

**Ação:** avance linha por linha.

Primeiro, as partes que implementamos à mão são comparadas com a biblioteca de referência. As **projeções** batem com diferença abaixo de um bilionésimo — e, na coorte real, com 1,45 milhão de arestas, a nossa foi até mais rápida que a do NetworkX, porque acumula os pares num único percurso. A **modularidade** difere em 3 × 10⁻¹⁵, que é ruído de ponto flutuante. O **autovetor** concorda com o mesmo critério de parada e bate uma forma fechada calculada no papel. E o **Louvain do laboratório** fica a menos de 0,02 da biblioteca por teste; na turma padrão, a partição é idêntica.

**Ação:** avance a faixa de baixo.

Segundo, **reprodutibilidade**: toda aleatoriedade tem semente gravada, as fixtures se regeneram byte a byte, e os valores esperados do menor caso de teste foram derivados no papel — para que o teste não vire tautologia, comparando a biblioteca com ela mesma.

**Fontes:** `docs/artigo/decisoes-metodologicas.md` (A-05, B-03, C-02) e ADR-0010, ADR-0011, ADR-0013.

### A5 · Decisões e desafios

**Fala:** Quatro problemas reais apareceram durante o desenvolvimento, e cada um virou uma decisão registrada.

**Ação:** avance um cartão por vez.

**Desempenho:** o Girvan–Newman cresce com o quadrado do número de arestas e não termina na base completa. Ele roda com orçamento de tempo, verificado a cada remoção; se estourar, devolve a melhor partição vista e marca o status — o sistema nunca quebra por isso.

**Esparsidade:** 91,8% dos alunos do OULAD cursaram um único módulo. Com a matrícula como ligação, quase não há informação entre alunos. Trocamos o critério para a interação com o ambiente virtual — os recursos que o aluno acessou —, e o grau mediano subiu de 1 para 40. Isso não muda o tema: o critério de aresta era parâmetro desde o primeiro dia.

**Visualização:** a projeção do ambiente virtual tem 1,75 milhão de arestas. Mandar só as 5.000 mais pesadas mostraria 193 alunos ligados e o resto solto — uma estrutura que não existe. Por isso a API manda o esqueleto: as ligações mais fortes de cada nó, e a tela declara o corte.

**Método:** como já adiantei, Q alto pode ser acaso. Todo Q é comparado com réplicas embaralhadas, e só afirmamos estrutura com z maior ou igual a 3.

### A6 · Segurança e tratamento de dados

**Fala:** Sobre segurança e dados, prefiro separar o que o sistema garante do que ele não se propõe a fazer.

**Ação:** avance os quatro itens e o cartão.

Os dados reais são públicos e anonimizados — a base OULAD, da Open University, sob licença CC BY 4.0. A turma do laboratório é inteiramente fictícia. Os rótulos ficam fora do grafo, como já vimos. O relatório interno não publica perfis de alunos individuais. E o laboratório tem limites para não ser usado para sobrecarregar o servidor.

O que **não** há é autenticação. O sistema foi feito para rodar localmente, num computador da instituição. Se um dia for publicado na internet, autenticação e controle de acesso precisam vir antes. Isso está registrado como consequência na decisão de arquitetura do laboratório.

**Transição:** “Chega de slides sobre o sistema — vamos ver o sistema.”

### A7 · Testes e evidências

**Fala:** Sobre validação da implementação: tudo o que mostramos está coberto por testes automáticos.

**Ação:** avance — os números.

São 428 testes Python passando na suíte completa e 32 testes da interface. As 23 especificações do projeto estão fechadas, e as 14 decisões de arquitetura estão registradas.

**Ação:** avance — as camadas.

Os testes estão em camadas. Os de **contrato** protegem as regras do trabalho: sem aprendizado de máquina, sem rótulo no grafo, sem import cruzado e escrita reproduzível. Os **unitários** conferem os valores — no menor caso, derivados no papel. Os da **API** conferem cada rota. Os da **interface**, a lógica da animação e do tour.

**Ação:** avance — a coluna da direita.

Lint e checagem de tipos passam sem nenhum aviso, e a integração contínua roda em duas versões do Python, além de um job que regenera as fixtures e exige que nada mude.

**Honestidade:** não há teste automatizado de navegador da interface; a spec C-05 trocou isso por um roteiro de verificação manual, documentado em `frontend/README.md`.

### A8 · Limitações

**Fala:** Todo trabalho tem limites, e preferimos mostrá-los antes de sermos perguntados.

**Ação:** avance duas vezes (três cartões por vez).

**Escala:** o Girvan–Newman só roda em amostras; na coorte por avaliação ele passa de duas horas, então ela ficou só com Louvain e centralidade. **Estrutura:** o sinal na base real é fraco em valor absoluto, ainda que inequívoco contra o acaso. **Causalidade:** como vimos, a centralidade não prevê o desfecho; além disso, o ETL guarda um desfecho por aluno, e o limiar de nota deixa de fora justamente os alunos que mais reprovam.

**Interpretação:** os papéis usam limiares adaptados do artigo original, e o “risco de evasão” é uma conta descritiva com pesos fixos — levamos ao orientador a pergunta se o nome deve mudar. **Generalização:** é uma instituição só. **Engenharia:** não há autenticação, há uma pendência conhecida no executor do pipeline quando a mesma base aparece em duas raízes, e a interface não tem teste automatizado de navegador. Tudo isso está registrado em `observacoes/` e nas ADRs.

### A9 · Fórmulas

Use este slide se pedirem a definição formal. Destaque o **A + I**: somar a identidade não muda os autovetores, só desloca os autovalores em uma unidade; num grafo bipartido, A tem −λ com o mesmo módulo de λ, e a iteração pura oscila sem parar (há um teste que mostra isso numa estrela).

Na alocação de recursos, o NetworkX não tem função pronta: `collaboration_weighted_projected_graph` é a de Newman (1/(grau−1)). A referência usada é `generic_weighted_projected_graph` com a fórmula de Zhou fornecida pelo grupo.

### A10 · Girvan–Newman: escolhas

Fonte: `docs/artigo/decisoes-metodologicas.md`, “Duas escolhas do Girvan-Newman” (B-02) e ADR-0006. Os números da mistura 100% foram conferidos via `POST /lab/run` (semente 12, 45 alunos) em 16/11/2026.

### A11 · Sinais por aluno

Fonte: ADR-0013, item 4; `src/edugraph/lab/signals.py` (W_LOAD = 0,35, W_INTENSITY = 0,35, W_GROUP = 0,30, RISK_ATENCAO = 0,25, RISK_ALTO = 0,50, Z_ESPECIALISTA = 1,5). O número de 94% vem de `docs/orientador/estudo-apresentacao-11-2026.md`, seção 5 (exige o ZIP de resultados do OULAD).

**Resposta curta** para “isso é aprendizado de máquina?”: não há treino nem parâmetro ajustado aos dados de desfecho; os pesos e os cortes foram fixados antes; o desfecho só aparece na conferência.

### A12 · Papéis dos nós

Fonte: `src/edugraph/lab/insight.py` e ADR-0013 (alternativas consideradas e consequências). Na turma padrão do laboratório: 6 referências, 0 conectores, 6 pontes e 31 periféricos.

### A13 · Conjuntos de dados

Os datasets do OULAD ficam fora do git (`data/processed/`), entregues como um ZIP de resultados de ~32 MB, instalado com `python scripts/iniciar.py --oulad <zip>`. Fonte: `docs/orientador/estudo-apresentacao-11-2026.md`, seção 4.

### A14 · Rotas da API

Fonte: `src/edugraph/api/routes.py` e `lab_routes.py`. Documentação interativa em `http://127.0.0.1:8000/docs` — pode ser aberta durante as perguntas. Erro de contrato vira 409; artefato ausente, 404.

### A15 · Como executar

Detalhes em `apresentacao/README.md` e `docs/orientador/estudo-apresentacao-11-2026.md`, seção 7.
