/**
 * Painel do nó selecionado — spec C-05.
 *
 * Comunidade, as três centralidades (com a posição no ranking) e os
 * vizinhos, do mais forte para o mais fraco. Clicar num vizinho o
 * seleciona, o que permite percorrer o grafo pelo painel durante a
 * apresentação.
 */

import { motion } from "framer-motion";

import { communityOrder, communityStyle } from "../palette";
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

/** Posição do nó no ranking da métrica (1 = maior), com o mesmo desempate por id da API. */
function posicao(scores: Record<string, number>, nodeId: string): number {
  const ordenados = Object.entries(scores).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
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
    .sort((a, b) => b.weight - a.weight || a.id.localeCompare(b.id));

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
        <button type="button" className="fechar" onClick={() => onSelect(null)} aria-label="Fechar">
          ×
        </button>
      </header>

      <dl className="inventario">
        <dt>comunidade</dt>
        <dd>
          {estiloComunidade ? (
            <span className="comunidade">
              <span className="amostra" style={{ background: estiloComunidade.color }} />
              {comunidade}
            </span>
          ) : (
            <span className="dim">—</span>
          )}
        </dd>
        {METRICAS.map(({ id, nome }) => {
          const scores = graph.centrality?.[id];
          const valor = scores?.[nodeId];
          return (
            <FragmentoMetrica
              key={id}
              nome={nome}
              valor={valor}
              posicao={scores && valor !== undefined ? posicao(scores, nodeId) : null}
              total={scores ? Object.keys(scores).length : 0}
            />
          );
        })}
      </dl>

      <h3>
        Vizinhos <span className="dim">({vizinhos.length})</span>
      </h3>
      {graph.truncation.truncated && (
        <p className="dim">Só entre as arestas mostradas (a resposta foi cortada).</p>
      )}
      <ul className="vizinhos">
        {vizinhos.slice(0, MAX_VIZINHOS).map((vizinho) => (
          <li key={vizinho.id}>
            <button type="button" onClick={() => onSelect(vizinho.id)}>
              <span>{rotulos.get(vizinho.id) ?? vizinho.id}</span>
              <span className="dim">{vizinho.weight.toLocaleString("pt-BR")}</span>
            </button>
          </li>
        ))}
      </ul>
      {vizinhos.length > MAX_VIZINHOS && (
        <p className="dim">e mais {vizinhos.length - MAX_VIZINHOS}</p>
      )}
    </motion.section>
  );
}

function FragmentoMetrica(props: {
  nome: string;
  valor: number | undefined;
  posicao: number | null;
  total: number;
}) {
  return (
    <>
      <dt>{props.nome.toLowerCase()}</dt>
      <dd>
        {props.valor === undefined ? (
          <span className="dim">não calculada</span>
        ) : (
          <>
            {props.valor.toFixed(4)}{" "}
            <span className="dim">
              {props.posicao}º/{props.total}
            </span>
          </>
        )}
      </dd>
    </>
  );
}
