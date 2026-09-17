# Briefing para Planejamento de Implementação — TCC Grupo 16

> Documento de contexto para geração do plano de implementação completo.
> Leia inteiro antes de produzir qualquer saída.

---

## 0. O que estou pedindo

Preciso de um **plano de implementação completo** para o projeto descrito
abaixo, materializado diretamente no repositório clonado. Não é código
pronto de todas as features — é a arquitetura, os contratos, o esqueleto,
a configuração e o plano de execução que permitam três pessoas
desenvolverem **em paralelo, sem bloqueio mútuo**.

Se as skills abaixo estiverem disponíveis nesta sessão, use-as:
`engineering:architecture` (para registrar as decisões arquiteturais como
ADRs), `engineering:system-design` (para o desenho de componentes e
fronteiras), `engineering:testing-strategy` (para a estratégia de testes,
que é o que sustenta o paralelismo) e `engineering:documentation` (para o
README e a documentação de contratos). Verifique com `/plugin` quais estão
instaladas.

**Se nenhuma estiver disponível, siga assim mesmo** — este documento é
autossuficiente, e o template de spec da seção 12 é obrigatório
independentemente de qualquer skill.

---

## 1. Contexto acadêmico

**Trabalho de Conclusão de Curso — Ciência da Computação**
Centro Universitário Padre Anchieta (UniAnchieta), Jundiaí/SP.

**Título:** "Análise Topológica e Detecção de Comunidades em Redes
Complexas: Projeção de Grafos Bipartidos e Métricas de Centralidade em
Dados Educacionais".

**Grupo 16:** Gabriel Luís Lopes, Pedro Alexandre dos Santos Chaves,
Lucas Timponi Mercadante Castro.
**Orientador:** Prof. Me. Clayton Augusto Valdo.

**Repositório:** https://github.com/luctmc/TCC.bipartite-network-analysis

O TCC é entregue como artigo de até 18 páginas, estruturado em Introdução,
Fundamentação, Resultados e Discussão, e Conclusão. A Introdução já foi
entregue e aprovada — o objetivo declarado nela é vinculante, e a
Conclusão terá que responder exatamente a ele.

### Objetivo declarado (transcrito da Introdução já entregue)

> Projetar e implementar um sistema de análise estrutural capaz de mapear
> e extrair padrões ocultos em bases de dados educacionais utilizando
> puramente algoritmos de Teoria dos Grafos. O trabalho modelará os dados
> relacionais como um Grafo Bipartido. A pesquisa focará na aplicação de
> algoritmos de projeção de redes (para inferir a força de relacionamento
> entre alunos com base em atributos compartilhados) e na execução de
> algoritmos de Detecção de Comunidades (como Louvain ou Girvan-Newman)
> para agrupar perfis semelhantes matematicamente, sem o uso de IA
> predeterminada. O estudo também avaliará a topologia da rede aplicando
> métricas de Centralidade (Intermediação e Autovetor) para identificar
> gargalos no fluxo educacional ou atributos de maior impacto no sistema.

As duas aplicações práticas declaradas são: **gestão pedagógica**
(agrupamentos interpretáveis de perfis de alunos + identificação de
disciplinas críticas no fluxo curricular) e **pesquisa em análise de
sistemas complexos** (demonstrar que técnicas clássicas de Ciência de
Redes são alternativa transparente aos modelos preditivos opacos).

---

## 2. Restrição inegociável

**Nenhum componente do sistema pode usar IA, aprendizado de máquina ou
qualquer modelo que dependa de treinamento com dados rotulados.**

Isso foi exigido explicitamente pelo orientador e é o diferencial
declarado do trabalho. Está fora de escopo, sem exceção:

- scikit-learn, TensorFlow, PyTorch, ou qualquer biblioteca de ML
- k-means, DBSCAN, ou qualquer clustering que não seja detecção de
  comunidades por otimização de modularidade
- embeddings de grafo (node2vec, DeepWalk, GNNs)
- classificadores, regressores, modelos preditivos de qualquer natureza

Toda inferência precisa ser **determinística e rastreável até a estrutura
do grafo**. Rótulos históricos presentes no dataset (ex: o desfecho da
matrícula) entram **apenas na etapa de validação a posteriori** — nunca
como entrada de algoritmo.

Ao propor qualquer biblioteca ou técnica no plano, verifique antes se ela
viola essa restrição. Se houver dúvida, escolha a alternativa clássica de
Teoria dos Grafos.

---

## 3. Material de referência anexado

Está anexado a este prompt um **starter kit** que valida, sobre dados
sintéticos, que o pipeline descrito neste documento fecha ponta a ponta:

