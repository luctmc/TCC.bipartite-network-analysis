# Consulta 01 — não há estrutura de comunidade entre alunos no OULAD

**Data:** 18/09/2026 · **Grupo 16** · **Redigido por:** Pedro (Frente A —
dados e modelagem) · **Decisão pedida até:** antes do fechamento da
Frente B

---

## O pedido, em quatro linhas

Medimos a base e descobrimos que a projeção aluno↔aluno do OULAD **não
tem estrutura de comunidade** — a modularidade alta que ela produz é
indistinguível do acaso. O diagnóstico está fechado e a causa é
conhecida. Já medimos uma saída que funciona, mas ela **troca o critério
de aresta** da matrícula para a interação no ambiente virtual, e isso é
uma mudança de modelagem que preferimos não tomar sozinhos.

**Pergunta central:** trocar o critério de aresta descaracteriza a
proposta aprovada, ou é o ajuste legítimo de quem mediu a base antes de
escrever?

---

## 1. O problema

O trabalho projeta um grafo bipartido aluno × disciplina em dois grafos
simples e procura comunidades no lado do aluno. Para isso funcionar,
alunos precisam **compartilhar disciplinas**. No OULAD eles não
compartilham.

| medida | valor |
|---|---|
| matrículas | 29.278 |
| alunos distintos | 26.099 |
| módulos | 7 |
| módulo × apresentação | 22 |
| **alunos que cursam um único módulo** | **91,8%** |

Com 91,8% dos alunos em grau 1, a projeção aluno↔aluno vira uma união de
cliques quase disjuntas: cada módulo produz um bloco de alunos totalmente
conectados entre si e desconectados do resto. A modularidade de um grafo
assim é alta **por construção**, não por haver grupos.

## 2. Por que temos certeza de que não é erro nosso

Esta é a parte que consideramos a contribuição metodológica do trabalho,
e ela vale independentemente da decisão tomada aqui.

Implementamos um **modelo nulo** (spec A-08): o mesmo grafo, com o mesmo
número de alunos, o mesmo grau de cada aluno e o mesmo total de arestas,
mas com **quem cursou o quê sorteado**. Toda estrutura relacional é
destruída de propósito. Rodar o mesmo Louvain nele dá a linha de base
contra a qual o Q real precisa ser comparado — a modularidade encontra
"comunidades" em qualquer grafo esparso, inclusive em grafos aleatórios
(Guimerà et al., 2004).

| base | Q real | Q do nulo | veredito |
|---|---|---|---|
| `synthetic_v1` (grupos plantados) | 0,4666 | 0,2079 ± 0,0168 | z = +15,4 — **estrutura** |
| `synthetic_v2` (grupos plantados) | 0,5392 | 0,4611 ± 0,0202 | z = +3,9 — **estrutura** |
| **OULAD** `module_presentation` | **0,7728** | **0,781** | **abaixo do acaso** |

A leitura é direta. Nas bases sintéticas, onde plantamos os grupos de
propósito, o método os encontra com folga — **o pipeline funciona**. No
OULAD, o Q de 0,77 é *menor* que o de réplicas embaralhadas. Não há o que
detectar ali, e reportar 0,77 como "forte estrutura de comunidades" seria
um erro que a banca teria todo direito de cobrar.

## 3. O que já tentamos, e por que não resolveu

| tentativa | resultado medido | por que falha |
|---|---|---|
| Granularidade mais fina: nó = **apresentação** do módulo (22 em vez de 7) | ajuda no lado *disciplina* (93 de 231 arestas); lado aluno inalterado | o aluno continua em uma apresentação só |
| Granularidade mais fina: nó = **avaliação**, na coorte BBB 2013J | 1.706 alunos, 11 avaliações, densidade **0,997**, Q = **0,021** | todos fazem as mesmas avaliações: o grafo fica quase completo, e grafo completo não tem comunidades |
| Rodar a base inteira sem amostra | > 5 GB, não termina em 10 min (~15,9 M pares) | limite de escala, não de método |

O problema não se move porque ele não é de parâmetro. É de **ausência de
informação relacional** no critério de aresta que estamos usando.

## 4. A saída que medimos hoje: o ambiente virtual

O OULAD traz uma segunda camada que não estávamos usando: o registro de
interação dos alunos com o **ambiente virtual de aprendizagem** — 6.364
recursos, classificados em 20 tipos de atividade (material, subpágina,
conteúdo, URL, fórum, questionário…).

Ali o aluno **não tem grau 1**:

| nó "disciplina" | grau mediano do aluno |
|---|---|
| módulo | 1 |
| módulo × apresentação | 1 |
| **recurso do ambiente virtual** | **40** |
| **tipo de atividade** | **7** |

