# Material de referência

## Starter kit — removido do working tree em 17/09/2026

O starter kit era uma prova de conceito de ~505 linhas de Python que
validava, sobre dados sintéticos, que o pipeline deste TCC fecha ponta a
ponta. Ele foi **removido** porque cumpriu inteiramente o seu papel: as
conclusões que ele produziu estão absorvidas nas ADRs, e os seus números
foram reproduzidos pelas fixtures versionadas.

O briefing (§13) pede que ele seja citado, e é o que este documento faz.

**Ele não sumiu.** Está no histórico do git, no commit `a5c3377`:

```bash
git show a5c3377 --stat -- reference/starter-kit/     # o que havia
git checkout a5c3377 -- reference/starter-kit/        # trazer de volta
git show a5c3377:reference/starter-kit/src/etl/build_graph.py   # ver um arquivo
```

## O que ele continha

| Arquivo | Frente | O que fazia |
|---|---|---|
| `data/synthetic/generate_synthetic.py` | — | 120 alunos em 3 grupos plantados, 30% em risco por grupo, seed 42 |
| `src/etl/build_graph.py` | A | ETL, bipartido, projeção simples e por alocação de recursos (Zhou et al.) |
| `src/community/detect.py` | B | Louvain e Girvan-Newman, modularidade, comparação de tempo |
| `src/centrality/metrics.py` | C | Grau, intermediação (Brandes), autovetor, discordância entre métricas |
| `src/api/main.py` | C | FastAPI expondo as três frentes, calculando por requisição |

Mais três `.gml` de projeções gravadas e o `studentInfo.csv` sintético.

## Os números que ele mediu

São **citáveis no artigo** e foram reproduzidos independentemente pelas
fixtures deste repositório:

| Medida | Starter kit | `data/fixtures/synthetic_v1` |
|---|---|---|
| Alunos no bipartido | 120 | **98** (nós isolados removidos) |
| Disciplinas | 7 | 7 |
| Arestas | 197 | **197** ✓ |
| Louvain, Q | ≈ 0,47 | **0,4666** ✓ |
| Louvain, comunidades | ~25 (3 grandes + isolados) | **3** (sem os isolados) |
| Girvan-Newman | ~645× mais lento que Louvain | a medir na spec B-02 |

As duas divergências são explicadas e deliberadas: o contrato remove nós
de grau zero, e as ~22 comunidades extras do starter kit eram justamente
esses alunos isolados, cada um virando uma comunidade de tamanho 1. Ver
[`../data/fixtures/synthetic_v1/REFERENCE.md`](../data/fixtures/synthetic_v1/REFERENCE.md).

**Uma observação do starter kit que não se confirmou.** O README dele
afirmava que a disciplina `EEE` tinha a maior intermediação. Na projeção
disciplina↔disciplina com V = módulo, o grafo é o **completo K₇** e
*todas* as disciplinas têm intermediação zero — não há líder. Isso é a
confirmação empírica da decisão D1, e nenhum teste deste repositório
afirma o contrário.

## O que ele provou, e onde cada conclusão foi parar

| O que ele mostrou | Onde virou decisão |
|---|---|
| O pipeline fecha: ETL → bipartido → projeção → comunidade → centralidade → API | a arquitetura inteira |
| A API importava comunidade e centralidade, amarrando as frentes | **ADR-0001** (fronteira em disco), **ADR-0003** (fronteira testada) |
| Salvava GML: 10.577 linhas para 120 nós e 1.971 arestas, com tipos inferidos na leitura | **ADR-0002** (CSV + `meta.json`) |
| Calculava por requisição HTTP | **ADR-0004** (API somente leitura) |
| Girvan-Newman ~645× mais lento que Louvain | **ADR-0006** (orçamento de tempo) |
| `SCORE_THRESHOLD = 60.0` como constante de módulo | **ADR-0007** (critério parametrizável) |
| Louvain sem semente fixa, resultado variando entre execuções | **ADR-0011** (determinismo) |
| Misturava português e inglês nos identificadores | decisão D2 (sem ADR) |

## O que sobreviveu dele no código

O gerador sintético. `src/edugraph/data/synthetic.py` é uma **porta
fiel** dele: mesma seed, mesmos três grupos de 40, mesmos sete módulos,
mesma taxa de risco e mesmo ruído entre grupos. É por isso que o número
de arestas bate exatamente.

O briefing (§3) foi explícito: *"a única coisa que precisa sobreviver é a
lógica validada (os algoritmos e como eles se encaixam), não os arquivos
em si"*.

## Referências bibliográficas

Estas continuam sendo as do artigo, independentemente do starter kit:

- Kuzilek, J.; Hlosta, M.; Zdrahal, Z. **Open University Learning
  Analytics dataset.** *Scientific Data*, 2017.
- Blondel, V. et al. **Fast unfolding of communities in large networks.**
  *J. Stat. Mech.*, 2008.
- Girvan, M.; Newman, M. **Community structure in social and biological
  networks.** *PNAS*, 2002.
- Brandes, U. **A faster algorithm for betweenness centrality.**
  *J. Math. Sociol.*, 2001.
- Zhou, T. et al. **Bipartite network projection and personal
  recommendation.** *Physical Review E*, 2007.
