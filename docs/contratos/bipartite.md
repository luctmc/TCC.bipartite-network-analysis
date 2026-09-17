# `BipartiteBundle` — o grafo bipartido

**Produz:** `[A]` (spec A-03) · **Consome:** `[B]` caracterização (B-05),
`[C]` API (C-04)
**Código:** `edugraph.contracts.types.BipartiteBundle`
**Em disco:** `<root>/<dataset>/bipartite/`

G = (U ∪ V, E), com U = estudantes e V = disciplinas. Responde ao passo 2
do pipeline da seção 6.1 do briefing.

## Tipo

```python
@dataclass
class BipartiteBundle:
    graph: nx.Graph
    spec: BipartiteSpec
    meta: Meta
```

`BipartiteSpec` é o que o grupo varia e compara (ADR-0007):

| Campo | Tipo | O que significa |
|---|---|---|
| `dataset` | `str` | nome da pasta em disco |
| `granularity` | `module` \| `module_presentation` \| `assessment` | o que conta como um nó de V (decisão D1) |
| `edge_criterion` | `score_threshold` \| `final_result_pass` \| `vle_activity` | o que cria uma aresta |
| `threshold` | `float \| None` | nota mínima, cliques mínimos… |
| `cohort` | `str \| None` | recorte por apresentação (spec A-06) |
| `seed` | `int \| None` | só para dados sintéticos |

## Em disco

`nodes.csv` — **exatamente** três colunas:

```csv
id,kind,label
DAAA,discipline,AAA
S100001,student,100001
```

`edges.csv`:

```csv
source,target,weight
S100001,DAAA,82.0
```

`meta.json` traz `schema_version`, `kind: "bipartite"`, a `spec`
serializada, `producer`, `created_at` e `stats` (nº de alunos, de
disciplinas e de arestas).

## Invariantes

O validador (`validate_bipartite`) recusa o artefato se:

- algum nó não tiver `kind` igual a `student` ou `discipline`;
- o prefixo do id não bater com o `kind` (`S` para aluno, `D` para
  disciplina);
- alguma aresta ligar dois nós do mesmo lado — **num bipartido, toda
  aresta cruza**;
- algum `weight` não for finito e positivo;
- houver laço;
- algum dos dois lados estiver vazio.

E `validate_node_file` recusa qualquer `nodes.csv` que contenha coluna de
desfecho, nota ou atributo demográfico (ADR-0008).

## Notas de implementação

**Nós isolados saem.** Um aluno que não satisfaz o critério de aresta em
disciplina nenhuma vira nó de grau zero: não participa de projeção
nenhuma e só polui o artefato. Nas fixtures isso é visível — o gerador
produz 120 alunos e `synthetic_v1` tem 98, porque 22 não alcançaram nota
60 em nada. O número entra em `meta.stats` e precisa ser reportado no
artigo, não escondido.

**Peso da aresta.** O que `weight` significa depende de
`edge_criterion`: nota média em `score_threshold`, número de cliques em
`vle_activity`. Como as projeções ignoram o peso do bipartido e usam só a
existência da aresta, isso não afeta o resto do pipeline — mas fica
disponível, e a spec A-03 precisa registrar a escolha.

**O desfecho não entra aqui.** Ele vive em `outcomes.csv`, no mesmo
diretório mas em arquivo separado. Ver [outcomes.md](outcomes.md).
