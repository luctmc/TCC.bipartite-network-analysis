/**
 * Grafo interativo — spec C-05.
 *
 * Cor e forma por comunidade, tamanho por centralidade, destaque da
 * vizinhança do nó selecionado e transição entre projeções preservando a
 * posição dos nós comuns.
 *
 * O Cytoscape é criado uma vez por grafo. Trocar a partição ou a métrica
 * **não** recria nada: só muda `data(color)` / `data(size)` dos nós, e a
 * transição de estilo do próprio Cytoscape anima a mudança — sem
 * recarregar a página e sem refazer o layout.
 *
 * Nota de escala: um grafo de milhares de arestas não renderiza bem. O
 * corte é da API (C-04, `truncation` no corpo); este componente confia
 * no que recebe, simplifica o desenho acima de `MAX_EDGES_CONFORTAVEL` e
 * avisa.
 */

import { useEffect, useRef } from "react";
import cytoscape, { type Core, type ElementDefinition, type Position } from "cytoscape";
import fcose from "cytoscape-fcose";

import { communityOrder, communityStyle, themeColor } from "../palette";
import type { CentralityMetric, GraphResponse } from "../types";

cytoscape.use(fcose);

/** Acima disto, o navegador começa a engasgar e a figura deixa de comunicar. */
export const MAX_EDGES_CONFORTAVEL = 3000;

/** Acima disto, os rótulos só aparecem no nó selecionado e na vizinhança. */
const MAX_NODES_ROTULADOS = 150;

const TAMANHO_MIN = 10;
const TAMANHO_MAX = 42;
const TAMANHO_NEUTRO = 16;
const DURACAO_MS = 450;

/**
 * Posições por id de nó, compartilhadas entre montagens do componente.
 * É o que faz a troca de projeção preservar o lugar dos nós em comum:
 * o grafo novo parte de onde o anterior parou.
 */
const posicoes = new Map<string, Position>();

interface GraphViewProps {
  graph: GraphResponse;
  /** Nó → comunidade. `null` = cor pelo tipo do nó. */
  membership: Record<string, number> | null;
  /** Métrica que dimensiona os nós. `null` = todos do mesmo tamanho. */
  sizeBy: CentralityMetric | null;
  selected: string | null;
  onSelect: (nodeId: string | null) => void;
}

/** Tamanho de cada nó pela métrica, em escala linear entre o menor e o maior score. */
export function nodeSizes(
  graph: GraphResponse,
  sizeBy: CentralityMetric | null,
): Map<string, number> {
  const scores = sizeBy ? graph.centrality?.[sizeBy] : undefined;
  const sizes = new Map<string, number>();
  if (!scores) {
    for (const node of graph.nodes) sizes.set(node.id, TAMANHO_NEUTRO);
    return sizes;
  }
  const values = graph.nodes.map((node) => scores[node.id] ?? 0);
  const min = Math.min(...values);
  const max = Math.max(...values);
  for (const node of graph.nodes) {
    const t = max > min ? ((scores[node.id] ?? 0) - min) / (max - min) : 0.5;
    sizes.set(node.id, TAMANHO_MIN + t * (TAMANHO_MAX - TAMANHO_MIN));
  }
  return sizes;
}

/** Posição inicial determinística (círculo por ordem de id) para quem ainda não tem posição. */
function posicaoInicial(ids: string[]): Map<string, Position> {
  const faltando = ids.filter((id) => !posicoes.has(id)).sort();
  const raio = Math.max(120, faltando.length * 4);
  const saida = new Map<string, Position>();
  faltando.forEach((id, i) => {
    const angulo = (2 * Math.PI * i) / Math.max(faltando.length, 1);
    saida.set(id, { x: raio * Math.cos(angulo), y: raio * Math.sin(angulo) });
  });
  return saida;
}

