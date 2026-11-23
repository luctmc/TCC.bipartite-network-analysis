/**
 * Desenho do exemplo dos seis alunos — um lugar só para as posições, que são
 * escolha de desenho (não dado). diagramas.js, motion.js e contexto.js leem
 * daqui, para que o mapa do contexto e o da fundamentação sejam o MESMO.
 *
 * Alunos 1 a 6 de tiny_v1 = Ana, Bruno, Carla, Diego, Elisa e Felipe;
 * disciplinas A, B e C = Sistemas de Computação, Algoritmos e Programação e
 * Circuitos Elétricos (os nomes vêm de js/dados.js → contexto).
 */
window.EDUGRAPH_DESENHO = (() => {
  // Ordem vertical do bipartido: o Felipe no topo, para a linha dele não cruzar as outras.
  const ALUNOS_BIP = ["S6", "S1", "S2", "S3", "S4", "S5"];
  return {
    ALUNOS: ["S1", "S2", "S3", "S4", "S5", "S6"],
    ALUNOS_BIP,
    /** Grafo bipartido: alunos numa coluna, disciplinas na outra (viewBox 900 × 600). */
    POS_BIP: Object.fromEntries(ALUNOS_BIP.map((a, i) => [a, [190, 70 + i * 96]])),
    DISC: { DA: [730, 160], DB: [730, 310], DC: [730, 460] },
    /** Projeção e mapa da turma (viewBox 900 × 600). */
    POS_PROJ: { S1: [250, 140], S2: [250, 480], S6: [86, 310], S3: [470, 310], S4: [720, 160], S5: [720, 460] },
    /** Espessura de uma ligação pelo peso de alocação de recursos (mesma escala em todo o deck). */
    larguraRA: (w) => 12 * w,
    /** E pelo peso simples (nº de disciplinas em comum). */
    larguraSimples: (w) => 4 * w,
  };
})();
