# Starter Kit — Frentes A, B, C

Código testado e funcional (rodei tudo ponta a ponta antes de entregar).
Usa dados sintéticos por padrão; comentários no código indicam onde
plugar o OULAD real.

## Instalação

```bash
pip install -r requirements.txt
```

## Ordem de execução

```bash
# 1. Gera os dados sintéticos (ou baixe o OULAD real e ajuste o schema
#    em src/etl/build_graph.py -> load_data())
python data/synthetic/generate_synthetic.py

# 2. Frente A — monta o grafo bipartido e as duas projeções, salva em .gml
python src/etl/build_graph.py

# 3. Frente B — Louvain vs. Girvan-Newman, modularidade e tempo
python src/community/detect.py

# 4. Frente C — as três centralidades nas duas projeções
python src/centrality/metrics.py

# 5. Sobe a API que amarra tudo
uvicorn src.api.main:app --reload
# depois abra http://localhost:8000/docs para a interface interativa
```

## O que cada arquivo faz

| Arquivo | Frente | O que testei |
|---|---|---|
| `data/synthetic/generate_synthetic.py` | — | Gera 120 alunos em 3 grupos plantados, com 30% de risco por grupo |
| `src/etl/build_graph.py` | A | ETL, grafo bipartido, projeção simples e projeção por alocação de recursos (Zhou et al.) |
| `src/community/detect.py` | B | Louvain e Girvan-Newman, modularidade, comparação de tempo |
| `src/centrality/metrics.py` | C | Grau, intermediação (Brandes), autovetor, detecção de discordância entre métricas |
| `src/api/main.py` | C | API FastAPI expondo as três frentes — testada com `TestClient`, todas as rotas retornando 200 |

## Resultado de referência (dados sintéticos, para conferir se rodou certo)

- Bipartido: 120 alunos, 7 disciplinas, 197 arestas
- Louvain: ~25 comunidades (3 grandes + várias de 1 aluno isolado), Q ≈ 0,47
- Girvan-Newman no mesmo grafo: centenas de vezes mais lento que Louvain — é exatamente o resultado esperado pela complexidade teórica (O(m²n) vs. O(n log n))
- Disciplina "EEE" com maior intermediação — é a que mais conecta alunos de grupos diferentes no dataset sintético

## Próximo passo real

Baixar o OULAD (`https://analyse.kmi.open.ac.uk/open-dataset`) e trocar
`DATA_PATH` em `src/etl/build_graph.py`, ajustando `load_data()` para o
schema real do `studentInfo.csv` (que tem mais colunas que o sintético
— confiram o dicionário de dados do dataset).