```
src/etl/build_graph.py        # ETL + grafo bipartido + 2 projeções
src/community/detect.py       # Louvain + Girvan-Newman + modularidade
src/centrality/metrics.py     # grau, intermediação (Brandes), autovetor
src/api/main.py               # FastAPI expondo as três camadas
data/synthetic/generate_synthetic.py  # gerador de dados de teste
requirements.txt              # versões fixadas e testadas
```

Resultados de referência já obtidos com ele (120 alunos sintéticos, 7
disciplinas, 197 arestas): Louvain encontra ~25 comunidades com Q ≈ 0,47;
Girvan-Newman chega ao mesmo número de comunidades com Q ≈ 0,42 e foi
**645x mais lento** neste grafo.

**Trate este material como prova de conceito, não como base a preservar.**
Ele existe para você entender que os algoritmos e as bibliotecas escolhidas
funcionam sobre o formato de dados descrito, e como referência de que
resultado esperar. Ele não foi desenhado para paralelismo entre frentes —
foi escrito e testado sequencialmente, por uma única pessoa. Sinta-se livre
para reorganizar, reescrever ou descartar qualquer parte dele ao propor a
arquitetura da seção 4; a única coisa que precisa sobreviver é a lógica
validada (os algoritmos e como eles se encaixam), não os arquivos em si.
Não é necessário justificar divergências dele em ADR — só divergências das
decisões explícitas deste documento (seções 2, 4 e 7) precisam de ADR.

---

## 4. REQUISITO CENTRAL — três frentes em paralelo

Esta é a razão principal deste pedido, e o critério pelo qual o plano será
avaliado.

O grupo tem três pessoas e vai trabalhar nas três frentes
**simultaneamente**, não em sequência. Na organização ingênua, isso não
funciona: a Frente B (comunidades) e a Frente C (centralidade) precisam da
projeção que a Frente A (dados) produz, então ficariam paradas esperando.

**Projete a arquitetura para eliminar esse bloqueio.** Espero que o plano
resolva isso com, no mínimo:

### 4.1 Contratos antes de implementação
Defina os contratos de dados entre as camadas **como primeira entrega**,
antes de qualquer lógica. Cada frente programa contra o contrato, não
contra a implementação da frente vizinha. Use tipagem explícita
(`typing.Protocol`, dataclasses, ou equivalente) para que o contrato seja
verificável por ferramenta, não só por convenção.

### 4.2 Fixtures determinísticas versionadas
Grafos de teste salvos no repositório, em formato estável, que as Frentes
B e C consomem **sem executar nada da Frente A**. O gerador sintético já
existente serve de base. As fixtures precisam ser determinísticas (seed
fixa) para que os testes não quebrem por acaso.

### 4.3 Fronteiras de módulo sem imports cruzados
Nenhuma frente importa diretamente o módulo de outra. A comunicação
acontece por contratos e por artefatos em disco. Isso também minimiza
conflito de merge: cada frente toca essencialmente sua própria pasta.

### 4.4 Testes de contrato
Cada frente testa contra o contrato, não contra a implementação real da
outra. Quando a Frente A entregar a projeção de verdade, B e C devem
funcionar sem alteração de código — só troca de fonte de dados.

### 4.5 Estratégia de branch e merge
Defina o fluxo de branches que permite três pessoas commitando ao mesmo
tempo com o mínimo de conflito. Inclua o que precisa estar em `main` desde
o primeiro dia para destravar todo mundo.

### 4.6 Ordem de entrega dentro do paralelismo
Mesmo em paralelo, existem dependências reais. Explicite quais são e como
cada uma é neutralizada (por fixture, por mock, por contrato), e o que
efetivamente precisa acontecer antes de qualquer outra coisa.

---

## 5. As três frentes

| Frente | Dono | Escopo |
|---|---|---|
| **A — Dados e Modelagem** | Pedro | ETL do OULAD, construção do grafo bipartido, projeção aluno↔aluno e disciplina↔disciplina, gerador de dados sintéticos |
| **B — Detecção de Comunidades** | Gabriel | Louvain, Girvan-Newman, cálculo de modularidade (Q), comparação de qualidade e custo, caracterização de comunidades |
| **C — Centralidade e Aplicação** | Lucas | Grau, intermediação, autovetor, aplicação sobre nós de disciplina, API, front-end de visualização |

---

## 6. Escopo funcional do sistema

### 6.1 Pipeline
1. **ETL** — dados educacionais brutos (CSV) → formato normalizado
2. **Grafo bipartido** — G = (U ∪ V, E), U = estudantes, V = disciplinas.
   Aresta = relação de desempenho/participação.
