# Enredo da apresentação

> **O que é:** o texto que vamos **falar no dia**, na ordem da
> apresentação, um slide de cada vez. Não é para ler palavra por palavra:
> é o jeito natural de contar cada parte, para ensaiar até sair com as
> próprias palavras.
>
> **Tempo:** cabe em **15 a 20 minutos**. A fala soma ≈ 1.500 palavras
> fora a demonstração (≈ 11 min a 140 palavras por minuto); com os
> avanços, as animações e ≈ 3 min de demonstração, **≈ 17 min**. Com
> `--curta` (sem `aluno-some` e `val-sintetico`), ≈ 16 min. A folga é de
> propósito: no dia, a fala sai mais devagar. Detalhes no fim, em "Tempo
> estimado"; para recontar, `python apresentacao/aplicar_enredo.py --contar`.
>
> **Como ler:**
> - **Na tela** diz qual slide (o `id` em `index.html`).
> - **▸** marca onde avançar (seta → ou espaço).
> - *Itálico entre colchetes* é ação ou lembrete, não se fala.
>
> As ideias e os números vêm da [`NARRATIVA.md`](NARRATIVA.md). As notas
> do apresentador (`<aside class="notas">`) **saem deste arquivo**:
> depois de mudar a fala, rode `python apresentacao/aplicar_enredo.py` e
> depois `python apresentacao/gerar_roteiro.py`.
>
> **Quem fala o quê** o grupo decide no ensaio; o texto não depende disso.
>
> **O que saiu da fala** (22/11/2026, para caber no tempo) não sumiu:
> virou slide do **apêndice** (tecla A), pronto para as perguntas — por
> que procurar dentro da comunidade, o escore *z*, o dicionário de termos,
> o grafo bipartido em detalhe, o Girvan–Newman passo a passo, o método em
> sequência, a turma da demonstração, a arquitetura, o clique, a interface
> e como o trabalho foi conduzido.

---

## Abertura

**Na tela:** `capa` · *[abra antes de a banca entrar; a animação leva ≈ 5 s]* · ≈ 25 s

Boa noite a todos. Somos o Grupo 16, os nossos nomes estão na tela, e
vamos apresentar o nosso Trabalho de Conclusão de Curso, orientado pelo
professor Clayton Valdo. Essa imagem é um mapa de alunos: cada ponto é
um aluno, e as cores são grupos que o nosso sistema encontrou sozinho.
Até o fim, todo mundo aqui vai saber ler esse mapa.

**Na tela:** `sumario` · ≈ 15 s

Primeiro o problema e a nossa ideia, num exemplo de seis alunos, sem
termo técnico. Depois os nomes técnicos, o método, o sistema ao vivo, os
resultados e o que concluímos.

**Na tela:** `sec-1` · ≈ 5 s

Por que olhar para as relações entre os alunos?

---

## O problema

**Na tela:** `aluno-some` · *[opcional; a animação começa sozinha]* · ≈ 30 s

Todo semestre, alguns alunos desaparecem, e quase nunca de uma vez.
Primeiro ele falta, depois deixa de entregar um trabalho, para de entrar
no ambiente virtual e, no fim, pede o trancamento. A instituição costuma
perceber só aqui, no fim. Mas os sinais estavam lá antes.

**Na tela:** `evasao-inep` · *[a animação começa sozinha]* · ≈ 40 s

E o problema é grande. Cada ponto é um por cento dos alunos que entraram
na graduação em 2015. No primeiro ano, 13% já tinham deixado o curso; no
segundo, 29%; depois de dez anos, 60%.

▸ Seis em cada dez. E quase três já tinham saído até o segundo ano:
a saída acontece cedo, quando ainda daria para agir.

▸ No ensino a distância, que é o da base real que usamos, 65%. Os números
são do Inep, o órgão do Ministério da Educação que faz o Censo da
Educação Superior.

**Na tela:** `contexto` · *[a animação começa sozinha]* · ≈ 40 s

