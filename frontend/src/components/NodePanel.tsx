/**
 * Painel do nó selecionado — spec C-05.
 *
 * Comunidade, as três centralidades (com a posição no ranking) e os
 * vizinhos, do mais forte para o mais fraco. Clicar num vizinho o
 * seleciona, o que permite percorrer o grafo pelo painel durante a
 * apresentação.
 */

import type { CSSProperties } from "react";
import { motion } from "framer-motion";

import { communityOrder, communityStyle } from "../palette";
import { SILHUETAS } from "./CommunityLegend";
import type { CentralityMetric, GraphResponse } from "../types";

const METRICAS: { id: CentralityMetric; nome: string }[] = [
  { id: "degree", nome: "Grau" },
  { id: "betweenness", nome: "Intermediação" },
  { id: "eigenvector", nome: "Autovetor" },
];

/** Vizinhos mostrados antes do "e mais N". */
const MAX_VIZINHOS = 12;

interface NodePanelProps {
  graph: GraphResponse;
  membership: Record<string, number> | null;
  nodeId: string;
  onSelect: (nodeId: string | null) => void;
}

/**
 * Ordem por ponto de código, a mesma do `sorted` do Python — `localeCompare`
 * ordena por idioma e, num empate, daria uma posição diferente da API.
 */
function porCodigo(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

/** Posição do nó no ranking da métrica (1 = maior), com o mesmo desempate por id da API. */
function posicao(scores: Record<string, number>, nodeId: string): number {
  const ordenados = Object.entries(scores).sort((a, b) => b[1] - a[1] || porCodigo(a[0], b[0]));
  return ordenados.findIndex(([id]) => id === nodeId) + 1;
}

export function NodePanel({ graph, membership, nodeId, onSelect }: NodePanelProps) {
  const no = graph.nodes.find((node) => node.id === nodeId);
  if (!no) return null;

  const rotulos = new Map(graph.nodes.map((node) => [node.id, node.label]));
  const vizinhos = graph.edges
    .filter((edge) => edge.source === nodeId || edge.target === nodeId)
    .map((edge) => ({
      id: edge.source === nodeId ? edge.target : edge.source,
      weight: edge.weight,
    }))
    .sort((a, b) => b.weight - a.weight || porCodigo(a.id, b.id));

  const pesoMax = vizinhos[0]?.weight ?? 0;

  const comunidade = membership?.[nodeId];
  const estiloComunidade =
    membership && comunidade !== undefined
      ? communityStyle(communityOrder(membership).get(comunidade) ?? 0)
      : null;

  return (
    <motion.section
      className="node-panel"
      key={nodeId}
      initial={{ opacity: 0, x: 12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
    >
      <header className="node-panel-topo">
        <div>
          <h2>{no.kind === "discipline" ? "Disciplina" : "Aluno"}</h2>
          <p className="node-panel-nome">{no.label}</p>
        </div>
        <button type="button" className="fechar" onClick={() => onSelect(null)} aria-label="Fechar painel do nó">
          <svg viewBox="0 0 14 14" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
            <path d="M3 3l8 8M11 3l-8 8" />
          </svg>
        </button>
      </header>

      <div className="comunidade-chip">
        {estiloComunidade ? (
          <span className="comunidade">
            <svg className="amostra" viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
              <path d={SILHUETAS[estiloComunidade.shape] ?? SILHUETAS.ellipse} fill={estiloComunidade.color} />
            </svg>
            comunidade {comunidade}
          </span>
        ) : (
          <span className="dim">sem comunidade</span>
        )}
      </div>

      <div className="metricas">
        {METRICAS.map(({ id, nome }) => {
          const scores = graph.centrality?.[id];
          const valor = scores?.[nodeId];
          return (
            <Metrica
              key={id}
              nome={nome}
              valor={valor}
              posicao={scores && valor !== undefined ? posicao(scores, nodeId) : null}
              total={scores ? Object.keys(scores).length : 0}
            />
          );
        })}
      </div>

      <div className="vizinhos-bloco">
        <h3>
          Vizinhos <span className="dim">({vizinhos.length})</span>
        </h3>
        {graph.truncation.truncated && (
          <p className="dim">Só entre as arestas mostradas (a resposta foi cortada).</p>
        )}
        <ul className="vizinhos">
          {vizinhos.slice(0, MAX_VIZINHOS).map((vizinho) => {
            const nome = rotulos.get(vizinho.id) ?? vizinho.id;
            return (
              <li key={vizinho.id}>
                <button
                  type="button"
                  onClick={() => onSelect(vizinho.id)}
                  title={nome}
                  style={{ "--w": `${pesoMax > 0 ? (100 * vizinho.weight) / pesoMax : 0}%` } as CSSProperties}
                >
                  <span>{nome}</span>
                  <span className="dim">{vizinho.weight.toLocaleString("pt-BR")}</span>
                </button>
              </li>
            );
          })}
        </ul>
        {vizinhos.length > MAX_VIZINHOS && (
          <p className="dim resto">e mais {vizinhos.length - MAX_VIZINHOS}</p>
        )}
      </div>
    </motion.section>
  );
}

/** Uma centralidade: valor em destaque, posição como badge e medidor da posição relativa. */
function Metrica(props: {
  nome: string;
  valor: number | undefined;
  posicao: number | null;
  total: number;
}) {
  const { nome, valor, posicao: pos, total } = props;
  return (
    <div className="metrica">
      <div className="metrica-topo">
        <span className="metrica-nome" title={nome}>
          {nome}
        </span>
        {valor !== undefined && pos !== null && (
          <span className="posicao" title={`${pos}º lugar entre ${total} nós`}>
            {pos}º<span>/{total}</span>
          </span>
        )}
      </div>
      {valor === undefined ? (
        <span className="metrica-valor metrica-nula">não calculada</span>
      ) : (
        <>
          <span className="metrica-valor">
            {valor.toLocaleString("pt-BR", { minimumFractionDigits: 4, maximumFractionDigits: 4 })}
          </span>
          <span
            className="medidor"
            role="img"
            aria-label={`${pos}º lugar entre ${total} nós`}
          >
            <span style={{ width: `${total > 0 && pos !== null ? (100 * (total - pos + 1)) / total : 0}%` }} />
          </span>
        </>
      )}
    </div>
  );
}
