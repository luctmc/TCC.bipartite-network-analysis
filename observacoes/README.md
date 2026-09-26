# Observações entre as frentes

Recados que uma pessoa do grupo deixa para outra: um problema achado num
arquivo que não é seu, uma pendência, uma decisão que precisa de alguém.
A regra do grupo é **não mexer no código de outra frente**; quem acha algo
registra aqui, e o dono resolve.

O `CLAUDE.md` manda ler esta pasta no começo de toda sessão de trabalho,
então o recado chega mesmo quando a pessoa trabalha com o Claude. E manda
mantê-la em dia **sem que ninguém peça**: o Claude anota sozinho o que
achar nos arquivos de outra frente e, antes de cada commit, move para
**Resolvidas** toda observação que a mudança resolver, mesmo que a tarefa
fosse outra.

## Os arquivos

| Arquivo | Para quem | Frente |
|---|---|---|
| [`para-pedro.md`](para-pedro.md) | Pedro | A — Dados e Modelagem |
| [`para-gabriel.md`](para-gabriel.md) | Gabriel | B — Detecção de Comunidades |
| [`para-lucas.md`](para-lucas.md) | Lucas | C — Centralidade e Aplicação |
| [`para-todos.md`](para-todos.md) | o grupo | decisões que envolvem mais de uma frente |

## Antes de começar a trabalhar

1. Abra o seu arquivo e o `para-todos.md`.
2. Veja a seção **Abertas**. Se alguma observação toca no que você vai
   fazer, resolva junto ou avise o grupo.

## Como deixar uma observação

Acrescente um item na seção **Abertas** do arquivo do destinatário, no
formato abaixo. O id é a inicial de quem **recebe** (`A`, `B`, `C` ou `T`
para todos) seguida de um número que ainda não foi usado naquele arquivo.

```markdown
### A-OBS-07 · Título curto do problema

- **De:** Lucas (Frente C) · **Data:** 26/09/2026
- **Onde:** `caminho/do/arquivo.py:78`
- **O quê:** o que está errado ou pendente, com a evidência (comando,
  saída, número).
- **Como resolver:** a correção sugerida, se houver.
```

Use caminho e linha sempre que der: é o que permite a outra pessoa (ou o
Claude dela) achar o ponto sem perguntar.

## Como fechar uma observação

Quem resolve move o item para a seção **Resolvidas** do mesmo arquivo e
acrescenta uma linha no fim dele:

```markdown
- **Resolvida:** 27/09/2026 por Pedro, commit `abc1234` — o que foi feito.
```

Se a observação não procede, ela também vai para **Resolvidas**, com o
motivo. Não apague itens: o histórico explica decisões na banca.
