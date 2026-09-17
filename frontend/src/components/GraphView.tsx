/**
 * Grafo interativo — spec C-05.
 *
 * O que já existe: o ciclo de vida do Cytoscape dentro do React (montar,
 * atualizar, destruir sem vazar), o layout fcose e o estilo base. É o
 * esqueleto sobre o qual a C-05 trabalha.
 *
 * O que a C-05 acrescenta está marcado com `TODO C-05`:
 * cor por comunidade, tamanho por centralidade, painel do nó selecionado
 * e as transições entre projeções.
 *
 * Nota de escala: um grafo de milhares de arestas não renderiza. O corte
 * é responsabilidade da API (spec C-04, `min_weight` / limite de
 * arestas), e este componente confia no que recebe, mas avisa quando o
 * número passa de `MAX_EDGES_CONFORTAVEL`.
 */

import { useEffect, useRef } from "react";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";
import fcose from "cytoscape-fcose";

import type { GraphResponse } from "../types";

cytoscape.use(fcose);

/** Acima disto, o navegador começa a engasgar e a figura deixa de comunicar. */
export const MAX_EDGES_CONFORTAVEL = 3000;

interface GraphViewProps {
  graph: GraphResponse;
  /** Métrica que dimensiona os nós. `null` = todos do mesmo tamanho. */
  sizeBy?: string | null;
  onSelect?: (nodeId: string | null) => void;
}

function toElements(graph: GraphResponse): ElementDefinition[] {
  const nodes: ElementDefinition[] = graph.nodes.map((node) => ({
    data: {
      id: node.id,
      label: node.label,
      kind: node.kind,
      // TODO C-05: a comunidade já chega aqui quando a API a embute;
      // falta mapeá-la para uma escala de cor qualitativa acessível.
      community: graph.community?.[node.id] ?? null,
    },
  }));

  const edges: ElementDefinition[] = graph.edges.map((edge) => ({
    data: {
      id: `${edge.source}--${edge.target}`,
      source: edge.source,
      target: edge.target,
      weight: edge.weight,
    },
  }));

  return [...nodes, ...edges];
}

export function GraphView({ graph, onSelect }: GraphViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: toElements(graph),
      style: [
        {
          selector: "node",
          style: {
            "background-color": "var(--node-student)",
            label: "data(label)",
            "font-size": "8px",
            color: "var(--text-muted)",
            "text-valign": "center",
            "text-halign": "center",
            width: 14,
            height: 14,
            "border-width": 1,
            "border-color": "var(--surface)",
          },
        },
        {
          selector: 'node[kind = "discipline"]',
          style: {
            "background-color": "var(--node-discipline)",
            shape: "round-rectangle",
            width: 26,
            height: 20,
            "font-size": "10px",
          },
        },
        {
          selector: "edge",
          style: {
            width: "mapData(weight, 0, 5, 0.5, 4)",
            "line-color": "var(--edge)",
            "curve-style": "haystack",
            opacity: 0.5,
          },
        },
        {
          selector: ":selected",
          style: {
            "border-width": 3,
            "border-color": "var(--accent)",
            "line-color": "var(--accent)",
            opacity: 1,
          },
        },
      ],
      layout: {
        name: "fcose",
        animate: true,
        animationDuration: 600,
        randomize: false, // mesma entrada, mesmo desenho
        nodeRepulsion: 6000,
        idealEdgeLength: 60,
      } as cytoscape.LayoutOptions,
      wheelSensitivity: 0.2,
    });

    cy.on("select", "node", (event) => onSelect?.(event.target.id()));
    cy.on("unselect", "node", () => onSelect?.(null));

    cyRef.current = cy;
    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [graph, onSelect]);

  const pesado = graph.edges.length > MAX_EDGES_CONFORTAVEL;

  return (
    <div className="graph-view">
      {pesado && (
        <p className="aviso" role="status">
          {graph.edges.length.toLocaleString("pt-BR")} arestas — acima de{" "}
          {MAX_EDGES_CONFORTAVEL.toLocaleString("pt-BR")} a visualização fica lenta e
          deixa de comunicar. Use um corte por peso mínimo na projeção (spec A-06).
        </p>
      )}
      <div ref={containerRef} className="graph-canvas" />
    </div>
  );
}