Refizemos toda a cadeia na coorte BBB 2013J usando recurso do ambiente
virtual como nó do lado direito: 1.870 alunos × 320 recursos, 67.531
arestas no bipartido.

| pesagem da projeção | Q real | Q do nulo | razão |
|---|---|---|---|
| contagem simples | 0,0393 | 0,0090 | 4,4× |
| **alocação de recursos** (Zhou et al., 2007) | **0,0825** | **0,0156** | **5,3×** |

Cada réplica nula cai muito abaixo do valor real, nas duas pesagens. O
sinal existe e é inequívoco.

**E aqui apareceu um achado que vale por si.** A escolha da pesagem
decide se o sinal é visível. Quando extraímos a espinha do grafo
(ficando só com as arestas mais pesadas), a **contagem simples inverte de
lado**: o Q real passa a ficar *abaixo* do nulo em todos os limiares
testados. A **alocação de recursos** se mantém acima em todos. A razão é
interpretável: a contagem simples premia o aluno que clicou muito, então
as arestas mais pesadas ligam os alunos mais ativos entre si — isso é
efeito de volume, não de afinidade. A alocação de recursos normaliza pelo
grau e desfaz exatamente esse viés.

Como o briefing já exige implementar as duas projeções à mão, o trabalho
tem como mostrar esse contraste com autoridade. É um resultado sobre
**método**, que sobrevive à decisão tomada aqui.

### Confirmação em três coortes independentes

Antes de propor isto como saída, testamos se o achado se sustenta fora de
BBB 2013J — tanto entre sementes do Louvain quanto entre módulos
diferentes. Usamos a pesagem por alocação de recursos, três sementes cada.

| coorte | alunos × recursos | Q real (3 sementes) | comunidades × tamanho | Q nulo (5 réplicas) | z |
|---|---|---|---|---|---|
| BBB 2013J | 1.870 × 320 | 0,0825 / 0,0825 / 0,0825 | 4: 941, 480, 322, 127 | 0,0158 ± 0,0002 | +268,9 |
| FFF 2013J | 2.098 × 526 | 0,0742 / 0,0742 / 0,0747 | 3: 1.457, 455, 186 | 0,0081 ± 0,0002 | +327,4 |
| DDD 2014J | 1.647 × 361 | 0,0511 / 0,0512 / 0,0512 | 3–4: 1.046, 540, 61 (ou 969, 515, 146, 17) | 0,0073 ± 0,0001 | +400,5 |

O padrão se repete nas três: Q real estável entre sementes (variação na
quarta casa decimal) e centenas de desvios acima do nulo. As partições
não são degeneradas — não é "uma comunidade gigante e sobras de nó
isolado". Há sempre uma comunidade maior (50% a 69% dos alunos) e duas ou
três menores com tamanho que permite caracterização, o que é o requisito
mínimo para a palavra "interpretável" do objetivo.

A única instabilidade encontrada: em DDD 2014J, a semente 42 converge
para 3 comunidades e as sementes 7 e 99 para 4 (a quarta, de 17 alunos,
ora aparece separada, ora dentro da terceira). O valor de Q não muda; só
a partição exata na margem. Registramos como limitação conhecida do
Louvain, não como falha do achado.

### As ressalvas, ditas antes de perguntarem

- **O Q absoluto é baixo** (0,08). A estrutura é estatisticamente
  inequívoca, mas fraca. Se ela vai ser *interpretável* — a palavra do
  nosso objetivo — depende da caracterização das comunidades, que ainda
  não fizemos.
- **A projeção fica quase completa** (densidade 0,9996): com 320
  recursos e grau 40, quase todo par de alunos compartilha algo. A
  informação está nos **pesos**, não na presença da aresta.
- **Aplicar limiar fragmenta o grafo**: nos cortes testados, o grafo se
  quebra em mais de 900 componentes, a maioria de nó isolado. O recorte
  honesto é a projeção cheia com alocação de recursos.
- **O desvio do nulo é estimado sobre poucas réplicas** (5 por coorte),
  então o z-score gigante deve ser lido como "muito acima", não como
  número exato. A razão entre Q real e Q nulo é a medida mais robusta, e
  é a que reportamos. Testamos em três coortes (BBB, FFF, DDD) e o
  afastamento se repete nas três, o que reduz a chance de ser
  particularidade de uma delas.
- **A partição exata varia um pouco entre sementes do Louvain** em pelo
  menos uma coorte (DDD 2014J oscila entre 3 e 4 comunidades). O valor de
  Q não muda; é a fronteira de uma comunidade pequena que se desloca.

### O custo

Estender o ETL para a tabela de interações (10,6 milhões de linhas) e
acrescentar um valor novo à granularidade do contrato. Isso mexe em
`contracts/`, que é congelado: exige ADR, aprovação dos três e subida da
versão do esquema. Estimamos duas a três sessões de trabalho.

