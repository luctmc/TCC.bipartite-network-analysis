# `oulad_mini` — OULAD em miniatura

Sete arquivos minúsculos com o **esquema real** do OULAD (Kuzilek;
Hlosta; Zdrahal, 2017), para desenvolver e testar o ETL da spec A-02 sem
depender do download de ~450 MB.

Os dados são inventados; os **nomes e tipos de coluna, não** — eles vêm
do dicionário de dados publicado do dataset. É essa fidelidade que faz
da fixture uma substituta honesta da base real: um ETL que passa aqui
tem chance de rodar lá.

## O que está representado de propósito

| Situação | Onde aparece | Por que importa |
|---|---|---|
| Aluno em dois módulos | `11391` em AAA e BBB | a agregação por (aluno, disciplina) precisa lidar com isso |
| Mesmo módulo em duas apresentações | AAA em 2013J e 2014J | é a diferença entre as granularidades `module` e `module_presentation` (decisão D1) |
| Matrícula cancelada | `30268`, `date_unregistration=12` | `Withdrawn` é desfecho, não ausência de dado |
| Avaliação sem data | `1758` (Exam) | coluna com nulo legítimo — o ETL não pode quebrar |
| Pesos diferentes de avaliação | `weight` de 5 a 100 | a nota média por matrícula é ponderada, não aritmética |
| Aluno sem nota em um módulo | `23629` só tem uma TMA | matrícula com pouca avaliação existe na base real |

## Fidelidade à distribuição real (conferida em 18/09/2026)

- **Cabeçalhos entre aspas** (`"code_module"`), como no zip real.
- **Valor ausente é `?`** na distribuição do UCI (a da Open University
  usa vazio). `1760/31604` em `studentAssessment` ficou sem nota de
  propósito: é o caso que derrubou a primeira rodada na base real.

## Limites

Não substitui a base real para **números**: qualquer estatística daqui é
de brinquedo. Serve para esquema, tipos, junções e casos de borda.