3. **Projeção** — dois grafos monopartidos ponderados:
   - aluno↔aluno, peso = função dos atributos compartilhados
   - disciplina↔disciplina, peso = função dos alunos em comum
   Duas estratégias de ponderação a implementar e comparar: contagem
   simples de vizinhos compartilhados, e alocação de recursos
   (Zhou et al., 2007), que corrige o viés a favor de nós de alto grau.
4. **Detecção de comunidades** — Louvain e Girvan-Newman, comparados por
   modularidade e tempo.
5. **Centralidade** — grau, intermediação (algoritmo de Brandes) e
   autovetor (iteração de potência), nas duas projeções.
6. **Apresentação** — API + visualização interativa do grafo.
7. **Validação** — cruzamento dos resultados com o desfecho real do
   dataset, a posteriori.

### 6.2 Saídas obrigatórias
Estas respondem diretamente ao objetivo declarado na Introdução:

- Agrupamentos interpretáveis de perfis de estudantes, com caracterização
  de quais disciplinas predominam em cada comunidade.
- Identificação de disciplinas críticas no fluxo curricular, via
  centralidade sobre os nós de **disciplina** — não apenas sobre alunos.
  *Este ponto é fácil de esquecer e é obrigatório.*
- Métricas comparativas: Q, número de comunidades, tempo de execução por
  algoritmo.
- Relatórios de uso **exclusivamente interno** da instituição. O sistema
  não expõe dados a terceiros.

---

## 7. Stack definida

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11+ |
| Processamento/ETL | pandas |
| Grafos e algoritmos | NetworkX, python-louvain, NumPy/SciPy |
| API | FastAPI + uvicorn |
| Persistência | arquivos (GML/Parquet) ou SQLite — sem banco de grafos |
| Front-end | a definir no plano; preferência por algo que renderize grafo interativo (Cytoscape.js é candidato) |

Versões já testadas e funcionando juntas: `fastapi==0.141.1`,
`networkx==3.6.1`, `numpy==2.4.4`, `pandas==3.0.2`, `python-louvain==0.16`,
`uvicorn==0.53.0`.

**Sobre usar bibliotecas prontas:** é legítimo e citável usar NetworkX
para os algoritmos. Mas o plano deve prever **pelo menos um algoritmo
implementado à mão** — a projeção bipartida é a candidata natural — para
comparação com a implementação da biblioteca. Isso demonstra domínio na
banca, não apenas uso de ferramenta.

---

## 8. Dados

**Base principal:** OULAD — Open University Learning Analytics Dataset.
Público, anonimizado, citável em artigo revisado por pares (Kuzilek;
Hlosta; Zdrahal, 2017, *Scientific Data*). Sete tabelas CSV, ~32 mil
estudantes, com estudantes, módulos, avaliações, interações no AVA e o
desfecho de cada matrícula.

**Base secundária:** gerador sintético próprio, com comunidades plantadas
de propósito, usado como *ground truth* para validar se os algoritmos
recuperam estrutura conhecida. Também serve de fixture para o
paralelismo descrito na seção 4.

**Decisão ainda aberta que o plano deve tratar:** qual critério define a
existência de uma aresta no grafo bipartido (nota mínima? resultado final
aprovado? participação no AVA?). O plano deve deixar esse critério
**parametrizável**, porque o grupo vai testar mais de uma configuração e
comparar os resultados no capítulo de Resultados.

**Atenção de escala:** o Girvan-Newman tem complexidade O(m²n) e
provavelmente não termina em tempo viável sobre o OULAD completo. O plano
precisa prever isso — amostragem, subgrafo por módulo, ou limite de tempo
configurável — e tratar essa limitação como resultado a reportar, não
como falha.

---

## 9. Requisitos que vêm do artigo, não do software

O código precisa produzir insumo para o texto acadêmico. Considere isso
requisito funcional:

- **Figuras reprodutíveis.** Um módulo ou notebook dedicado só a gerar as
  figuras que vão para o artigo, de forma que refazer uma figura na semana
  da entrega seja um comando, não uma arqueologia.
- **Métricas exportáveis.** Todos os números (Q, tempos, tamanhos de
  comunidade, rankings de centralidade) precisam sair em formato
  tabelável, porque viram tabelas do capítulo 3.
- **Rastreabilidade das decisões.** Cada escolha não-óbvia (critério de
  aresta, função de ponderação, parâmetros dos algoritmos) precisa estar
  registrada, porque vira parágrafo de justificativa no texto e pergunta
  de banca.
- **Comparações, não só resultados.** O trabalho compara Louvain vs.
  Girvan-Newman e projeção simples vs. ponderada. A arquitetura deve
  tornar trivial rodar as duas variantes e coletar as duas saídas.

---

## 10. Entregas esperadas do plano

1. **ADRs** das decisões arquiteturais principais, com alternativas
   consideradas e trade-offs.
