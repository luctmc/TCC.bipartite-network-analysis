# Plano de ajuste da apresentação: contexto primeiro

> **Para quem é este arquivo:** para a conversa (e para quem do grupo)
> que vai **alterar a apresentação** em `apresentacao/`. Ele diz o que
> mudar, em que ordem, com que dados e como conferir. O **conteúdo** vem
> de dois arquivos irmãos:
>
> - [`NARRATIVA.md`](NARRATIVA.md): o que explicamos e por quê (a fonte
>   das ideias, dos números e das decisões);
> - [`ENREDO.md`](ENREDO.md): o texto falado no dia, tópico a tópico. As
>   notas do apresentador (`<aside class="notas">`) saem dele.
>
> Se este plano e a narrativa discordarem num número ou numa frase, vale a
> narrativa. Se a narrativa e o código discordarem, vale o código: rode o
> sistema e corrija a narrativa.

---

## 0. Antes de começar

1. Leia o `CLAUDE.md` da raiz e as **Abertas** de `observacoes/` (em
   especial `para-todos.md`: T-OBS-05, T-OBS-06 e T-OBS-07 tocam neste
   trabalho; ver a seção 9 deste plano).
2. Leia, nesta ordem: [`README.md`](README.md) (como a pasta funciona),
   [`NARRATIVA.md`](NARRATIVA.md), [`ENREDO.md`](ENREDO.md),
   [`VERIFICACAO.md`](VERIFICACAO.md).
3. Abra `index.html`, `js/motion.js` (o player `Filme` e as três
   sequências), `js/diagramas.js` (o exemplo `tiny_v1`) e `gerar_dados.py`.
4. Crie um branch: `c/apresentacao-contexto`. Não faça commit nem PR sem o
   usuário pedir.

**Regras que valem para todo texto que for para a tela ou para as notas:**

- **Siglas por extenso** na primeira vez, com a sigla entre parênteses, ou
  trocadas por palavras (tabela "Siglas" da narrativa). Inclui OULAD, AVA,
  NMI, ADS e Inep nos slides que já existem.
- **Ninguém do grupo é citado** em slide, nota ou documentação, a não ser
  na autoria (capa, encerramento). Nada de "eu, Lucas" nas notas: a fala
  da capa diz "somos o Grupo 16" e os nomes ficam na tela.
- **Não dizer que "sem IA" foi exigência do orientador.** Foi escolha do
  grupo. Dizer que o sistema **não usa aprendizado de máquina** e por quê.
  A nota do slide `objetivos` (hoje `index.html:119`) diz o contrário e
  precisa ser corrigida.
- **"Aponta, não prevê".** Nunca "o sistema prevê evasão" (tabela de
  cuidados de linguagem, seção 11 da narrativa).
- **Nada ilustrativo sem aviso.** O `README.md` da pasta promete "nada é
  ilustrativo". Os únicos elementos inventados deste plano são os nomes e
  cursos do exemplo e a linha do tempo do slide `aluno-some`; os dois
  ganham aviso na linha de fonte do slide e uma entrada no
  `VERIFICACAO.md`.

---

## 1. O que muda e por quê

A apresentação de hoje (34 slides principais) segue o artigo e começa
técnica: o slide 4 já fala em OULAD, Ciência de Redes e modelos
preditivos; a fundamentação vem logo depois; risco e talento só aparecem
no apêndice (A11, `a-sinais`). Quem não é da área chega ao grafo sem saber
**para que** ele serve.

O ajuste mantém a estrutura de TCC (as seis seções do artigo, que a banca
espera), mas:

1. **A Introdução vira o contexto completo** (seções 2 a 8 da
   narrativa): o problema, o exemplo dos seis alunos, ligação, rede,
   comunidade, papéis, atenção e talento, por que procurar na comunidade,
   a solução. **Sem nenhum termo técnico**, com uma animação por ideia.
2. **A Fundamentação explica cada termo técnico** (seção 9 da narrativa),
   começando por "o que é um grafo", e sempre com os **mesmos seis alunos,
   agora com nome**. Ganha um slide sobre o escore *z* (como o sistema
   decide "abaixo da turma").
3. **Os slides técnicos que já existem trocam números por nomes**: "aluno
   3" vira "Carla", "disciplina A" vira "Sistemas de Computação", "3–4"
   vira "Carla–Diego". O desenho e as posições não mudam: quem viu o
   contexto reconhece o mapa.
4. **No Desenvolvimento, a demonstração vem antes da engenharia**
   (arquitetura e "por dentro de um clique" passam para depois da demo e
   ficam candidatos a `data-opcional`).
5. **Nos Resultados**, cada slide ganha uma frase "em palavras simples", e
   o resultado de 94% dos alunos em risco alto (hoje só no apêndice) entra
   no slide `desfecho`.

---

## 2. Decisões já tomadas (não reabrir)

| Decisão | Onde está |
|---|---|
| Exemplo: ADS e Engenharia Elétrica; Sistemas de Computação (A), Algoritmos e Programação (B), Circuitos Elétricos (C); Ana, Bruno, Carla, Diego, Elisa, Felipe = alunos 1 a 6 de `tiny_v1` | narrativa, seção 3 |
| O dado do Inep entra **só na apresentação** (não no artigo). Referência no slide `referencias`, com a exceção dita na nota | narrativa, seção 12, item 2 |
| O contexto fica inteiro e vem antes do sistema. Cortes, se precisar, saem da engenharia (seção 4 do deck) | narrativa, seção 12, item 3 |
| Textos de atenção e talento conferidos em 21/11/2026; conferir de novo no dia | narrativa, seção 12, item 4 |
| A estrutura de seis seções do artigo continua | este plano |
| As fixtures (`data/fixtures/`) não mudam | `CLAUDE.md` |

