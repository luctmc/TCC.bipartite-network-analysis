# Roteiro da defesa — edugraph

Gerado de `index.html` por `gerar_roteiro.py`: **não edite à mão** — edite as
notas (`<aside class="notas">`) de cada slide e rode o script de novo.

33 slides principais e 26 de apêndice.
Marcas: **Fala** é o que dizer; **Ação** é o que fazer (avançar, clicar);
**Se perguntarem** antecipa perguntas da banca.


## Abertura e sumário

### 01 · Abertura

**Ação:** abra antes de a banca entrar; a animação leva ≈ 5 s.

**Fala:** Boa noite a todos. Somos o Grupo 16, os nossos nomes estão na tela, e vamos apresentar o nosso Trabalho de Conclusão de Curso, orientado pelo professor Clayton Valdo. Essa imagem é um mapa de alunos: cada ponto é um aluno, e as cores são grupos que o nosso sistema encontrou sozinho. Até o fim, todo mundo aqui vai saber ler esse mapa.

### 02 · Sumário

**Fala:** Primeiro o problema e a nossa ideia, num exemplo de seis alunos, sem termo técnico. Depois os nomes técnicos, o método, o sistema ao vivo, os resultados e o que concluímos.


## 1 · Introdução

### 03 · 1 · Introdução

**Fala:** Por que olhar para as relações entre os alunos?

### 04 · O aluno que some

**Ação:** opcional; a animação começa sozinha.

**Fala:** Todo semestre, alguns alunos desaparecem, e quase nunca de uma vez. Primeiro ele falta, depois deixa de entregar um trabalho, para de entrar no ambiente virtual e, no fim, pede o trancamento. A instituição costuma perceber só aqui, no fim. Mas os sinais estavam lá antes.

### 05 · O tamanho do problema

**Ação:** a animação começa sozinha.

**Fala:** E o problema é grande. Cada ponto é um por cento dos alunos que entraram na graduação em 2015. No primeiro ano, 13% já tinham deixado o curso; no segundo, 29%; depois de dez anos, 60%.

**Ação:** avance. Seis em cada dez. E quase três já tinham saído até o segundo ano: a saída acontece cedo, quando ainda daria para agir.

**Ação:** avance. No ensino a distância, que é o da base real que usamos, 65%. Os números são do Inep, o órgão do Ministério da Educação que faz o Censo da Educação Superior.

**Se perguntarem:** “deixar o curso” inclui quem trocou de curso; por isso não dizemos “abandonaram a faculdade”. E são indicadores de trajetória do Inep, não “estatística oficial” (o próprio relatório avisa, p. 32).

### 06 · Os dados já existem

**Ação:** a animação começa sozinha.

**Fala:** A instituição já tem os dados: as matrículas, as notas, os acessos ao ambiente virtual. Mas costuma ler tudo como uma lista, um aluno por linha. Na lista, o Felipe é só mais uma linha. Quando a gente olha para as relações entre os alunos, a mesma informação vira um mapa, e o mapa mostra o que a lista esconde: o Felipe está quase sozinho, na beirada.

### 07 · Uma disciplina, uma ligação

**Fala:** Nosso exemplo: uma universidade inventada, com seis alunos de Análise e Desenvolvimento de Sistemas, a ADS, e de Engenharia Elétrica.

**Ação:** avance. A Ana, de ADS, e a Carla, de Engenharia Elétrica, cursam Sistemas de Computação. **▸** Isso cria uma ligação entre elas. É a ideia central do trabalho: dividir uma disciplina liga dois alunos. **▸** Bruno e Felipe também estão lá, e todos ficam ligados. Nenhuma ligação é inventada: cada uma vem de uma matrícula.

**Ação:** avance. Mas nem toda ligação é igual. Ana e Bruno dividem duas disciplinas; a ligação engrossa. **▸** E dividir uma turma pequena diz mais do que dividir uma lotada. Sistemas de Computação é a mais cheia, então as ligações que vêm só dela afinam.

**Fonte:** espessuras proporcionais aos pesos reais de `tiny_v1` (simples e alocação de recursos); as duas turmas do cartão são ilustrativas.

### 08 · Os grupos e o lugar de cada aluno

**Fala:** Juntando as ligações, temos o mapa da turma. **▸** Nele aparecem grupos: alunos muito ligados entre si e pouco ligados ao resto. Cada grupo é uma comunidade.

**Ação:** avance. E uma surpresa: a Carla é de Engenharia Elétrica, mas ficou no grupo de ADS. O sistema não sabe o curso de ninguém; ele mostra com quem cada um estuda de fato.

**Ação:** avance. A Carla também é ponte: **▸** sem ela, Diego e Elisa ficam desligados de todo o resto. **▸** Já o Felipe está na beirada: uma disciplina só, a mais cheia.

**Ação:** avance. A Carla tem média 69; o Felipe, 66. Notas parecidas, lugares muito diferentes. Em turmas maiores aparece também a referência, quem os colegas rodeiam; vamos vê-la na demonstração.

