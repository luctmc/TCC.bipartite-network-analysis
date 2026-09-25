/**
 * Cores e formas das comunidades — spec C-05.
 *
 * **Escala qualitativa acessível.** As oito cores são a paleta de
 * Okabe & Ito (2008), desenhada para ser distinguível por quem tem
 * daltonismo. Ela não garante, sozinha, distinção em escala de cinza —
 * laranja e azul-celeste têm luminância parecida —, e as capturas do
 * capítulo 3 podem ser impressas. Por isso cada comunidade recebe também
 * uma **forma**: em cinza, a forma separa o que a cor não separa.
 *
 * A partir da nona comunidade, cor e forma se repetem com um deslocamento
 * (a 9ª tem a cor da 1ª e a forma da 2ª), o que mantém pares vizinhos
 * distintos até 8 × 8 = 64 comunidades.
 */

import type { Css } from "cytoscape";

/** Okabe & Ito (2008), na ordem que alterna tons quentes e frios. */
export const COMMUNITY_COLORS: readonly string[] = [
  "#56B4E9", // azul-celeste
  "#E69F00", // laranja
  "#009E73", // verde-azulado
  "#F0E442", // amarelo
  "#0072B2", // azul
  "#D55E00", // vermelhão
  "#CC79A7", // rosa
  "#BBBBBB", // cinza claro
];

/** Formas nativas do Cytoscape, escolhidas por serem bem distintas em tamanho pequeno. */
export const COMMUNITY_SHAPES: readonly Css.NodeShape[] = [
  "ellipse",
  "triangle",
  "round-rectangle",
  "diamond",
  "hexagon",
  "star",
  "vee",
  "pentagon",
];

export interface CommunityStyle {
  color: string;
  shape: Css.NodeShape;
}

/** Cor e forma da comunidade `index` (a posição dela na ordem da partição). */
export function communityStyle(index: number): CommunityStyle {
  const n = COMMUNITY_COLORS.length;
  const cycle = Math.floor(index / n);
  return {
    color: COMMUNITY_COLORS[index % n],
    shape: COMMUNITY_SHAPES[(index + cycle) % COMMUNITY_SHAPES.length],
  };
}

/**
 * Comunidade → posição, das maiores para as menores.
 *
 * A maior comunidade fica com a primeira cor, sempre: o mesmo grafo
 * recebe as mesmas cores em qualquer execução, independentemente do
 * número que o algoritmo deu a cada comunidade.
 */
export function communityOrder(membership: Record<string, number>): Map<number, number> {
  const sizes = new Map<number, number>();
  for (const community of Object.values(membership)) {
    sizes.set(community, (sizes.get(community) ?? 0) + 1);
  }
  const ordered = [...sizes.entries()].sort((a, b) => b[1] - a[1] || a[0] - b[0]);
  return new Map(ordered.map(([community], position) => [community, position]));
}

/**
 * Lê uma variável CSS do tema. O Cytoscape desenha em canvas e **não**
 * entende `var(--x)`; as cores do tema precisam chegar a ele resolvidas.
 */
export function themeColor(name: string, fallback: string): string {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}
