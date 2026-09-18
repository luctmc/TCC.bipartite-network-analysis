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

## Datasets derivados: `derive_outcomes`

Reduções da spec A-06 (amostra, coorte) criam um dataset novo com um
subconjunto dos alunos. O validador exige que todo desfecho aponte para
um nó existente, então o `outcomes.csv` do derivado precisa ser o da
origem **filtrado**.

Quem faz isso é `contracts.io.derive_outcomes(roots, origem, out,
destino, keep=alunos)`: lê, filtra e regrava, e **não devolve os rótulos
ao chamador**. Ela vive no contrato pela mesma razão que `load_outcomes`
vive: é manuseio genérico do artefato, sem olhar o valor do rótulo. A
Frente A a usa em `data sample` e `data cohort` sem nunca ver um
desfecho — e o teste `test_apenas_evaluate_le_outcomes` foi o que
impediu a alternativa errada (a frente chamar `load_outcomes` e filtrar
por conta própria).

> **Nota de processo.** `derive_outcomes` foi acrescentada ao pacote
> congelado em 18/09/2026, na spec A-06. É aditiva: nenhum tipo, layout
> ou coluna mudou, e `SCHEMA_VERSION` continua `1.0`. Pela ADR-0009,
> mudança em `contracts/` pede o aceite dos três — este é o registro
> para esse aceite.

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
