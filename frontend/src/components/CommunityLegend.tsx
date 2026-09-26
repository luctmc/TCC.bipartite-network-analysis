/**
 * Legenda das comunidades — spec C-05.
 *
 * Mostra cor **e** forma de cada comunidade, com o tamanho: em escala de
 * cinza é a forma que identifica o grupo (ver `palette.ts`).
 */

import { communityOrder, communityStyle } from "../palette";

/** Comunidades listadas antes do "e mais N" — as menores costumam ser unitárias. */
const MAX_ITENS = 10;

/** Silhueta em SVG da forma do Cytoscape, para a legenda. */
const SILHUETAS: Record<string, string> = {
  ellipse: "M8 1a7 7 0 1 0 0.01 0Z",
  triangle: "M8 1 15 15H1Z",
  "round-rectangle": "M3 2h10a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Z",
  diamond: "M8 0 16 8 8 16 0 8Z",
  hexagon: "M4 1h8l4 7-4 7H4L0 8Z",
  star: "M8 0l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L8 12.4 3 15.2l1.2-5.6L0 5.8l5.6-.6Z",
  vee: "M0 1 8 6 16 1 8 15Z",
  pentagon: "M8 0 16 6 13 15H3L0 6Z",
};

export function CommunityLegend({ membership }: { membership: Record<string, number> }) {
  const ordem = communityOrder(membership);
  const tamanhos = new Map<number, number>();
  for (const comunidade of Object.values(membership)) {
    tamanhos.set(comunidade, (tamanhos.get(comunidade) ?? 0) + 1);
  }
  const itens = [...ordem.entries()].sort((a, b) => a[1] - b[1]);
  const total = Object.keys(membership).length;

  return (
    <ul className="legenda">
      {itens.slice(0, MAX_ITENS).map(([comunidade, posicao]) => {
        const { color, shape } = communityStyle(posicao);
        const n = tamanhos.get(comunidade) ?? 0;
        return (
          <li key={comunidade}>
            <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
              <path d={SILHUETAS[shape] ?? SILHUETAS.ellipse} fill={color} />
            </svg>
            <span>comunidade {comunidade}</span>
            <span className="dim">
              {n} · {((100 * n) / total).toFixed(0)}%
            </span>
          </li>
        );
      })}
      {itens.length > MAX_ITENS && (
        <li className="dim">e mais {itens.length - MAX_ITENS} comunidades menores</li>
      )}
    </ul>
  );
}
