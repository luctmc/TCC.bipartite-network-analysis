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

import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, MotionConfig, motion } from "framer-motion";

import { ApiError, api } from "./api";
import { CommunityLegend } from "./components/CommunityLegend";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { GraphView } from "./components/GraphView";
import { NodePanel } from "./components/NodePanel";
import { Seletor } from "./components/Seletor";
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

type Tema = "light" | "dark";
const CHAVE_TEMA = "edugraph-tema";

/** O atributo já foi posto por `index.html` antes da primeira pintura. */
function temaInicial(): Tema {
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

export default function App() {
  const [tema, setTema] = useState<Tema>(temaInicial);
  // Timeout que tira a classe de transição do tema; só pode haver um.
  const fimTransicaoTema = useRef(0);

  // Ao desmontar: cancela o timeout e não deixa a classe para trás.
  useEffect(
    () => () => {
      window.clearTimeout(fimTransicaoTema.current);
      document.documentElement.classList.remove("tema-trocando");
    },
    [],
  );
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

  /**
   * Alterna claro/escuro. O atributo é posto **antes** de `setTema`: o canvas
   * do grafo lê as cores dos tokens CSS ao reagir à troca, então eles já
   * precisam valer. A transição curta só roda sem movimento reduzido.
   */
  const alternarTema = () => {
    const novo: Tema = tema === "light" ? "dark" : "light";
    const raiz = document.documentElement;
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      raiz.classList.add("tema-trocando");
      window.clearTimeout(fimTransicaoTema.current);
      fimTransicaoTema.current = window.setTimeout(() => raiz.classList.remove("tema-trocando"), 320);
    }
    raiz.dataset.theme = novo;
    try {
      localStorage.setItem(CHAVE_TEMA, novo);
    } catch {
      /* sem armazenamento: a escolha vale só nesta sessão */
    }
    setTema(novo);
  };

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
    <MotionConfig reducedMotion="user">
    <div className="app">
      <header className="topo">
        <div className="hero">
          <p className="sobrelinha">
            Trabalho de Conclusão de Curso <span aria-hidden="true">·</span> Grupo 16{" "}
            <span aria-hidden="true">·</span> UniAnchieta
          </p>
          <h1>Análise Topológica e Detecção de Comunidades em Redes Complexas</h1>
          <p className="autores" title={AUTORES.join(", ")}>
            {AUTORES.join(" · ")}
          </p>
        </div>
        <div className="topo-lado">
          <span className="wordmark">
            <svg className="marca-simbolo" viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true">
              <g stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.65">
                <path d="M6 5 18 12M6 12h12M6 19h12" />
              </g>
              <g fill="currentColor">
                <circle cx="6" cy="5" r="2" />
                <circle cx="6" cy="12" r="2" />
                <circle cx="6" cy="19" r="2" />
                <circle cx="18" cy="19" r="2" />
                <circle cx="18" cy="5" r="2" opacity="0.6" />
              </g>
              <circle cx="18" cy="12" r="2.6" fill="var(--accent)" />
            </svg>
            edugraph
          </span>
          <div className="topo-status">
            <StatusApi estado={health} />
            <BotaoTema tema={tema} onAlternar={alternarTema} />
          </div>
        </div>
      </header>

      <aside className="painel" aria-label="Controles do grafo">
        <section className="cartao">
          <Passo n={1} titulo="Dados" ajuda="Conjunto lido do disco." icone={ICONE_DADOS} />
          {datasets.status === "carregando" && (
            <p className="nota nota-carregando">
              <span className="giro giro-pequeno" />
              carregando datasets…
            </p>
          )}
          {datasets.status === "erro" && (
            <p className="nota nota-erro" role="alert">
              API fora do ar: {datasets.erro.message}
              <br />
              <code>python -m edugraph api serve --root data/fixtures</code>
            </p>
          )}
          {datasets.status === "pronto" && (
            <Campo id={null}>
              <Seletor
                nome="Dataset"
                icone={ICONE_DADOS}
                value={datasetAtivo ?? ""}
                titulo={datasetAtivo ?? undefined}
                opcoes={datasets.dados.map((d) => ({ value: d.dataset, rotulo: d.dataset }))}
                onChange={(escolhido) => {
                  setDatasetAtivo(escolhido);
                  const resumo = datasets.dados.find((d) => d.dataset === escolhido);
                  setProjecaoAtiva(resumo?.projections[0] ?? null);
                }}
              />
            </Campo>
          )}
        </section>

        {resumoAtivo && (
          <>
            <section className="cartao">
              <Passo
                n={2}
                titulo="Projeção"
                ajuda="Rede de um só tipo de nó."
                icone={ICONE_PROJECAO}
              />
              {resumoAtivo.projections.length === 0 ? (
                <p className="nota">nenhuma projeção neste dataset</p>
              ) : (
                <Campo id={ROTULO_PROJECAO[projecaoAtiva ?? ""] ? projecaoAtiva : null}>
                  <Seletor
                    nome="Projeção"
                    icone={ICONE_PROJECAO}
                    value={projecaoAtiva ?? ""}
                    titulo={projecaoAtiva ?? undefined}
                    opcoes={resumoAtivo.projections.map((id) => ({
                      value: id,
                      rotulo: ROTULO_PROJECAO[id] ?? id,
                      id: ROTULO_PROJECAO[id] ? id : undefined,
                    }))}
                    onChange={(id) => setProjecaoAtiva(id)}
                  />
                </Campo>
              )}
            </section>

            <section className="cartao">
              <Passo
                n={3}
                titulo="Comunidades"
                ajuda="Definem a cor e a forma."
                icone={ICONE_COMUNIDADES}
              />
              {particoes.length === 0 ? (
                <p className="nota">nenhuma partição desta projeção em disco</p>
              ) : (
                <Campo id={null}>
                  <Seletor
                    nome="Algoritmo de comunidades"
                    icone={ICONE_COMUNIDADES}
                    value={particaoAtiva ?? ""}
                    titulo={particaoAtiva ?? undefined}
                    opcoes={[
                      { value: "", rotulo: "sem cor por comunidade" },
                      ...particoes.map((id) => {
                        const algoritmo = id.split("__")[0];
                        return { value: id, rotulo: ROTULO_ALGORITMO[algoritmo] ?? algoritmo };
                      }),
                    ]}
                    onChange={(id) => setParticaoAtiva(id || null)}
                  />
                </Campo>
              )}
              {particao && membership && (
                <>
                  <div className="q-metrica">
                    <div>
                      <span className="q-rotulo">Modularidade Q</span>
                      <span className="q-valor">
                        {particao.modularity.toLocaleString("pt-BR", {
                          minimumFractionDigits: 4,
                          maximumFractionDigits: 4,
                        })}
                      </span>
                    </div>
                    <span className="q-chip">{particao.n_communities} comunidades</span>
                    {particao.status !== "ok" && <span className="q-chip q-chip-aviso">{particao.status}</span>}
                  </div>
                  <CommunityLegend membership={membership} />
                </>
              )}
            </section>

            <section className="cartao">
              <Passo
                n={4}
                titulo="Centralidade"
                ajuda="Define o tamanho dos nós."
                icone={ICONE_CENTRALIDADE}
              />
              {dadosGrafo && metricasDisponiveis.length === 0 ? (
                <p className="nota">
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
                      <span className="segmentado-icone" aria-hidden="true">
                        {ICONE_METRICA[m.id ?? "igual"]}
                      </span>
                      {m.nome}
                    </button>
                  ))}
                </div>
              )}
            </section>
          </>
        )}

        <GuiaDeLeitura />
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
            {grafo === null && (
              <Vazio tipo="vazio" icone={ICONE_GRAFO}>
                Escolha um dataset e uma projeção para ver o grafo.
              </Vazio>
            )}
            {grafo?.status === "carregando" && (
              <Vazio tipo="carregando" icone={<span className="giro" />}>
                carregando grafo…
              </Vazio>
            )}
            {grafo?.status === "erro" && (
              <Vazio tipo="erro" icone={ICONE_ALERTA}>
                {grafo.erro.message}
              </Vazio>
            )}
            {dadosGrafo && (
              <ErrorBoundary resetKey={`${datasetAtivo}/${projecaoAtiva}`}>
                <GraphView
                  graph={dadosGrafo}
                  membership={membership}
                  sizeBy={metricaAtiva}
                  tema={tema}
                  selected={selecionado}
                  onSelect={setSelecionado}
                />
              </ErrorBoundary>
            )}
          </motion.div>
        </AnimatePresence>

        {!(dadosGrafo && selecionado) && (
          <aside className="inspetor-vazio">
            <span className="vazio-icone" aria-hidden="true">
              {ICONE_GRAFO}
            </span>
            <p>Selecione um nó no grafo para ver comunidade, centralidades e vizinhos.</p>
          </aside>
        )}
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
        <a
          className="rodape-link"
          href={URL_REPOSITORIO}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Repositório do TCC no GitHub (abre em nova aba)"
        >
          <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor" aria-hidden="true">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
          </svg>
          <span>Repositório do TCC</span>
          <code className="rodape-slug">luctmc/TCC.bipartite-network-analysis</code>
        </a>
        <span className="rodape-autoria">TCC · Grupo 16 · UniAnchieta</span>
      </footer>
    </div>
    </MotionConfig>
  );
}