**Fonte:** grupos do Louvain sobre `tiny_v1`; papel “ponte” dado pelo sistema (`insight.roles`); médias das notas de `tiny_v1` (Carla: 77, 68 e 61).

### 09 · Quem merece atenção, quem se destaca

**Fala:** Com o mapa, o sistema compara cada aluno com a turma em três perguntas: quantas disciplinas cursa, como vai nas notas e o quanto está ligado ao grupo.

**Ação:** avance. O Felipe fica abaixo nas três, e o sistema escreve o motivo, este texto é dele mesmo: "nota média 66, abaixo da turma", "pouco ligado ao próprio grupo". **▸** Diego e Elisa ficam "em atenção": eles vão bem, mas o grupo deles depende de uma pessoa só. **▸** E o outro lado: numa turma maior, a Alice, referência no grupo, uma monitora natural.

**Ação:** avance. O sistema não diz que o Felipe vai desistir. Diz que alguém deveria conversar com ele, e por quê.

**Fonte:** textos gerados por `run_lab` (`tiny_v1`; turma padrão do laboratório, semente 12), lidos de `js/dados.js`. O rótulo do sistema (“Risco alto”) aparece só como texto do sistema: o nome está em discussão (T-OBS-05). O texto que o sistema escreve hoje para Diego e Elisa não é mostrado (T-OBS-06).

### 10 · A solução: o edugraph

**Ação:** a animação começa sozinha.

**Fala:** É isso que o edugraph, o sistema que construímos, faz: entra a lista de matrículas, sai o mapa da turma, com os grupos, o papel de cada aluno, quem merece atenção e quem se destaca, sempre com o motivo. E sem aprendizado de máquina, por escolha do grupo: nenhum modelo foi treinado com o passado dos alunos, e dá para refazer a conta à mão. O desfecho de cada aluno fica guardado à parte e só entra no fim, para conferir.

**Se perguntarem** “mas a nota entra?”: a nota de cada disciplina entra, como força da matrícula; o que fica fora é o desfecho final (ADR-0008).

### 11 · Problema de pesquisa e justificativa

**Fala:** Daí a pergunta do trabalho: dá para encontrar esses grupos, e quem precisa de atenção, só olhando as ligações, de um jeito que qualquer um consiga conferir? **▸** **▸** **▸** Isso serve à gestão, à transparência e à pesquisa.

**Observação para o grupo:** a formulação técnica foi derivada do objetivo da Introdução aprovada (`docs/briefing.md`, seção 1). Se o artigo enuncia o problema com outras palavras, use as do artigo.

### 12 · Objetivos

**Fala:** O objetivo é um sistema que faça isso só com Teoria dos Grafos. **▸** **▸** **▸** **▸** Em quatro passos: modelar, projetar, agrupar e medir. **▸** E dois testes automáticos garantem que nada de aprendizado de máquina entra.

**Se perguntarem** “NMI e pureza não são de aprendizado de máquina?”: são medidas entre dois agrupamentos já prontos; não treinam nada e foram implementadas à mão.


## 2 · Fundamentação teórica

### 13 · 2 · Fundamentação teórica

**Fala:** Agora, o mesmo exemplo com os nomes técnicos.

**Fonte do exemplo:** a fixture `tiny_v1` do repositório, o caso de teste que o grupo resolveu no papel; os números dos próximos slides são dela.

### 14 · Grafo e grafo bipartido

**Fala:** Tudo aqui é grafo, e grafo não é gráfico. **▸** Pensem num mapa de metrô: só estações e quem se liga a quem. **▸** Pontos e linhas: cada ponto é um nó, cada linha uma aresta, e a aresta pode ter um peso.

**Ação:** avance. No nosso caso, os nós são alunos e disciplinas, e as arestas são as matrículas. Dois tipos de ponto: é um grafo bipartido. **▸** A Carla é a única nas três disciplinas, e Sistemas de Computação é a mais cheia.

**Nota:** o mapa de metrô é genérico (sem nomes, cores ou traçado de uma rede real). O grafo bipartido em detalhe está no apêndice.

### 15 · Projeção ponderada

**Fala:** A projeção tira as disciplinas e liga direto os alunos com algo em comum, como o "quem assistiu a este filme também assistiu a…". **▸** No peso simples, Ana e Bruno valem 2. **▸** Na alocação de recursos, cada disciplina vale um sobre o número de alunos: a ligação de Ana e Felipe cai para 0,25. São os valores que o grupo conferiu no papel.

### 16 · Comunidades e modularidade

**Fala:** Para dar nota a uma divisão em grupos, usamos a modularidade, Q. **▸** Como mesas numa festa: se as conversas ficam dentro das mesas, a divisão faz sentido. **▸** Acima de 0,3 costuma ser bom; esta rede tem 0,47. **▸** Mas quem decide é o teste contra o acaso: comparamos com redes embaralhadas.