---

## 3. A nova ordem dos slides

Legenda: **novo**, **ajustado** (conteúdo muda), **mantido**, **movido**.
"Narr." é a seção da narrativa de onde sai o conteúdo; "Mov." é a
animação do catálogo da seção 5.

| # | `id` | Título (`data-titulo`) | Estado | Narr. | Mov. |
|---|---|---|---|---|---|
| 1 | `capa` | Abertura | ajustado (só a fala) | 1 | já existe |
| 2 | `sumario` | Sumário | ajustado | — | — |
| 3 | `sec-1` | 1 · Introdução | ajustado (pergunta) | — | — |
| 4 | `aluno-some` | O aluno que some | **novo** | 2 | M1 |
| 5 | `evasao-inep` | O tamanho do problema | **novo** | 2 | M2 |
| 6 | `contexto` | Os dados já existem | ajustado (reescrito) | 2 | M3 |
| 7 | `ligacao` | Uma disciplina, uma ligação | **novo** | 3, 4 | M4 |
| 8 | `forca` | Nem toda ligação é igual | **novo** | 4 | M5 |
| 9 | `comunidades-ctx` | O mapa da turma e seus grupos | **novo** | 4 | M6 |
| 10 | `papeis-ctx` | O lugar de cada aluno | **novo** | 4 | M7 |
| 11 | `atencao-talento` | Quem merece atenção, quem se destaca | **novo** | 5 | M8 |
| 12 | `por-que-comunidade` | Por que procurar dentro da comunidade | **novo** | 6 | M9 |
| 13 | `solucao` | A solução: o edugraph | **novo** | 7 | M10 |
| 14 | `problema-pesquisa` | Problema de pesquisa e justificativa | ajustado | — | — |
| 15 | `objetivos` | Objetivos | ajustado | 7 | — |
| 16 | `sec-2` | 2 · Fundamentação teórica | ajustado (pergunta) | 9 | — |
| 17 | `grafo` | O que é um grafo | **novo** | 9.1 | M11 |
| 18 | `bipartido` | Grafo bipartido | ajustado | 9.2 | já existe |
| 19 | `projecao` | Projeção ponderada | ajustado | 9.3, 9.4 | já existe |
| 20 | `modularidade` | Comunidades e modularidade | ajustado | 9.5, 9.6 | já existe |
| 21 | `louvain` | Louvain | ajustado | 9.7 | já existe |
| 22 | `girvan-newman` | Girvan–Newman | ajustado | 9.7 | já existe |
| 23 | `centralidade` | Centralidade | ajustado | 9.8, 9.9 | já existe |
| 24 | `escore-z` | Comparar com a turma | **novo** | 9.10 | M12 |
| 25 | `dicionario` | Do contexto ao nome técnico | **novo**, `data-opcional` | 9 (resumo) | M13 |
| 26 | `sec-3` | 3 · Metodologia | mantido | — | — |
| 27 | `metodo-caracterizacao` | Caracterização da pesquisa | ajustado (siglas) | 9.6, 9.11 | — |
| 28 | `pipeline` | O método em sequência | ajustado (nomes) | — | já existe |
| 29 | `sec-4` | 4 · Desenvolvimento | ajustado (fala) | — | — |
| 30 | `desenvolvimento-processo` | Como o trabalho foi conduzido | mantido, `data-opcional` | — | — |
| 31 | `sinteticos` | Os dados da demonstração | **movido** (antes da demo), perde `data-opcional` | — | — |
| 32 | `demo` | Demonstração ao vivo | ajustado (roteiro) | 5, 8 | — |
| 33 | `interface` | A interface | mantido, `data-opcional` | — | — |
| 34 | `arquitetura` | Arquitetura | **movido** (depois da demo), candidato a `data-opcional` | — | — |
| 35 | `clique` | Por dentro de um clique | **movido** (depois da demo), candidato a `data-opcional` | — | já existe |
| 36 | `sec-5` | 5 · Resultados e discussão | mantido | — | — |
| 37 | `acaso` | O teste contra o acaso | ajustado (frase simples) | 9.6 | já existe |
| 38 | `val-sintetico` | Validação no sintético | ajustado (NMI explicado) | 8, 9.11 | — |
| 39 | `oulad` | A base real | ajustado (siglas, frase simples) | 8 | — |
| 40 | `desfecho` | O desfecho revelado | ajustado (+ 94%) | 6, 8 | — |
| 41 | `criticas` | Disciplinas críticas | ajustado (frase simples) | 9.8 | — |
| 42 | `sec-6` | 6 · Considerações finais | mantido | — | — |
| 43 | `conclusao` | Conclusão | ajustado | 7, 8 | — |
| 44 | `limites-futuro` | Limitações e trabalhos futuros | ajustado (siglas) | 8 | — |
| 45 | `referencias` | Referências | ajustado (+ Inep) | refs. | — |
| 46 | `encerramento` | Obrigado · Perguntas | mantido | — | já existe |

O apêndice (15 slides) fica como está. Só o `a-sinais` ganha uma linha na
nota dizendo que a versão simples está no slide `escore-z`.

**Sobre o tamanho:** são 46 slides principais (eram 34), doze deles
novos. A fala completa do `ENREDO.md` dá **≈ 34 minutos** com a
demonstração (hoje são 15 a 20). O grupo decidiu manter assim até saber o
tempo da defesa. Quando souber, cortar na ordem da tabela "Tempo
estimado" do enredo; os slides cortáveis (`dicionario`, `interface`,
`desenvolvimento-processo`, `clique`, `arquitetura`) ficam com
`data-opcional`, para `servir.py --curta` tirar de uma vez. Atualize
`duracaoAlvoMin` em `js/config.js` quando o tempo for definido.

