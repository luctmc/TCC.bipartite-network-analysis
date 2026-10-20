/**
 * Faixa de números sobre o grafo — acabamento da C-05.
 *
 * Os números contam até o valor quando o grafo muda: na apresentação, a
 * troca de projeção fica legível ("de 98 para 22 nós") em vez de um salto.
 */

import { useEffect, useRef, useState } from "react";
import { animate, motion, useReducedMotion } from "framer-motion";

import type { GraphResponse, PartitionResponse } from "../types";

function Contador({ valor, casas = 0 }: { valor: number; casas?: number }) {
  const [mostrado, setMostrado] = useState(valor);
  const anterior = useRef(valor);
  const reduzir = useReducedMotion();

  useEffect(() => {
    const controle = animate(anterior.current, valor, {
      duration: reduzir ? 0 : 0.8,
      ease: "easeOut",
      onUpdate: (v) => setMostrado(v),
    });
    anterior.current = valor;
    return () => controle.stop();
  }, [valor, reduzir]);

  return (
    <>
      {mostrado.toLocaleString("pt-BR", {
        minimumFractionDigits: casas,
        maximumFractionDigits: casas,
      })}
    </>
  );
}

interface StatsBarProps {
  graph: GraphResponse;
  partition: PartitionResponse | null;
}

const traco = (filhos: React.ReactNode) => (
  <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {filhos}
  </svg>
);
const ICONE_NOS = traco(
  <>
    <circle cx="12" cy="12" r="3.2" fill="currentColor" />
    <circle cx="12" cy="12" r="8" />
  </>,
);
const ICONE_ARESTAS = traco(
  <>
    <circle cx="5" cy="12" r="2.4" />
    <circle cx="19" cy="12" r="2.4" />
    <path d="M7.6 12h8.8" />
  </>,
);
const ICONE_COMUNIDADES = traco(
  <>
    <circle cx="8" cy="9" r="3" />
    <circle cx="16" cy="9" r="3" />
    <circle cx="12" cy="16" r="3" />
  </>,
);
const ICONE_Q = traco(
  <>
    <path d="M4.5 17a7.5 7.5 0 0 1 15 0" />
    <path d="M12 17l3.6-4.6" />
  </>,
);

export function StatsBar({ graph, partition }: StatsBarProps) {
  const itens: {
    rotulo: string;
    valor: number;
    icone: React.ReactNode;
    casas?: number;
    dica?: string;
    /** Q: medidor de 0 a 1 (só apresentação do mesmo valor). */
    medidor?: number;
  }[] = [
    { rotulo: "Nós", valor: graph.truncation.n_nodes, icone: ICONE_NOS },
    {
      rotulo: "Arestas",
      valor: graph.truncation.n_edges_total,
      icone: ICONE_ARESTAS,
      dica: graph.truncation.truncated
        ? `${graph.truncation.n_edges_returned.toLocaleString("pt-BR")} desenhadas`
        : undefined,
    },
  ];
  if (partition) {
    itens.push(
      { rotulo: "Comunidades", valor: partition.n_communities, icone: ICONE_COMUNIDADES },
      {
        rotulo: "Modularidade Q",
        valor: partition.modularity,
        casas: 3,
        icone: ICONE_Q,
        medidor: Math.min(1, Math.max(0, partition.modularity)),
      },
    );
  }

  return (
    <motion.dl
      className="stats"
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      {itens.map((item) => (
        <div key={item.rotulo} className={item.medidor === undefined ? "stat" : "stat stat-q"} title={item.dica}>
          <dt>
            <span className="stat-icone" aria-hidden="true">
              {item.icone}
            </span>
            {item.rotulo}
          </dt>
          <dd>
            <Contador valor={item.valor} casas={item.casas} />
            {item.medidor !== undefined && (
              <span className="stat-medidor" aria-hidden="true">
                <span style={{ width: `${item.medidor * 100}%` }} />
              </span>
            )}
          </dd>
        </div>
      ))}
    </motion.dl>
  );
}
