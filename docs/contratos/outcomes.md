# `Outcomes` — os rótulos históricos

**Produz:** `[A]` · **Consome:** `[B]` e `[C]`, **apenas** em
`evaluate.py`
**Código:** `edugraph.contracts.types.Outcomes`
**Em disco:** `<root>/<dataset>/bipartite/outcomes.csv`

Este contrato existe para **separar**, não para integrar. Ele materializa
a restrição inegociável do briefing §2 (ADR-0008).

## A regra

> Rótulos históricos presentes no dataset entram **apenas** na etapa de
> validação a posteriori — nunca como entrada de algoritmo.

Duas verificações automáticas fazem a regra valer:

1. `validate_node_file` recusa qualquer `nodes.csv` com coluna de
   desfecho, nota ou atributo demográfico. Roda sobre **todo** artefato
   nos testes de contrato.
2. `tests/contract/test_outcomes_isolation.py` analisa o código com `ast`
   e falha se `load_outcomes` for chamada de qualquer módulo que não seja
   um `evaluate.py`.

Se você precisa do desfecho e não está num `evaluate.py`, pare: ou o
código está no lugar errado, ou a análise que você ia fazer não é a que o
trabalho se propôs a fazer.

## Tipo

```python
@dataclass
class Outcomes:
    final_result: dict[str, str]  # aluno → Pass/Distinction/Fail/Withdrawn
    planted_group: dict[str, int] | None  # só sintético: ground truth
    meta: Meta
```

`planted_group` só existe nos datasets sintéticos: é o grupo que o
gerador plantou, e serve de *ground truth* para verificar se os
algoritmos recuperam estrutura conhecida (specs B-06 e C-06). No OULAD
ele é `None`, e a validação se apoia só em `final_result`.

## Em disco

```csv
student_id,final_result,planted_group
S100001,Pass,0
S100002,Withdrawn,1
```

A coluna `planted_group` é omitida quando não existe.

## Invariantes

`validate_outcomes` recusa se:

- algum `final_result` estiver fora de
  `{Pass, Distinction, Fail, Withdrawn}` — o vocabulário do OULAD;
- houver desfecho para aluno que não existe no bipartido. Isso acontece
  de verdade: alunos removidos pelo corte do critério de aresta precisam
  sair de `outcomes.csv` também, e `make_fixtures.py` faz esse filtro.

## O que se valida, e o que não se está fazendo

O que se mede nos `evaluate.py` **não é acurácia de um modelo** — não há
modelo. É se uma estrutura descoberta *apenas pela topologia* guarda
relação com um desfecho conhecido.

- NMI e pureza contra o grupo plantado (B-06);
- distribuição de desfechos por comunidade (B-06);
- taxa de reprovação nas disciplinas críticas contra a base (C-06);
- desfecho por quartil de centralidade do aluno (C-06).

NMI, pureza e correlação de Spearman são medidas de teoria da informação
e estatística descritiva **entre duas partições já conhecidas**. Nenhuma
delas treina nada.

Se a relação existir, é achado. **Se não existir, também é achado** — o
artigo reporta que centralidade estrutural e desempenho histórico são
dimensões independentes, e isso é um resultado legítimo, não um fracasso.

## Uma ressalva que a banca vai levantar

O critério de aresta `final_result_pass` (ADR-0007) usa `final_result`
para decidir se a aresta existe. Isso **não viola** a regra: é uma
definição declarada de aresta, registrada em `BipartiteSpec` e visível no
`meta.json` — não é um algoritmo inferindo a partir do rótulo.

Mas a distinção é sutil e precisa estar escrita no artigo, não só aqui.
Ver `docs/artigo/decisoes-metodologicas.md`. Se o grupo preferir não se
expor à discussão, a alternativa é usar só `score_threshold` e
`vle_activity`, e citar `final_result_pass` como configuração
considerada e descartada.