A instituição já tem os dados: as matrículas, as notas, os acessos ao
ambiente virtual. Mas costuma ler tudo como uma lista, um aluno por
linha. Na lista, o Felipe é só mais uma linha. Quando a gente olha para
as relações entre os alunos, a mesma informação vira um mapa, e o mapa
mostra o que a lista esconde: o Felipe está quase sozinho, na beirada.

---

## A nossa ideia, no exemplo

**Na tela:** `ligacao` · ≈ 60 s

Nosso exemplo: uma universidade inventada, com seis alunos de Análise e
Desenvolvimento de Sistemas, a ADS, e de Engenharia Elétrica.

▸ A Ana, de ADS, e a Carla, de Engenharia Elétrica, cursam Sistemas de
Computação. ▸ Isso cria uma ligação entre elas. É a ideia central do
trabalho: dividir uma disciplina liga dois alunos. ▸ Bruno e Felipe
também estão lá, e todos ficam ligados. Nenhuma ligação é inventada:
cada uma vem de uma matrícula.

▸ Mas nem toda ligação é igual. Ana e Bruno dividem duas disciplinas;
a ligação engrossa. ▸ E dividir uma turma pequena diz mais do que
dividir uma lotada. Sistemas de Computação é a mais cheia, então as
ligações que vêm só dela afinam.

**Na tela:** `comunidades-ctx` · ≈ 65 s

Juntando as ligações, temos o mapa da turma. ▸ Nele aparecem grupos:
alunos muito ligados entre si e pouco ligados ao resto. Cada grupo é uma
comunidade.

▸ E uma surpresa: a Carla é de Engenharia Elétrica, mas ficou no grupo
de ADS. O sistema não sabe o curso de ninguém; ele mostra com quem cada
um estuda de fato.

▸ A Carla também é ponte: ▸ sem ela, Diego e Elisa ficam desligados de
todo o resto. ▸ Já o Felipe está na beirada: uma disciplina só, a mais
cheia.

▸ A Carla tem média 69; o Felipe, 66. Notas parecidas, lugares muito
diferentes. Em turmas maiores aparece também a referência, quem os
colegas rodeiam; vamos vê-la na demonstração.

**Na tela:** `atencao-talento` · ≈ 55 s

Com o mapa, o sistema compara cada aluno com a turma em três perguntas:
quantas disciplinas cursa, como vai nas notas e o quanto está ligado ao
grupo.

▸ O Felipe fica abaixo nas três, e o sistema escreve o motivo, este
texto é dele mesmo: "nota média 66, abaixo da turma", "pouco ligado ao
próprio grupo". ▸ Diego e Elisa ficam "em atenção": eles vão bem, mas o
grupo deles depende de uma pessoa só. ▸ E o outro lado: numa turma
maior, a Alice, referência no grupo, uma monitora natural.

▸ O sistema não diz que o Felipe vai desistir. Diz que alguém deveria
conversar com ele, e por quê.

**Na tela:** `solucao` · *[a animação começa sozinha]* · ≈ 40 s

É isso que o edugraph, o sistema que construímos, faz: entra a lista de
matrículas, sai o mapa da turma, com os grupos, o papel de cada aluno,
quem merece atenção e quem se destaca, sempre com o motivo. E sem
aprendizado de máquina, por escolha do grupo: nenhum modelo foi treinado
com o passado dos alunos, e dá para refazer a conta à mão. O desfecho de
cada aluno fica guardado à parte e só entra no fim, para conferir.

**Na tela:** `problema-pesquisa` · ≈ 20 s

Daí a pergunta do trabalho: dá para encontrar esses grupos, e quem
precisa de atenção, só olhando as ligações, de um jeito que qualquer um
consiga conferir? ▸ ▸ ▸ Isso serve à gestão, à transparência e à
pesquisa.

**Na tela:** `objetivos` · ≈ 20 s

