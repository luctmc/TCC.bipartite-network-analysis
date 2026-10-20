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

/**
 * Rótulos visíveis sem interação, conforme o zoom deixa ler
 * (`min-zoomed-font-size`). Acima destes limites, só no nó sob o mouse, no
 * selecionado e na vizinhança dele.
 *
 * Disciplinas têm nome que diz algo (`DDD_2014J`) e são poucas; alunos são
 * números de matrícula que, a partir de umas dezenas, só se sobrepõem.
 */
const MAX_DISCIPLINAS_ROTULADAS = 600;
const MAX_ALUNOS_ROTULADOS = 40;

/** Vizinhos do nó selecionado com nome visível; acima disto, só o painel lista. */
const MAX_VIZINHOS_ROTULADOS = 15;

/** Mesma pilha de fontes do CSS: o rótulo do canvas combina com a interface. */
const FONTE = 'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';

/**
 * Tamanho do rótulo **na tela**, em px. O fit amplia grafos pequenos (7 nós
 * chegam a zoom 3), e um rótulo de 8–10px de modelo virava texto de 30px,
 * maior que qualquer título da interface. O tamanho de modelo passa a ser
 * `min(base, ROTULO_TELA / zoom)`: perto, o rótulo para em ~11px; longe, segue
 * a regra antiga (`min-zoomed-font-size` o esconde quando ilegível).
 */
const ROTULO_TELA = 11.5;
const ROTULO_ALUNO = 8;
const ROTULO_DISCIPLINA = 10;

/** Até aqui as arestas são curvas (bézier); acima, retas curtas (haystack). */
const MAX_EDGES_CURVAS = 400;

/**
 * Zoom máximo do enquadramento automático. Grafo pequeno (7 nós) chegava a
 * zoom ~3 e os nós ficavam enormes perto de rótulos de 11,5px; o usuário
 * ainda pode aproximar à mão (`maxZoom` do Cytoscape continua 4).
 */
const ZOOM_MAX_ENQUADRAMENTO = 2.4;

const PADDING_FIT = 72;
const PADDING_FIT_ESTREITO = 28;
const TAMANHO_MIN = 10;
const TAMANHO_MAX = 42;
const TAMANHO_NEUTRO = 16;
const DURACAO_MS = 450;

/**
 * Fator de escala dos nós pelo tamanho do grafo. Com 22 disciplinas os
 * nós podem ser grandes; com 1.870 alunos, no mesmo tamanho, viram uma
 * mancha. Raiz quadrada: a área ocupada cresce devagar com n.
 */
