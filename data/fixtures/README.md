Fixtures versionadas e imutáveis. Geradas por scripts/make_fixtures.py.

Nova fixture = nova pasta. Ver ADR-0011 e docs/arquitetura/paralelismo.md.

**Regenere sob Python 3.13**, a versão usada para gerar o que está
commitado. Em outra versão, `--force` pode produzir uma partição Louvain
diferente para as projeções de peso fracionário
(`*_resource_allocation`) — mesma seed, Q muda no 4º decimal — porque o
`python-louvain` itera um `set()` de ids de comunidade cuja ordem não é
garantida estável entre versões do CPython. Não é uma regressão: rode
`git diff data/fixtures/` depois de regenerar, e se a única mudança for
nesses artefatos, é isso. Detalhes no docstring de `make_fixtures.py` e
na ADR-0011.
