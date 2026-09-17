"""API somente leitura sobre artefatos pré-computados  ``[C]``.

A API **não calcula nada** (ADR-0004). Ela lê o que está em disco e
serve como JSON. O cálculo acontece pela CLI (``python -m edugraph run
configs/x.toml``), por três razões:

1. Girvan-Newman sobre um grafo real não termina dentro de uma
   requisição HTTP — servir cálculo seria prometer o que não se cumpre.
2. Se a API calculasse, ela importaria ``community`` e ``centrality``, e
   a fronteira entre frentes (ADR-0003) cairia no primeiro endpoint.
3. Um resultado servido de disco é reproduzível e citável: o
   ``meta.json`` ao lado dele diz com que parâmetros foi gerado.

Consequência boa para o paralelismo: a API sobe no dia 0 sobre
``data/fixtures`` e não sabe se a partição veio da Frente B ou da
biblioteca.
"""

from edugraph.api.app import create_app

__all__ = ["create_app"]
