# Como explicamos o projeto: o contexto e a solução

> **Para que serve este arquivo:** é o texto-base de **como contamos o
> trabalho** para qualquer pessoa, da área de tecnologia ou não, antes de
> entrar no grafo e nos algoritmos. Primeiro refinamos as ideias aqui;
> depois elas são levadas para a apresentação que já está montada.
>
> **Regra do texto:** até a seção 9, nenhum termo técnico. Nada de
> "grafo", "nó", "aresta", "algoritmo", "modularidade" ou "centralidade".
> Só palavras do dia a dia: *ligação*, *rede*, *comunidade*, *ponte*,
> *atenção*, *talento*. Na seção 9 os termos técnicos entram, e **cada um
> é explicado**, com exemplo do dia a dia e com os seis alunos.
>
> **Arquivos que saem deste:** [`PLANO-AJUSTE.md`](PLANO-AJUSTE.md), o
> que mudar nos slides, e [`ENREDO.md`](ENREDO.md), o texto falado no dia.
>
> **Regra das siglas:** toda sigla aparece **por extenso na primeira vez**,
> no texto e no slide, com a sigla entre parênteses, por exemplo
> "Análise e Desenvolvimento de Sistemas (ADS)". Se a sigla não for
> necessária para a plateia, como as do relatório do Inep, fica só a
> explicação em palavras. As siglas deste texto estão explicadas na seção
> "Siglas", no fim.

---

## 1. O projeto em poucas frases

**Em uma frase:**
> Montamos um mapa das ligações entre os alunos, a partir das disciplinas
> que eles cursam, para mostrar à instituição quais grupos existem, quem
> está se afastando e quem se destaca, sempre com o motivo explicado.

**Em um parágrafo:**
> Toda instituição de ensino sabe em que disciplinas cada aluno se
> matriculou e como ele foi em cada uma. Normalmente esses dados são lidos
> aluno por aluno, numa planilha. Nós olhamos para eles de outro jeito:
> pelas **relações** entre os alunos. Dois alunos que cursam a mesma
> disciplina têm uma ligação. Juntando todas as ligações, aparece um mapa
> da turma, e nele aparecem grupos naturais de alunos parecidos, alunos que
> fazem a ponte entre grupos, alunos que estão isolados e alunos que se
> destacam. O sistema que construímos monta esse mapa sozinho e aponta para
> a instituição **onde olhar primeiro**. Tudo isso sem inteligência
> artificial: cada conclusão pode ser conferida à mão.

---

## 2. O problema: o aluno que some

Todo semestre alguns alunos desaparecem. Primeiro faltam, depois deixam de
entregar trabalhos, depois deixam de acessar o ambiente virtual. A
instituição costuma perceber só no fim, quando sai a nota final ou chega o
pedido de trancamento, e aí já é tarde para ajudar.

Só que os sinais estavam lá antes. A instituição já guarda:

- **em que disciplinas** cada aluno se matriculou;
- **que nota** ele teve em cada uma;
- no ensino a distância, **o que ele acessou** no ambiente virtual.

O problema não é falta de dados. É que esses dados são lidos como uma
lista, um aluno de cada vez. Numa lista, ninguém vê que um aluno está
**sozinho**: que não divide disciplina com quase ninguém, que ficou fora
do grupo de colegas com quem começou. Isso só aparece quando olhamos para
as **relações entre os alunos**.

### O tamanho do problema, em números

> **De cada 10 alunos que entraram na graduação em 2015, 6 deixaram o
> curso em que ingressaram. Quase 3 já tinham saído até o fim do segundo
> ano.**
> *Fonte: Instituto Nacional de Estudos e Pesquisas Educacionais Anísio
> Teixeira (Inep), Resumo técnico do Censo da Educação Superior 2024.*

O Inep é o órgão do Ministério da Educação que faz o Censo da Educação
Superior, a pesquisa anual que todas as faculdades e universidades do
país são obrigadas a responder. No slide, basta "Inep, órgão do
Ministério da Educação"; o nome completo fica na referência.

A segunda frase é a que sustenta o argumento: a saída acontece **cedo**,
justamente quando ainda daria para agir. Se couber, um complemento que
conversa com a nossa base real (ensino a distância): **no ensino a
distância, a desistência chega a 65%**, contra 59% no presencial.

Números conferidos no próprio relatório do Inep (turma que entrou em
2015, acompanhada até 2024):

| Indicador | Valor | Onde está no relatório |
|---|---|---|
| Deixaram o curso em que entraram | **60%** (39% concluíram; 1% ainda cursa) | Gráfico 15, p. 33; texto na p. 34 |
| Desistência acumulada no 1º ano | 13% | Gráfico 15, p. 33 |
| Até o 2º ano | 29% | Gráfico 15, p. 33 |
| Até o 3º ano | 40% | Gráfico 15, p. 33 |
| A distância × presencial (10 anos) | **65% × 59%** | Gráfico 18, p. 36 |
| A distância × presencial (1º ano) | 16% × 12% | Gráfico 18, p. 36 |
| Rede privada × pública (10 anos) | 62% × 53% | Gráfico 17, p. 35 |