### 17 · Louvain

**Fala:** O Louvain encontra os grupos juntando: cada aluno muda para o grupo em que o Q mais sobe. **▸** **▸** **▸** **▸** Diego vai para a Elisa, Bruno para a Ana, depois Carla e Felipe. Ninguém mais quer mudar: dois grupos.

**Ação:** avance. Na turma da demonstração, 41 movimentos em um milésimo de segundo. E o Girvan–Newman, que corta em vez de juntar, chega aos mesmos grupos.

### 18 · Centralidade

**Fala:** Por fim, centralidade: quão importante é um aluno, em três sentidos. **▸** Grau: com quantos colegas; a Carla, com todos. **▸** Intermediação: por quem os caminhos passam; só pela Carla, o gargalo. **▸** Autovetor: ligado a quem é bem ligado; Ana, Bruno e Carla. **▸** Combinando isso, o sistema dá o papel de cada aluno: a Carla é ponte.

**Fonte:** grau e intermediação em `tiny_v1/expected/student_simple.centrality.csv` (derivados no papel); autovetor pela implementação da Frente C.


## 3 · Metodologia

### 19 · 3 · Metodologia

**Fala:** O método.

### 20 · Caracterização da pesquisa

**Fala:** É uma pesquisa aplicada e quantitativa, com experimentos que se repetem iguais. **▸** Duas bases: a pública da Open University, e uma turma inventada em que plantamos os grupos. **▸** E cada pergunta tem critério: existe grupo, contra o acaso; é o grupo certo, contra o plantado.

**Observação para o grupo:** a classificação (aplicada, quantitativa, experimental) descreve o que o repositório faz; se o artigo usar outra terminologia, alinhe.


## 4 · Desenvolvimento

### 21 · 4 · Desenvolvimento

**Fala:** Agora, o sistema funcionando.

### 22 · Demonstração ao vivo

**Ação:** Enter para entrar; ≈ 3 min no total.

**Fala:** *[Tour, só os primeiros passos.]* Esse é o edugraph, rodando neste computador, com uma turma inventada de Computação, gerada na hora. A área certa de cada aluno fica guardada à parte.

*[▶ com Louvain.]* As matrículas, as ligações entre alunos, o algoritmo juntando os grupos, com o Q subindo ao vivo, e três grupos com nome.

*[Painel de sinais.]* Um aluno que merece atenção, com o motivo escrito. Os nomes coincidem com os do exemplo, mas são outras pessoas. E a Alice T., referência no grupo, a monitora natural.

*[Revelar.]* E as áreas plantadas: o sistema acertou cem por cento dos alunos sem saber de nada.

*[Voltar pelo botão no topo.]*

**Antes:** a barra da janela deve dizer “Ao vivo · sistema conectado”. Se não, use as capturas e diga que são capturas.

**Não revelar** sinais × desfecho nesta turma: o gerador sorteia nota e desfecho do mesmo perfil de risco, então a coincidência ali é de construção. A evidência do risco vem da Open University (slide “O que o mapa nunca viu”).


## 5 · Resultados e discussão

### 23 · 5 · Resultados e discussão

**Fala:** Os resultados.

### 24 · O teste contra o acaso

**Ação:** a sequência começa sozinha.

**Fala:** Primeiro, o teste contra o acaso. A turma inventada de 98 alunos tem Q de 0,47. Embaralhando quem cursou o quê, a estrutura some e o Q cai para perto de 0,2. A rede real fica mais de quinze desvios acima: os grupos são de verdade. Na base real, esse teste vai dizer o contrário.

**Fonte:** `null_replicas(synthetic_v1, n=5, seed=0)`, projeção simples, Louvain com semente 42 (`gerar_dados.py`); desvio populacional. A réplica desenhada é a nº 1. As cores dos alunos são as da rede real, mantidas para mostrar a mistura.

### 25 · Validação no sintético

**Ação:** opcional.

**Ação:** avance. Na turma inventada, os grupos batem com as áreas plantadas: pureza 0,95 e concordância de 0,82, mesmo com ruído. **▸** O Girvan–Newman confirma, mil vezes mais lento. **▸** E com quase todos numa disciplina só, a concordância cai: é o que acontece na base real.

**Para leigos:** NMI (informação mútua normalizada) mede, de 0 a 1, o quanto duas divisões em grupos concordam; pureza é a fração de alunos que caiu num grupo em que a maioria é da mesma área que ele.

### 26 · A base real: Open University

**Fala:** Na Open University, **▸** pela matrícula o Q é 0,77, mas o acaso dá 0,78: quase todos cursam um módulo só, e não há grupo. O sistema disse isso. **▸** Pelos materiais acessados no ambiente virtual, os grupos aparecem, de cinco a nove vezes acima do acaso. **▸** E o jeito de pesar decide se o sinal aparece.