const URL_REPOSITORIO = "https://github.com/luctmc/TCC.bipartite-network-analysis";

/** Autores do trabalho (os mesmos de `pyproject.toml`). */
const AUTORES = [
  "Gabriel Luís Lopes",
  "Pedro Alexandre dos Santos Chaves",
  "Lucas Timponi Mercadante Castro",
];

/**
 * Rótulos de exibição. O `value` das opções e o id que vai para a API continuam
 * sendo o id técnico; o id aparece abaixo do seletor, em fonte monoespaçada.
 */
const ROTULO_PROJECAO: Record<string, string> = {
  discipline_resource_allocation: "Disciplinas · alocação de recursos",
  discipline_simple: "Disciplinas · projeção simples",
  student_resource_allocation: "Alunos · alocação de recursos",
  student_simple: "Alunos · projeção simples",
};
const ROTULO_ALGORITMO: Record<string, string> = {
  louvain: "Louvain",
  girvan_newman: "Girvan–Newman",
};

function Passo(props: { n: number; titulo: string; ajuda: string; icone: React.ReactNode }) {
  return (
    <header className="passo">
      <span className="passo-num" aria-hidden="true">
        {props.n}
      </span>
      <div className="passo-texto">
        <h2>{props.titulo}</h2>
        <p>{props.ajuda}</p>
      </div>
      <span className="passo-icone" aria-hidden="true">
        {props.icone}
      </span>
    </header>
  );
}

