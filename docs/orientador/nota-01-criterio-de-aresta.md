# Nota 01 — troca do critério de aresta

**Data:** 18/09/2026 · **Estado:** informativa, não bloqueia

Não é consulta. O tema que o orientador definiu **já contempla** esta
configuração: a fundamentação dele descreve o bipartido como
*"Aluno → Comportamento"*, e o briefing §8 já listava "participação no
AVA" entre os critérios de aresta candidatos. Seguimos e avisamos.

Detalhe técnico e números em
[`../artigo/decisoes-metodologicas.md`](../artigo/decisoes-metodologicas.md),
seção "O critério de aresta muda de matrícula para interação no AVA".

---

## Texto para enviar

> Professor,
>
> Rodamos a base e encontramos um problema na modelagem, com saída dentro
> do tema que o senhor ajustou. Resumo em três parágrafos.
>
> **O problema.** 91,8% dos alunos do OULAD cursam um único módulo. Com a
> aresta definida por matrícula, a projeção aluno↔aluno não tem estrutura
> de comunidade: a modularidade que ela produz (Q = 0,77) é *menor* que a
> de um grafo com os mesmos graus e as ligações sorteadas. Rodamos o mesmo
> pipeline em bases sintéticas com grupos plantados e ele os recupera com
> folga, então não é erro de implementação — é ausência de sinal no
> critério de aresta.
>
> **A saída.** Trocamos o critério de aresta de "cursou o módulo" para
> "interagiu com recurso do ambiente virtual", que é o
> *Aluno → Comportamento* da fundamentação que o senhor enviou. O grau
> mediano do aluno passa de 1 para 40. Medimos em três coortes: a
> modularidade real fica de 5 a 9 vezes acima da do grafo sorteado, com
> comunidades de tamanho interpretável.
>
> **O que não muda.** O tema, o objetivo e os algoritmos seguem os
> mesmos: projeção de bipartido, Louvain e Girvan-Newman, intermediação e
> autovetor. O grafo por módulo continua no trabalho, servindo à análise
> de disciplinas críticas, onde ele funciona bem. Muda apenas o que define
> a aresta na análise de alunos, que o briefing já deixava em aberto.
>
> Seguimos por esse caminho salvo orientação em contrário.

---

## Se ele perguntar "por que não perceberam antes?"

Porque só dá para perceber medindo. O modelo nulo que revelou o problema
é a spec A-08, escrita **depois** da primeira rodada real, justamente
porque um Q de 0,77 parecia excelente até ser comparado com o acaso.
Detectar isso antes de escrever o capítulo de resultados é o desfecho bom
desta história, não o ruim.
