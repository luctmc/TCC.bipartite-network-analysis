# Enredo da apresentação

> **O que é:** o texto que vamos **falar no dia**, na ordem da
> apresentação, um tópico de cada vez. Não é para ler palavra por palavra:
> é o jeito natural de contar cada parte, para ensaiar até sair com as
> próprias palavras.
>
> **Como ler:**
> - **Na tela** diz qual slide (o `id` em `index.html`, como no
>   [`PLANO-AJUSTE.md`](PLANO-AJUSTE.md)).
> - **▸** marca onde avançar (seta → ou espaço).
> - *Itálico entre colchetes* é ação ou lembrete, não se fala.
> - O tempo de cada tópico é uma estimativa a 140 palavras por minuto.
>
> As ideias e os números vêm da [`NARRATIVA.md`](NARRATIVA.md). Quando a
> apresentação for ajustada, a fala de cada slide (`<aside class="notas">`)
> sai daqui, e o `ROTEIRO.md` gerado deve bater com este texto.
>
> **Quem fala o quê** o grupo decide no ensaio; o texto não depende disso.

---

## Abertura

**Na tela:** `capa` · *[espere a animação terminar, ≈ 5 s]* · ≈ 40 s

Boa noite a todos. Somos o Grupo 16, os nossos nomes estão aqui na tela, e
vamos apresentar o nosso Trabalho de Conclusão de Curso, orientado pelo
professor Clayton Valdo.

Essa imagem que acabou de se formar é um mapa de alunos. Cada ponto é um
aluno, cada linha liga dois alunos que cursam disciplinas em comum, e as
cores são grupos que o nosso sistema encontrou sozinho. Agora ela pode
parecer só um desenho bonito. A ideia é que, até o fim da apresentação,
todo mundo aqui consiga ler esse mapa e entender por que ele importa.

## O caminho da apresentação

**Na tela:** `sumario` · ≈ 25 s

Vamos começar pelo problema e pela nossa ideia, com um exemplo bem
pequeno, de seis alunos, sem nenhum termo técnico. Depois, os mesmos seis
alunos com os nomes técnicos. Em seguida, como a pesquisa foi feita, o
sistema funcionando ao vivo, os resultados e o que concluímos.

**Na tela:** `sec-1` · ≈ 5 s

Começando: por que olhar para as relações entre os alunos?

---

## O aluno que some

**Na tela:** `aluno-some` · *[a animação começa sozinha]* · ≈ 45 s

Todo semestre, alguns alunos desaparecem. E quase nunca é de uma vez.
Primeiro ele falta uma aula, depois outra. Deixa de entregar um trabalho.
Para de entrar no ambiente virtual. E, no fim, chega o pedido de
trancamento, ou a nota final mostra que ele já tinha ido embora.

Reparem onde a instituição costuma perceber: lá no fim. Quando já é tarde
para ajudar.

Só que os sinais estavam lá antes. Eles aparecem nas matrículas, nas
notas, no que o aluno acessa. A pergunta do nosso trabalho começa aqui:
dá para enxergar esses sinais mais cedo?

## O tamanho do problema

**Na tela:** `evasao-inep` · *[a animação começa sozinha]* · ≈ 1 min 05 s

E não é um problema pequeno. Cada ponto aqui é um por cento dos alunos que
entraram na graduação no Brasil em 2015, acompanhados por dez anos.

No primeiro ano, 13% já tinham deixado o curso. No segundo, 29%. No
terceiro, 40%. Depois de dez anos, 60%.

▸ Ou seja: de cada dez alunos que entraram, seis deixaram o curso em que
ingressaram. E quase três já tinham saído até o fim do segundo ano. Esse
é o ponto que mais nos interessa: a saída acontece cedo, justamente
quando ainda daria para fazer alguma coisa.

▸ *[se houver o passo]* No ensino a distância, que é o caso da base real
que vamos usar, é ainda maior: 65%, contra 59% no presencial.

Esses números são do Inep, o órgão do Ministério da Educação que faz o
Censo da Educação Superior. *[Se perguntarem: "deixar o curso" inclui
quem trocou de curso; por isso não dizemos "abandonaram a faculdade".]*

## Os dados já existem

**Na tela:** `contexto` · *[a animação começa sozinha]* · ≈ 1 min

O curioso é que a instituição já tem os dados para enxergar isso. Ela
sabe em que disciplinas cada aluno se matriculou, que nota ele teve e, no
ensino a distância, o que ele acessou.