---

## 4. Os slides, um a um

O texto **na tela** é curto: título de uma linha e no máximo três frases
ou cartões. A explicação longa vai para a fala (`ENREDO.md`). Todos os
slides de contexto (4 a 13) seguem a **regra da narrativa**: nenhum termo
técnico na tela nem na fala.

### 4.1 `capa` (ajustado)

Só a fala muda (ver `ENREDO.md`, "Abertura"). A legenda técnica da capa
("synthetic_v1… Q = 0,4666") pode ficar, porque é pequena, mas a fala não
lê: diz que cada ponto é um aluno, cada linha são disciplinas em comum, e
que "até o fim, vocês vão saber ler este mapa".

### 4.2 `sumario` (ajustado)

Descrições das seis seções em linguagem simples:

1. Introdução: o problema, a nossa ideia e a solução, num exemplo de seis
   alunos
2. Fundamentação teórica: os mesmos seis alunos, com os nomes técnicos
3. Metodologia: como a pesquisa foi feita e avaliada
4. Desenvolvimento: o sistema, rodando ao vivo
5. Resultados e discussão: numa turma inventada e numa universidade real
6. Considerações finais: o que concluímos e o que fica para depois

### 4.3 `sec-1` (ajustado)

`div-pergunta`: "Por que olhar para as relações entre os alunos?"

### 4.4 `aluno-some` (novo) · M1

- **Título:** "Todo semestre, alguns alunos desaparecem. A instituição
  costuma perceber no fim."
- **Na tela:** a animação M1 ocupando a largura; embaixo, uma frase: "Os
  sinais aparecem antes: nas matrículas, nas notas, no ambiente virtual."
- **Fonte:** "Linha do tempo ilustrativa, sem dado de aluno real."
- **Passos:** a animação é um filme (começa sozinha, K pausa).

### 4.5 `evasao-inep` (novo) · M2

- **Título:** "De cada 10 alunos que entraram na graduação em 2015, 6
  deixaram o curso em que ingressaram."
- **Na tela:** M2 (os 100 pontos) à esquerda; à direita, o número grande
  que acompanha a animação e, no passo 1, a frase "Quase 3 já tinham saído
  até o fim do 2º ano." No passo 2 (opcional), duas barras pequenas: "a
  distância: 65% · presencial: 59%".
- **Fonte (obrigatória, na tela):** "Inep, órgão do Ministério da
  Educação. Resumo técnico do Censo da Educação Superior 2024 (Inep,
  2026), Gráficos 15 e 18, p. 33 e 36. Indicadores de trajetória da turma
  de 2015, acompanhada até 2024."
- **Cuidados da narrativa (seção 2):** "deixaram o curso", nunca
  "abandonaram a faculdade"; nunca "estatística oficial"; nada de números
  do Semesp; a sigla TDA não aparece.

### 4.6 `contexto` (ajustado, reescrito) · M3

Substitui os três cartões de hoje (OULAD, Ciência de Redes, modelos
preditivos), que saem da Introdução: o OULAD reaparece nos Resultados, e
"modelos preditivos" vai para o slide `solucao`.

- **Título:** "A instituição já tem os dados. O problema é que eles são
  lidos como uma lista."
- **Na tela:** M3 (planilha que vira mapa). Três rótulos pequenos aparecem
  com a animação: "em que disciplinas cada aluno se matriculou", "que nota
  teve", "o que acessou no ambiente virtual".
- **Frase final na tela:** "Numa lista, ninguém vê quem está sozinho. No
  mapa, dá para ver."

### 4.7 `ligacao` (novo) · M4

- **Título:** "Dois alunos que cursam a mesma disciplina têm uma ligação."
- **Na tela, à esquerda:** a tabela dos seis alunos (nome, curso,
  disciplinas). À direita, M4.
- **Destaque (último passo):** "Nenhuma ligação é inventada: cada uma vem
  de uma matrícula."
- É **o exemplo do professor**: a Ana, de ADS, e a Carla, de Engenharia
  Elétrica, em Sistemas de Computação. Dizer isso na fala.

### 4.8 `forca` (novo) · M5

- **Título:** "Nem toda ligação é igual."
- **Dois cartões, um por passo:** "Mais disciplinas em comum, ligação mais
  forte" e "Dividir uma turma pequena diz mais do que dividir uma turma
  lotada".
- Sem números de peso na tela: a espessura das linhas é que mostra.

### 4.9 `comunidades-ctx` (novo) · M6

- **Título:** "Juntando as ligações, aparece o mapa da turma, e nele, os
  grupos."
- **Passos:** (1) os grupos aparecem; (2) os cursos aparecem por cima e a
  Carla se destaca; (3) a frase "Ninguém disse ao sistema quantos grupos
  existem nem o curso de ninguém."
- **Cartão do passo 2:** "A Carla é de Engenharia Elétrica, mas estuda com
  o grupo de Sistemas. A comunidade mostra com quem cada um estuda de
  fato, não o curso da matrícula."

### 4.10 `papeis-ctx` (novo) · M7

- **Título:** "Cada aluno ocupa um lugar diferente no mapa."
- **Passos:** (1) ponte: a Carla; (2) "sem ela, Diego e Elisa ficam
  desligados de todo o resto"; (3) beirada: o Felipe; (4) a comparação
  "A Carla tem média 69 e o Felipe, 66: notas parecidas, lugares muito
  diferentes."