### 27 · O desfecho revelado

**Fala:** Agora entra o desfecho, que o mapa nunca viu. **▸** Entre os alunos menos centrais, 89% não concluíram; entre os mais centrais, 10%. **▸** O grupo de pouco engajados teve 69% de reprovação ou desistência, contra 7%. **▸** E dos 197 marcados com risco alto, 94%. **▸** Mas não é previsão: quem desiste para de acessar. O sistema aponta onde olhar.

**Fonte do 94%:** `docs/orientador/estudo-apresentacao-11-2026.md`, seção 5 (exige o ZIP de resultados do OULAD; não se reproduz só com o repositório).

### 28 · Disciplinas críticas

**Fala:** E nas disciplinas: **▸** as três medidas apontam disciplinas diferentes; **▸** ser muito cursada e ser ponte são coisas diferentes. **▸** E a disciplina que mais conecta o currículo não é a que mais reprova.


## 6 · Considerações finais

### 29 · 6 · Considerações finais

**Fala:** Para fechar.

### 30 · Conclusão

**Fala:** Voltando à pergunta: sim, com uma condição: o sinal precisa existir nos dados. **▸** **▸** **▸** **▸** O sistema encontra os grupos plantados, as medidas trazem informação, e na base real ele soube dizer quando não havia grupo. **▸** E o mesmo mapa aponta quem merece atenção e quem se destaca, sempre com o motivo.

### 31 · Limitações e trabalhos futuros

**Fala:** Os limites, antes da pergunta: **▸** não é previsão; **▸** o sinal real é fraco; **▸** o Girvan–Newman não escala; **▸** a nota mínima deixa gente de fora; **▸** e o uso é local. O próximo passo natural: dados de uma instituição brasileira.


## Referências e encerramento

### 32 · Referências

**Fala:** As referências, incluindo o relatório do Inep.

**Observação para o grupo:** a lista segue a do artigo, com uma exceção decidida pelo grupo: o dado do Inep está só na apresentação, para mostrar o tamanho do problema (NARRATIVA.md, seção 12). Pela NBR 6023, a entrada começa por “BRASIL.”, por isso fica logo depois de BRANDES (e não entre HAGBERG e KUZILEK, como sugeria o plano).

### 33 · Obrigado · Perguntas

**Fala:** Agradecemos a atenção de todos e ao nosso orientador. Ficamos à disposição para as perguntas.

**Durante as perguntas:** A abre o apêndice técnico; O mostra todos os slides; D volta à demonstração.

**Perguntas prováveis:** o critério de aresta que usa o desfecho (ADR-0007); por que Louvain e Brandes não foram implementados à mão (ADR-0010); se o “risco de evasão” é aprendizado de máquina (não — apêndice A3); por que a intermediação ignora o peso (apêndice A2).


## Apêndice técnico

### A1 · Por que procurar dentro da comunidade

**Fala:** Mas por que fazer isso dentro da comunidade, e não só olhando a nota? Por quatro motivos.

**Ação:** avance. Primeiro, a comunidade dá contexto. Uma nota 66 sozinha não diz muita coisa. Uma nota 66 de um aluno que cursa uma disciplina só e está na beirada do grupo conta outra história.

**Ação:** avance. Segundo, o isolamento costuma vir antes da desistência. O aluno que vai se afastando do curso se afasta primeiro dos colegas: cursa menos, divide menos, fica na beirada. Na planilha isso não aparece. No mapa, aparece.

**Ação:** avance. Terceiro, às vezes o problema não é de uma pessoa, é de um grupo inteiro. Na base real que usamos, de uma universidade inglesa, o sistema encontrou um grupo de alunos pouco engajados em que 69% reprovaram ou desistiram. No grupo de engajamento moderado, foram 7%. E o sistema nunca viu o desfecho dos alunos. Para a instituição, isso indica onde uma ação coletiva faz sentido: um reforço, uma tutoria, uma mudança na disciplina.

**Ação:** avance. E quarto, o talento vira apoio. Quem é referência no grupo é o monitor natural daquele grupo, porque os colegas já estudam com ele.

**Ação:** avance. Na prática, a coordenação vê quais grupos existem de fato; a tutoria sabe com quem conversar primeiro, e já sabe o motivo; os professores encontram monitores; e a instituição consegue agir antes da nota final, não depois.

### A2 · Comparar com a turma

**Fala:** Falta explicar uma coisa: como o sistema decide que alguém está “abaixo da turma”.

**Ação:** avance. Ele mede em passos. Se a média da sala é 70 e as notas costumam variar uns 10 pontos, um aluno com 90 está dois passos acima, e um com 60 está um passo abaixo. Esse passo se chama desvio-padrão, e o número de passos é o escore z. *(É um exemplo de conta, não dado do sistema.)*

**Ação:** avance. O sistema faz essa conta para as três perguntas: quantas disciplinas o aluno cursa, como vai nas notas e o quanto está ligado ao grupo. E junta as três com pesos fixos: 35%, 35% e 30%.