O objetivo é um sistema que faça isso só com Teoria dos Grafos.
▸ ▸ ▸ ▸ Em quatro passos: modelar, projetar, agrupar e medir. ▸ E dois
testes automáticos garantem que nada de aprendizado de máquina entra.

---

## Os nomes técnicos

**Na tela:** `sec-2` · ≈ 8 s

Agora, o mesmo exemplo com os nomes técnicos.

**Na tela:** `grafo` · ≈ 45 s

Tudo aqui é grafo, e grafo não é gráfico. ▸ Pensem num mapa de metrô: só
estações e quem se liga a quem. ▸ Pontos e linhas: cada ponto é um nó,
cada linha uma aresta, e a aresta pode ter um peso.

▸ No nosso caso, os nós são alunos e disciplinas, e as arestas são as
matrículas. Dois tipos de ponto: é um grafo bipartido. ▸ A Carla é a
única nas três disciplinas, e Sistemas de Computação é a mais cheia.

**Na tela:** `projecao` · ≈ 40 s

A projeção tira as disciplinas e liga direto os alunos com algo em
comum, como o "quem assistiu a este filme também assistiu a…".
▸ No peso simples, Ana e Bruno valem 2. ▸ Na alocação de recursos, cada
disciplina vale um sobre o número de alunos: a ligação de Ana e Felipe
cai para 0,25. São os valores que o grupo conferiu no papel.

**Na tela:** `modularidade` · ≈ 40 s

Para dar nota a uma divisão em grupos, usamos a modularidade, Q. ▸ Como
mesas numa festa: se as conversas ficam dentro das mesas, a divisão faz
sentido. ▸ Acima de 0,3 costuma ser bom; esta rede tem 0,47. ▸ Mas quem
decide é o teste contra o acaso: comparamos com redes embaralhadas.

**Na tela:** `louvain` · ≈ 40 s

O Louvain encontra os grupos juntando: cada aluno muda para o grupo em
que o Q mais sobe. ▸ ▸ ▸ ▸ Diego vai para a Elisa, Bruno para a Ana,
depois Carla e Felipe. Ninguém mais quer mudar: dois grupos.

▸ Na turma da demonstração, 41 movimentos em um milésimo de segundo. E o
Girvan–Newman, que corta em vez de juntar, chega aos mesmos grupos.

**Na tela:** `centralidade` · ≈ 40 s

Por fim, centralidade: quão importante é um aluno, em três sentidos.
▸ Grau: com quantos colegas; a Carla, com todos. ▸ Intermediação: por
quem os caminhos passam; só pela Carla, o gargalo. ▸ Autovetor: ligado a
quem é bem ligado; Ana, Bruno e Carla. ▸ Combinando isso, o sistema dá o
papel de cada aluno: a Carla é ponte.

---

## Como a pesquisa foi feita

**Na tela:** `sec-3` · ≈ 5 s

O método.

**Na tela:** `metodo-caracterizacao` · ≈ 30 s

É uma pesquisa aplicada e quantitativa, com experimentos que se repetem
iguais. ▸ Duas bases: a pública da Open University, e uma turma
inventada em que plantamos os grupos. ▸ E cada pergunta tem critério:
existe grupo, contra o acaso; é o grupo certo, contra o plantado.

---

## O sistema, ao vivo

**Na tela:** `sec-4` · ≈ 5 s

Agora, o sistema funcionando.

**Na tela:** `demo` · *[Enter para entrar; ≈ 3 min no total]*

*[Tour, só os primeiros passos.]* Esse é o edugraph, rodando neste
computador, com uma turma inventada de Computação, gerada na hora. A área
certa de cada aluno fica guardada à parte.

*[▶ com Louvain.]* As matrículas, as ligações entre alunos, o algoritmo
juntando os grupos, com o Q subindo ao vivo, e três grupos com nome.

*[Painel de sinais.]* Um aluno que merece atenção, com o motivo escrito.
Os nomes coincidem com os do exemplo, mas são outras pessoas. E a Alice
T., referência no grupo, a monitora natural.

