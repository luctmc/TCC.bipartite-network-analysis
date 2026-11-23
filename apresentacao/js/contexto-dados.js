/**
 * Dados de FORA do repositório, escritos à mão e conferidos no relatório.
 * São os únicos números da apresentação que não saem de gerar_dados.py.
 *
 * Fonte: BRASIL. Inep. Resumo técnico do Censo da Educação Superior 2024.
 * Brasília, DF: Inep, 2026. Indicadores de trajetória da turma que entrou
 * em 2015, acompanhada até 2024 (NARRATIVA.md, seção 2). Os números de
 * página são os impressos no rodapé do relatório.
 *
 * Cuidados (NARRATIVA.md, seção 2): "deixou o curso" inclui quem se
 * transferiu de curso; não são "estatísticas oficiais" (o próprio Inep
 * avisa, p. 32); nada de números do Semesp, que medem outra coisa.
 */
window.EDUGRAPH_INEP = {
  citacao: "Inep, 2026",
  turma: 2015,
  ate: 2024,
  /** Desistência acumulada, em % da turma de entrada. Gráfico 15, p. 33.
   *  Só os anos conferidos: os anos 4 a 9 não são interpolados. */
  desistencia: [
    { ano: 1, pct: 13 },
    { ano: 2, pct: 29 },
    { ano: 3, pct: 40 },
    { ano: 10, pct: 60 },
  ],
  /** Situação no 10º ano. Gráfico 15, p. 33; texto na p. 34. */
  concluiram: 39,
  cursando: 1,
  /** Desistência no 10º ano por modalidade. Gráfico 18, p. 36. */
  distancia: 65,
  presencial: 59,
};