**Ação:** avance. A partir de 0,25, o aluno fica em atenção. A partir de 0,5, risco alto. O Felipe ficou com 0,64.

**Ação:** avance. E por que isso não é aprendizado de máquina: os pesos e os cortes foram definidos antes de olhar o resultado dos alunos e nunca foram ajustados a ele. Não tem treino. É conta.

**Fonte:** `src/edugraph/lab/signals.py` (W_LOAD = 0,35, W_INTENSITY = 0,35, W_GROUP = 0,30, RISK_ATENCAO = 0,25, RISK_ALTO = 0,50); detalhes no apêndice “Sinais por aluno”.

### A3 · Do contexto ao nome técnico

**Opcional** (sai com `--curta`; primeiro corte se faltar tempo).

**Fala:** Resumindo o que vimos: **avance a cada termo** — o aluno é um nó; a ligação é uma aresta; a força é o peso; o grupo é uma comunidade; a ponte é quem tem a maior intermediação; e “abaixo da turma” é um escore z negativo. Mesma história, outros nomes.

### A4 · Grafo bipartido

**Fala:** O primeiro tipo de grafo que usamos é o bipartido. “Bi” porque tem dois tipos de ponto: de um lado os alunos, do outro as disciplinas. E as linhas só ligam um tipo ao outro.

**Ação:** avance. É como pessoas e filmes num serviço de vídeo: a linha liga a pessoa ao filme que ela assistiu. Pessoa não se liga direto a pessoa.

**Ação:** avance. No exemplo são dez matrículas, dez linhas. A Carla é a única nas três disciplinas, e Sistemas de Computação é a mais cheia, com quatro alunos. Esse grafo é exatamente a lista que a instituição já tem. Mas, nele, a relação entre dois alunos ainda está escondida: ela passa pela disciplina.

### A5 · Girvan–Newman

**Fala:** O segundo faz o caminho contrário: o Girvan–Newman corta.

**Ação:** avance — a ligação em vermelho. Ele procura a ligação mais usada como passagem, aquela por onde passam mais caminhos entre todos os pares de alunos. Aqui, é a ligação entre a Carla e o Diego.

**Ação:** avance — a rede se parte. Apaga essa ligação, recalcula, apaga a da Carla com a Elisa, e a rede se parte em dois.

**Ação:** avance — a curva. Ele continua cortando até o fim e fica com o corte de maior nota.

**Ação:** avance — a tabela. Por que usar dois? Porque, se duas receitas opostas chegam aos mesmos grupos, o resultado é dos dados, não de um algoritmo. O Louvain é centenas de vezes mais rápido; o Girvan–Newman serve de confirmação.

**Fonte:** `girvan_newman_trace` sobre `tiny_v1`; tabela por `run_lab` com os valores padrão (semente 12), medida em 22/11/2026 — o tempo varia com a máquina.

### A6 · O método em sequência

**Ação:** a sequência começa sozinha (16 s). K pausa e retoma; J e L voltam e avançam 2 s.

**Fala:** Aqui está o caminho inteiro, com os nossos seis alunos: a planilha de matrículas vira o grafo bipartido; a projeção liga os alunos; o Louvain forma os grupos; e a centralidade aponta a Carla como ponte. É o mesmo caminho que o sistema faz com seis alunos ou com vinte e dois mil. À direita, as etapas acendem junto com a animação.

As etapas 6 e 7 — a validação, em que o desfecho dos alunos entra só no fim, e a API com a interface — completam o caminho. Cada etapa grava um arquivo que a próxima lê, e um comando roda tudo a partir de um arquivo de configuração: `python -m edugraph run configs/synthetic_v1.toml`.

**Fonte:** fixture `tiny_v1` e rastro real de `edugraph.lab.trace`; a frase final cita os 22.425 alunos de `oulad_module_presentation`.

### A7 · Os dados sintéticos

**Fala:** Para a demonstração, o sistema gera na hora uma turma inventada de Computação, com três áreas: desenvolvimento, infraestrutura e dados. Cada aluno faz duas ou três disciplinas da sua área e, às vezes, uma de fora.

O importante: a área verdadeira de cada aluno fica guardada fora do mapa. No fim, revelamos e vemos se o sistema acertou.

Um aviso: os nomes dessa turma coincidem com os do nosso exemplo — Ana, Bruno, Carla —, mas são outras pessoas. Na tela, eles aparecem com a inicial do sobrenome (“Carla N.”).

### A8 · Arquitetura

**Opcional** (sai com `--curta`).

**Fala:** Por dentro, o sistema tem três partes: os dados, as comunidades e as medidas de centralidade com a interface. Uma regra de projeto: nenhuma parte usa o código da outra. Elas conversam por arquivos num formato fixo. Isso deixou o grupo trabalhar em paralelo desde o primeiro dia, e um teste automático garante que a regra continua valendo.

