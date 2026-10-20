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

export function StatsBar({ graph, partition }: StatsBarProps) {
  const itens: { rotulo: string; valor: number; casas?: number; dica?: string }[] = [
    { rotulo: "Nós", valor: graph.truncation.n_nodes },
    { rotulo: "Arestas", valor: graph.truncation.n_edges_total,
      dica: graph.truncation.truncated ? `${graph.truncation.n_edges_returned.toLocaleString("pt-BR")} desenhadas` : undefined },
  ];
  if (partition) itens.push(
    { rotulo: "Comunidades", valor: partition.n_communities },
    { rotulo: "Modularidade", valor: partition.modularity, casas: 3 },
  );
  return <motion.dl className="stats" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.15 }}>
    {itens.map(item => <div key={item.rotulo} className="stat" title={item.dica}>
      <dt>{item.rotulo}</dt>
      <dd>{item.casas === 3 && <i>Q </i>}<Contador valor={item.valor} casas={item.casas} /></dd>
    </div>)}
  </motion.dl>;
}