O problema é como esses dados costumam ser lidos: como uma lista. Uma
planilha, um aluno por linha. Olhem o Felipe aqui: na planilha, ele é só
mais uma linha. Nada chama a atenção.

Agora vejam o que acontece quando, em vez de ler a lista, a gente olha
para as relações entre os alunos. A mesma informação vira um mapa. E no
mapa dá para ver uma coisa que a lista esconde: o Felipe está quase
sozinho, na beirada.

É essa a nossa ideia, numa frase: olhar para os alunos pelas relações
entre eles, e não um de cada vez.

## O nosso exemplo e a primeira ideia: a ligação

**Na tela:** `ligacao` · ≈ 1 min

Para explicar, vamos usar uma universidade bem pequena, inventada. Seis
alunos, de dois cursos: Análise e Desenvolvimento de Sistemas, que vamos
chamar de ADS, e Engenharia Elétrica. E três disciplinas: Sistemas de
Computação, Algoritmos e Programação e Circuitos Elétricos.

Pensem numa situação comum numa universidade: um aluno de ADS e um aluno
de Engenharia Elétrica podem se inscrever na mesma disciplina.
*[Se o grupo quiser, dizer de quem foi a dica do exemplo.]*

▸ A Ana, que faz ADS, e a Carla, que faz Engenharia Elétrica, se
inscreveram as duas em Sistemas de Computação.

▸ Isso cria uma ligação entre elas. É a ideia mais importante do
trabalho, e a mais simples: dividir uma disciplina liga dois alunos.

▸ O Bruno e o Felipe também estão em Sistemas de Computação, então todos
os quatro ficam ligados entre si.

E um detalhe que importa: nenhuma ligação é inventada. Cada uma vem de um
registro de matrícula que a instituição já tem.

## Nem toda ligação é igual

**Na tela:** `forca` · ≈ 45 s

Mas nem toda ligação tem a mesma força.

▸ A Ana e o Bruno dividem duas disciplinas: Sistemas de Computação e
Algoritmos. A Ana e o Felipe, só uma. Então a ligação entre Ana e Bruno é
mais forte, e a linha fica mais grossa.

▸ E tem outra coisa. Pensem em estar junto com alguém numa disciplina de
trezentos alunos. Isso quase não diz nada sobre vocês dois. Agora, estar
junto numa turma de quinze diz bastante.

▸ O sistema leva isso em conta. No exemplo, Sistemas de Computação é a
turma mais cheia, então as ligações que vêm só dela ficam um pouco mais
fracas.

## O mapa da turma e seus grupos

**Na tela:** `comunidades-ctx` · ≈ 1 min

Juntando todas essas ligações, temos o mapa da turma: quem está ligado a
quem, e com que força. É isso que chamamos de rede.

▸ E olhando o mapa aparecem grupos: alunos muito ligados entre si e pouco
ligados ao resto. Cada grupo desses é uma comunidade. Aqui são duas: a
Ana, o Bruno, a Carla e o Felipe, de um lado; o Diego e a Elisa, do outro.

▸ Agora vejam uma coisa interessante. Se a gente colocar o curso de cada
um por cima, a Carla é de Engenharia Elétrica, mas ficou no grupo de ADS.

Isso não é erro. A comunidade não mostra o curso que está na matrícula.
Mostra com quem cada aluno estuda de verdade. A Carla faz as disciplinas
de computação junto com a Ana e o Bruno.

▸ E ninguém disse ao sistema quantos grupos existiam, nem o curso de
ninguém. Ele encontrou sozinho, só olhando as ligações.

## O lugar de cada aluno

**Na tela:** `papeis-ctx` · ≈ 1 min

Dentro do mapa, cada aluno ocupa um lugar diferente.

▸ A Carla é o que chamamos de ponte: ela liga grupos que, sem ela,
ficariam separados.

▸ Se a Carla sair, vejam o que acontece: o Diego e a Elisa ficam
desligados de todo o resto da turma.

▸ Já o Felipe está na beirada. Ele tem poucas ligações, e fracas, porque
neste semestre está matriculado em uma disciplina só, justamente a mais
cheia.

▸ E aqui está o que o mapa mostra e a nota não mostra. A Carla tem média
69. O Felipe tem média 66. Notas parecidas. Mas a situação dos dois é
completamente diferente: uma é a peça que liga a turma, o outro está
quase sozinho.

Em turmas maiores aparece também a referência, aquele aluno que os
colegas rodeiam. Vamos ver um na demonstração.

## Quem merece atenção e quem pode se destacar

**Na tela:** `atencao-talento` · ≈ 1 min 35 s

