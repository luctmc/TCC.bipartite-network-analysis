/**
 * Aplicação — Frente C, spec C-05.
 *
 * Os seletores são montados a partir de `/datasets`, sem nome de dataset
 * embutido no código: o que estiver em disco sob as raízes da API
 * aparece aqui.
 *
 * Duas requisições por tela, de propósito:
 *
 * - a **projeção**, com as centralidades embutidas, muda quando muda o
 *   dataset ou a projeção — e só então o grafo é redesenhado;
 * - a **partição** vem à parte, para que trocar a cor não recarregue nem
 *   re-diagrame o grafo: só os nós mudam de cor, com transição.
 */

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

import { ApiError, api } from "./api";
import { CommunityLegend } from "./components/CommunityLegend";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { GraphView } from "./components/GraphView";
import { NodePanel } from "./components/NodePanel";
import { StatsBar } from "./components/StatsBar";
import type {
  CentralityMetric,
  DatasetSummary,
  GraphResponse,
  HealthResponse,
  PartitionResponse,
} from "./types";

type Estado<T> =
  | { status: "carregando" }
  | { status: "pronto"; dados: T }
  | { status: "erro"; erro: ApiError };

const METRICAS: { id: CentralityMetric; nome: string }[] = [
  { id: "degree", nome: "Grau" },
  { id: "betweenness", nome: "Intermediação" },
  { id: "eigenvector", nome: "Autovetor" },
];

/** Partições da projeção ativa: `<algoritmo>__<projection_id>`, Louvain primeiro. */
function particoesDa(resumo: DatasetSummary | null, projecao: string | null): string[] {
  if (!resumo || !projecao) return [];
  return resumo.partitions
    .filter((id) => id.endsWith(`__${projecao}`))
    .sort((a, b) => Number(!a.startsWith("louvain")) - Number(!b.startsWith("louvain")) || a.localeCompare(b));
}

