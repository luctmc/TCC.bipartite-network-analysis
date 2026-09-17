# [B-05] Caracterização: quais disciplinas predominam em cada comunidade

**Frente:** B
**Dono:** Gabriel
**Status:** não iniciada

## Objetivo

Para cada comunidade encontrada, dizer **o que ela é** — tamanho, densidade
interna e disciplinas predominantes.

## Contexto

**Cumpre:** `communities/<id>/profile.csv`.
**Consome:** `Partition`, `BipartiteBundle`.

**Saída obrigatória do TCC.** O briefing §6.2 exige "agrupamentos
interpretáveis de perfis de estudantes, com caracterização de quais
disciplinas predominam em cada comunidade". Uma partição sem esta etapa
diz *quem está junto*, não *por quê* — e não responde ao objetivo
declarado na Introdução.

É a única spec da Frente B que precisa do **bipartido**, além das
projeções.

## Dependências

- B-01, para ter partições.
- Bipartido da Frente A.
- **Neutralizada por:** `data/fixtures/synthetic_v1/bipartite/`.

## Escopo

### Incluído

- `characterize(partition, bipartite, top_k)` → linhas no formato de
  `PROFILE_COLUMNS`.
- **Frequência em excesso sobre a base, não em absoluto.** A disciplina
  obrigatória que todo mundo cursa aparece em todas as comunidades e não
  caracteriza nenhuma. Reportar a frequência relativa ao lado da
  absoluta.
- `community_sizes()` para a figura da B-07.
- Comando `edugraph community characterize`.

### Fora de escopo

- Cruzar com o desfecho — é a B-06, e misturar as duas coisas aqui
  arriscaria o vazamento que a ADR-0008 impede.

## Critérios de aceite

- [ ] Dada a partição de referência de `synthetic_v1`, então há uma linha
      por comunidade, com as colunas de `PROFILE_COLUMNS`.
- [ ] As comunidades grandes (≥10 alunos) têm **conjuntos diferentes** de
      disciplinas predominantes — se todas listarem as mesmas, a
      frequência está sendo medida em absoluto.
- [ ] O gerador plantou três áreas (exatas, sistemas, humanas); as três
      comunidades grandes de `synthetic_v1` refletem isso.
- [ ] `profile.csv` é escrito com escrita canônica e é legível por quem
      não programa — é o insumo do relatório interno (C-07).
- [ ] Nenhum acesso a `outcomes.csv` neste módulo (verificado pelo teste
      de contrato).

## Testes exigidos

- **Contrato:** `test_outcomes_isolation` continua verde — este módulo
  não pode ler rótulo.
- **Unitários** (já escritos como `xfail`): colunas do perfil; comunidades
  grandes se distinguem.

## Arquivos criados ou alterados

- `src/edugraph/community/characterize.py`.
- `src/edugraph/community/cli.py` — `cmd_characterize`.
- `tests/community/test_caracterizacao.py` — remover os `xfail`.

## Impacto no artigo

**Saída obrigatória**: é a tabela que mostra que os agrupamentos são
interpretáveis, que é metade do que a Conclusão precisa responder.
