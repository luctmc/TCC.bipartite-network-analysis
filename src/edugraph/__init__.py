"""edugraph — análise topológica de redes educacionais bipartidas.

Pacote do TCC do Grupo 16 (UniAnchieta). A organização interna segue a
regra de fronteira da ADR-0003: cada frente vive em um subpacote e
**nenhum subpacote de frente importa outro**. A comunicação acontece
por artefatos em disco, definidos em :mod:`edugraph.contracts`.

Subpacotes
----------
contracts  [T] tipos, protocolos, leitura/escrita e validadores (congelado)
data       [A] ETL, grafo bipartido e projeções
community  [B] Louvain, Girvan-Newman, modularidade, caracterização
centrality [C] grau, intermediação, autovetor, disciplinas críticas
api        [C] FastAPI somente leitura sobre os artefatos
reporting  [T] escrita de tabelas e figuras para o artigo
"""

__version__ = "0.1.0"
