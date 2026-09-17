"""Frente B — Detecção de Comunidades  ``[B]`` Gabriel.

Louvain, Girvan-Newman, modularidade Q implementada à mão, comparação de
qualidade e custo, e caracterização das comunidades encontradas.

**Produz** ``communities/`` (partição, perfil, Q, tempo, status) e
``metrics/communities.csv``. **Consome** ``projections/`` e
``bipartite/``; lê ``outcomes.csv`` apenas em :mod:`~edugraph.community.evaluate`.

Fronteira (ADR-0003): este subpacote não importa ``edugraph.data``,
``edugraph.centrality`` nem ``edugraph.api``. No dia 0 ele trabalha
sobre ``data/fixtures/synthetic_v1`` e ``tiny_v1``, sem executar uma
linha da Frente A.
"""