Com o mapa pronto, o sistema olha cada aluno e faz três perguntas, sempre
comparando com a turma. Quantas disciplinas ele cursa? Como está o
desempenho dele? E o quanto ele está ligado ao próprio grupo?

▸ No exemplo, o Felipe fica abaixo da turma nas três. E o sistema não
devolve só um número: ele escreve o motivo. Aqui está o texto que ele
gerou de verdade, rodando sobre esses seis alunos: "nota média 66, abaixo
da turma, que é 74", e "pouco ligado ao próprio grupo".

▸ O Diego e a Elisa aparecem num nível mais leve, "em atenção". Os dois
vão bem nas notas. O sinal aqui é do grupo: é um grupo de duas pessoas que
depende de uma colega só para se ligar ao resto da turma.

▸ E o mesmo mapa mostra o outro lado: quem pode se destacar. Numa turma
maior, a da demonstração, o sistema aponta, por exemplo, a Alice: nota
acima da turma, destaque em Estruturas de Dados e referência no próprio
grupo, ou seja, alguém que pode apoiar os colegas como monitora. E a
Larissa, que se destaca em Redes e liga grupos diferentes sem perder
desempenho.

▸ Um cuidado importante: o sistema não diz que o Felipe vai desistir. Ele
diz que alguém deveria conversar com ele. E diz por quê.

## Por que procurar dentro da comunidade

**Na tela:** `por-que-comunidade` · ≈ 1 min 35 s

Mas por que fazer isso dentro da comunidade, e não só olhando a nota?
Por quatro motivos.

▸ Primeiro, a comunidade dá contexto. Uma nota 66 sozinha não diz muita
coisa. Uma nota 66 de um aluno que cursa uma disciplina só e está na
beirada do grupo conta outra história.

▸ Segundo, o isolamento costuma vir antes da desistência. O aluno que vai
se afastando do curso se afasta primeiro dos colegas: cursa menos, divide
menos, fica na beirada. Na planilha isso não aparece. No mapa, aparece.

▸ Terceiro, às vezes o problema não é de uma pessoa, é de um grupo
inteiro. Na base real que usamos, de uma universidade inglesa, o sistema
encontrou um grupo de alunos pouco engajados em que 69% reprovaram ou
desistiram. No grupo de engajamento moderado, foram 7%. E o sistema nunca
viu a nota final. Para a instituição, isso indica onde uma ação coletiva
faz sentido: um reforço, uma tutoria, uma mudança na disciplina.

▸ E quarto, o talento vira apoio. Quem é referência no grupo é o monitor
natural daquele grupo, porque os colegas já estudam com ele.

▸ Na prática, a coordenação vê quais grupos existem de fato; a tutoria
sabe com quem conversar primeiro, e já sabe o motivo; os professores
encontram monitores; e a instituição consegue agir antes da nota final,
não depois.

## A nossa solução: o edugraph

**Na tela:** `solucao` · *[a animação começa sozinha]* · ≈ 1 min 20 s

E é isso que o sistema que construímos faz. Ele se chama edugraph.

Entra a lista de matrículas e, quando existe, o registro de acessos ao
ambiente virtual. Sai o mapa da turma, com os grupos já com nome, o papel
de cada aluno, quem merece atenção e quem pode se destacar. Sempre com o
motivo escrito. E o sistema ainda mostra, passo a passo, como chegou ao
resultado.

Uma escolha nossa desde o começo: o edugraph não usa aprendizado de
máquina. Nenhum modelo foi treinado com o passado dos alunos. Tudo sai de
contar ligações e comparar cada aluno com a própria turma.

Por quê? Porque, em vez de dizer "este aluno tem 73% de chance de
evadir", o sistema diz "cursa uma disciplina só, nota abaixo da turma,
pouco ligado ao grupo". A coordenação pode concordar, discordar ou
conferir. Dá para refazer a conta à mão, e foi o que fizemos com esses
seis alunos. E o resultado final dos alunos fica guardado à parte: só
entra no fim, para conferir se o mapa acertou. Se entrasse antes, o
sistema estaria colando.

## A pergunta de pesquisa e os objetivos

**Na tela:** `problema-pesquisa` · ≈ 40 s

Com isso, a pergunta do trabalho fica fácil de entender. Dá para
encontrar esses grupos, e quem precisa de atenção, só olhando as
ligações, de um jeito que qualquer pessoa consiga conferir?

▸ ▸ ▸ Isso importa para a gestão, que precisa de grupos que consiga
explicar; para a transparência, porque cada resultado pode ser rastreado
até as ligações; e para a pesquisa, porque testa se a Teoria dos Grafos
clássica dá conta, inclusive quando a resposta honesta é "aqui não há
grupos".