- A média da Carla, 68,7, sai de `tiny_v1` (77, 68, 61) e deve ser
  calculada em `gerar_dados.py`, não digitada.
- "Referência" aparece só como texto: "Em turmas maiores aparece também a
  **referência**: quem os colegas rodeiam. Vamos vê-la na demonstração."

### 4.11 `atencao-talento` (novo) · M8

- **Título:** "O sistema compara cada aluno com a turma e escreve o
  porquê."
- **Na tela:** à esquerda, as três perguntas (quantas disciplinas cursa,
  como vai, o quanto está ligado ao grupo); à direita, M8.
- **Passos:** (1) Felipe: as três réguas e o cartão com o texto do
  sistema, entre aspas, **lido de `dados.js`**, nunca digitado; (2) Diego
  e Elisa, "em atenção": o sinal é do grupo, não da nota (os dois vão
  bem); (3) o outro lado: dois cartões de talento da turma da
  demonstração, com nome e inicial (Alice T. e Larissa J.), rotulados
  "turma da demonstração"; (4) a frase "O sistema não diz que o Felipe vai
  desistir. Diz que alguém deveria conversar com ele."
- **Cuidado:** o rótulo do sistema é "Risco de evasão"/"Risco alto". O
  nome está em discussão (T-OBS-05, pergunta 3). Na tela, usar "merece
  atenção" como título e o rótulo do sistema só dentro do cartão, entre
  aspas, como texto do sistema.
- **Cuidado com o texto de Diego e Elisa:** o sistema escreve hoje "ficou
  num grupo só dele", o que está impreciso para um grupo de dois
  (T-OBS-06). Se a pendência não estiver resolvida, **não mostrar** esse
  texto: mostrar só o rótulo "Em atenção" e a frase do slide.

### 4.12 `por-que-comunidade` (novo) · M9

- **Título:** "Por que procurar esses alunos dentro da comunidade."
- **Quatro passos, um por ideia** (narrativa, seção 6): o contexto que a
  nota não dá; o isolamento vem antes da desistência; agir no grupo, não
  só no aluno (69% × 7%, Open University); talento vira apoio (monitoria).
- **Último passo:** a tabela "quem usa o mapa" (coordenação, tutoria,
  professores, instituição), em quatro linhas curtas.
- **Fonte do 69% × 7%:** a mesma do slide `desfecho`.

### 4.13 `solucao` (novo) · M10

- **Título:** "O edugraph: entra a lista de matrículas, sai o mapa da
  turma, com o motivo de cada alerta."
- **Na tela:** M10; embaixo, a faixa "Sem aprendizado de máquina" com os
  quatro pontos da narrativa (seção 7) em uma linha cada: nenhum modelo
  aprendeu com o passado; todo alerta tem um porquê; dá para refazer a
  conta à mão; o resultado do aluno fica fora do mapa.
- **Não** dizer que foi exigência de ninguém.

### 4.14 `problema-pesquisa` (ajustado)

A pergunta de pesquisa fica (é a do artigo). Acrescentar, acima dela,
uma linha em palavras simples: "Em outras palavras: dá para encontrar
esses grupos, e quem precisa de atenção, só olhando as ligações, de um
jeito que qualquer pessoa consiga conferir?" A fala muda (ver `ENREDO.md`).

### 4.15 `objetivos` (ajustado)

- Corrigir a nota: tirar "que foi exigência do orientador".
- Os objetivos específicos ficam (são do artigo), mas cada um ganha, entre
  parênteses, a palavra do contexto: "Modelar (o mapa de quem cursa o
  quê)", "Projetar (as ligações entre alunos)", "Agrupar (as
  comunidades)", "Medir (pontes e gargalos)".

### 4.16 `sec-2` (ajustado)

`div-pergunta`: "Os mesmos seis alunos, agora com os nomes técnicos, e o
que cada um quer dizer." Fala: a frase de passagem da narrativa (seção 9).

### 4.17 `grafo` (novo) · M11

- **Título:** "Grafo: pontos e linhas que dizem quem está ligado a quem."
- **Passos:** (1) um mapa de metrô **genérico** (estações sem nome real,
  sem cores de linhas reais); (2) o mapa vira só pontos e linhas, com os
  rótulos **nó** e **aresta**; (3) os pontos viram os seis alunos.
- **Cartão pequeno:** "Grafo não é gráfico. Gráfico mostra números; grafo
  mostra ligações."

### 4.18 a 4.23 Os slides técnicos que já existem

Mudanças comuns a `bipartido`, `projecao`, `modularidade`, `louvain`,
`girvan-newman`, `centralidade` e `pipeline`:

- **Nomes no lugar de números.** Nos SVGs (`js/diagramas.js`,
  `seqMetodo` em `js/motion.js`) o nó mostra a **inicial** (A, B, C, D, E,
  F) e o nome aparece ao lado quando houver espaço. No texto e nas notas,
  "aluno 3" vira "Carla", "1 e 2" vira "Ana e Bruno", "3–4" vira
  "Carla–Diego".
- **Disciplinas por nome.** Os quadrados deixam de mostrar "A", "B", "C"
  (que confundiriam com as iniciais): mostram uma abreviação
  ("Sist. Comp.", "Algoritmos", "Circuitos") e o rótulo completo ao lado.
- **As posições não mudam** (`POS_BIP`, `POS_PROJ` em `diagramas.js`): é o
  mesmo desenho do contexto.