*[Revelar.]* E as áreas plantadas: o sistema acertou cem por cento dos
alunos sem saber de nada.

*[Voltar pelo botão no topo.]*

---

## Resultados

**Na tela:** `sec-5` · ≈ 5 s

Os resultados.

**Na tela:** `acaso` · *[a sequência começa sozinha]* · ≈ 40 s

Primeiro, o teste contra o acaso. A turma inventada de 98 alunos tem Q de
0,47. Embaralhando quem cursou o quê, a estrutura some e o Q cai para
perto de 0,2. A rede real fica mais de quinze desvios acima: os grupos
são de verdade. Na base real, esse teste vai dizer o contrário.

**Na tela:** `val-sintetico` · *[opcional]* · ≈ 30 s

▸ Na turma inventada, os grupos batem com as áreas plantadas: pureza
0,95 e concordância de 0,82, mesmo com ruído. ▸ O Girvan–Newman confirma,
mil vezes mais lento. ▸ E com quase todos numa disciplina só, a
concordância cai: é o que acontece na base real.

**Na tela:** `oulad` · ≈ 35 s

Na Open University, ▸ pela matrícula o Q é 0,77, mas o acaso dá 0,78:
quase todos cursam um módulo só, e não há grupo. O sistema disse isso.
▸ Pelos materiais acessados no ambiente virtual, os grupos aparecem, de
cinco a nove vezes acima do acaso. ▸ E o jeito de pesar decide se o sinal
aparece.

**Na tela:** `desfecho` · ≈ 40 s

Agora entra o desfecho, que o mapa nunca viu. ▸ Entre os alunos menos
centrais, 89% não concluíram; entre os mais centrais, 10%. ▸ O grupo de
pouco engajados teve 69% de reprovação ou desistência, contra 7%. ▸ E
dos 197 marcados com risco alto, 94%. ▸ Mas não é previsão: quem desiste
para de acessar. O sistema aponta onde olhar.

**Na tela:** `criticas` · ≈ 30 s

E nas disciplinas: ▸ as três medidas apontam disciplinas diferentes;
▸ ser muito cursada e ser ponte são coisas diferentes. ▸ E a disciplina
que mais conecta o currículo não é a que mais reprova.

---

## O que concluímos

**Na tela:** `sec-6` · ≈ 5 s

Para fechar.

**Na tela:** `conclusao` · ≈ 35 s

Voltando à pergunta: sim, com uma condição: o sinal precisa existir nos
dados. ▸ ▸ ▸ ▸ O sistema encontra os grupos plantados, as medidas trazem
informação, e na base real ele soube dizer quando não havia grupo.
▸ E o mesmo mapa aponta quem merece atenção e quem se destaca, sempre com
o motivo.

**Na tela:** `limites-futuro` · ≈ 20 s

Os limites, antes da pergunta: ▸ não é previsão; ▸ o sinal real é fraco;
▸ o Girvan–Newman não escala; ▸ a nota mínima deixa gente de fora; ▸ e o
uso é local. O próximo passo natural: dados de uma instituição
brasileira.

**Na tela:** `referencias` · ≈ 5 s

As referências, incluindo o relatório do Inep.

**Na tela:** `encerramento` · ≈ 15 s

Agradecemos a atenção de todos e ao nosso orientador. Ficamos à
disposição para as perguntas.

---

## Se perguntarem

Respostas curtas, no mesmo tom. Os detalhes estão no apêndice (tecla A).

**"Então o sistema diz quem vai desistir?"**
Não. Ele diz quem está se afastando da turma e por quê. Quem decide o que
fazer é a instituição.

**"Por que procurar dentro da comunidade, e não só pela nota?"**
A comunidade dá o contexto que a nota não dá, mostra o isolamento, que
costuma vir antes da desistência, e permite agir no grupo inteiro.
*[Apêndice: `por-que-comunidade`.]*