O relatório também diz, na p. 34, que a desistência cresce mais depressa
até o quarto ano de acompanhamento. (No original: "o ritmo de aumento da
TDA é maior até o quarto ano"; TDA é a sigla que o Inep usa para **Taxa
de Desistência Acumulada**, a porcentagem da turma de entrada que já
deixou o curso até aquele ano. Na apresentação, não usar a sigla: dizer
"desistência".) Os números de página são os impressos no rodapé do
relatório.

**Três cuidados com esse número:**

1. **"Deixou o curso" não é "abandonou o ensino superior".** Pela
   definição do Inep (nota 5, p. 34), a Taxa de Desistência Acumulada
   (TDA) conta quem se desvinculou **ou foi transferido** do curso em que
   entrou. Quem trocou de curso também está nos 60%. Na fala: *"deixaram
   o curso em que ingressaram"*.
2. **Não chamar de "estatística oficial".** Na p. 32, o próprio Inep
   avisa que os indicadores de trajetória "resultam de tratamento de
   bases de dados, não correspondendo às estatísticas oficiais". Dizer
   *"segundo o Inep"* ou *"indicadores de trajetória do Inep"*.
3. **Não misturar fontes.** Os números que circulam na imprensa (41,6% a
   distância e 24,8% presencial, por exemplo) costumam vir do Mapa do
   Ensino Superior do Semesp (Sindicato das Entidades Mantenedoras de
   Estabelecimentos de Ensino Superior no Estado de São Paulo, que
   representa as faculdades particulares), que mede evasão **anual**, com outra
   metodologia. Algumas matérias também trocam 59% (desistência no
   presencial) por 34% (conclusão a distância). Usar só a tabela acima.

---

## 3. O exemplo que usamos do começo ao fim

Para explicar, usamos uma universidade pequena, inventada: **seis alunos
de dois cursos, Análise e Desenvolvimento de Sistemas (ADS) e Engenharia
Elétrica, e três disciplinas.**

| Aluno | Curso | Disciplinas que cursa (nota) |
|---|---|---|
| **Ana** | ADS | Sistemas de Computação (82), Algoritmos e Programação (71) |
| **Bruno** | ADS | Sistemas de Computação (64), Algoritmos e Programação (90) |
| **Carla** | Engenharia Elétrica | Sistemas de Computação (77), Algoritmos e Programação (68), Circuitos Elétricos (61) |
| **Diego** | Engenharia Elétrica | Circuitos Elétricos (85) |
| **Elisa** | Engenharia Elétrica | Circuitos Elétricos (73) |
| **Felipe** | ADS | Sistemas de Computação (66) |

Duas coisas desta tabela vão importar mais adiante:

- **o Felipe, neste semestre, está matriculado numa disciplina só**, e
  justamente na mais cheia;
- **o Diego e a Elisa só fazem Circuitos Elétricos**: a única colega que
  eles têm em comum com o resto da turma é a Carla.

Não é um exemplo de enfeite: são os mesmos seis alunos e três disciplinas
do caso de teste do sistema (`tiny_v1`), cujos valores o grupo conferiu
no papel. Só ganharam nomes e cursos. Por isso, quando a apresentação
chegar à parte técnica, **o desenho é o mesmo**: quem entendeu a história
já conhece o grafo.

**Por que este exemplo, e não outro.** Avaliamos alternativas (uma turma
de um curso só, como a da demonstração; disciplinas de outras áreas) e
ficamos com este por três motivos:

1. É a **dica do professor**: alunos de ADS e de Engenharia Elétrica que se
   encontram em Sistemas de Computação. Uma disciplina compartilhada por
   dois cursos é o jeito mais natural de mostrar que a ligação não depende
   do curso.
2. Ele mostra, com só seis pessoas, **tudo o que queremos explicar**:
   ligação, força da ligação, comunidade diferente do curso (a Carla),
   ponte (a Carla de novo), beirada e atenção (o Felipe), um grupo pequeno
   que depende de uma pessoa só (Diego e Elisa).
3. **Os números são conferidos.** Cada peso, cada grupo e cada medida do
   exemplo foi calculado no papel pelo grupo e é exigido pelos testes.

A ordem dos nomes também ajuda: **a inicial segue a numeração do caso de
teste** (aluno 1 é a Ana, 2 o Bruno, 3 a Carla, 4 o Diego, 5 a Elisa, 6 o
Felipe), e as disciplinas A, B e C do caso de teste são, na ordem,
Sistemas de Computação, Algoritmos e Programação e Circuitos Elétricos.

> **Cuidado na demonstração:** a turma fictícia do sistema usa os mesmos
> primeiros nomes (Ana, Bruno, Carla…) seguidos de uma inicial, mas são
> **outras pessoas**, com outros papéis. Na turma padrão, por exemplo, a
> "Carla N." está em risco alto, e não é a ponte. Na demonstração, citar
> sempre o nome com a inicial e dizer que é outra turma.

---

## 4. Os conceitos, na linguagem do dia a dia

### Ligação

> Numa universidade, alunos de cursos diferentes podem se inscrever na
> mesma disciplina. A Ana, de ADS, e a Carla, de Engenharia Elétrica,
> cursam as duas **Sistemas de Computação**. Isso cria uma **ligação**
> entre elas.

É a ideia mais importante de todas, e a mais simples: **dividir uma
disciplina liga dois alunos.** Nenhuma ligação é inventada. Cada uma vem
de um registro de matrícula.

