# Índice de tabelas

> **Arquivo gerado** a partir de `results/tables/`. Mesma regra do índice
> de figuras: não editar à mão.

Lista planejada, com a spec que produz cada tabela.

| # | Tabela | Spec | Fonte | Onde no artigo |
|---|---|---|---|---|
| 1 | Estatísticas do dataset | A-07 | `metrics/` | seção de dados |
| 2 | Projeção à mão × NetworkX | A-05 | `metrics/projections.csv` | seção de projeção |
| 3 | **Louvain × Girvan-Newman × ponderação** | B-04 | `metrics/communities.csv` | **tabela principal** |
| 4 | Perfil das comunidades | B-05 | `communities/*/profile.csv` | comunidades |
| 5 | Validação: NMI, pureza, desfecho por comunidade | B-06 | `results/tables/tab5-validacao-*.csv` | validação |
| 6 | Disciplinas críticas por métrica | C-03 | `results/tables/tab6-criticas-*.csv` (de `metrics/centrality_top.csv`) | disciplinas críticas |
| 6b | Sensibilidade da intermediação: saltos × distância inversa | C-03 | `results/tables/tab6-sensibilidade-*.csv` | disciplinas críticas |
| 7 | Discordância entre métricas | C-03 | `results/tables/tab7-discordancia-*.csv` | discussão |
| 8 | Reprovação nas disciplinas críticas × base | C-06 | `results/tables/tab8-reprovacao-*.csv` | validação |
| 8b | Desfecho por faixa de centralidade do aluno | C-06 | `results/tables/tab8b-desfecho-faixa-*.csv` | validação |
| 9 | Tamanhos por recorte de escala | A-06 | — | limitações |

## Regras

- `metrics/` é **rascunho de trabalho**, reescrito a cada rodada;
  `results/tables/` é o que foi para o texto, e é versionado. Ter as duas
  coisas separadas é o que permite comparar a tabela do rascunho com a da
  versão final e explicar a diferença.
- Toda tabela carrega as colunas que identificam a configuração
  (`dataset`, `projection_id`, `algorithm`) — senão a linha não é
  reproduzível.
- A tabela 3 traz a coluna `status`: uma execução que estourou o
  orçamento entra na comparação **com o status visível** (ADR-0006).
- Números com o mesmo número de casas decimais dentro de uma coluna.
- Ao reportar o número de comunidades, **dizer quantas são unitárias**.

## Configuração das tabelas da Frente C

As exportações `tab6-criticas-*`, `tab7-discordancia-*` e
`tab6-sensibilidade-*` carregam `weight_mode`, `k`, `estimate` e `seed`,
com legenda própria em `<nome>.caption.txt`: a de disciplinas críticas
explica o ranking por métrica, a de discordância explica conjuntos e
Spearman, e a de sensibilidade explica a comparação dos modos. Nenhuma
legenda depende da leitura de outra tabela. `none` usa saltos e `inverse` usa
`1/w` como distância. `k` vazio com `estimate=False` indica cálculo
exato; com estimativa, `k` e `seed` identificam a amostragem. Na tabela 6
os campos são da métrica da linha (vazios para grau/autovetor); na 7
identificam a intermediação usada nas comparações. Os CSVs de fronteira
em `metrics/` mantêm seu esquema congelado.

```bash
python -m edugraph centrality critical --root data/processed --dataset oulad_module_presentation --out data/processed --tables results/tables
python -m edugraph centrality sensitivity --root data/processed --dataset oulad_module_presentation --tables results/tables
python -m edugraph centrality critical --root data/processed --dataset oulad_vle_bbb_2013j --out data/processed --tables results/tables
python -m edugraph centrality sensitivity --root data/processed --dataset oulad_vle_bbb_2013j --tables results/tables
```

A sensibilidade compara `none` e `inverse` com normalização, pivôs e
semente da centralidade principal, sem sobrescrevê-la. Os dois modos
ficam identificados por linha. As tabelas OULAD versionadas ainda precisam
ser regeneradas em uma máquina com os artefatos reais (C-OBS-03); adicionar
a rotina não significa que esses números já foram atualizados.