/** Espaço do seletor, com o id técnico (secundário) logo abaixo quando há. */
function Campo(props: { id: string | null; children: React.ReactNode }) {
  return (
    <div className="campo">
      {props.children}
      {props.id && <code className="campo-id">{props.id}</code>}
    </div>
  );
}

function GuiaDeLeitura() {
  return (
    <section className="guia" aria-labelledby="guia-titulo">
      <h2 id="guia-titulo">Como ler o grafo</h2>
      <ul>
        <li>
          <span className="guia-glifos" aria-hidden="true">
            <svg viewBox="0 0 16 16" width="14" height="14"><circle cx="8" cy="8" r="6.5" fill="#56B4E9" /></svg>
            <svg viewBox="0 0 16 16" width="14" height="14"><path d="M8 1 15 14H1Z" fill="#E69F00" /></svg>
            <svg viewBox="0 0 16 16" width="14" height="14"><rect x="1.5" y="1.5" width="13" height="13" rx="3" fill="#009E73" /></svg>
          </span>
          <span>
            <strong>Forma e cor</strong> são a comunidade (a forma separa em cinza).
          </span>
        </li>
        <li>
          <span className="guia-glifos" aria-hidden="true">
            <svg viewBox="0 0 16 16" width="14" height="14"><circle cx="4" cy="8" r="2.4" fill="currentColor" /></svg>
            <svg viewBox="0 0 16 16" width="14" height="14"><circle cx="8" cy="8" r="6.5" fill="currentColor" /></svg>
          </span>
          <span>
            <strong>Tamanho</strong> é a centralidade do passo 4.
          </span>
        </li>
        <li>
          <span className="guia-glifos" aria-hidden="true">
            <svg viewBox="0 0 24 16" width="22" height="14"><path d="M1 4h22" stroke="currentColor" strokeWidth="1" /><path d="M1 11h22" stroke="currentColor" strokeWidth="3" /></svg>
          </span>
          <span>
            <strong>Espessura</strong> da aresta é o peso.
          </span>
        </li>
        <li>
          <span className="guia-glifos" aria-hidden="true">
            <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"><path d="M3 2l9 5-4 1.2L6.5 12 3 2Z" /></svg>
          </span>
          <span>
            <strong>Clique</strong> no nó abre os detalhes.
          </span>
        </li>
      </ul>
    </section>
  );
}

const icone = (children: React.ReactNode, tamanho = 18) => (
  <svg viewBox="0 0 24 24" width={tamanho} height={tamanho} fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {children}
  </svg>
);