### Força da ligação

Nem toda ligação é igual.

- **Quanto mais disciplinas em comum, mais forte.** A Ana e o Bruno
  dividem duas disciplinas; a Ana e o Felipe, só uma. A ligação entre Ana
  e Bruno é mais forte.
- **Dividir uma turma pequena diz mais do que dividir uma turma lotada.**
  Estar junto numa disciplina de 300 alunos quase não diz nada sobre duas
  pessoas. Estar junto numa de 15 diz bastante. O sistema leva isso em
  conta: Sistemas de Computação tem quatro alunos, a mais cheia do
  exemplo, então conta um pouco menos que as outras.

### Rede

> Quando juntamos todas as ligações, temos um **mapa da turma**: quem está
> ligado a quem, e com que força. É isso que chamamos de **rede**.

No exemplo, o mapa mostra que a Ana, o Bruno e a Carla estão muito ligados
entre si; o Diego e a Elisa estão ligados entre si e à Carla; e o Felipe
está ligado aos três primeiros, mas fraco.

### Comunidade

> Olhando o mapa, aparecem **grupos de alunos muito ligados entre si e
> pouco ligados ao resto**. Cada grupo é uma **comunidade**.

Alunos que cursam as mesmas disciplinas e têm muitos colegas em comum
acabam na mesma comunidade. No exemplo, são duas:

- **Ana, Bruno, Carla e Felipe**, o grupo de Sistemas e Algoritmos;
- **Diego e Elisa**, o grupo de Circuitos.

Aqui há uma surpresa que vale contar: **a Carla é de Engenharia Elétrica,
mas ficou no grupo de ADS.** O sistema não sabe o curso de ninguém. A
comunidade não mostra o rótulo da matrícula, e sim a **afinidade real**:
com quem cada aluno de fato estuda. Ninguém disse ao sistema quantos
grupos existem nem quem é de qual. Ele descobriu sozinho, só pelas
ligações.

### O papel de cada aluno no mapa

Dentro do mapa, cada aluno ocupa um lugar diferente:

- **Ponte:** liga grupos que, sem ele, ficariam separados. A Carla é a
  ponte do exemplo. Se ela sair, o Diego e a Elisa ficam desligados de
  todo o resto.
- **Referência:** muito ligado dentro do próprio grupo; é quem os colegas
  "rodeiam". Aparece em turmas maiores, como a da demonstração.
- **Beirada:** poucas ligações, e fracas. É o Felipe: ele divide só uma
  disciplina, justamente a mais cheia.

Esse papel importa porque diz coisas que a nota não diz. Um aluno pode ter
nota boa e estar isolado; outro pode ter nota mediana e ser a ponte que
mantém dois grupos conversando.

---

## 5. Quem merece atenção e quem pode se destacar

Com o mapa pronto, o sistema olha cada aluno e faz três perguntas, sempre
**comparando com a turma**:

1. **Quantas disciplinas ele cursa?** Bem menos que os colegas é sinal de
   afastamento.
2. **Como está o desempenho dele?** A nota média dele contra a média da
   turma (no ensino a distância, o quanto ele usa o ambiente virtual).
3. **O quanto ele está ligado ao próprio grupo?** Estar na comunidade, mas
   na beirada dela, é diferente de estar no centro.

### Quem merece atenção

> É o aluno que fica abaixo da turma em várias dessas perguntas ao mesmo
> tempo: cursa pouco, vai mal e está pouco ligado ao grupo.

No exemplo, é o **Felipe**. E isso não é uma suposição nossa: rodando o
sistema sobre esses seis alunos, ele aparece em **risco alto**, e o sistema
escreve o motivo com estas palavras:

> *"nota média 66, abaixo da turma (74)"* · *"pouco ligado ao próprio
> grupo"*

O sistema não diz que o Felipe vai desistir. Diz que **alguém deveria
conversar com ele**.

O Diego e a Elisa aparecem num nível mais leve, **"em atenção"**: o grupo
deles tem só dois alunos e depende da Carla para se ligar ao resto da
turma. Aqui o sinal é sobre o **grupo**, não sobre a nota de cada um (os
dois vão bem: 85 e 73). É o tipo de caso em que a ação faz sentido para o
grupo inteiro. (O texto que o sistema escreve para eles hoje, "ficou num
grupo só dele", está impreciso para um grupo de dois; está registrado
como pendência T-OBS-06.)

Numa turma maior, a da demonstração, o aluno em risco alto aparece com
os três motivos juntos:

> *"cursa só 1 disciplina (média da turma: 2,16)"* · *"nota média 52,
> abaixo da turma (70)"* · *"pouco ligado ao próprio grupo"*

### Quem pode se destacar

O mesmo mapa mostra o outro lado: alunos acima da turma, ou que se
destacam numa disciplina, ou que fazem a ponte entre grupos sem perder
desempenho. Na turma fictícia da demonstração (valores padrão do
laboratório: 43 alunos, 8 em risco alto, 4 em atenção e 12 possíveis
talentos), o sistema aponta, por exemplo:

> **Alice T.:** *"nota média 82, acima da turma (70)"* · *"se destaca em
> Estruturas de Dados"* · *"é referência no próprio grupo: pode apoiar
> colegas como monitor"*
>
> **Larissa J.:** *"se destaca em Redes de Computadores"* · *"liga grupos
> diferentes sem perder desempenho"*

> **Nota para o grupo:** no exemplo dos seis alunos o sistema não marca
> nenhum talento, porque ele só aponta "se destaca numa disciplina" quando
> ela tem pelo menos 6 alunos. Por isso o exemplo de talento vem da turma
> da demonstração. O Bruno (90 em Algoritmos) pode ser citado como "o tipo
> de aluno que procuramos", mas sem dizer que o sistema o marcou.

---

## 6. Por que procurar esses alunos dentro da comunidade

Esta é a parte que responde ao **"para quê"**, e precisa ficar clara para
qualquer pessoa.

**A comunidade dá o contexto que a nota sozinha não dá.**
Uma nota 66 não diz muita coisa sozinha. Uma nota 66 de um aluno que cursa
uma disciplina só, numa turma lotada, e que está na beirada do grupo com
quem deveria estar estudando conta outra história. O sinal fica mais
claro quando juntamos o desempenho e o lugar do aluno na rede.

**Ela mostra o isolamento, que é o que vem antes da desistência.**
O aluno que vai se afastando do curso costuma se afastar antes dos
colegas: cursa menos, divide menos, fica na beirada. Numa planilha isso
não aparece. No mapa, aparece.

**Ela permite agir no grupo, não só no aluno.**
Às vezes o problema não é de uma pessoa, é de um grupo inteiro. Na base
real que usamos, o sistema separou os alunos por nível de engajamento, e
o grupo que ele chamou de "Pouco engajados" tinha **69% de reprovados ou
desistentes, contra 7% no grupo de engajamento moderado**. E o sistema
nunca viu a nota final. Para a instituição, isso indica onde uma ação
coletiva faz sentido: reforço, tutoria, mudança na disciplina.

**Ela transforma talento em apoio.**
Um aluno que é referência no próprio grupo é o candidato natural a
**monitor** daquele grupo, porque os colegas já estudam com ele. Um aluno
que é ponte entre grupos é alguém que circula bem. São bons nomes para
monitoria, iniciação científica e bolsas.

**Na prática, para a instituição:**

| Quem | O que faz com o mapa |
|---|---|
| Coordenação | Vê quais grupos existem de fato e quais estão em dificuldade |
| Tutoria / apoio ao aluno | Sabe com quem conversar primeiro, e já sabe o motivo |
| Professores | Encontram monitores dentro dos grupos que precisam de ajuda |
| Instituição | Age antes da nota final, não depois |

---

## 7. A solução que propomos: o edugraph

> **Entra** a lista de matrículas (e, quando há, os acessos ao ambiente
> virtual). **Sai** o mapa da turma, com:
>
> - os **grupos** já com nome, pelas disciplinas que cada um reúne;
> - o **papel** de cada aluno: ponte, referência, beirada;
> - **quem merece atenção**, com o motivo escrito;
> - **quem pode se destacar**, com o motivo escrito.

Além disso, o sistema mostra **como chegou ao resultado**: no laboratório
ao vivo, dá para ver o mapa sendo montado e os grupos se formando passo a
passo. Não é animação ilustrativa: é o que o sistema fez de verdade.

### Por que sem inteligência artificial

O edugraph não usa aprendizado de máquina: nenhum modelo é treinado com
dados do passado. Tudo sai de contar ligações e comparar cada aluno com a
própria turma.

- **Nenhum modelo aprendeu com o passado de ninguém.** O sistema só conta
  ligações e compara cada aluno com a turma. As regras foram fixadas antes
  de olhar o resultado dos alunos.
- **Todo alerta tem um porquê.** Em vez de "este aluno tem 73% de chance
  de evadir", o sistema diz "cursa uma disciplina só, nota abaixo da
  turma, pouco ligado ao grupo". A coordenação pode concordar, discordar
  ou conferir.
- **Dá para refazer a conta à mão.** Foi o que o grupo fez com o exemplo
  dos seis alunos, e o sistema é testado contra essas contas.
- **O desfecho do aluno fica fora do mapa.** Se ele aprovou, reprovou ou
  desistiu fica guardado à parte e só entra no fim, para conferir se o
  mapa acertou. Se entrasse antes, o sistema estaria "colando". (A nota de
  cada disciplina entra, como força da matrícula, e é por isso que o
  alerta pode dizer "nota média 66"; o que fica fora é o desfecho final.)

---

## 8. Funciona? O que dá para dizer, com honestidade

Também em linguagem simples, antes dos números técnicos:

- **Numa turma inventada, em que nós sabíamos a resposta**, o sistema
  encontrou os grupos certos. Na demonstração, as três áreas da turma de
  Computação foram reencontradas para 100% dos alunos, sem o sistema saber
  quais eram.
- **Numa universidade de verdade**, a Open University, do Reino Unido, com
  ensino a distância e dados públicos e anônimos, aprendemos duas coisas:
  - **Só a matrícula não basta**: quase todos os alunos (91,8%) cursavam
    um módulo só, então quase não havia ligações. O sistema disse isso com
    honestidade: "aqui não há grupos".
  - **O comportamento no ambiente virtual, sim**: ligando alunos pelos
    materiais que acessaram, os grupos apareceram. Dos 197 alunos que o
    sistema marcou com risco alto, **94% reprovaram ou desistiram** (na
    turma toda, 43%).