**"Por que não usar inteligência artificial, que talvez acertasse mais?"**
Talvez acertasse, mas não explicaria por quê. Para um coordenador chamar
um aluno para conversar, ele precisa saber o motivo.

**"Esse cálculo de risco não é aprendizado de máquina?"**
Não. Não há treino: é o escore z, quantos passos o aluno está da média
da turma, com pesos e cortes fixados antes de olhar o desfecho.
*[Apêndice: `escore-z` e `a-sinais`.]*

**"Como o Girvan–Newman funciona?"**
Ele corta a ligação mais usada como passagem, recalcula e repete; fica
com o corte de maior Q. *[Apêndice: `girvan-newman`.]*

**"Não é injusto marcar um aluno como risco?"**
Por isso a palavra é "atenção", e por isso o motivo vem escrito. É um
convite para conversar, não um rótulo.

**"Dois alunos com notas parecidas ficam ligados?"**
Não. A ligação vem de cursar as mesmas disciplinas, ou de acessar os
mesmos materiais. A nota entra depois. A Carla e o Felipe têm notas
parecidas e estão em situações bem diferentes.

**"Mas a nota não entra no mapa?"**
A nota de cada disciplina entra, como força da matrícula. O que fica fora
é o desfecho: se aprovou, reprovou ou desistiu.

**"60% de evasão não é exagero?"**
É o número do Inep para quem entrou em 2015, acompanhado por dez anos, e
conta quem deixou o curso em que entrou, inclusive quem só trocou de
curso. Por isso falamos em "deixaram o curso".

**"Os dados dos alunos estão expostos?"**
Os dados reais são públicos e anônimos, da Open University. Os alunos com
nome são inventados.

**"Funciona na UniAnchieta?"**
O método funciona com qualquer lista de matrículas. Testar com dados de
uma instituição brasileira é o próximo passo natural.

**"Como o sistema é por dentro?"**
Três partes que não usam o código uma da outra e conversam por arquivos
num formato fixo; um teste garante a regra. *[Apêndice: `arquitetura` e
`clique`.]*

---

## Tempo estimado

| Parte | Slides | Fala | Com avanços e animações |
|---|---|---|---|
| Abertura | capa, sumário, abertura do capítulo | ≈ 100 palavras | ≈ 50 s |
| Problema e ideia | aluno que some*, Inep, os dados, ligação, grupos e papéis, atenção, solução | ≈ 620 palavras | ≈ 5 min 30 s |
| Pergunta e objetivos | | ≈ 70 palavras | ≈ 40 s |
| Nomes técnicos | grafo, projeção, modularidade, Louvain, centralidade | ≈ 320 palavras | ≈ 3 min |
| Método | caracterização | ≈ 50 palavras | ≈ 30 s |
| Sistema ao vivo | demonstração | roteiro de ações | ≈ 3 min |
| Resultados | acaso, turma inventada*, Open University, desfecho, disciplinas | ≈ 240 palavras | ≈ 2 min 30 s |
| Conclusão e encerramento | conclusão, limites, referências, encerramento | ≈ 110 palavras | ≈ 1 min |
| **Total** | **33 slides principais** (6 são aberturas de capítulo) | **≈ 1.500 palavras** | **≈ 17 min** |

\* opcionais: saem com `--curta` (≈ 16 min).

A fala foi contada por `aplicar_enredo.py --contar` (140 palavras por
minuto); somam-se ≈ 2 s por avanço, a espera das animações e a
demonstração. **Ensaie com o cronômetro do modo apresentador (tecla P)**:
o alvo está em `js/config.js` (`duracaoAlvoMin`).

Se no ensaio passar de 20 minutos, corte nesta ordem: (1) `--curta`;
(2) na demonstração, pular o tour e ir direto ao ▶ (≈ 30 s);
(3) `criticas` (≈ 30 s), dizendo a frase final dela na conclusão.
