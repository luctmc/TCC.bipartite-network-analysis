/**
 * Faixa de números sobre o grafo — acabamento da C-05.
 *
 * Os números contam até o valor quando o grafo muda: na apresentação, a
 * troca de projeção fica legível ("de 98 para 22 nós") em vez de um salto.
 */

import { useEffect, useRef, useState } from "react";
import { animate, motion } from "framer-motion";

import type { GraphResponse, PartitionResponse } from "../types";

function Contador({ valor, casas = 0 }: { valor: number; casas?: number }) {
  const [mostrado, setMostrado] = useState(valor);
  const anterior = useRef(valor);

  useEffect(() => {
    const controle = animate(anterior.current, valor, {
      duration: 0.8,
      ease: "easeOut",
      onUpdate: (v) => setMostrado(v),
    });
    anterior.current = valor;
    return () => controle.stop();
  }, [valor]);

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

export function StatsBar({ graph, partition }: StatsBarProps) {
  const itens: { rotulo: string; valor: number; casas?: number; dica?: string }[] = [
    { rotulo: "nós", valor: graph.truncation.n_nodes },
    {
      rotulo: "arestas",
      valor: graph.truncation.n_edges_total,
      dica: graph.truncation.truncated
        ? `${graph.truncation.n_edges_returned.toLocaleString("pt-BR")} desenhadas`
        : undefined,
    },
  ];
  if (partition) {
    itens.push(
      { rotulo: "comunidades", valor: partition.n_communities },
      { rotulo: "modularidade Q", valor: partition.modularity, casas: 3 },
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
        <div key={item.rotulo} className="stat" title={item.dica}>
          <dt>{item.rotulo}</dt>
          <dd>
            <Contador valor={item.valor} casas={item.casas} />
          </dd>
        </div>
      ))}
    </motion.dl>
  );
}