**Ação:** avance os quatro passos.

Cada frente é um pacote Python. Os contratos dos dados e fixtures completas entraram no primeiro dia, então ninguém esperou ninguém. A regra é verificada por um teste que falha se aparecer import cruzado. E trocar os dados sintéticos pelo OULAD é trocar um argumento, sem mudar código.

**Se perguntarem** sobre tecnologias: Python com NetworkX nos algoritmos, FastAPI na API, React com Cytoscape.js na interface — detalhes no apêndice (tecla A).

### A9 · Por dentro de um clique

**Ação:** a sequência começa sozinha (15 s); K pausa.

**Opcional** (sai com `--curta`).

**Fala:** E é isso que acontece quando se aperta o botão. O navegador envia o pedido; a API confere os limites e chama o pacote `lab`. O `lab` não importa as frentes: chama cada uma pelo registro. A Frente A gera a turma e faz a projeção; a Frente B roda o Louvain guardando cada movimento — e a biblioteca oficial confere o resultado; a Frente C calcula as centralidades. Tudo volta numa única resposta, em cerca de 0,13 s, e o navegador transforma o rastro em animação. Ou seja: o que vocês viram na demonstração é exatamente o que o algoritmo fez.

**Fontes:** `api/lab_routes.py`, `lab/service.py` (`PROJECTIONS`, `COMMUNITIES`, `CENTRALITIES`); números de `POST /lab/run` com os valores padrão (16/11/2026; o tempo varia com a máquina).

### A10 · A interface

**Fala:** Para quem usa, o sistema tem duas telas: o **Laboratório ao vivo**, que monta uma rede na hora e anima o que o algoritmo fez, e o **Explorar resultados**, com os resultados já calculados sobre as bases completas. A identidade visual é a de uma página de periódico, com cores legíveis para quem tem daltonismo e uma forma para cada grupo.

### A11 · Como o trabalho foi conduzido

**Fala:** O desenvolvimento durou cerca de sete semanas, com as três frentes trabalhando ao mesmo tempo.

**Ação:** avance a linha do tempo.

No dia zero entraram a arquitetura, os contratos dos dados e fixtures completas — o que permitiu que as frentes não esperassem umas pelas outras. Logo depois vieram os dados, os algoritmos de comunidade, a centralidade e a aplicação. Em outubro, uma auditoria e o redesenho da interface; no começo de novembro, o laboratório ao vivo e a revisão de entrega.

**Ação:** avance os números.

Tudo foi guiado por 23 especificações, com 14 decisões de arquitetura registradas, entrando na branch principal só por pull request com a integração contínua verde.

**Fonte:** histórico do git (109 commits entre 17/09 e 04/11/2026); `docs/specs/`, `docs/adr/`.

### A12 · Tecnologias e porquês

**Fala:** Cada tecnologia foi escolhida por um motivo, e cada motivo está registrado numa ADR — um registro de decisão de arquitetura. São quatorze no repositório.

**Ação:** avance linha por linha.

Para os **algoritmos**, Python com NetworkX, que é a referência acadêmica de grafos; as partes que implementamos à mão são comparadas numericamente com ela. Para o **armazenamento**, arquivos CSV com um `meta.json` que diz quem gerou o artefato, com que parâmetros e quando — não há banco de dados, e isso foi deliberado: os artefatos são legíveis, versionáveis e podem ser comparados byte a byte. A **API** usa FastAPI. A **interface**, React com TypeScript e Vite; o grafo é desenhado com Cytoscape.js, que usa canvas e aguenta milhares de arestas. Na **qualidade**, testes, lint e checagem de tipos rodam a cada pull request, em duas versões do Python.

**Se perguntarem** “por que não um banco de dados?”: os dados são lidos inteiros por algoritmos de grafo, não consultados por linha; arquivos com escrita canônica permitem provar reprodutibilidade (diff vazio). Um banco foi analisado e ficou como trabalho futuro em `docs/entrega.md`.

### A13 · Dados e contratos

**Fala:** Este é o modelo de dados na prática. Cada etapa do pipeline é uma pasta, sempre no mesmo lugar.

**Ação:** avance as camadas da árvore.

No **bipartido**, os nós — com só três colunas: identificador, tipo e rótulo —, as arestas com peso e, separado, o arquivo de desfechos. Depois vêm as **projeções**, as **comunidades**, com a pertença de cada nó a um grupo, e as **centralidades**, uma por métrica.

Toda pasta tem um `meta.json` que diz qual versão do formato, qual especificação gerou, com que parâmetros e quem produziu. É isso que permite responder, para qualquer número do artigo, “de onde veio isto?”.

E há um comando que valida tudo: confere as colunas e a coerência entre as camadas.

**Nível técnico:** a escrita é canônica — nós e arestas ordenados, floats no menor `repr` que retorna ao mesmo valor, UTF-8 e `\n` explícitos. Por isso as fixtures se regeneram byte a byte, e a CI confere isso num job próprio.