- **Linha de fonte:** continua citando `tiny_v1` e acrescenta "nomes e
  cursos inventados para o exemplo; alunos 1 a 6 = Ana a Felipe;
  disciplinas A, B e C = Sistemas de Computação, Algoritmos e
  Programação, Circuitos Elétricos".

Mudanças específicas (o conteúdo de cada uma está na narrativa, seção 9):

| Slide | O que acrescentar |
|---|---|
| `bipartido` | cartão "No dia a dia: pessoas e filmes num serviço de vídeo"; "a Carla é a única nas três disciplinas; Sistemas de Computação é a mais cheia" |
| `projecao` | cartão "No dia a dia: 'quem assistiu a este filme também assistiu a…'"; os pesos com nomes (Ana e Bruno: 2 e 0,58; Ana e Felipe: 1 e 0,25) |
| `modularidade` | analogia da festa e das mesas; no passo do "cuidado", a analogia do dado viciado para o teste contra o acaso |
| `louvain` | os quatro movimentos com nomes (o rastro real diz quem se move; ler de `dados.js`) |
| `girvan-newman` | "a ligação mais usada como passagem: Carla–Diego"; depois Carla–Elisa |
| `centralidade` | uma linha por medida com o exemplo da empresa (narrativa, 9.8) e, no fim, a tabela de papéis (9.9), dizendo que no exemplo cinco dos seis são "periféricos" e que o Felipe é o mais afastado do centro do grupo |
| `pipeline` | `seqMetodo` com nomes na planilha e nos nós; legendas sem "aluno 3" |

### 4.24 `escore-z` (novo) · M12

- **Título:** "'Abaixo da turma' tem uma conta: quantos passos da média."
- **Passos:** (1) M12, a régua com a média e o "passo típico"
  (desvio-padrão), no exemplo genérico da narrativa (média 70, passo 10;
  90 é z = +2, 60 é z = −1), **rotulado "exemplo de conta"**; (2) as três
  medidas do sistema (carga, desempenho, vínculo) e os pesos fixos 35%,
  35% e 30%; (3) a régua do risco de 0 a 1 com os cortes 0,25 e 0,50 e o
  Felipe em 0,64 (valor lido de `dados.js`); (4) a faixa "Sem treino: pesos
  e cortes fixados antes de olhar o desfecho".
- Os detalhes (fórmula do componente, z de Guimerà e Amaral) continuam no
  apêndice `a-sinais`.

### 4.25 `dicionario` (novo, `data-opcional`) · M13

A tabela-resumo da narrativa (fim da seção 9), animada sobre o desenho dos
seis alunos. Serve de recapitulação antes da Metodologia; é o primeiro
corte se faltar tempo.

### 4.26 Metodologia e Desenvolvimento

