# `ProjectionBundle` — a projeção monopartida ponderada

**Produz:** `[A]` (specs A-04 e A-05) · **Consome:** `[B]` e `[C]`
**Código:** `edugraph.contracts.types.ProjectionBundle`
**Em disco:** `<root>/<dataset>/projections/<projection_id>/`

É o contrato mais usado do projeto: quase tudo que as Frentes B e C fazem
começa lendo uma projeção.

## As quatro projeções

Dois lados × duas ponderações. Todas as quatro existem em ambas as
fixtures.

| `projection_id` | Responde a |
|---|---|
| `student_simple` | comunidades de alunos, ponderação simples |
| `student_resource_allocation` | idem, com o viés de grau corrigido |
| `discipline_simple` | disciplinas críticas no fluxo curricular |
| `discipline_resource_allocation` | idem, com o viés corrigido |

O lado **disciplina** é o que responde à parte do objetivo declarado
sobre gargalos no fluxo curricular. A seção 13 do briefing avisa que é
fácil esquecer dele.

## As duas ponderações

**`simple`** — peso = número de vizinhos compartilhados. Equivale à
diagonal externa de `B · Bᵀ`. Enviesada a favor de nós de alto grau: uma
disciplina obrigatória cursada por todo mundo aproxima todo mundo de todo
mundo, sem discriminar nada.

**`resource_allocation`** — Zhou et al. (2007). Cada vizinho comum `k`
contribui com `1/grau(k)`. Uma disciplina rara e específica pesa mais que
uma popular.

A diferença é visível em `tiny_v1`, e o teste
`test_as_duas_ponderacoes_ordenam_pares_de_forma_diferente` existe para
isso: os pares S1-S6 e S3-S4 **empatam em 1** na projeção simples, mas em
alocação de recursos ficam 0,25 e 1/3 — porque DC (grau 3) discrimina
mais que DA (grau 4). Se esse teste passar a falhar, a correção de viés
se perdeu.

## Tipo

```python
@dataclass
class ProjectionBundle:
    graph: nx.Graph
    spec: ProjectionSpec  # side, weighting, implementation, min_weight
    source: BipartiteSpec  # de que bipartido veio
    meta: Meta
```

`projection_id` é derivado: `f"{side}_{weighting}"`. `source` é o que
permite rastrear uma projeção até a configuração que a gerou, e é o que o
artigo cita.

`min_weight` registra um corte por peso mínimo (spec A-06). Quando
presente, o validador confere que nenhuma aresta abaixo dele sobreviveu —
o corte fica auditável no artefato.

## Em disco

Mesmo formato do bipartido: `nodes.csv` (`id,kind,label`), `edges.csv`
(`source,target,weight`), `meta.json` com `spec` e `source`.

## Invariantes

`validate_projection` recusa se:

- houver laço — um nó não compartilha vizinho consigo mesmo;
- o grafo for multigrafo;
- algum nó tiver `kind` diferente de `spec.side` — **uma projeção tem um
  lado só**;
- algum `weight` não for finito e positivo;
- alguma aresta estiver abaixo de `min_weight`, quando ele existe.

## Notas de escala

A projeção aluno↔aluno de uma coorte com dois mil alunos chega a milhões
de arestas. Três reduções, todas na spec A-06 e todas registradas no
artefato: recorte por coorte, corte por peso mínimo e núcleo-k.

**Sobre a degeneração do lado disciplina.** Com poucas disciplinas e
alunos cursando várias, a projeção disciplina↔disciplina tende ao grafo
completo. Em `synthetic_v1` isso acontece: 7 nós, 21 arestas, K₇ — toda
intermediação zero. É a confirmação empírica da decisão D1, e está
registrada em `data/fixtures/synthetic_v1/REFERENCE.md`. A saída é
granularidade mais fina (`module_presentation`, `assessment`), que já é
parâmetro (ADR-0007).