### A14 · Laboratório ao vivo: o fluxo

**Fala:** Este slide mostra como os componentes conversam quando alguém aperta ▶ no laboratório.

**Ação:** avance mensagem por mensagem.

O navegador envia um `POST /lab/run` com as escolhas da tela: tamanho da turma, mistura entre áreas, o que projetar, qual algoritmo. A API valida os limites e chama o pacote `lab`.

O `lab` gera a turma fictícia com o mesmo gerador sintético do trabalho, monta o bipartido e a projeção e roda o algoritmo **guardando o rastro**: cada movimento do Louvain ou cada corte do Girvan–Newman. Depois produz a leitura em português: nome dos grupos, papel de cada aluno, sinais de atenção.

Tudo volta num único JSON. No navegador, uma função pura transforma esse rastro em quadros de animação, e o canvas apenas liga e desliga estilos. Ou seja: **a animação não é encenação** — ela reproduz o que o algoritmo fez de fato.

Para proteger o servidor há limites de tamanho e de tempo; o cálculo pesado, sobre a base real inteira, continua só pela linha de comando.

**Se perguntarem** “o Louvain da tela é o mesmo do artigo?”: não é o mesmo código — a biblioteca python-louvain não expõe os movimentos. Por isso um teste exige que o Q da nossa versão fique a menos de 0,02 da biblioteca, e a própria tela mostra os dois Q lado a lado. Na turma padrão, a partição é idêntica.

### A15 · Verificação e reprodutibilidade

**Fala:** Uma pergunta natural é: como sabemos que os resultados estão certos? A resposta tem duas partes.

**Ação:** avance linha por linha.

Primeiro, as partes que implementamos à mão são comparadas com a biblioteca de referência. As **projeções** batem com diferença abaixo de um bilionésimo — e, na coorte real, com 1,45 milhão de arestas, a nossa foi até mais rápida que a do NetworkX, porque acumula os pares num único percurso. A **modularidade** difere em 3 × 10⁻¹⁵, que é ruído de ponto flutuante. O **autovetor** concorda com o mesmo critério de parada e bate uma forma fechada calculada no papel. E o **Louvain do laboratório** fica a menos de 0,02 da biblioteca por teste; na turma padrão, a partição é idêntica.

**Ação:** avance a faixa de baixo.

Segundo, **reprodutibilidade**: toda aleatoriedade tem semente gravada, as fixtures se regeneram byte a byte, e os valores esperados do menor caso de teste foram derivados no papel — para que o teste não vire tautologia, comparando a biblioteca com ela mesma.

**Fontes:** `docs/artigo/decisoes-metodologicas.md` (A-05, B-03, C-02) e ADR-0010, ADR-0011, ADR-0013.

### A16 · Decisões e desafios

**Fala:** Quatro problemas reais apareceram durante o desenvolvimento, e cada um virou uma decisão registrada.

**Ação:** avance um cartão por vez.

**Desempenho:** o Girvan–Newman cresce com o quadrado do número de arestas e não termina na base completa. Ele roda com orçamento de tempo, verificado a cada remoção; se estourar, devolve a melhor partição vista e marca o status — o sistema nunca quebra por isso.

**Esparsidade:** 91,8% dos alunos do OULAD cursaram um único módulo. Com a matrícula como ligação, quase não há informação entre alunos. Trocamos o critério para a interação com o ambiente virtual — os recursos que o aluno acessou —, e o grau mediano subiu de 1 para 40. Isso não muda o tema: o critério de aresta era parâmetro desde o primeiro dia.

**Visualização:** a projeção do ambiente virtual tem 1,75 milhão de arestas. Mandar só as 5.000 mais pesadas mostraria 193 alunos ligados e o resto solto — uma estrutura que não existe. Por isso a API manda o esqueleto: as ligações mais fortes de cada nó, e a tela declara o corte.

**Método:** como já adiantei, Q alto pode ser acaso. Todo Q é comparado com réplicas embaralhadas, e só afirmamos estrutura com z maior ou igual a 3.

### A17 · Segurança e tratamento de dados

**Fala:** Sobre segurança e dados, prefiro separar o que o sistema garante do que ele não se propõe a fazer.

**Ação:** avance os quatro itens e o cartão.

Os dados reais são públicos e anonimizados — a base OULAD, da Open University, sob licença CC BY 4.0. A turma do laboratório é inteiramente fictícia. Os rótulos ficam fora do grafo, como já vimos. O relatório interno não publica perfis de alunos individuais. E o laboratório tem limites para não ser usado para sobrecarregar o servidor.

O que **não** há é autenticação. O sistema foi feito para rodar localmente, num computador da instituição. Se um dia for publicado na internet, autenticação e controle de acesso precisam vir antes. Isso está registrado como consequência na decisão de arquitetura do laboratório.