- **E o cuidado que sempre vai junto:** isso **não é previsão**. Quem
  desiste para de acessar, então parte desse sinal aparece porque o aluno
  já está saindo. O sistema **aponta onde olhar**. Para falar em
  antecipar a evasão, seria preciso usar só as primeiras semanas, e isso
  fica como trabalho futuro.

---

## 9. A parte técnica, explicada

Só depois de tudo isso entram os nomes técnicos. A plateia já entendeu as
ideias; agora cada uma ganha o nome que tem na Teoria dos Grafos, e **cada
nome vem explicado**, com um exemplo do dia a dia e com os seis alunos.
Quem não é da área precisa sair sabendo com o que o sistema trabalha, não
só ouvir os nomes.

A frase de passagem pode ser: *"Agora vamos ver como o sistema faz isso.
É o mesmo exemplo dos seis alunos; só que agora cada coisa ganha o nome
técnico, e vamos explicar cada um."*

### 9.1 Grafo

**Em uma frase:** um grafo é um conjunto de **pontos** ligados por
**linhas**; os pontos são as coisas, e as linhas dizem quem está ligado a
quem.

**No dia a dia:** o mapa do metrô é um grafo. Cada estação é um ponto,
cada trecho de trilho entre duas estações é uma linha. O mapa não mostra
a distância real nem as ruas; mostra só **o que se liga com o quê**, e é
isso que permite responder "dá para ir daqui até lá?" ou "por qual
estação todo mundo passa?". Outro exemplo: uma rede de amigos, em que
cada pessoa é um ponto e cada amizade é uma linha.

**Os nomes:** cada ponto se chama **nó** (ou vértice), e cada linha se
chama **aresta**. Uma aresta pode ter um **peso**, um número que diz o
quanto aquela ligação é forte (no metrô, poderia ser o tempo de viagem).

**No nosso exemplo:** os alunos são nós, e "a Ana e a Carla cursam a mesma
disciplina" é uma aresta.

> Grafo, aqui, **não é gráfico** (de barras ou de linha). A palavra é
> parecida, a ideia é outra: grafo é um mapa de ligações. Vale dizer isso
> em voz alta.

### 9.2 Grafo bipartido

**Em uma frase:** é um grafo com **dois tipos de nó**, em que as arestas
só ligam um tipo ao outro, nunca dois do mesmo tipo.

**No dia a dia:** pessoas e filmes num serviço de vídeo. Uma linha liga a
pessoa ao filme que ela assistiu. Pessoa não se liga direto a pessoa, nem
filme a filme.

**No nosso exemplo:** de um lado os seis alunos, do outro as três
disciplinas; cada matrícula é uma aresta. São 10 matrículas. A Carla é a
única ligada às três disciplinas; Sistemas de Computação é a disciplina
com mais alunos (quatro).

**Por que começar por ele:** é exatamente o formato em que a instituição
guarda os dados (a lista de matrículas). Nada é inventado nessa etapa.
Mas, nele, a relação entre dois alunos ainda está **escondida**: ela
passa pela disciplina.

### 9.3 Projeção

**Em uma frase:** projetar é tirar um dos tipos de nó do desenho e ligar
diretamente os do outro tipo que tinham alguma coisa em comum.

**No dia a dia:** é a lógica do "quem assistiu a este filme também
assistiu a…". A partir de "quem viu o quê", liga-se duas pessoas que
viram os mesmos filmes. O artigo que usamos para os pesos (Zhou e
colegas, 2007) vem justamente da área de recomendação.

**No nosso exemplo:** as disciplinas saem e ficam só os alunos. A Ana e a
Carla ficam ligadas porque dividem Sistemas de Computação (e também
Algoritmos). Essa nova rede, só de alunos, é a que os algoritmos leem. O
mesmo pode ser feito do outro lado: uma rede só de disciplinas, ligadas
quando têm alunos em comum (é ela que mostra as disciplinas-ponte do
currículo).

### 9.4 Peso da ligação

**Em uma frase:** o peso é o número que diz o quanto dois alunos estão
ligados. Usamos duas formas de calcular.

- **Peso simples:** conta as disciplinas em comum. Ana e Bruno dividem
  duas disciplinas: peso 2. Ana e Felipe dividem uma: peso 1.
- **Alocação de recursos:** cada disciplina vale **1 dividido pelo número
  de alunos dela**. Sistemas de Computação tem 4 alunos e vale ¼;
  Algoritmos e Circuitos têm 3 e valem ⅓. Ana e Bruno ficam com
  ¼ + ⅓ ≈ 0,58; Ana e Felipe, só com ¼ = 0,25.

**Por que a segunda existe:** é a ideia da "turma lotada" da seção 4.
Dividir uma disciplina que todo mundo cursa diz pouco sobre duas pessoas;
dividir uma rara diz muito. Na base real, essa escolha decidiu se o sinal
aparecia ou não.

### 9.5 Comunidade e modularidade (*Q*)

**Comunidade**, no sentido técnico, é o mesmo que explicamos antes: um
grupo de nós **muito ligados entre si e pouco ligados ao resto**.