- `metodo-caracterizacao`: "OULAD" por extenso na primeira vez (*Open
  University Learning Analytics Dataset*, base pública da Open
  University); "NMI" com a explicação ("concordância de 0 a 1 entre duas
  divisões"); "réplicas nulas" com "redes embaralhadas".
- `sec-4`: fala nova: "Agora, o sistema funcionando."
- **Ordem nova:** `desenvolvimento-processo` (opcional) → `sinteticos` →
  `demo` → `interface` (opcional) → `arquitetura` → `clique`.
- `sinteticos` deixa de ser opcional (a plateia precisa saber que a turma
  da demonstração é inventada e que a resposta certa fica guardada).
- `demo`, roteiro (`ol.roteiro-demo` e notas): tour; ▶ com Louvain;
  **abrir o painel de sinais e mostrar um aluno em risco e um talento,
  lendo o motivo escrito** (Alice T. como referência/talento; Larissa J.
  como ponte); revelar as áreas; Girvan–Newman se houver tempo. Avisar na
  fala que os nomes da turma fictícia coincidem com os do exemplo, mas são
  outras pessoas.

### 4.27 Resultados

Cada slide ganha uma linha `p.em-uma-frase` (a classe já existe) "Em
palavras simples", com o texto da seção 8 da narrativa:

| Slide | "Em palavras simples" |
|---|---|
| `acaso` | "Se uma rede embaralhada dá o mesmo resultado, os grupos não querem dizer nada. Aqui, a rede real ficou muito acima." |
| `val-sintetico` | "Na turma inventada, em que sabíamos a resposta, o sistema encontrou os grupos certos." Explicar NMI e pureza na própria tela (hoje só na nota). |
| `oulad` | "Só a matrícula não basta: quase todos cursavam um módulo só. O comportamento no ambiente virtual, sim, mostra grupos." Trocar "AVA" por "ambiente virtual" no rótulo e "OULAD" por "Open University" no título. |
| `desfecho` | **novo passo** antes do cartão "não é previsão": "Dos 197 alunos que o sistema marcou com risco alto, 94% reprovaram ou desistiram (na turma, 43%)". Fonte: `docs/orientador/estudo-apresentacao-11-2026.md`, seção 5 (a mesma do `a-sinais`). |
| `criticas` | "A disciplina que mais conecta o currículo não é a que mais reprova." |

### 4.28 Considerações finais e referências

- `conclusao`: acrescentar um quinto item ou uma linha final: "E o mesmo
  mapa aponta quem merece atenção e quem se destaca, sempre com o motivo
  escrito."
- `limites-futuro`: "AVA" por extenso ou "ambiente virtual".
- `referencias`: acrescentar, em ordem alfabética (entre HAGBERG e
  KUZILEK), a referência do Inep exatamente como está no fim da
  narrativa. Na nota, trocar "a apresentação deve citar só o que o artigo
  cita" por "exceção decidida pelo grupo: o dado do Inep está só na
  apresentação, para mostrar o tamanho do problema".

---

## 5. Catálogo de animações

### 5.1 Princípios (os mesmos de hoje, no `README.md`, seção "Motion design")

- **Sem bibliotecas, offline**, em SVG e JavaScript puros.
- Dois tipos, como já existe:
  - **Filme** (`.filme[data-seq]` + função em `motion.js` que devolve
    `{duracao, legendas, marcos, render(t)}`): começa sozinho ao chegar no
    slide, K pausa, J e L voltam e avançam. `render(t)` é função pura do
    tempo. Usar para M1, M2, M3 e M10.
  - **Por passos** (o slide recebe `data-etapa`; o desenho reage por CSS
    ou por uma função de atualização, como `atualizarExemplo` em
    `diagramas.js`): quem apresenta controla o ritmo com a seta. Usar para
    M4 a M9 e M11 a M13. **Prefira passos no contexto**, porque a fala
    precisa casar com o desenho.
- **Um desenho só para os seis alunos.** Crie `js/contexto.js` com uma
  função que desenha os seis alunos nas **mesmas posições** de
  `POS_PROJ` (`diagramas.js:68`), com as mesmas formas e cores (círculo
  azul `#56B4E9` para o grupo maior, triângulo laranja `#E69F00` para
  Diego e Elisa, como na interface). Melhor ainda: extraia as posições
  para um lugar só e faça `diagramas.js` e `contexto.js` lerem dele.
- **Espessura das linhas = peso real** (`D.tiny.alocacao`), sem número na
  tela no contexto.
- **Cores de Okabe e Ito** e **forma junto com a cor** (ninguém depende só
  da cor). "Deixou o curso", "risco" e afins nunca só em vermelho: sempre
  com forma ou rótulo.
- **`prefers-reduced-motion`**: tudo abre no quadro final (filmes) ou no
  estado do passo (passos), como hoje.
- **Legendas dos filmes** sem termo técnico nos slides 4 a 13.
- **Transições curtas** (0,4 a 0,8 s por mudança de passo).

### 5.2 As animações

**M1 · Linha do tempo de um aluno que some** (filme, ≈ 12 s, `aluno-some`)
Uma linha horizontal de semestre (semana 1 a 16) com um aluno (círculo
neutro). Os eventos aparecem em ordem, como marcas na linha: falta (sem.
3), outra falta (sem. 5), não entrega um trabalho (sem. 7), para de
acessar o ambiente virtual (sem. 9), pede trancamento (sem. 14). Na
semana 16, um marcador "a instituição percebe aqui" (nota final). Por
fim, um destaque varre de volta as semanas 3 a 9 com a legenda "os sinais
estavam aqui". O aluno vai ficando mais transparente a cada evento.
**Ilustrativo** (avisar na fonte).

**M2 · De cada 100 que entraram** (filme, ≈ 14 s, `evasao-inep`)
Grade 10 × 10, cada ponto = 1% da turma de 2015. Um contador de ano:
Ano 1 → 13 pontos mudam para "deixou o curso" (contorno vazio, deslizam
levemente para fora da grade); Ano 2 → 29; Ano 3 → 40; "…"; Ano 10 → 60.
No fim, 39 pontos ganham o estado "concluiu" (preenchidos) e 1 "ainda
cursa". Número grande sincronizado ("60%"). **Só os anos conferidos**
(1, 2, 3 e 10); não interpolar os anos 4 a 9. Os números ficam num
arquivo à mão, `js/contexto-dados.js`, com a fonte e a página de cada um
(tabela da narrativa, seção 2).

**M3 · A lista vira mapa** (filme, ≈ 16 s, `contexto`)
Começa com a planilha das 10 matrículas (nome, disciplina, nota), como a
de `seqMetodo`, mas com nomes. A linha "Felipe · Sistemas de Computação ·
66" pisca sem nada de especial: legenda "Numa lista, o Felipe é só mais
uma linha". As linhas se desfazem: os nomes viram seis pontos, e os pontos
que dividem disciplina se ligam por linhas (sem mostrar o grafo
bipartido; isso fica para a Fundamentação). Os pontos se acomodam em
`POS_PROJ`; o Felipe fica na borda, com três linhas finas. Legenda final:
"No mapa, dá para ver quem está sozinho".

**M4 · Uma disciplina, uma ligação** (passos, `ligacao`)
0: Ana (etiqueta "ADS") à esquerda, Carla (etiqueta "Engenharia
Elétrica") à direita, a caixa "Sistemas de Computação" no meio.
1: as duas entram na caixa (setas curtas).
2: uma linha se desenha entre Ana e Carla, com o rótulo "ligação".
3: Bruno e Felipe também entram na caixa; as linhas entre os quatro se
desenham.

**M5 · A força da ligação** (passos, `forca`)
1: aparece "Algoritmos e Programação"; a linha Ana–Bruno engrossa (duas
disciplinas em comum), a Ana–Felipe continua fina.
2: painel lateral com duas turmas, uma de 300 pontinhos e outra de 15; a
linha entre dois alunos da turma lotada é fininha, a da turma pequena é
grossa.
3: volta ao exemplo: as linhas que vêm só de Sistemas de Computação (a
mais cheia) ficam um pouco mais finas. Espessuras de `D.tiny.alocacao`.

**M6 · Os grupos aparecem** (passos, `comunidades-ctx`)
0: o mapa dos seis, todos neutros.
1: um fundo suave envolve cada grupo (`D.tiny.louvain.membership`), e os
nós ganham cor e forma.
2: etiquetas de curso sobre cada nó; a da Carla ("Engenharia Elétrica")
se destaca dentro do grupo de maioria de ADS.
3: as etiquetas de curso esmaecem; fica o grupo.

**M7 · Ponte e beirada** (passos, `papeis-ctx`)
1: halo na Carla, rótulo "ponte".
2: a Carla esmaece; as linhas Carla–Diego e Carla–Elisa somem; Diego e
Elisa se afastam um pouco do resto. Depois, a Carla volta.
3: as três linhas do Felipe pulsam (finas); rótulo "beirada".
4: dois cartões lado a lado: "Carla · média 69 · ponte" e "Felipe · média
66 · beirada".

**M8 · As três perguntas** (passos, `atencao-talento`)
Três réguas horizontais (quantas disciplinas, como vai, quanto está
ligado ao grupo), cada uma com uma marca da média da turma. 1: o
marcador do Felipe desliza para abaixo da média nas três; aparece o
cartão com o texto do sistema. 2: Diego e Elisa destacados no mapa com o
fundo do grupo pulsando; cartão "em atenção: o grupo depende de uma
pessoa só". 3: dois cartões de talento (demonstração). Os valores das
réguas (disciplinas por aluno, média de nota, média da turma) vêm de
`dados.js`. A régua do vínculo é qualitativa no contexto (abaixo / na
média / acima), sem número.

**M9 · Do aluno ao grupo** (passos, `por-que-comunidade`)
1: um cartão "nota 66" sozinho, que depois "pousa" no Felipe, na borda do
mapa. 2: um ícone de pessoa se afastando de um grupo (ilustrativo, sem
números). 3: duas barras, "Pouco engajados 69%" e "Engajamento moderado
7%". 4: uma seta da Alice T. (referência) para o grupo dela, com o rótulo
"monitora natural do grupo". 5: a tabela "quem usa".

**M10 · Entra, sai** (filme curto, ≈ 10 s, `solucao`)
À esquerda, linhas de matrícula entrando; no meio, a marca do edugraph
(círculo, triângulo, quadrado, a mesma da capa); à direita, o mapa dos
seis alunos saindo, com quatro etiquetas que aparecem uma a uma: "grupos
com nome", "papel de cada aluno", "quem merece atenção, e por quê",
"quem se destaca, e por quê". No fim, um selo "mostra como chegou ao
resultado".

**M11 · O que é um grafo** (passos, `grafo`)
1: um mapa de metrô genérico (6 a 8 estações, duas linhas, sem nomes
reais). 2: o traçado vira pontos e linhas retas, com os rótulos "nó" e
"aresta". 3: os pontos se reorganizam no desenho dos seis alunos (posições
`POS_BIP`), como ponte para o slide `bipartido`.

**M12 · A régua do z** (passos, `escore-z`)
1: régua de notas com a média (70) e as faixas de um e dois passos (±10,
±20); dois marcadores, "90 → z = +2" e "60 → z = −1" (exemplo de conta).
2: três barras pequenas (carga, desempenho, vínculo) com os pesos 35%,
35% e 30%. 3: régua de risco de 0 a 1 com as faixas "sem sinais", "em
atenção" (0,25) e "risco alto" (0,50), e o Felipe em 0,64.

**M13 · O dicionário** (passos, `dicionario`, opcional)
O desenho dos seis alunos; a cada passo, uma palavra do contexto se
transforma no nome técnico sobre o próprio desenho: aluno → nó; ligação →
aresta; força → peso; grupo → comunidade; ponte → maior intermediação;
"abaixo da turma" → z negativo.

---

## 6. Dados: o que gerar e de onde

**Princípio:** todo número e todo texto do sistema que aparece num slide
vem de `js/dados.js`, gerado por `gerar_dados.py` a partir do repositório.
Nada é digitado à mão no HTML.

Acrescentar a `gerar_dados.py` um bloco `contexto` em `EDUGRAPH_DADOS`:

```text
contexto:
  nomes:        {S1: "Ana", S2: "Bruno", S3: "Carla", S4: "Diego", S5: "Elisa", S6: "Felipe"}
  cursos:       {S1: "ADS", S2: "ADS", S3: "Engenharia Elétrica", S4: ..., S6: "ADS"}
  disciplinas:  {DA: "Sistemas de Computação", DB: "Algoritmos e Programação", DC: "Circuitos Elétricos"}
  alunos:       por aluno: n_disciplinas, nota_media, papel, tier, risco, why (de run_lab)
  turma:        nota_media (74), disciplinas_por_aluno (1,67)
  demo:         counts, um exemplo de risco (why) e dois talentos (label + why),
                nomes das comunidades e NMI da revelação, de run_lab(demo)
```

- `nomes`, `cursos` e `disciplinas` são **escolha de desenho** (como as
  posições): declarar isso no comentário e na linha de fonte.
- `alunos` e `turma`: `edugraph.lab.service.run_lab(roots=ArtifactRoots
  ([Path("data/fixtures")]), source="tiny_v1", students=6)`, campos
  `insight.signals.students` e `insight.roles`; `n_disciplinas` e
  `nota_media` calculados das matrículas de `D.tiny`.
- `demo`: `run_lab(..., source="demo", students=45, seed=12, noise=0.2)`,
  os **valores padrão do laboratório** (`frontend/src/components/LabView.tsx:52`).
  Escolher os talentos por regra fixa, não à mão: o primeiro talento com a
  marca `apoio` (referência) e o primeiro com `polimata` (ponte). Em
  21/11/2026 eram Alice T. e Larissa J. Se mudar, a fala muda junto.
- `ArtifactRoots` mora em `edugraph.contracts.paths`. Rode com o Python do
  `.venv` (o do sistema não acha o `edugraph`).

Valores conferidos em 21/11/2026, para comparar depois de gerar:

| O quê | Valor |
|---|---|
| Felipe (S6) | risco 0,642, "Risco alto"; why: "nota média 66, abaixo da turma (74)" · "pouco ligado ao próprio grupo" |
| Diego (S4), Elisa (S5) | "Em atenção" (0,463 e 0,483); why: "ficou num grupo só dele…" (ver T-OBS-06) |
| Carla (S3) | papel "ponte", risco 0,177, sem sinais |
| Turma padrão do laboratório | 43 alunos, *Q* = 0,528, 3 grupos; 8 risco alto, 4 em atenção, 12 talentos |
| Exemplo de risco na demo | "cursa só 1 disciplina (média da turma: 2,16)" · "nota média 52, abaixo da turma (70)" · "pouco ligado ao próprio grupo" |
| Alice T. | "nota média 82, acima da turma (70)" · "se destaca em Estruturas de Dados" · "é referência no próprio grupo: pode apoiar colegas como monitor" |
| Larissa J. | "se destaca em Redes de Computadores" · "liga grupos diferentes sem perder desempenho" |

**Dados de fora do repositório** (Inep): ficam em `js/contexto-dados.js`,
escrito à mão, com um comentário por número citando gráfico e página.
Entram no `VERIFICACAO.md` como "conferido no relatório, não gerado".

---

## 7. Outros arquivos a atualizar

| Arquivo | O quê |
|---|---|
| `js/config.js` | `secoes` continua igual; `duracaoAlvoMin` quando o tempo da defesa for definido |
| `css/slides.css` | estilos novos com prefixo `ctx-` |
| `index.html` | carregar `js/contexto-dados.js` e `js/contexto.js` (scripts clássicos, sem módulo, como os outros) |
| `README.md` da pasta | contagem de slides (46 + 15), a lista de sequências em "Motion design", a nova ordem, o tempo, e a exceção "nomes, cursos e a linha do tempo do slide 4 são ilustrativos" em "De onde vêm os números" |
| `VERIFICACAO.md` | o que foi conferido (dados do Inep, textos do sistema, nomes), o que não foi |
| `ROTEIRO.md` | **não editar à mão**: rodar `python apresentacao/gerar_roteiro.py` depois de mexer nas notas |
| `apresentador.html` / `js/apresentador.js` | nada estrutural: ele lê as notas do `index.html`. Conferir que notas mais longas cabem e rolam |

---

## 8. Como conferir antes de entregar

1. `python apresentacao/gerar_dados.py` e conferir os valores da tabela da
   seção 6.
2. `python apresentacao/servir.py` e percorrer **todos** os slides com a
   seta, passo a passo, na janela da plateia e no modo apresentador (P):
   as duas janelas sincronizadas, as notas certas em cada slide.
3. Abrir `index.html` direto do disco (duplo clique): slides e animações
   funcionam sem servidor.
4. Ativar "reduzir movimento" no sistema operacional e ver que todo slide
   abre no quadro final.
5. `--curta`: os opcionais somem e a numeração continua certa.
6. Visão geral (O): os títulos novos aparecem.
7. **Varreduras de texto** (no `index.html`):
   - nenhum "exigência do orientador";
   - nenhum "prevê"/"previsão" afirmativo (só em "não é previsão");
   - nenhum "aluno 1…6", "disciplina A/B/C" ou "3–4" fora das linhas de
     fonte;
   - cada sigla (ADS, Inep, OULAD, AVA, NMI) por extenso na primeira vez;
   - nenhum nome de integrante fora da capa e do encerramento (incluindo
     a fala da capa).
8. `python apresentacao/gerar_roteiro.py` e ler o `ROTEIRO.md` gerado
   contra o `ENREDO.md`: a fala de cada slide deve ser a do enredo.
9. Projetor ou tela 1280 × 720: o texto dos slides novos é legível de
   longe (mínimo do corpo igual ao dos slides atuais).
10. Rodar a demonstração inteira uma vez, incluindo o painel de sinais.

---

## 9. Observações relacionadas (`observacoes/para-todos.md`)

- **T-OBS-05**, pergunta 3: o nome "risco de evasão". Enquanto não houver
  resposta, os slides usam "merece atenção" e mostram o rótulo do sistema
  só como texto do sistema.
- **T-OBS-06**: o texto "ficou num grupo só dele" para grupos de dois
  alunos. Se for corrigido antes do ajuste, o slide `atencao-talento`
  pode mostrar o texto novo de Diego e Elisa.
- **T-OBS-07**: a frase "exigência do orientador" em `README.md`,
  `CLAUDE.md`, ADR-0008, `tests/contract/test_no_ml.py` e no estudo da
  apresentação. Neste ajuste, corrigir só a nota do slide `objetivos` (e,
  com ela, o `ROTEIRO.md` gerado); o resto fica para a pendência. Se o
  ajuste resolver a parte da apresentação, atualizar o item.

Fechar ou atualizar esses itens no mesmo commit que os resolver, como
manda o `CLAUDE.md`.

---

## 10. Fora do escopo

- Não mudar o sistema (`src/`, `frontend/`) para a apresentação, exceto se
  o grupo decidir resolver T-OBS-06 (e aí com teste).
- Não mudar `data/fixtures/`.
- Não usar biblioteca de animação, vídeo renderizado ou CDN.
- Não copiar mapa de metrô real (nomes, cores ou traçado de uma rede
  existente): o M11 é genérico.
