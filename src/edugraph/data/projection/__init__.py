"""Projeções do bipartido em grafos monopartidos ponderados  ``[A]``.

Duas ponderações, as duas exigidas pela seção 6.1 do briefing:

``simple``
    Peso = número de vizinhos em comum. Enviesada a favor de nós de alto
    grau.
``resource_allocation``
    Zhou et al. (2007). Cada vizinho comum contribui com ``1/grau``:
    uma disciplina cursada por muita gente discrimina pouco e pesa menos.

E dois lados: ``student`` (aluno↔aluno, base das comunidades) e
``discipline`` (disciplina↔disciplina, base das disciplinas críticas —
o ponto que a seção 13 do briefing manda não esquecer).

A implementação à mão (:mod:`~edugraph.data.projection.manual`) é a
obrigatória do artigo; :mod:`~edugraph.data.projection.networkx_ref` é a
referência com que ela é comparada (ADR-0010).
"""