**Na tela:** `objetivos` · ≈ 40 s

O objetivo geral é construir um sistema que encontre esses padrões usando
só Teoria dos Grafos, sem inteligência artificial.

▸ ▸ ▸ ▸ Na prática, quatro passos: montar o mapa de quem cursa o quê;
transformar isso em ligações entre alunos; encontrar as comunidades; e
medir quem faz ponte e onde estão os gargalos.

▸ E a regra de não usar aprendizado de máquina não ficou só na
intenção: dois testes automáticos falham se alguém usar uma biblioteca de
aprendizado de máquina ou deixar o resultado dos alunos entrar antes da
hora.

---

## Passagem: agora, os nomes técnicos

**Na tela:** `sec-2` · ≈ 15 s

Agora vamos ver como o sistema faz isso. É o mesmo exemplo dos seis
alunos. Só que, agora, cada coisa ganha o nome técnico, e vamos explicar
cada um.

## O que é um grafo

**Na tela:** `grafo` · ≈ 50 s

Tudo o que o sistema faz é sobre grafos. E grafo, aqui, não é gráfico de
barras: é outra coisa.

▸ Pensem num mapa de metrô. Ele não mostra as ruas nem a distância real.
Mostra só as estações e quais estão ligadas a quais.

▸ Se a gente tirar o resto e deixar só isso, pontos e linhas, temos um
grafo. Cada ponto se chama nó, e cada linha se chama aresta. E uma aresta
pode ter um peso, um número que diz o quanto aquela ligação é forte.

▸ No nosso caso, os pontos são os alunos e as disciplinas, e as linhas
são as matrículas.

## Grafo bipartido

**Na tela:** `bipartido` · ≈ 45 s

O primeiro tipo de grafo que usamos é o bipartido. "Bi" porque tem dois
tipos de ponto: de um lado os alunos, do outro as disciplinas. E as
linhas só ligam um tipo ao outro.

▸ É como pessoas e filmes num serviço de vídeo: a linha liga a pessoa ao
filme que ela assistiu. Pessoa não se liga direto a pessoa.

▸ No exemplo são dez matrículas, dez linhas. A Carla é a única nas três
disciplinas, e Sistemas de Computação é a mais cheia, com quatro alunos.
Esse grafo é exatamente a lista que a instituição já tem. Mas, nele, a
relação entre dois alunos ainda está escondida: ela passa pela
disciplina.

## Projeção e peso

**Na tela:** `projecao` · ≈ 1 min

Para trazer essa relação para fora, fazemos a projeção: tiramos as
disciplinas do desenho e ligamos direto os alunos que tinham alguma em
comum.

É a mesma lógica do "quem assistiu a este filme também assistiu a…". E
não é coincidência: o método de peso que usamos vem de um artigo da área
de recomendação.

▸ O peso mais simples conta as disciplinas em comum. Ana e Bruno dividem
duas: peso 2. Ana e Felipe, uma: peso 1.

▸ O segundo peso é a ideia da turma lotada. Cada disciplina vale um
dividido pelo número de alunos dela. Sistemas de Computação tem quatro
alunos, então vale um quarto. As outras têm três, valem um terço. A
ligação da Ana com o Felipe, que vem só de Sistemas de Computação,
encolhe para 0,25. Esses valores o grupo calculou no papel, e os testes
exigem que o sistema chegue neles.

## Comunidade e modularidade

**Na tela:** `modularidade` · ≈ 1 min 25 s

A comunidade, no sentido técnico, é o que já vimos: um grupo muito ligado
por dentro e pouco ligado ao resto. Só que existem muitas formas de
dividir uma rede em grupos. Como saber se uma divisão é boa?

▸ Para isso existe uma nota, a modularidade, que se escreve com a letra
Q. Pensem numa festa em que as pessoas foram separadas em mesas. Se quase
todas as conversas acontecem dentro das mesas, a divisão faz sentido. Se
as pessoas conversam com qualquer mesa igualmente, as mesas não querem
dizer nada. O Q mede quanto das ligações fica dentro dos grupos, tirando
o que ficaria lá por sorte.

▸ Perto de zero, a divisão não é melhor que sortear. Acima de 0,3, os
grupos são bem definidos. Essa rede aqui, de 98 alunos, tem 0,47.