function toElements(graph: GraphResponse): ElementDefinition[] {
  const iniciais = posicaoInicial(graph.nodes.map((node) => node.id));
  const nodes: ElementDefinition[] = graph.nodes.map((node) => ({
    data: {
      id: node.id,
      label: node.label,
      kind: node.kind,
      size: TAMANHO_NEUTRO,
    },
    position: { ...(posicoes.get(node.id) ?? iniciais.get(node.id) ?? { x: 0, y: 0 }) },
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

function estilo(graph: GraphResponse): cytoscape.StylesheetJson {
  const pesos = graph.edges.map((edge) => edge.weight);
  const pesoMin = pesos.length ? Math.min(...pesos) : 0;
  const pesoMax = pesos.length ? Math.max(...pesos) : 1;
  const rotularTodos = graph.nodes.length <= MAX_NODES_ROTULADOS;
  const cor = {
    student: themeColor("--node-student", "#6ea8fe"),
    discipline: themeColor("--node-discipline", "#f0a868"),
    edge: themeColor("--edge", "#3c4654"),
    surface: themeColor("--surface", "#171b21"),
    text: themeColor("--text", "#e6e9ee"),
    muted: themeColor("--text-muted", "#9aa5b1"),
    accent: themeColor("--accent", "#6ea8fe"),
  };

  return [
    {
      selector: "node",
      style: {
        "background-color": cor.student,
        label: rotularTodos ? "data(label)" : "",
        "font-size": 8,
        color: cor.muted,
        "text-valign": "bottom",
        "text-margin-y": 3,
        width: "data(size)",
        height: "data(size)",
        "border-width": 1,
        "border-color": cor.surface,
        "transition-property": "width, height, background-color, opacity",
        "transition-duration": DURACAO_MS,
        "transition-timing-function": "ease-in-out-cubic",
      },
    },
    {
      selector: 'node[kind = "discipline"]',
      style: {
        "background-color": cor.discipline,
        shape: "round-rectangle",
        "font-size": 10,
      },
    },
    {
      selector: "node[color]",
      // "data(shape)" é válido no Cytoscape, mas os tipos só aceitam formas literais.
      style: { "background-color": "data(color)", shape: "data(shape)" } as unknown as cytoscape.Css.Node,
    },
    {
      selector: "edge",
      style: {
        width: pesoMax > pesoMin ? `mapData(weight, ${pesoMin}, ${pesoMax}, 0.5, 4)` : 1,
        "line-color": cor.edge,
        "curve-style": "haystack",
        opacity: 0.45,
        "transition-property": "opacity, line-color",
        "transition-duration": DURACAO_MS,
      },
    },
    { selector: ".apagado", style: { opacity: 0.08 } },
    {
      selector: "node.vizinho, node:selected",
      style: { label: "data(label)", color: cor.text, "z-index": 10 },
    },
    { selector: "edge.vizinho", style: { opacity: 0.9, "line-color": cor.accent } },
    {
      selector: "node:selected",
      style: { "border-width": 3, "border-color": cor.accent, "font-size": 11 },
    },
  ];
}

export function GraphView({ graph, membership, sizeBy, selected, onSelect }: GraphViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  // O callback mais recente sem recriar o Cytoscape quando o pai re-renderiza.
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  // 1. Um Cytoscape por grafo.
  useEffect(() => {
    if (!containerRef.current) return;

    const pesado = graph.edges.length > MAX_EDGES_CONFORTAVEL;
    const conhecidos = graph.nodes.filter((node) => posicoes.has(node.id)).length;
    const continuar = conhecidos >= graph.nodes.length / 2;

    const cy = cytoscape({
      container: containerRef.current,
      elements: toElements(graph),
      style: estilo(graph),
      layout: {
        name: "fcose",
        // Com a maioria dos nós já posicionada, o layout continua de onde
        // o grafo anterior parou; sem isso, parte do zero. Nos dois casos
        // a amostragem é gulosa, não aleatória: mesma entrada, mesmo desenho.
        randomize: !continuar,
        samplingType: false,
        quality: pesado ? "draft" : "default",
        animate: !pesado,
        animationDuration: 700,
        nodeRepulsion: 6000,
        idealEdgeLength: 60,
        fit: true,
        padding: 24,
      } as cytoscape.LayoutOptions,
      wheelSensitivity: 0.2,
      minZoom: 0.05,
      maxZoom: 4,
    });

    cy.on("layoutstop", () => {
      cy.nodes().forEach((node) => {
        posicoes.set(node.id(), { ...node.position() });
      });
    });
    cy.on("tap", "node", (event) => onSelectRef.current(event.target.id()));
    cy.on("tap", (event) => {
      if (event.target === cy) onSelectRef.current(null);
    });

    cyRef.current = cy;
    return () => {
      cy.nodes().forEach((node) => {
        posicoes.set(node.id(), { ...node.position() });
      });
      cy.destroy();
      cyRef.current = null;
    };
  }, [graph]);

  // 2. Cor e forma pela partição — sem recriar o grafo.
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    const ordem = membership ? communityOrder(membership) : null;
    cy.batch(() => {
      cy.nodes().forEach((node) => {
        const comunidade = membership?.[node.id()];
        if (ordem && comunidade !== undefined) {
          const { color, shape } = communityStyle(ordem.get(comunidade) ?? 0);
          node.data({ color, shape });
        } else {
          node.removeData("color shape");
        }
      });
    });
  }, [graph, membership]);

  // 3. Tamanho pela métrica, animado pela transição de estilo.
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    const tamanhos = nodeSizes(graph, sizeBy);
    cy.batch(() => {
      cy.nodes().forEach((node) => {
        node.data("size", tamanhos.get(node.id()) ?? TAMANHO_NEUTRO);
      });
    });
  }, [graph, sizeBy]);

  // 4. Seleção vinda de fora (painel) e destaque da vizinhança.
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.batch(() => {
      cy.elements().removeClass("apagado vizinho");
      cy.nodes(":selected").unselect();
      if (!selected) return;
      const alvo = cy.getElementById(selected);
      if (alvo.empty()) return;
      alvo.select();
      const vizinhanca = alvo.closedNeighborhood();
      vizinhanca.addClass("vizinho");
      cy.elements().difference(vizinhanca).addClass("apagado");
    });
  }, [graph, selected]);

  const pesado = graph.edges.length > MAX_EDGES_CONFORTAVEL;
  const { truncation } = graph;

  return (
    <div className="graph-view">
      {(pesado || truncation.truncated) && (
        <p className="aviso" role="status">
          {truncation.truncated && (
            <>
              {truncation.criterion === "backbone"
                ? `Esqueleto: as ${truncation.k_per_node} ligações mais fortes de cada nó`
                : "As arestas de maior peso"}{" "}
              — {truncation.n_edges_returned.toLocaleString("pt-BR")} de{" "}
              {truncation.n_edges_total.toLocaleString("pt-BR")} arestas; todos os{" "}
              {truncation.n_nodes.toLocaleString("pt-BR")} nós estão aqui.{" "}
            </>
          )}
          {pesado && (
            <>
              Acima de {MAX_EDGES_CONFORTAVEL.toLocaleString("pt-BR")} arestas o desenho é
              simplificado e fica mais lento.
            </>
          )}
        </p>
      )}
      <div ref={containerRef} className="graph-canvas" />
    </div>
  );
}