O problema é que existem muitas formas de dividir uma rede em grupos.
Para saber se uma divisão é boa, usamos uma nota chamada **modularidade**,
representada pela letra ***Q***.

**Em uma frase:** *Q* mede quanto das ligações fica **dentro** dos grupos,
descontado o quanto ficaria lá **por sorte**.

**No dia a dia:** imagine uma festa em que as pessoas foram separadas em
mesas. Se quase todas as conversas acontecem dentro das mesas, a divisão
faz sentido. Se as pessoas conversam com qualquer mesa igualmente, as
mesas não querem dizer nada. *Q* é a nota dessa divisão.

**Como ler o número:** perto de 0, a divisão não é melhor que sortear;
acima de 0,3, costuma indicar grupos bem definidos. É uma **regra
prática**: quem decide é o teste contra o acaso (9.6). Na base real, um
*Q* de 0,77 não passou nesse teste e um de 0,08 passou. No exemplo, a divisão
{Ana, Bruno, Carla, Felipe} e {Diego, Elisa} tem *Q* = 0,11 (com seis
alunos, o número fica baixo mesmo). Na turma da demonstração, 0,53.

### 9.6 O teste contra o acaso (modelo nulo)

**Em uma frase:** antes de confiar num *Q*, comparamos com redes
**embaralhadas** de propósito, para ver se o acaso daria o mesmo número.

**No dia a dia:** é como conferir se um dado está viciado: joga-se muitas
vezes e compara-se com o que um dado honesto daria.

**Como fazemos:** sorteamos de novo quem cursou o quê, mas **mantendo
quantas disciplinas cada aluno faz e quantos alunos cada disciplina
tem**. Nessa rede sorteada não existe grupo de verdade. Se ela também der
um *Q* alto, o *Q* da rede real não prova nada. Fazemos pelo menos 5
sorteios e só aceitamos a estrutura se o *Q* real ficar **3 desvios
acima** dos sorteados (o "desvio" está explicado em 9.10).

**Por que importa:** foi esse teste que mostrou que, na base real, a
matrícula sozinha não forma grupos (o *Q* real e o sorteado deram quase o
mesmo).

### 9.7 Os dois algoritmos que encontram as comunidades

Um **algoritmo** é uma receita de passos que o computador segue. Usamos
dois, que fazem o caminho contrário um do outro:

- **Louvain (juntar).** Cada aluno começa sozinho no próprio grupo. Um de
  cada vez, ele muda para o grupo vizinho em que a nota *Q* mais sobe. O
  processo para quando ninguém mais quer mudar. É como a festa em que cada
  pessoa vai trocando de mesa até ficar na mesa em que mais conversa. No
  exemplo, são 4 movimentos e o resultado são os dois grupos.
- **Girvan–Newman (cortar).** Começa com a rede inteira e procura a
  ligação **mais usada como passagem**, aquela por onde passam mais
  caminhos entre todos os pares de alunos. Apaga essa ligação e repete.
  Aos poucos a rede se parte, e o algoritmo fica com o corte de maior
  *Q*. No exemplo, as primeiras ligações cortadas são Carla–Diego e
  Carla–Elisa, e a rede se parte nos mesmos dois grupos do Louvain.

**Por que dois:** se dois métodos com lógicas opostas chegam aos mesmos
grupos, o resultado é da estrutura dos dados, não de um algoritmo. O
Louvain é muito mais rápido (na demonstração, cerca de 1 milésimo de
segundo contra meio segundo).

### 9.8 Centralidade

**Em uma frase:** centralidade é uma medida de **quão importante** é um
nó na rede. Só que "importante" tem mais de um sentido, e cada medida faz
uma pergunta diferente:

| Medida | Pergunta | No exemplo |
|---|---|---|
| **Grau** | Com quantos colegas ele está ligado? | A Carla está ligada aos outros cinco; é o maior grau. |
| **Intermediação** | Por quantos caminhos entre outros alunos ele é passagem obrigatória? | Só a Carla: todo caminho até Diego e Elisa passa por ela. É o que chamamos de **gargalo**. |
| **Autovetor** | Ele está ligado a colegas que também são bem ligados? | Ana, Bruno e Carla quase empatam: formam o bloco mais denso. O Felipe fica abaixo, e Diego e Elisa bem abaixo. |

**No dia a dia:** numa empresa, quem conhece mais gente (grau) não é
necessariamente quem faz a ponte entre dois departamentos
(intermediação), nem quem é próximo da diretoria (autovetor).

Com a rede de disciplinas, a mesma ideia encontra as **disciplinas-ponte
do currículo**, por onde passam alunos de áreas diferentes.

### 9.9 O papel de cada aluno (ponte, referência, periférico)

Os papéis da seção 4 também têm nome técnico. Eles combinam duas medidas,
de Guimerà e Amaral (2005):

- o quanto o aluno está ligado **dentro do próprio grupo**, comparado com
  os colegas do grupo;
- o quanto as ligações dele se **espalham por outros grupos**, comparado
  com os colegas do próprio grupo (por isso Diego e Elisa, com metade das
  ligações para fora, mas iguais um ao outro, não contam como "espalhados").