Um detalhe a favor: o contrato **já prevê** `vle_activity` como critério
de aresta. A arquitetura foi desenhada admitindo esta rota; falta só
habilitá-la.

## 5. As saídas, lado a lado

**Saída 1 — Trocar o critério de aresta para a interação no ambiente
virtual.** *(a que recomendamos)*
Entrega o resultado positivo que o objetivo declarado pede, com sinal
medido e linha de base. Custo de duas a três sessões e uma ADR. Risco: o
Q baixo pode gerar comunidades pouco interpretáveis.

**Saída 2 — Reposicionar a análise para o lado das disciplinas.**
A projeção disciplina↔disciplina **já funciona**: 22 nós, 93 de 231
arestas, e a intermediação discrimina bem. As comunidades passariam a ser
de disciplinas — áreas curriculares — em vez de alunos. Custo quase zero,
porque a Frente C (disciplinas críticas) já se apoia nisso e está segura.
Risco: mexe no objetivo declarado na Introdução, que fala em agrupar
alunos.

**Saída 3 — Trocar de base.**
EdNet, ASSISTments, Junyi Academy e xAPI-Edu-Data têm interação aluno ×
item, que é o grau alto que falta. Custo: ETL do zero e perda do OULAD,
que é a base citável em periódico (Kuzilek; Hlosta; Zdrahal, *Scientific
Data*, 2017). Só faz sentido se a Saída 1 falhar na caracterização.

**Saída 4 — Reportar o resultado negativo como resultado.**
O trabalho afirmaria que, em nível de módulo, a modularidade alta da
projeção aluno↔aluno do OULAD é artefato da esparsidade e não estrutura —
sustentado pelo modelo nulo e pelo controle sintético. Custo zero.
**Esta saída é compatível com todas as outras e entra no artigo de
qualquer forma**, porque é ela que justifica por que mudamos de rota.

**Saída 5 — Trocar a métrica de comunidade.** *(não recomendamos, e
explicamos por quê)*
Percolação de cliques (Palla et al., 2005) ou componentes com corte de
peso não resolvem: o problema não é a métrica, é a ausência de vizinhança.
Com 91,8% dos alunos em grau 1, nenhum algoritmo cria relação que o dado
não tem. Vale registrar que descartamos essa via **por diagnóstico**, não
por desconhecimento.

## 6. O que pedimos ao senhor

1. Trocar o critério de aresta de "cursou o módulo" para "interagiu com o
   recurso" mantém o trabalho dentro do que foi aprovado?
2. Se sim, aceitamos manter o objeto em comunidades de **alunos**, com a
   ressalva de que o Q é baixo embora inequívoco?
3. Se não, o senhor prefere reposicionar para comunidades de
   **disciplinas** (Saída 2) ou assumir o achado negativo como resultado
   principal (Saída 4)?
4. Há preferência por preservar o OULAD como base citável, ou vale abrir
   a busca por outra fonte?

Nossa inclinação é **Saída 1 combinada com a Saída 4**: a interação no
ambiente virtual dá o resultado positivo, e o achado do modelo nulo entra
no capítulo de método como a justificativa da mudança. Assim o trabalho
tem um resultado positivo e uma contribuição metodológica, e nenhuma das
duas depende da outra dar certo. A confiança nessa inclinação subiu desde
a primeira medição: o sinal se repete em três coortes independentes
(BBB, FFF, DDD), com partições equilibradas e Q estável entre sementes —
não é mais uma observação isolada de uma única coorte.

---

### Como reproduzir os números

```bash
python scripts/download_oulad.py    # espelho do UCI, SHA-256 conferido
python -m edugraph data etl
python -m edugraph data null --root data/processed \
    --dataset oulad_module_presentation --replicas 5
```

Detalhamento em [`docs/specs/frente-a/A-08-modelo-nulo.md`](../specs/frente-a/A-08-modelo-nulo.md)
e [`docs/artigo/decisoes-metodologicas.md`](../artigo/decisoes-metodologicas.md).
As medições do ambiente virtual desta consulta são exploratórias e ainda
não estão versionadas como spec — viram a A-09 se a Saída 1 for aprovada.

### Referências citadas

- GUIMERÀ, R. et al. Modularity from fluctuations in random graphs and
  complex networks. *Physical Review E*, v. 70, 2004.
- KUZILEK, J.; HLOSTA, M.; ZDRAHAL, Z. Open University Learning Analytics
  dataset. *Scientific Data*, v. 4, 2017.
- PALLA, G. et al. Uncovering the overlapping community structure of
  complex networks in nature and society. *Nature*, v. 435, 2005.
- ZHOU, T. et al. Bipartite network projection and personal
  recommendation. *Physical Review E*, v. 76, 2007.