▸ Mas tem um cuidado. Em algumas redes, até uma rede sorteada dá um Q
alto. Então fazemos como quem confere se um dado está viciado: embaralhamos
a rede várias vezes, mantendo quantas disciplinas cada aluno faz, e
comparamos. Só aceitamos os grupos se a rede real ficar bem acima das
embaralhadas. Esse teste vai decidir um resultado importante mais para a
frente.

## Louvain: juntar

**Na tela:** `louvain` · ≈ 50 s

Para encontrar as comunidades usamos dois algoritmos, duas receitas que
o computador segue. O primeiro é o Louvain, e ele junta.

Voltando à festa: cada pessoa começa sozinha numa mesa e, uma de cada
vez, muda para a mesa vizinha em que a nota da divisão mais sobe.

▸ ▸ ▸ ▸ No exemplo são quatro movimentos. A cada um, o Q sobe. Quando
ninguém mais quer mudar, para. E chega nos dois grupos que vimos no
começo.

▸ Na turma da demonstração, o mesmo processo faz 41 movimentos e leva
cerca de um milésimo de segundo. É exatamente esse rastro que o sistema
anima ao vivo.

## Girvan–Newman: cortar

**Na tela:** `girvan-newman` · ≈ 50 s

O segundo faz o caminho contrário: o Girvan–Newman corta.

▸ Ele procura a ligação mais usada como passagem, aquela por onde passam
mais caminhos entre todos os pares de alunos. Aqui, é a ligação entre a
Carla e o Diego.

▸ Apaga essa ligação, recalcula, apaga a da Carla com a Elisa, e a rede
se parte em dois.

▸ Ele continua cortando até o fim e fica com o corte de maior nota.

▸ Por que usar dois? Porque, se duas receitas opostas chegam aos mesmos
grupos, o resultado é dos dados, não de um algoritmo. O Louvain é muito
mais rápido; o Girvan–Newman serve de confirmação.

## Centralidade e papéis

**Na tela:** `centralidade` · ≈ 1 min 10 s

A última ideia é a centralidade: quão importante é um aluno na rede. Só
que "importante" tem mais de um sentido.

Numa empresa, quem conhece mais gente não é necessariamente quem faz a
ponte entre dois departamentos, nem quem é próximo da diretoria. Cada
medida faz uma dessas perguntas.

▸ O grau pergunta com quantos colegas ele está ligado. A Carla está
ligada a todos os outros cinco.

▸ A intermediação pergunta por quantos caminhos ele é passagem
obrigatória. Só a Carla: todo caminho até o Diego e a Elisa passa por
ela. É o que chamamos de gargalo.

▸ E o autovetor pergunta se ele está ligado a colegas que também são bem
ligados. Ana, Bruno e Carla quase empatam: são o bloco mais denso.

Os papéis que vimos no contexto, ponte, referência e beirada, vêm da
combinação dessas medidas. Com seis alunos, o sistema chama quase todos
de periféricos; o Felipe é o mais afastado do centro do grupo.

## Comparar com a turma

**Na tela:** `escore-z` · ≈ 1 min 05 s

Falta explicar uma coisa: como o sistema decide que alguém está "abaixo
da turma".

▸ Ele mede em passos. Se a média da sala é 70 e as notas costumam variar
uns 10 pontos, um aluno com 90 está dois passos acima, e um com 60 está um
passo abaixo. Esse passo se chama desvio-padrão, e o número de passos é o
escore z.

▸ O sistema faz essa conta para as três perguntas: quantas disciplinas o
aluno cursa, como vai nas notas e o quanto está ligado ao grupo. E junta
as três com pesos fixos.

▸ A partir de 0,25, o aluno fica em atenção. A partir de 0,5, risco alto.
O Felipe ficou com 0,64.

▸ E por que isso não é aprendizado de máquina: os pesos e os cortes foram
definidos antes de olhar o resultado dos alunos e nunca foram ajustados a
ele. Não tem treino. É conta.

## Do contexto ao nome técnico *(opcional)*

**Na tela:** `dicionario` · ≈ 30 s

Resumindo o que vimos: o aluno é um nó; a ligação é uma aresta; a força é
o peso; o grupo é uma comunidade; a ponte é quem tem a maior
intermediação; e "abaixo da turma" é um escore z negativo. Mesma
história, outros nomes.

---

## Como a pesquisa foi feita

**Na tela:** `sec-3` e `metodo-caracterizacao` · ≈ 50 s

Sobre o método. É uma pesquisa aplicada, porque produz um sistema;
quantitativa, porque tudo é medido; e feita com experimentos no
computador que dão sempre o mesmo resultado quando repetidos.

