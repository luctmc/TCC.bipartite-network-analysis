# edugraph

**Análise Topológica e Detecção de Comunidades em Redes Complexas:
Projeção de Grafos Bipartidos e Métricas de Centralidade em Dados
Educacionais**

TCC — Ciência da Computação, Centro Universitário Padre Anchieta
(UniAnchieta), Jundiaí/SP.
**Grupo 16:** Gabriel Luís Lopes, Pedro Alexandre dos Santos Chaves,
Lucas Timponi Mercadante Castro.
**Orientador:** Prof. Me. Clayton Augusto Valdo.

Modela dados educacionais como um grafo bipartido aluno↔disciplina,
projeta em grafos monopartidos ponderados, detecta comunidades e mede
centralidade — **usando apenas algoritmos de Teoria dos Grafos, sem
aprendizado de máquina**.

---

## Comece aqui

```bash
git clone https://github.com/luctmc/TCC.bipartite-network-analysis
cd TCC.bipartite-network-analysis

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

pip install -e ".[dev]"
```

Confira que está tudo de pé:

```bash
python -m edugraph validate --root data/fixtures
pytest
```

Esperado: os dois datasets de fixture validando, e a suíte com **61
testes passando e 33 `xfail`**. Os `xfail` são as specs ainda abertas —
cada um traz o id da spec que o destrava.

Requer **Python 3.11+**. O front-end requer **Node 18+**, e é opcional:
a análise inteira funciona sem ele.

## O que dá para fazer agora

```bash
# validar todos os artefatos sob uma raiz
python -m edugraph validate --root data/fixtures

# subir a API sobre as fixtures
python -m edugraph api serve --root data/fixtures
#   http://127.0.0.1:8000/health    · sobre que raízes está olhando
#   http://127.0.0.1:8000/datasets  · o que já existe em disco
#   http://127.0.0.1:8000/docs      · a documentação da API

# ver o que o pipeline faria
python -m edugraph run configs/synthetic_v1.toml --dry-run

# regenerar as fixtures (byte a byte idênticas)
python scripts/make_fixtures.py --force

# ver os comandos de cada frente
python -m edugraph data --help
python -m edugraph community --help
python -m edugraph centrality --help
```

Os comandos de cálculo ainda respondem `não implementado` com o id da
spec correspondente: **este repositório é a arquitetura e o esqueleto**,
e as implementações são as 21 specs de [`docs/specs/`](docs/specs/README.md).

## Como o projeto está organizado

Três pessoas, três frentes, trabalhando **ao mesmo tempo**. O que torna
isso possível:

1. **A fronteira entre frentes é o disco.** Nenhuma frente importa outra;
   elas se comunicam por artefatos num layout fixo. Um teste falha se
   alguém cruzar a fronteira.
2. **As fixtures são completas.** `data/fixtures/synthetic_v1` já tem
   bipartido, quatro projeções, partições e centralidades. As Frentes B e
   C rodam, testam e sobem a API **sem executar uma linha da Frente A**.
3. **Trocar de fonte é trocar `--root`.** Quando o OULAD estiver em
   `data/processed`, ninguém muda código.

| Frente | Dono | Escopo |
|---|---|---|
| **A** — Dados e Modelagem | Pedro | ETL do OULAD, gerador sintético, bipartido, projeções |
| **B** — Comunidades | Gabriel | Louvain, Girvan-Newman, modularidade, caracterização |
| **C** — Centralidade e Aplicação | Lucas | grau, intermediação, autovetor, disciplinas críticas, API, front-end |

```
src/edugraph/
├── contracts/     [T] tipos, io, validadores — CONGELADO
├── data/          [A]  ├── community/   [B]  ├── centrality/  [C]
├── api/           [C]  └── reporting/   [T]
└── __main__.py    [T] a única composição das três frentes
configs/           uma configuração de experimento por arquivo
data/fixtures/     [T] commitado, imutável
docs/              ADRs, contratos, specs, material do artigo
frontend/          [C] React + Vite + Cytoscape.js
```

## A restrição inegociável

**Nenhum componente usa IA, aprendizado de máquina ou qualquer modelo
treinado com dados rotulados.** Foi exigência do orientador e é o
diferencial declarado do trabalho.

Rótulos históricos (o desfecho de cada matrícula) vivem em
`outcomes.csv`, separados do grafo, e entram **apenas** na validação a
posteriori.

Isso não é só uma regra escrita: `tests/contract/test_no_ml.py` varre o
código e as dependências, e `test_outcomes_isolation.py` garante que
nenhum módulo fora de `evaluate.py` lê um rótulo. Quebrar a regra quebra
a CI.

## Os dados

**Base principal:** [OULAD](https://analyse.kmi.open.ac.uk/open_dataset)
(Kuzilek; Hlosta; Zdrahal, 2017). Público e anonimizado. O download é
**passo manual**: baixe o zip, extraia as sete tabelas em
`data/raw/oulad/` e rode `python -m edugraph data etl`. A pasta é
ignorada pelo git.

Não é preciso baixá-lo para trabalhar: `tests/data/oulad_mini/` traz as
sete tabelas em miniatura, com o esquema real.

**Base secundária:** gerador sintético com comunidades plantadas, que
serve de *ground truth* e de fixture.

## Documentação

Comece por [`docs/README.md`](docs/README.md). Os atalhos:

- [Visão geral da arquitetura](docs/arquitetura/visao-geral.md)
- [Como as frentes não se bloqueiam](docs/arquitetura/paralelismo.md)
- [As 21 specs](docs/specs/README.md)
- [As 11 ADRs](docs/adr/README.md)
- [Os contratos de dados](docs/contratos/README.md)
- [Estratégia de testes](docs/testes/estrategia.md)

## Contribuindo

`main` é protegida: só entra por PR com CI verde. Uma spec, um branch, um
PR (`a/A-04-projecao-manual`). Commits em português com o id da spec.
Detalhes em [branches-e-merge.md](docs/arquitetura/branches-e-merge.md).

Antes de abrir o PR:

```bash
ruff check . && ruff format --check . && mypy src/edugraph/contracts && pytest -m "not slow"
```

## Referências

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

O starter kit que validou o pipeline ponta a ponta (120 alunos, 7
disciplinas, 197 arestas; Louvain Q ≈ 0,47; Girvan-Newman ~645× mais
lento) foi removido depois de cumprir esse papel — as conclusões dele
estão nas ADRs e os números foram reproduzidos pelas fixtures.
[`reference/README.md`](reference/README.md) registra o que ele mediu, o
que sobreviveu dele no código, e como recuperá-lo do histórico do git.
