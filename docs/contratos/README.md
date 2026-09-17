# Contratos de dados entre as camadas

Esta pasta descreve, em prosa, o que `src/edugraph/contracts/` define em
código. Quem vai implementar lê aqui; quem vai depurar lê o código.

**O contrato tem três partes, e as três são verificáveis por ferramenta:**

1. **O tipo Python** — dataclass ou `Protocol`, checado por `mypy` em
   modo estrito sobre `contracts/`.
2. **O layout em disco** — CSV + `meta.json`, lido e escrito só por
   `contracts.io`.
3. **O validador** — `contracts.validate`, executado pelos testes de
   contrato sobre **cada** artefato encontrado sob a raiz em uso.

Quem programa contra o contrato nunca vê a implementação da frente
vizinha.

## Congelado

`src/edugraph/contracts/` entrou em `main` no dia 0 e está **congelado**.
Mudança exige ADR e aprovação dos três (ADR-0009). Mudar layout, nome de
coluna ou semântica de campo exige, além disso, subir `SCHEMA_VERSION`.

Isso não é burocracia: é o que permite às três frentes programarem contra
algo estável enquanto trabalham em paralelo. Um contrato que muda toda
semana não é contrato.

## Os contratos

| Documento | Contrato | Produz | Consome |
|---|---|---|---|
| [bipartite.md](bipartite.md) | `BipartiteBundle` | [A] | [B] caracterização · [C] API |
| [projection.md](projection.md) | `ProjectionBundle` | [A] | [B] · [C] |
| [partition.md](partition.md) | `Partition` | [B] | [C] API e front |
| [centrality.md](centrality.md) | `CentralityResult` | [C] | [C] API e front |
| [outcomes.md](outcomes.md) | `Outcomes` | [A] | [B] · [C], só em `evaluate.py` |
| [metrics.md](metrics.md) | `metrics/*.csv` | todos | o artigo |
| [layout-em-disco.md](layout-em-disco.md) | o layout completo e a resolução de raízes | — | — |

## O que fazer quando o contrato não couber

Vai acontecer: alguma spec vai precisar de um campo que não existe. Na
ordem de preferência:

1. **Cabe em `params` ou em `meta.stats`?** Os dois são dicionários
   livres, existem para isso, e não mexem no esquema.
2. **É um artefato novo em vez de um campo novo?** Uma tabela a mais em
   `metrics/` não muda contrato nenhum.
3. **Só então:** ADR, `SCHEMA_VERSION` nova, validador atualizado e
   fixtures regeneradas — nesta ordem, num PR só, aprovado pelos três.

A pergunta que separa (1) e (2) de (3): *outra frente precisa saber
disso?* Se não precisa, não é contrato.