export function escala(n: number): number {
  return Math.min(1, Math.max(0.35, Math.sqrt(60 / Math.max(n, 1))));
}

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
  const f = escala(graph.nodes.length);
  if (!scores) {
    for (const node of graph.nodes) sizes.set(node.id, TAMANHO_NEUTRO * f);
    return sizes;
  }
  const values = graph.nodes.map((node) => scores[node.id] ?? 0);
  const min = Math.min(...values);
  const max = Math.max(...values);
  for (const node of graph.nodes) {
    const t = max > min ? ((scores[node.id] ?? 0) - min) / (max - min) : 0.5;
    sizes.set(node.id, f * (TAMANHO_MIN + t * (TAMANHO_MAX - TAMANHO_MIN)));
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

function estilo(graph: GraphResponse, zoom: () => number): cytoscape.StylesheetJson {
  const fonteRotulo = (base: number) => () => Math.min(base, ROTULO_TELA / Math.max(zoom(), 0.01));
  const fonteDestaque = () => ROTULO_TELA / Math.max(zoom(), 0.01);
  // Larguras em px **de tela**: em unidades do modelo elas escalam com o zoom
  // (grafos pequenos chegam a zoom 3) e o anel/aresta viravam traço grosso.
  const px = (n: number) => () => n / Math.max(zoom(), 0.01);
  const larguraAresta = (aresta: cytoscape.EdgeSingular) => {
    const t = pesoMax > pesoMin ? (Number(aresta.data("weight")) - pesoMin) / (pesoMax - pesoMin) : 0.5;
    return (0.8 + t * 1.0) / Math.max(zoom(), 0.01);
  };
  const pesos = graph.edges.map((edge) => edge.weight);
  const pesoMin = pesos.length ? Math.min(...pesos) : 0;
  const pesoMax = pesos.length ? Math.max(...pesos) : 1;
  const rotularAlunos = graph.nodes.length <= MAX_ALUNOS_ROTULADOS;
  const rotularDisciplinas = graph.nodes.length <= MAX_DISCIPLINAS_ROTULADAS;
  const cor = {
    student: themeColor("--node-student", "#6ea8fe"),
    discipline: themeColor("--node-discipline", "#f0a868"),
    edge: themeColor("--edge", "#5d6d84"),
    surface: themeColor("--surface", "#131820"),
    bg: themeColor("--bg", "#0c0f13"),
    text: themeColor("--text", "#e9edf2"),
    muted: themeColor("--text-muted", "#8e9aa8"),
    text2: themeColor("--text-2", "#b4bdc8"),
    accent: themeColor("--accent", "#7db4ff"),
    accentStrong: themeColor("--accent-strong", "#c4dcff"),
  };

  // Bézier fica elegante, mas custa caro com milhares de arestas: acima do
  // limite o haystack (reta curta, sem controle) segura o desenho.
  const estiloCurva = graph.edges.length <= MAX_EDGES_CURVAS ? "bezier" : "haystack";

  return [
    {
      selector: "node",
      style: {
        "background-color": cor.student,
        "background-opacity": 0.95,
        label: rotularAlunos ? "data(label)" : "",
        "font-family": FONTE,
        "font-size": fonteRotulo(ROTULO_ALUNO),
        "font-weight": 500,
        // Só desenha o rótulo quando ele fica legível na tela: longe, o
        // grafo é forma; perto, é nome.
        "min-zoomed-font-size": 10,
        color: cor.text,
        "text-opacity": 0.82,
        "text-valign": "bottom",
        "text-margin-y": 5,
        // Sem pílula: o contorno na cor do fundo separa o texto das arestas.
        "text-outline-width": 2,
        "text-outline-color": cor.bg,
        "text-outline-opacity": 0.4,
        // Halo suave na cor do próprio nó, no lugar de borda escura.
        "underlay-color": cor.student,
        // Em repouso o nó é limpo (só o anel fino); o halo aparece ao interagir.
        "underlay-opacity": 0,
        "underlay-padding": px(5),
        "underlay-shape": "ellipse",
        "overlay-opacity": 0,
        width: "data(size)",
        height: "data(size)",
        // Anel fino e claro: dá borda ao nó sem desenhar um adesivo.
        "border-width": px(1.2),
        "border-color": "#ffffff",
        "border-opacity": 0.32,
        "transition-property": "width, height, background-color, underlay-color, underlay-opacity, opacity",
        "transition-duration": DURACAO_MS,
        "transition-timing-function": "ease-in-out-cubic",
      } as unknown as cytoscape.Css.Node,
    },
    {
      selector: 'node[kind = "discipline"]',
      style: {
        "background-color": cor.discipline,
        "underlay-color": cor.discipline,
        shape: "round-rectangle",
        "font-size": fonteRotulo(ROTULO_DISCIPLINA),
        label: rotularDisciplinas ? "data(label)" : "",
      } as unknown as cytoscape.Css.Node,
    },
    {
      // Por classe, não por "[color]": o Cytoscape não reavalia seletor de
      // dado quando o dado é removido, e a cor antiga ficava na tela.
      selector: "node.comunidade",
      // "data(shape)" é válido no Cytoscape, mas os tipos só aceitam formas literais.
      style: {
        "background-color": "data(color)",
        "underlay-color": "data(color)",
        shape: "data(shape)",
      } as unknown as cytoscape.Css.Node,
    },
    {
      selector: "edge",
      style: {
        // Com muitas arestas, largura fixa fina: reavaliar milhares a cada zoom pesa.
        width: graph.edges.length <= MAX_EDGES_CURVAS * 4 ? larguraAresta : 0.5,
        "line-color": cor.edge,
        "line-cap": "round",
        "curve-style": estiloCurva,
        opacity: 0.28,
        "transition-property": "opacity, line-color",
        "transition-duration": DURACAO_MS,
      } as unknown as cytoscape.Css.Edge,
    },
    {
      // Aresta dentro de uma comunidade ganha a cor dela: os grupos
      // aparecem pela trama, não só pelos nós.
      selector: "edge.intra",
      style: { "line-color": "data(color)", opacity: 0.5 },
    },
    { selector: ".apagado", style: { opacity: 0.06 } },
    {
      selector: "node.realce",
      style: {
        label: "data(label)",
        "min-zoomed-font-size": 0,
        "font-size": fonteDestaque,
        "font-weight": 600,
        color: cor.text,
        "text-opacity": 1,
        "text-outline-width": 2.5,
        "text-outline-opacity": 0.7,
        "border-width": px(1.8),
        "border-opacity": 0.85,
        "underlay-opacity": 0.22,
        "z-index": 20,
      } as unknown as cytoscape.Css.Node,
    },
    {
      selector: "node.rotulo, node:selected",
      style: {
        label: "data(label)",
        "min-zoomed-font-size": 0,
        "font-size": fonteDestaque,
        color: cor.text,
        "text-opacity": 1,
        "z-index": 10,
      } as unknown as cytoscape.Css.Node,
    },
    { selector: "edge.vizinho", style: { opacity: 0.85, "line-color": cor.accentStrong } },
    {
      selector: "node:selected",
      style: {
        "border-width": px(2.2),
        "border-color": cor.accentStrong,
        "border-opacity": 1,
        "underlay-color": cor.accent,
        "underlay-opacity": 0.3,
        "underlay-padding": px(8),
        "font-weight": 600,
        "text-outline-width": 2.5,
        "text-outline-opacity": 0.7,
      } as unknown as cytoscape.Css.Node,
    },
  ];
}

/**
 * Roda o fcose, com duas redes de proteção.
 *
 * Com a maioria dos nós já posicionada, o layout continua de onde o grafo
 * anterior parou; sem isso, parte do zero. Nos dois casos a amostragem é
 * gulosa, não aleatória: mesma entrada, mesmo desenho.
 *
 * **Só continua em grafo conexo.** Com `randomize: false`, o fcose
 * quebra em grafo desconexo ("Cannot read properties of undefined
 * (reading 'nodeIndexes')", em `relocateComponent`) — o passo que
 * reposiciona as componentes depende do passo espectral, que só roda com
 * `randomize: true`. Se ainda assim o layout falhar, tenta do zero; se
 * falhar de novo, fica a grade: um desenho feio é melhor que uma tela em
 * branco na apresentação.
 */
function rodarLayout(cy: Core, { continuar, pesado }: { continuar: boolean; pesado: boolean }) {
  const padding = cy.width() < 600 ? PADDING_FIT_ESTREITO : PADDING_FIT;
  const base = {
    name: "fcose",
    samplingType: false,
    quality: pesado ? "draft" : "default",
    animate: !pesado,
    animationDuration: 700,
    nodeRepulsion: 6000,
    idealEdgeLength: 60,
    fit: true,
    // Folga maior que a de antes: a faixa de números e o painel do nó
    // flutuam sobre o palco e cobriam os nós da borda.
    padding,
  };
  const conexo = cy.elements().components().length <= 1;
  const tentativas = [
    { ...base, randomize: !(continuar && conexo) },
    { ...base, randomize: true, packComponents: true },
    { name: "grid", fit: true, padding },
  ];
  for (const opcoes of tentativas) {
    try {
      cy.layout(opcoes as cytoscape.LayoutOptions).run();
      return;
    } catch (erro) {
      console.warn(`[GraphView] layout ${opcoes.name} falhou, tentando o próximo`, erro);
    }
  }
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
      style: estilo(graph, () => cyRef.current?.zoom() ?? 1),
      layout: { name: "preset" },
      wheelSensitivity: 0.2,
      minZoom: 0.05,
      maxZoom: 4,
    });

    cy.on("layoutstop", () => {
      if (cy.zoom() > ZOOM_MAX_ENQUADRAMENTO) {
        cy.zoom(ZOOM_MAX_ENQUADRAMENTO);
        cy.center();
      }
      cy.nodes().forEach((node) => {
        posicoes.set(node.id(), { ...node.position() });
      });
    });
    rodarLayout(cy, { continuar, pesado });

    // O tamanho do rótulo depende do zoom: reavalia o estilo dos nós quando
    // ele muda (no máximo uma vez por quadro, e só se o tamanho mudou).
    let quadro = 0;
    let ultimoZoom = -1;
    cy.on("zoom", () => {
      if (quadro) return;
      quadro = requestAnimationFrame(() => {
        quadro = 0;
        if (cy.destroyed()) return;
        const z = cy.zoom();
        if (Math.abs(z - ultimoZoom) < 0.01) return;
        ultimoZoom = z;
        cy.style().update();
      });
    });

    cy.on("mouseover", "node", (event) => {
      event.target.addClass("realce");
      if (containerRef.current) containerRef.current.style.cursor = "pointer";
    });
    cy.on("mouseout", "node", (event) => {
      event.target.removeClass("realce");
      if (containerRef.current) containerRef.current.style.cursor = "";
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
          node.addClass("comunidade");
        } else {
          node.removeClass("comunidade");
        }
      });
      cy.edges().forEach((edge) => {
        const a = membership?.[edge.source().id()];
        const b = membership?.[edge.target().id()];
        if (ordem && a !== undefined && a === b) {
          edge.data("color", communityStyle(ordem.get(a) ?? 0).color);
          edge.addClass("intra");
        } else {
          edge.removeClass("intra");
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
      cy.elements().removeClass("apagado vizinho rotulo");
      cy.nodes(":selected").unselect();
      if (!selected) return;
      const alvo = cy.getElementById(selected);
      if (alvo.empty()) return;
      alvo.select();
      const vizinhanca = alvo.closedNeighborhood();
      vizinhanca.addClass("vizinho");
      // Nome dos vizinhos só em vizinhança pequena: com dezenas, os rótulos
      // se sobrepõem, e a lista completa já está no painel do nó.
      if (vizinhanca.nodes().length <= MAX_VIZINHOS_ROTULADOS + 1) {
        vizinhanca.nodes().addClass("rotulo");
      }
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
              {truncation.criterion === "backbone" && (truncation.k_per_node ?? 0) > 0
                ? `Esqueleto: as ${truncation.k_per_node} ligações mais fortes de cada nó`
                : truncation.criterion === "backbone"
                  ? "Nem uma ligação por nó coube no limite: ficaram as mais fortes, e alguns nós aparecem soltos"
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