Usamos duas bases. Uma real e pública, da Open University, uma
universidade inglesa de ensino a distância, com dados anônimos. E uma
turma inventada por um gerador, em que nós plantamos os grupos, para
saber a resposta certa.

▸ E cada pergunta tem um critério. Existe grupo? Comparamos com as redes
embaralhadas. Os grupos são os certos? Comparamos com os grupos plantados.
Quanto custa? Medimos o tempo. Tem relação com o desempenho? Só cruzamos
com o resultado dos alunos depois de tudo.

## Do dado ao resultado

**Na tela:** `pipeline` · *[a sequência começa sozinha, 16 s]* · ≈ 35 s

Aqui está o caminho inteiro, com os nossos seis alunos: a planilha de
matrículas vira o grafo bipartido; a projeção liga os alunos; o Louvain
forma os grupos; e a centralidade aponta a Carla como ponte. É o mesmo
caminho que o sistema faz com seis alunos ou com vinte e dois mil.

---

## O sistema, ao vivo

**Na tela:** `sec-4` · ≈ 5 s

Agora, o sistema funcionando.

**Na tela:** `sinteticos` · ≈ 35 s

Para a demonstração, o sistema gera na hora uma turma inventada de
Computação, com três áreas: desenvolvimento, infraestrutura e dados. Cada
aluno faz duas ou três disciplinas da sua área e, às vezes, uma de fora.

O importante: a área verdadeira de cada aluno fica guardada fora do mapa.
No fim, revelamos e vemos se o sistema acertou.

Um aviso: os nomes dessa turma coincidem com os do nosso exemplo, Ana,
Bruno, Carla, mas são outras pessoas.

**Na tela:** `demo` · *[Enter para entrar]* · ≈ 4 min

*[Tour, lendo só os títulos.]* Esse é o edugraph, rodando aqui neste
computador. Primeiro, um tour rápido do que tem na tela.

*[▶ com Louvain.]* Agora vou apertar para rodar. Primeiro as matrículas:
43 alunos e 8 disciplinas. Depois a projeção: as ligações entre alunos, as
mais grossas dentro de cada área. Agora o algoritmo, juntando os alunos em
grupos; olhem a nota Q subindo ao vivo. E o resultado: três grupos, cada
um já com nome, pelas disciplinas que reúne.

*[Abrir o painel de sinais.]* Aqui está o que vimos no exemplo, numa turma
maior. Este aluno merece atenção, e o sistema escreve por quê: cursa uma
disciplina só, nota abaixo da turma, pouco ligado ao grupo. E do outro
lado, a Alice: nota acima da turma, destaque em Estruturas de Dados,
referência no grupo, uma monitora natural.

*[Revelar.]* E agora a parte que só dá para fazer numa turma inventada:
revelar as áreas que o gerador plantou. O sistema não sabia de nada e
acertou cem por cento dos alunos.

*[Se houver tempo: Girvan–Newman.]* O mesmo com o outro algoritmo: as
pontes somem, uma a uma, e chega nos mesmos grupos, só que bem mais
devagar.

*[Voltar à apresentação pelo botão no topo.]*

## Por dentro do sistema *(candidatos a corte)*

**Na tela:** `arquitetura` · ≈ 35 s

Por dentro, o sistema tem três partes: os dados, as comunidades e as
medidas de centralidade com a interface. Uma regra de projeto: nenhuma
parte usa o código da outra. Elas conversam por arquivos num formato fixo.
Isso deixou o grupo trabalhar em paralelo desde o primeiro dia, e um
teste automático garante que a regra continua valendo.

**Na tela:** `clique` · *[a sequência começa sozinha, 15 s]* · ≈ 30 s

E é isso que acontece quando se aperta o botão: o navegador pede, o
sistema monta a turma, faz a projeção, roda o algoritmo guardando cada
passo, calcula as medidas, e tudo volta numa resposta só, em cerca de um
décimo de segundo. O que vocês viram na demonstração é exatamente o que o
algoritmo fez.

---

## Primeiro resultado: não é por acaso

**Na tela:** `sec-5` e `acaso` · *[a sequência começa sozinha, 15 s]* · ≈ 50 s

Agora os resultados. Primeiro, o teste contra o acaso.

À esquerda, a rede da turma inventada de 98 alunos, com Q de 0,47. Agora
vejam: embaralhamos quem cursou o quê, mantendo quantas disciplinas cada
um faz. As cores se misturam, a estrutura some, e mesmo assim sai um Q de
0,22. Esse é o Q do acaso.

Repetindo cinco vezes, o acaso fica sempre perto de 0,2. A rede real
está muito acima, mais de quinze desvios. Então aqui os grupos são de
verdade. Guardem esse teste, porque na base real ele vai dizer o
contrário.

