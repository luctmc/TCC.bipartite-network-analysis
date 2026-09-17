/**
 * Aplicação — Frente C, specs C-04 e C-05.
 *
 * Estado do dia 0: conecta na API, mostra sobre que raízes ela está
 * olhando e lista o que já existe em disco. Os seletores são montados a
 * partir de `/datasets`, sem nome de dataset embutido no código — quando
 * a Frente A gravar o OULAD em `data/processed`, ele aparece aqui
 * sozinho.
 *
 * O grafo depende da rota de projeção, que é a spec C-04. Enquanto ela
 * responde 501, a interface diz isso explicitamente em vez de fingir
 * erro.
 */

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

import { ApiError, api } from "./api";
import { GraphView } from "./components/GraphView";
import type { DatasetSummary, GraphResponse, HealthResponse } from "./types";

type Estado<T> =
  | { status: "carregando" }
  | { status: "pronto"; dados: T }
  | { status: "erro"; erro: ApiError }
  | { status: "aguardando-spec"; spec: string };

export default function App() {
  const [health, setHealth] = useState<Estado<HealthResponse>>({ status: "carregando" });
  const [datasets, setDatasets] = useState<Estado<DatasetSummary[]>>({ status: "carregando" });
  const [datasetAtivo, setDatasetAtivo] = useState<string | null>(null);
  const [projecaoAtiva, setProjecaoAtiva] = useState<string | null>(null);
  const [grafo, setGrafo] = useState<Estado<GraphResponse> | null>(null);

  useEffect(() => {
    api
      .health()
      .then((dados) => setHealth({ status: "pronto", dados }))
      .catch((erro: ApiError) => setHealth({ status: "erro", erro }));

    api
      .datasets()
      .then(({ datasets: lista }) => {
        setDatasets({ status: "pronto", dados: lista });
        const primeiro = lista.find((d) => d.projections.length > 0) ?? lista[0];
        if (primeiro) {
          setDatasetAtivo(primeiro.dataset);
          setProjecaoAtiva(primeiro.projections[0] ?? null);
        }
      })
      .catch((erro: ApiError) => setDatasets({ status: "erro", erro }));
  }, []);

  const resumoAtivo = useMemo(
    () =>
      datasets.status === "pronto"
        ? (datasets.dados.find((d) => d.dataset === datasetAtivo) ?? null)
        : null,
    [datasets, datasetAtivo],
  );

  useEffect(() => {
    if (!datasetAtivo || !projecaoAtiva) {
      setGrafo(null);
      return;
    }

    setGrafo({ status: "carregando" });
    api
      .projection(datasetAtivo, projecaoAtiva)
      .then((dados) => setGrafo({ status: "pronto", dados }))
      .catch((erro: ApiError) =>
        setGrafo(
          erro.notImplemented
            ? { status: "aguardando-spec", spec: "C-04" }
            : { status: "erro", erro },
        ),
      );
  }, [datasetAtivo, projecaoAtiva]);

  return (
    <div className="app">
      <header className="topo">
        <div>
          <h1>edugraph</h1>
          <p className="subtitulo">
            Análise topológica e detecção de comunidades em redes educacionais
          </p>
        </div>
        <StatusApi estado={health} />
      </header>

      <aside className="painel">
        <section>
          <h2>Dataset</h2>
          {datasets.status === "carregando" && <p className="dim">carregando…</p>}
          {datasets.status === "erro" && (
            <p className="erro">
              API fora do ar: {datasets.erro.message}
              <br />
              <code>python -m edugraph api serve --root data/fixtures</code>
            </p>
          )}
          {datasets.status === "pronto" && (
            <select
              value={datasetAtivo ?? ""}
              onChange={(event) => {
                const escolhido = event.target.value;
                setDatasetAtivo(escolhido);
                const resumo = datasets.dados.find((d) => d.dataset === escolhido);
                setProjecaoAtiva(resumo?.projections[0] ?? null);
              }}
            >
              {datasets.dados.map((d) => (
                <option key={d.dataset} value={d.dataset}>
                  {d.dataset}
                </option>
              ))}
            </select>
          )}
        </section>

        {resumoAtivo && (
          <>
            <section>
              <h2>Projeção</h2>
              {resumoAtivo.projections.length === 0 ? (
                <p className="dim">nenhuma projeção neste dataset</p>
              ) : (
                <select
                  value={projecaoAtiva ?? ""}
                  onChange={(event) => setProjecaoAtiva(event.target.value)}
                >
                  {resumoAtivo.projections.map((id) => (
                    <option key={id} value={id}>
                      {id}
                    </option>
                  ))}
                </select>
              )}
            </section>

            <section>
              <h2>Disponível em disco</h2>
              <dl className="inventario">
                <dt>projeções</dt>
                <dd>{resumoAtivo.projections.length}</dd>
                <dt>partições</dt>
                <dd>{resumoAtivo.partitions.length}</dd>
                <dt>centralidades</dt>
                <dd>{resumoAtivo.centralities.length}</dd>
              </dl>
              {/* TODO C-05: seletores de partição (cor) e de métrica
                  (tamanho), alimentados por estas duas listas. */}
            </section>
          </>
        )}
      </aside>

      <main className="palco">
        <AnimatePresence mode="wait">
          <motion.div
            key={`${datasetAtivo}/${projecaoAtiva}/${grafo?.status}`}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="palco-conteudo"
          >
            {grafo === null && <Vazio>Escolha um dataset e uma projeção.</Vazio>}
            {grafo?.status === "carregando" && <Vazio>carregando grafo…</Vazio>}
            {grafo?.status === "aguardando-spec" && (
              <Vazio>
                A rota de projeção é a spec <strong>{grafo.spec}</strong>, ainda aberta.
                <br />
                <span className="dim">
                  O resto da interface já funciona sobre os artefatos em disco.
                </span>
              </Vazio>
            )}
            {grafo?.status === "erro" && <Vazio>{grafo.erro.message}</Vazio>}
            {grafo?.status === "pronto" && <GraphView graph={grafo.dados} />}
          </motion.div>
        </AnimatePresence>
      </main>

      <footer className="rodape">
        Uso interno da instituição · TCC Grupo 16 · UniAnchieta
      </footer>
    </div>
  );
}

function StatusApi({ estado }: { estado: Estado<HealthResponse> }) {
  if (estado.status !== "pronto") {
    return <span className="pill pill-off">API offline</span>;
  }
  return (
    <div className="status-api">
      <span className="pill pill-on">API v{estado.dados.version}</span>
      <span className="dim" title="Raízes de artefatos consultadas, em ordem">
        {estado.dados.roots.join(" · ")}
      </span>
    </div>
  );
}

function Vazio({ children }: { children: React.ReactNode }) {
  return <div className="vazio">{children}</div>;
}