2. **Desenho de componentes** com as fronteiras entre as três frentes
   explícitas, e o diagrama que vai abrir o capítulo 3 do artigo.
3. **Contratos de dados** entre camadas, tipados e documentados.
4. **Estrutura de diretórios completa**, criada no repositório,
   incluindo obrigatoriamente uma pasta de documentação (ver seção 11).
5. **Specs por feature**, organizadas por frente (ver seção 12).
6. **Esqueleto de código** por frente: assinaturas, docstrings e stubs
   que compilam, com os pontos de implementação marcados.
7. **Fixtures** determinísticas para desenvolvimento paralelo.
8. **Estratégia de testes**, incluindo os testes de contrato que
   sustentam o paralelismo.
9. **Configuração de ambiente**: requirements, setup, linting,
   `.gitignore`, `CLAUDE.md`.
10. **Plano de execução**: ordem das tarefas por frente, o que destrava o
    quê, e o que precisa existir em `main` desde o dia um.
11. **README** de onboarding — alguém que clona o repositório consegue
    rodar tudo seguindo só ele.

---

## 11. Pasta de documentação

Toda a documentação do projeto vive numa pasta dedicada no repositório,
versionada junto com o código. Proponha a organização interna, mas ela
precisa comportar pelo menos:

- as **specs** de feature, separadas por frente (seção 12)
- os **ADRs** com as decisões arquiteturais
- a documentação dos **contratos de dados** entre camadas
- o material que alimenta o artigo: decisões metodológicas registradas,
  índice das figuras geradas, tabelas de métricas exportadas

O critério é: se alguém do grupo precisar responder "por que fizemos
assim?" três semanas depois, ou na banca, a resposta está nessa pasta.
Nada de decisão importante morando só no histórico do chat ou na cabeça
de quem implementou.

---

## 12. Specs por feature

Além do plano macro, quero **uma spec por unidade de trabalho
implementável**, de modo que cada pessoa possa pegar uma spec e executá-la
de ponta a ponta sem precisar perguntar o que fazer.

**Organização:** agrupadas por frente, para que cada dono saiba quais são
as suas. Uma pessoa pode pegar qualquer spec da sua frente sem depender de
spec de outra frente estar concluída — isso é consequência direta do
requisito de paralelismo da seção 4, e as specs devem refletir isso.

**Granularidade:** cada spec deve ser executável em uma sessão de trabalho
razoável. Se uma spec parece grande demais para isso, quebre em duas. Se
duas specs são pequenas demais e sempre seriam feitas juntas, funda.

**Template obrigatório.** Toda spec segue exatamente esta estrutura, para
que qualquer pessoa do grupo consiga pegar uma spec de outra frente e
entender sem contexto adicional:

```markdown
# [ID] Título da spec

**Frente:** A | B | C
**Dono:** Pedro | Gabriel | Lucas
**Status:** não iniciada | em andamento | concluída

## Objetivo
Uma ou duas frases: o que passa a existir depois desta spec.

## Contexto
Que contratos esta spec consome e que contratos ela cumpre.
Referência ao documento de contratos correspondente.

## Dependências
- O que precisa estar pronto antes.
- Quando houver dependência de outra frente: qual fixture ou mock a
  substitui, para que esta spec não fique bloqueada.

## Escopo
### Incluído
- ...
### Fora de escopo
- ...

## Critérios de aceite
Verificáveis, no formato "dado X, quando Y, então Z".
- [ ] ...
- [ ] ...

## Testes exigidos
- Testes de contrato: ...
- Testes unitários: ...

## Arquivos criados ou alterados
- `caminho/do/arquivo.py` — o que muda

## Impacto no artigo
Se esta spec gera uma figura, uma tabela de métricas, ou uma decisão
metodológica que precisa ser registrada, descreva aqui. Se não gera,
escreva "nenhum".
```

Deixe as specs prontas para virarem issues do GitHub — o grupo vai
transportá-las para o quadro do projeto.

---

## 13. O que não fazer

- Não introduzir IA/ML em nenhum ponto (seção 2).
- Não desenhar uma arquitetura que force execução sequencial das frentes
  (seção 4) — é exatamente o problema a resolver.
- Não propor infraestrutura pesada (Kubernetes, microsserviços, filas,
  banco de grafos dedicado). É um TCC de três pessoas com poucas semanas,
  rodando em notebook. Complexidade que não vira parágrafo no artigo é
  custo puro.
- Não deixar de citar o material de referência anexado — mesmo que a
  arquitetura final diverja bastante dele, ele é o que prova que o
  pipeline funciona.
- Não esquecer a projeção disciplina↔disciplina: ela responde à parte do
  objetivo declarado sobre disciplinas críticas.