## A turma inventada: o sistema acerta

**Na tela:** `val-sintetico` · ≈ 50 s

Segunda pergunta: os grupos encontrados são os certos? Na turma inventada
dá para saber, porque nós plantamos as áreas.

▸ O sistema encontra três grupos, e eles batem com as áreas plantadas.
Usamos duas medidas de acerto: a pureza, que é a fração de alunos que
caiu no grupo certo, deu 0,95; e o NMI, que mede de zero a um o quanto
duas divisões concordam, deu 0,82. Isso com 35% de ruído de propósito.

▸ O Girvan–Newman chega à mesma estrutura, só que mais de mil vezes mais
lento.

▸ E quando deixamos 70% dos alunos com uma disciplina só, a concordância
cai pela metade. Guardem isso também: é o que acontece na base real.

## A universidade real

**Na tela:** `oulad` · ≈ 1 min

Na base real, da Open University, o resultado tem duas partes, e a
primeira é negativa.

▸ Ligando os alunos pelas disciplinas, o Q dá 0,77, que parece ótimo. Mas
a rede embaralhada dá 0,78. Ou seja, é igual ao acaso. Por quê? Porque
quase 92% dos alunos cursam um módulo só. Não há ligação para encontrar.
Dizer que achamos grupos ali seria falso, e o sistema disse isso.

▸ Então trocamos a ligação: em vez da disciplina, os materiais que cada
aluno acessou no ambiente virtual. E aí os grupos aparecem: o Q é baixo,
mas de cinco a nove vezes maior que o do acaso, em três turmas
diferentes.

▸ E um achado de método: o jeito de calcular o peso decide se o sinal
aparece. Com o peso da turma lotada, ele aparece; com o peso simples, não.

## O que o mapa nunca viu

**Na tela:** `desfecho` · ≈ 1 min

Agora o momento em que o resultado dos alunos, que ficou guardado à
parte, finalmente entra.

▸ Dividimos os alunos em quatro faixas, dos menos centrais aos mais
centrais na rede. Entre os menos centrais, 89% não concluíram. Entre os
mais centrais, 10,5%. A turma toda tem 43%.

▸ Nas comunidades, o grupo de pouco engajados tem 69% de reprovados ou
desistentes, contra 7% no grupo de engajamento moderado.

▸ E dos 197 alunos que o sistema marcou com risco alto, 94% reprovaram ou
desistiram. Na turma toda, 43%.

▸ Mas precisamos ser honestos: isso não é previsão. Quem desiste para de
acessar o ambiente virtual, então parte desse sinal aparece porque o aluno
já está indo embora. O sistema aponta onde olhar. Para falar em
antecipar, seria preciso usar só as primeiras semanas, e isso fica como
trabalho futuro.

## As disciplinas que ligam o currículo

**Na tela:** `criticas` · ≈ 30 s

O último resultado olha para as disciplinas, com a mesma ideia de
centralidade.

▸ As três medidas apontam disciplinas diferentes. Ser muito cursada e ser
ponte entre áreas são coisas diferentes.

▸ E as disciplinas que mais fazem ponte não são as que mais reprovam: a
taxa delas fica só um ponto acima da média. Ou seja, a disciplina que
mais conecta o currículo não é a disciplina difícil. É um ponto de
passagem.

---

## O que concluímos

**Na tela:** `sec-6` e `conclusao` · ≈ 1 min

Voltando à pergunta: dá para encontrar esses padrões só com as ligações,
sem inteligência artificial, de um jeito que se possa conferir? Sim, com
uma condição: o sinal precisa existir nos dados.

▸ ▸ ▸ ▸ Montamos e projetamos o grafo com implementações nossas,
conferidas com uma biblioteca de referência. Na turma inventada, o
sistema encontra os grupos plantados. As medidas de centralidade
discordam, e isso também é informação. E na base real o sinal está no
comportamento, não na matrícula, e o sistema soube dizer quando não havia
grupo.

E o mesmo mapa aponta quem merece atenção e quem se destaca, sempre com o
motivo escrito. Essa é a contribuição: resultados que a instituição
consegue ler, explicar e conferir.

## O que fica para depois

**Na tela:** `limites-futuro` · ≈ 35 s

Preferimos mostrar os limites antes de alguém perguntar.

▸ O principal: não é previsão de evasão; o próximo passo é usar só as
primeiras semanas. ▸ O sinal real é fraco em valor absoluto. ▸ O
Girvan–Newman não dá conta da base inteira. ▸ A nota mínima para contar
uma matrícula deixa de fora justamente quem mais reprova. ▸ E o sistema
foi feito para rodar na máquina da instituição, sem login.