const ICONE_DADOS = icone(
  <>
    <ellipse cx="12" cy="6" rx="7" ry="3" />
    <path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6" />
  </>,
);
const ICONE_PROJECAO = icone(
  <>
    <circle cx="6" cy="7" r="2.3" />
    <circle cx="6" cy="17" r="2.3" />
    <rect x="14" y="9.5" width="6.5" height="5" rx="1.4" />
    <path d="M8 8l6 3M8 16l6-3" />
  </>,
);
const ICONE_COMUNIDADES = icone(
  <>
    <circle cx="8" cy="9" r="3" />
    <circle cx="16" cy="9" r="3" />
    <circle cx="12" cy="16" r="3" />
  </>,
);
const ICONE_CENTRALIDADE = icone(
  <>
    <circle cx="12" cy="12" r="2.4" fill="currentColor" />
    <circle cx="12" cy="12" r="6.5" />
    <path d="M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21" />
  </>,
);

const ICONE_METRICA: Record<string, React.ReactNode> = {
  igual: icone(
    <>
      <circle cx="5" cy="12" r="2.6" />
      <circle cx="12" cy="12" r="2.6" />
      <circle cx="19" cy="12" r="2.6" />
    </>,
    15,
  ),
  degree: icone(
    <>
      <circle cx="12" cy="12" r="3" fill="currentColor" />
      <path d="M12 9V4.5M12 15v4.5M9 12H4.5M15 12h4.5" />
      <circle cx="12" cy="3.5" r="1.4" />
      <circle cx="12" cy="20.5" r="1.4" />
      <circle cx="3.5" cy="12" r="1.4" />
      <circle cx="20.5" cy="12" r="1.4" />
    </>,
    15,
  ),
  betweenness: icone(
    <>
      <circle cx="4.5" cy="12" r="2.2" />
      <circle cx="19.5" cy="12" r="2.2" />
      <circle cx="12" cy="12" r="3" fill="currentColor" />
      <path d="M6.8 12H9M15 12h2.2" />
    </>,
    15,
  ),
  eigenvector: icone(
    <>
      <circle cx="12" cy="12" r="2.4" fill="currentColor" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="9.5" opacity="0.5" />
    </>,
    15,
  ),
};

function BotaoTema({ tema, onAlternar }: { tema: Tema; onAlternar: () => void }) {
  const claro = tema === "light";
  return (
    <button
      type="button"
      className="tema-botao"
      aria-pressed={claro}
      aria-label="Modo claro"
      title={claro ? "Voltar ao modo escuro" : "Usar o modo claro"}
      onClick={onAlternar}
    >
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        {claro ? (
          <>
            <circle cx="12" cy="12" r="4" />
            <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4 7 17M17 7l1.4-1.4" />
          </>
        ) : (
          <path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z" />
        )}
      </svg>
    </button>
  );
}

function StatusApi({ estado }: { estado: Estado<HealthResponse> }) {
  if (estado.status !== "pronto") {
    return <span className="pill pill-off">API offline</span>;
  }
  return (
    <div className="status-api">
      <span className="pill pill-on">API v{estado.dados.version}</span>
      <span
        className="status-raizes"
        tabIndex={0}
        title={`Raízes de artefatos consultadas, em ordem: ${estado.dados.roots.join(" · ")}`}
      >
        {estado.dados.roots.join(" · ")}
      </span>
    </div>
  );
}

const ICONE_GRAFO = (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
    <path d="M7 7l10 3M7 7l4 10M17 10l-6 7" />
    <circle cx="7" cy="7" r="2.4" />
    <circle cx="17" cy="10" r="2.4" />
    <circle cx="11" cy="17" r="2.4" />
  </svg>
);

const ICONE_ALERTA = (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M12 4 3 20h18L12 4Z" />
    <path d="M12 10v4M12 17.2v.1" />
  </svg>
);

function Vazio({
  children,
  tipo,
  icone,
}: {
  children: React.ReactNode;
  tipo: "vazio" | "carregando" | "erro";
  icone: React.ReactNode;
}) {
  return (
    <div
      className={`vazio vazio-${tipo}`}
      role={tipo === "erro" ? "alert" : "status"}
      aria-live={tipo === "erro" ? undefined : "polite"}
    >
      <span className="vazio-icone">{icone}</span>
      <span className="vazio-texto">{children}</span>
    </div>
  );
}