**Transição:** “Chega de slides sobre o sistema — vamos ver o sistema.”

### A18 · Testes e evidências

**Fala:** Sobre validação da implementação: tudo o que mostramos está coberto por testes automáticos.

**Ação:** avance — os números.

São 428 testes Python passando na suíte completa e 32 testes da interface. As 23 especificações do projeto estão fechadas, e as 14 decisões de arquitetura estão registradas.

**Ação:** avance — as camadas.

Os testes estão em camadas. Os de **contrato** protegem as regras do trabalho: sem aprendizado de máquina, sem rótulo no grafo, sem import cruzado e escrita reproduzível. Os **unitários** conferem os valores — no menor caso, derivados no papel. Os da **API** conferem cada rota. Os da **interface**, a lógica da animação e do tour.

**Ação:** avance — a coluna da direita.

Lint e checagem de tipos passam sem nenhum aviso, e a integração contínua roda em duas versões do Python, além de um job que regenera as fixtures e exige que nada mude.

**Honestidade:** não há teste automatizado de navegador da interface; a spec C-05 trocou isso por um roteiro de verificação manual, documentado em `frontend/README.md`.

### A19 · Limitações

**Fala:** Todo trabalho tem limites, e preferimos mostrá-los antes de sermos perguntados.

**Ação:** avance duas vezes (três cartões por vez).

**Escala:** o Girvan–Newman só roda em amostras; na coorte por avaliação ele passa de duas horas, então ela ficou só com Louvain e centralidade. **Estrutura:** o sinal na base real é fraco em valor absoluto, ainda que inequívoco contra o acaso. **Causalidade:** como vimos, a centralidade não prevê o desfecho; além disso, o ETL guarda um desfecho por aluno, e o limiar de nota deixa de fora justamente os alunos que mais reprovam.

**Interpretação:** os papéis usam limiares adaptados do artigo original, e o “risco de evasão” é uma conta descritiva com pesos fixos — levamos ao orientador a pergunta se o nome deve mudar. **Generalização:** é uma instituição só. **Engenharia:** não há autenticação, há uma pendência conhecida no executor do pipeline quando a mesma base aparece em duas raízes, e a interface não tem teste automatizado de navegador. Tudo isso está registrado em `observacoes/` e nas ADRs.

### A20 · Fórmulas

Use este slide se pedirem a definição formal. Destaque o **A + I**: somar a identidade não muda os autovetores, só desloca os autovalores em uma unidade; num grafo bipartido, A tem −λ com o mesmo módulo de λ, e a iteração pura oscila sem parar (há um teste que mostra isso numa estrela).

Na alocação de recursos, o NetworkX não tem função pronta: `collaboration_weighted_projected_graph` é a de Newman (1/(grau−1)). A referência usada é `generic_weighted_projected_graph` com a fórmula de Zhou fornecida pelo grupo.

### A21 · Girvan–Newman: escolhas

Fonte: `docs/artigo/decisoes-metodologicas.md`, “Duas escolhas do Girvan-Newman” (B-02) e ADR-0006. Os números da mistura 100% foram conferidos via `POST /lab/run` (semente 12, 45 alunos) em 16/11/2026.

### A22 · Sinais por aluno

Fonte: ADR-0013, item 4; `src/edugraph/lab/signals.py` (W_LOAD = 0,35, W_INTENSITY = 0,35, W_GROUP = 0,30, RISK_ATENCAO = 0,25, RISK_ALTO = 0,50, Z_ESPECIALISTA = 1,5). O número de 94% vem de `docs/orientador/estudo-apresentacao-11-2026.md`, seção 5 (exige o ZIP de resultados do OULAD).

A versão em linguagem simples desta conta está no slide “Comparar com a turma” (Fundamentação).

**Resposta curta** para “isso é aprendizado de máquina?”: não há treino nem parâmetro ajustado aos dados de desfecho; os pesos e os cortes foram fixados antes; o desfecho só aparece na conferência.

### A23 · Papéis dos nós

Fonte: `src/edugraph/lab/insight.py` e ADR-0013 (alternativas consideradas e consequências). Na turma padrão do laboratório: 6 referências, 0 conectores, 6 pontes e 31 periféricos.

### A24 · Conjuntos de dados

Os datasets do OULAD ficam fora do git (`data/processed/`), entregues como um ZIP de resultados de ~32 MB, instalado com `python scripts/iniciar.py --oulad <zip>`. Fonte: `docs/orientador/estudo-apresentacao-11-2026.md`, seção 4.

### A25 · Rotas da API

Fonte: `src/edugraph/api/routes.py` e `lab_routes.py`. Documentação interativa em `http://127.0.0.1:8000/docs` — pode ser aberta durante as perguntas. Erro de contrato vira 409; artefato ausente, 404.

### A26 · Como executar

Detalhes em `apresentacao/README.md` e `docs/orientador/estudo-apresentacao-11-2026.md`, seção 7.