| Papel no sistema | Dentro do grupo | Para fora | No exemplo |
|---|---|---|---|
| Referência do grupo | muito ligado | pouco | não aparece (turma pequena demais) |
| Conector | muito ligado | espalhado | não aparece |
| Ponte | pouco | espalhado | a Carla |
| Periférico | pouco | pouco | os outros cinco |

> **Honestidade com o exemplo:** com só seis alunos, o sistema classifica
> cinco deles como "periféricos". O que chamamos de "beirada" no contexto
> é o mais afastado do centro do grupo: o Felipe, com a menor ligação
> dentro do grupo de toda a turma. Nos slides técnicos, usar o nome do
> sistema, "periférico", e dizer isso.

### 9.10 "Comparado com a turma": o escore *z*

**Em uma frase:** o escore *z* diz **quantos "passos típicos"** um valor
está acima ou abaixo da média da turma.

**No dia a dia:** se a média da sala é 70 e as notas costumam variar uns
10 pontos para cima ou para baixo, um aluno com 90 está 2 passos acima
(z = +2), e um aluno com 60 está 1 passo abaixo (z = −1). O "passo típico"
tem nome: **desvio-padrão**.

**Para que serve aqui:** é assim que o sistema decide "abaixo da turma" e
"acima da turma" sem número mágico. Ele calcula o *z* de cada aluno em
três coisas (as três perguntas da seção 5):

- **carga:** quantas disciplinas cursa;
- **desempenho:** a nota de cada matrícula frente à média da disciplina
  (na base real, a atividade no ambiente virtual);
- **vínculo:** o quanto está ligado ao próprio grupo.

Cada *z* negativo vira um pedaço de risco, e os três são somados com pesos
fixos (35%, 35% e 30%). A partir de 0,25 o aluno fica "em atenção"; a
partir de 0,50, "risco alto". O Felipe fica com 0,64. Para talento, a
lógica é a mesma ao contrário: 1 passo acima da turma, ou 1,5 passo acima
numa disciplina com pelo menos 6 alunos, ou ser ponte sem perder
desempenho.

**Por que isso não é aprendizado de máquina:** os pesos e os cortes foram
fixados **antes** de olhar o desfecho dos alunos e nunca foram ajustados a
ele. Não há treino: é estatística descritiva sobre medidas de rede.

### 9.11 Como sabemos que os grupos são os certos (NMI e pureza)

Na turma fictícia, sabemos a resposta certa, porque o gerador plantou as
áreas de cada aluno e guardou à parte. Então dá para comparar:

- **Pureza:** a fração de alunos que caiu num grupo em que a maioria é da
  mesma área que ele. 1 é perfeito.
- **NMI** (sigla em inglês para *informação mútua normalizada*): mede, de 0
  a 1, o quanto duas divisões em grupos concordam. 1 é concordância total,
  0 é nenhuma relação.

Na demonstração padrão, o Louvain reencontra as áreas plantadas com NMI =
1,00: acerta todos os alunos.

### Resumo: do contexto ao nome técnico

| O que explicamos no contexto | Nome técnico | Onde está explicado |
|---|---|---|
| mapa de ligações | grafo | 9.1 |
| aluno, disciplina | nó (vértice) | 9.1 |
| ligação | aresta | 9.1 |
| o mapa de quem cursa o quê | grafo bipartido | 9.2 |
| ligar alunos pelo que têm em comum | projeção | 9.3 |
| a força da ligação | peso (simples ou alocação de recursos) | 9.4 |
| comunidade | comunidade | 9.5 |
| "o quanto os grupos estão bem separados" | modularidade *Q* | 9.5 |
| "não é por acaso" | modelo nulo, *z* ≥ 3 | 9.6 |
| "o sistema encontrou os grupos sozinho" | Louvain, Girvan–Newman | 9.7 |
| quem é importante na rede | centralidade (grau, intermediação, autovetor) | 9.8 |
| ponte, referência, beirada | papéis de Guimerà e Amaral (ponte, referência, periférico) | 9.9 |
| "comparado com a turma" | escore *z*, desvio-padrão | 9.10 |
| "acertou os grupos" | NMI e pureza | 9.11 |

---

## 10. Perguntas que qualquer pessoa pode fazer

**"Então o sistema diz quem vai desistir?"**
Não. Ele diz quem está se afastando da turma e por quê. Quem decide o que
fazer é a instituição.

**"Por que não usar inteligência artificial, que acerta mais?"**
Talvez acertasse mais, mas não explicaria por quê. Para um coordenador
chamar um aluno para conversar, ele precisa saber o motivo. E o trabalho
quis mostrar que dá para chegar lá só com as ligações, sem aprendizado de
máquina.

**"Não é injusto marcar um aluno como risco?"**
Por isso a palavra é *atenção*, e por isso o motivo vem escrito. É um
convite para conversar, não um rótulo.

**"Dois alunos com notas parecidas ficam ligados?"**
Não. A ligação vem de cursar as mesmas disciplinas (ou acessar os mesmos
materiais). A nota entra depois, para dizer quem merece atenção e quem se
destaca.

**"Os dados dos alunos estão expostos?"**
Os dados reais são públicos e anônimos (Open University). Os alunos com
nome são inventados.