export default function App() {
  const [health, setHealth] = useState<Estado<HealthResponse>>({ status: "carregando" });
  const [datasets, setDatasets] = useState<Estado<DatasetSummary[]>>({ status: "carregando" });
  const [datasetAtivo, setDatasetAtivo] = useState<string | null>(null);
  const [projecaoAtiva, setProjecaoAtiva] = useState<string | null>(null);
  const [particaoAtiva, setParticaoAtiva] = useState<string | null>(null);
  const [metricaAtiva, setMetricaAtiva] = useState<CentralityMetric | null>("degree");
  const [selecionado, setSelecionado] = useState<string | null>(null);
  const [grafo, setGrafo] = useState<Estado<GraphResponse> | null>(null);
  const [particao, setParticao] = useState<PartitionResponse | null>(null);

  useEffect(() => {
    api
      .health()
      .then((dados) => setHealth({ status: "pronto", dados }))
      .catch((erro: ApiError) => setHealth({ status: "erro", erro }));

    api
      .datasets()
      .then(({ datasets: lista }) => {
        setDatasets({ status: "pronto", dados: lista });
        const primeiro =
          lista.find((d) => d.projections.length > 0 && d.partitions.length > 0) ??
          lista.find((d) => d.projections.length > 0) ??
          lista[0];
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
  const particoes = useMemo(
    () => particoesDa(resumoAtivo, projecaoAtiva),
    [resumoAtivo, projecaoAtiva],
  );

  // Ao trocar de projeção: a primeira partição dela, e nenhum nó selecionado.
  useEffect(() => {
    setParticaoAtiva(particoes[0] ?? null);
    setSelecionado(null);
  }, [particoes]);

  // A projeção, com as centralidades que existirem em disco.
  useEffect(() => {
    if (!datasetAtivo || !projecaoAtiva) {
      setGrafo(null);
      return;
    }
    let cancelado = false;
    const temCentralidade = resumoAtivo?.centralities.includes(projecaoAtiva) ?? false;
    const todas = METRICAS.map((m) => m.id);

    setGrafo({ status: "carregando" });
    (temCentralidade
      ? api.availableMetrics(datasetAtivo, projecaoAtiva, todas)
      : Promise.resolve<CentralityMetric[]>([])
    )
      .then((metrics) => api.projection(datasetAtivo, projecaoAtiva, { metrics }))
      .then((dados) => !cancelado && setGrafo({ status: "pronto", dados }))
      .catch((erro: ApiError) => !cancelado && setGrafo({ status: "erro", erro }));
    return () => {
      cancelado = true;
    };
  }, [datasetAtivo, projecaoAtiva, resumoAtivo]);

  // A partição, à parte: trocar a cor não redesenha o grafo.
  useEffect(() => {
    // Limpa já: sem isto a legenda e o Q da partição anterior ficam na
    // tela até a resposta nova chegar.
    setParticao(null);
    if (!datasetAtivo || !particaoAtiva) return;
    let cancelado = false;
    api
      .partition(datasetAtivo, particaoAtiva)
      .then((dados) => !cancelado && setParticao(dados))
      .catch(() => !cancelado && setParticao(null));
    return () => {
      cancelado = true;
    };
  }, [datasetAtivo, particaoAtiva]);

  const dadosGrafo = grafo?.status === "pronto" ? grafo.dados : null;
  const metricasDisponiveis = METRICAS.filter((m) => dadosGrafo?.centrality?.[m.id]);
  const membership = particao?.membership ?? null;
  const chaveMetricas = metricasDisponiveis.map((m) => m.id).join(",");

  // Se a métrica escolhida não existe nesta projeção, cai na primeira que existir.
  useEffect(() => {
    if (!dadosGrafo) return;
    const ids = chaveMetricas ? (chaveMetricas.split(",") as CentralityMetric[]) : [];
    setMetricaAtiva((atual) => (atual === null || ids.includes(atual) ? atual : (ids[0] ?? null)));
  }, [dadosGrafo, chaveMetricas]);

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
              <h2>Cor: comunidades</h2>
              {particoes.length === 0 ? (
                <p className="dim">nenhuma partição desta projeção em disco</p>
              ) : (
                <select
                  value={particaoAtiva ?? ""}
                  onChange={(event) => setParticaoAtiva(event.target.value || null)}
                >
                  <option value="">sem cor por comunidade</option>
                  {particoes.map((id) => (
                    <option key={id} value={id}>
                      {id.split("__")[0]}
                    </option>
                  ))}
                </select>
              )}
              {particao && membership && (
                <>
                  <p className="dim resumo-particao">
                    Q = {particao.modularity.toLocaleString("pt-BR", { minimumFractionDigits: 4, maximumFractionDigits: 4 })} · {particao.n_communities} comunidades
                    {particao.status !== "ok" && ` · ${particao.status}`}
                  </p>
                  <CommunityLegend membership={membership} />
                </>
              )}
            </section>

            <section>
              <h2>Tamanho: centralidade</h2>
              {dadosGrafo && metricasDisponiveis.length === 0 ? (
                <p className="dim">
                  sem centralidades desta projeção em disco
                  <br />
                  <code>python -m edugraph centrality all</code>
                </p>
              ) : (
                <div className="segmentado" role="radiogroup" aria-label="Métrica de tamanho">
                  {[{ id: null, nome: "Igual" }, ...metricasDisponiveis].map((m) => (
                    <button
                      key={m.id ?? "nenhuma"}
                      type="button"
                      role="radio"
                      aria-checked={metricaAtiva === m.id}
                      className={metricaAtiva === m.id ? "ativo" : ""}
                      onClick={() => setMetricaAtiva(m.id as CentralityMetric | null)}
                    >
                      {m.nome}
                    </button>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </aside>

      <main className="palco">
        {dadosGrafo && <StatsBar graph={dadosGrafo} partition={particao} />}
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
            {grafo?.status === "erro" && <Vazio>{grafo.erro.message}</Vazio>}
            {dadosGrafo && (
              <ErrorBoundary resetKey={`${datasetAtivo}/${projecaoAtiva}`}>
                <GraphView
                  graph={dadosGrafo}
                  membership={membership}
                  sizeBy={metricaAtiva}
                  selected={selecionado}
                  onSelect={setSelecionado}
                />
              </ErrorBoundary>
            )}
          </motion.div>
        </AnimatePresence>

        <AnimatePresence>
          {dadosGrafo && selecionado && (
            <NodePanel
              graph={dadosGrafo}
              membership={membership}
              nodeId={selecionado}
              onSelect={setSelecionado}
            />
          )}
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