E um próximo passo natural: testar com dados de uma instituição
brasileira.

## Referências e encerramento

**Na tela:** `referencias` · ≈ 10 s

Essas são as referências do trabalho, incluindo o relatório do Inep que
usamos no começo.

**Na tela:** `encerramento` · ≈ 15 s

Agradecemos a atenção de todos e ao nosso orientador. Ficamos à
disposição para as perguntas.

---

## Se perguntarem

Respostas curtas, no mesmo tom. Os detalhes técnicos estão no apêndice
(tecla A).

**"Então o sistema diz quem vai desistir?"**
Não. Ele diz quem está se afastando da turma e por quê. Quem decide o que
fazer é a instituição.

**"Por que não usar inteligência artificial, que talvez acertasse mais?"**
Talvez acertasse, mas não explicaria por quê. Para um coordenador chamar
um aluno para conversar, ele precisa saber o motivo. E o trabalho quis
mostrar que dá para chegar lá só com as ligações.

**"Esse cálculo de risco não é aprendizado de máquina?"**
Não. Não há treino: os pesos e os cortes foram fixados antes de olhar o
resultado dos alunos, e o resultado só entra na conferência. *[Apêndice:
`a-sinais`.]*

**"Não é injusto marcar um aluno como risco?"**
Por isso a palavra é "atenção", e por isso o motivo vem escrito. É um
convite para conversar, não um rótulo.

**"Dois alunos com notas parecidas ficam ligados?"**
Não. A ligação vem de cursar as mesmas disciplinas, ou de acessar os
mesmos materiais. A nota entra depois, para dizer quem merece atenção e
quem se destaca. A Carla e o Felipe têm notas parecidas e estão em
situações bem diferentes.

**"60% de evasão não é exagero?"**
É o número do Inep para quem entrou em 2015 e foi acompanhado por dez
anos. Ele conta quem deixou o curso em que entrou, inclusive quem só
trocou de curso. Por isso falamos em "deixaram o curso".

**"Os dados dos alunos estão expostos?"**
Os dados reais são públicos e anônimos, da Open University. Os alunos com
nome são inventados.

**"Funciona na UniAnchieta?"**
O método funciona com qualquer lista de matrículas. Testar com dados de
uma instituição brasileira é o próximo passo natural.

**"Por que a Carla, que é de Elétrica, ficou no grupo de ADS?"**
Porque o sistema não sabe o curso de ninguém. Ele agrupa por com quem
cada um estuda, e a Carla faz as disciplinas de computação com a Ana e o
Bruno.

---

## Tempo estimado

| Parte | Tópicos | Tempo |
|---|---|---|
| Abertura e caminho | Abertura, sumário | ≈ 1 min |
| Contexto e solução | do "aluno que some" à "nossa solução" | ≈ 11 min |
| Pergunta e objetivos | | ≈ 1 min 15 s |
| Nomes técnicos | do "grafo" ao "comparar com a turma" | ≈ 8 min (+ 20 s do dicionário) |
| Método | | ≈ 1 min 10 s |
| Sistema ao vivo | turma inventada e demonstração | ≈ 4 min 30 s |
| Por dentro (cortável) | arquitetura, clique | ≈ 50 s |
| Resultados | | ≈ 4 min |
| Conclusão e encerramento | | ≈ 1 min 45 s |
| **Total** | | **≈ 34 min** (≈ 33 min sem os cortáveis) |

Contado pelas palavras da fala (≈ 4.200, a 140 por minuto), mais os 4
minutos da demonstração.

Ficou maior que os 15 a 20 minutos de hoje. O grupo decidiu manter o
contexto inteiro e ajustar quando souber o tempo da defesa. Quando
souber, por ordem de corte:

1. `dicionario` e "por dentro do sistema" (≈ 1 min 10 s);
2. o Girvan–Newman na demonstração (≈ 40 s);
3. nos nomes técnicos, um exemplo do dia a dia por slide, não dois
   (≈ 2 min);
4. no contexto, enxugar a fala sem tirar tópico: cada tópico com uma
   ideia e um exemplo (de ≈ 11 para ≈ 7 min, a estimativa da narrativa);
5. só como último recurso: juntar "nem toda ligação é igual" ao slide da
   ligação, e tirar o passo do ensino a distância do Inep.

Cronometrar no primeiro ensaio: a estimativa pode errar para mais ou para
menos.