**"60% de evasão não é exagero?"**
É o número do Inep para quem entrou em 2015 e foi acompanhado por dez
anos, mas ele conta quem deixou o curso em que entrou, inclusive quem só
trocou de curso. Por isso falamos em "deixaram o curso", não em
"abandonaram a faculdade".

**"Funciona na UniAnchieta?"**
O método funciona com qualquer lista de matrículas. Testar com dados de
uma instituição brasileira é um próximo passo natural.

---

## 11. Cuidados de linguagem

| Evitar | Usar |
|---|---|
| "o sistema prevê evasão" | "o sistema aponta quem merece atenção" |
| "o aluno vai desistir" | "alguém deveria conversar com ele" |
| "alunos com notas parecidas formam uma comunidade" | "alunos que cursam as mesmas disciplinas e têm muitos colegas em comum formam uma comunidade" |
| "o algoritmo descobriu" (no contexto) | "o sistema encontrou, só pelas ligações" |
| "dados da faculdade" | "dados públicos de uma universidade inglesa" / "turma inventada" |
| "60% abandonam a faculdade" | "60% deixam o curso em que entraram" |
| "estatística oficial do Inep" | "segundo o Inep" / "indicadores de trajetória do Inep" |

O nome "risco de evasão" ainda está em aberto com o orientador. É a
pergunta 3 da pendência T-OBS-05, registrada no arquivo de pendências do
grupo, `observacoes/para-todos.md`. ("T-OBS" é só o código interno das
pendências que valem para todas as frentes; não aparece na apresentação.) Usar "merece atenção" na
explicação funciona com qualquer resposta.

---

## 12. Decisões do grupo (antes "em aberto")

1. **Exemplo:** fica o de ADS e Engenharia Elétrica, com Sistemas de
   Computação, Algoritmos e Programação e Circuitos Elétricos. As
   alternativas avaliadas e o motivo estão na seção 3.
2. **Número de evasão:** o dado do Inep entra **só na apresentação**, para
   mostrar o tamanho real do problema; não precisa entrar no artigo. A
   referência entra no slide de Referências, e a regra "a apresentação só
   cita o que o artigo cita" tem essa exceção declarada.
3. **Tamanho do contexto:** o contexto vem **antes** do sistema. *(Revisto
   em 22/11/2026: com a defesa de 15 a 20 minutos, a fala foi enxugada e
   parte dele foi para o apêndice; ver `ENREDO.md` e `PLANO-AJUSTE.md`.)*
   Na versão original, ficava inteiro (seções 2 a 8). Na fala do `ENREDO.md`, com a
   solução, dá ≈ 11 minutos; enxuto, ≈ 7. Quando o grupo souber o tempo
   da defesa, os cortes começam pela parte de engenharia, não pelo
   contexto.
4. **Textos de atenção e talento:** os da seção 5 foram conferidos em
   21/11/2026 rodando o sistema (`tiny_v1` e a turma padrão do
   laboratório). Conferir de novo no dia, porque mudam se mudar o código.

---

## Siglas

| Sigla | Significado | Vai para a apresentação? |
|---|---|---|
| ADS | Análise e Desenvolvimento de Sistemas (curso superior de tecnologia) | Sim, sempre por extenso na primeira vez |
| Inep | Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira, órgão do Ministério da Educação que faz o Censo da Educação Superior | Sim, como "Inep, órgão do Ministério da Educação" |
| TDA | Taxa de Desistência Acumulada: porcentagem da turma de entrada que já deixou o curso até determinado ano | Não; dizer "desistência" |
| Semesp | Sindicato das Entidades Mantenedoras de Estabelecimentos de Ensino Superior no Estado de São Paulo | Não; só aparece para avisar que não usamos os números dele |
| T-OBS | Código interno das pendências do grupo que valem para todas as frentes (`observacoes/para-todos.md`) | Não |
| NMI | *Normalized Mutual Information*, informação mútua normalizada: concordância de 0 a 1 entre duas divisões em grupos | Sim, nos resultados, sempre com a explicação |
| AVA | Ambiente Virtual de Aprendizagem | De preferência não; dizer "ambiente virtual" |
| OULAD | *Open University Learning Analytics Dataset*, a base pública da Open University | Só na fonte; na fala, "a base de dados da Open University" |

Ao aplicar o texto nos slides, vale o mesmo cuidado com as siglas que já
estão na apresentação atual: OULAD (*Open University Learning Analytics
Dataset*, a base de dados pública da Open University) e AVA (Ambiente
Virtual de Aprendizagem) aparecem nos resultados e precisam vir por
extenso na primeira vez, ou ser trocadas por palavras, como "a base de
dados da Open University" e "ambiente virtual".

---

## Referências usadas neste texto

BRASIL. Instituto Nacional de Estudos e Pesquisas Educacionais Anísio
Teixeira (Inep). **Resumo técnico do Censo da Educação Superior 2024**.
Brasília, DF: Inep, 2026. Disponível em:
https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_superior/resumo_tecnico_do_censo_da_educacao_superior_2024.pdf.
Acesso em: 20 nov. 2026.

> O ano é 2026 porque é o da ficha catalográfica (publicação online em
> março de 2026), embora os resultados do Censo 2024 tenham sido
> divulgados antes. Na citação do slide: (Inep, 2026). Ao aplicar, essa
> referência também entra no slide de Referências (hoje, o 33).
