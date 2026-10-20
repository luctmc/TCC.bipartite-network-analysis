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

import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { AnimatePresence, MotionConfig, motion } from "framer-motion";

import { ApiError, api } from "./api";
import { CommunityLegend } from "./components/CommunityLegend";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { GraphView, type GraphViewHandle } from "./components/GraphView";
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
  const grafoRef = useRef<GraphViewHandle>(null);
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

  /** Atalhos de zoom: valem só com o foco dentro do palco (grafo, controles ou painel do nó). */
  const atalhosDoPalco = (event: KeyboardEvent<HTMLElement>) => {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    const acao =
      event.key === "+" || event.key === "="
        ? grafoRef.current?.aproximar
        : event.key === "-" || event.key === "_"
          ? grafoRef.current?.afastar
          : event.key === "0"
            ? grafoRef.current?.centralizar
            : undefined;
    if (!acao) return;
    event.preventDefault();
    acao();
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
          <p className="sobrelinha">Trabalho de Conclusão de Curso · Grupo 16 · UniAnchieta</p>
          <h1>Análise Topológica e Detecção de Comunidades em Redes Complexas</h1>
          <p className="autores" title={AUTORES.join(", ")}>{AUTORES.join(", ")}</p>
        </div>
        <div className="topo-lado">
          <span className="wordmark"><Marca /> edugraph</span>
          <div className="topo-status"><StatusApi estado={health} /><BotaoTema tema={tema} onAlternar={alternarTema} /></div>
        </div>
      </header>
      <main className="palco" onKeyDown={atalhosDoPalco}>
        <section className="figura-area" aria-label="Figura da rede">
          {dadosGrafo && <StatsBar graph={dadosGrafo} partition={particao} />}
          <div className="figura">
            <AnimatePresence mode="wait">
              <motion.div
                key={`${datasetAtivo}/${projecaoAtiva}/${grafo?.status}`}
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }} className="palco-conteudo"
              >
                {grafo === null && <Vazio tipo="vazio">Escolha um dataset e uma projeção para ver o grafo.</Vazio>}
                {grafo?.status === "carregando" && <Vazio tipo="carregando">{datasetAtivo} · {projecaoAtiva}</Vazio>}
                {grafo?.status === "erro" && <Vazio tipo="erro">{grafo.erro.message}</Vazio>}
                {dadosGrafo && (
                  <ErrorBoundary resetKey={`${datasetAtivo}/${projecaoAtiva}`}>
                    <GraphView ref={grafoRef} graph={dadosGrafo} membership={membership}
                      sizeBy={metricaAtiva} tema={tema} selected={selecionado} onSelect={setSelecionado} />
                  </ErrorBoundary>
                )}
              </motion.div>
            </AnimatePresence>
            {dadosGrafo && <ControlesZoom aoAproximar={() => grafoRef.current?.aproximar()}
              aoAfastar={() => grafoRef.current?.afastar()} aoCentralizar={() => grafoRef.current?.centralizar()} />}
          </div>
          <p className="legenda-fig">
            <b>Figura 1.</b> {ROTULO_PROJECAO[projecaoAtiva ?? ""] ?? "Rede educacional"}
            {datasetAtivo && <>, <i>{datasetAtivo}</i></>}. <b>Forma e cor</b>{" "}
            <span className="glifos-legenda"><Marca /></span> indicam a comunidade
            {particao && <> ({ROTULO_ALGORITMO[particao.algorithm] ?? particao.algorithm})</>}; a forma basta para ler em cinza.{" "}
            <b>Tamanho</b> {metricaAtiva ? `é ${METRICAS.find(m => m.id === metricaAtiva)?.nome.toLowerCase()}` : "é igual para todos os nós"}.{" "}
            <b>Espessura</b> da linha é o peso da ligação. Clique num nó para ver os detalhes.
          </p>
        </section>
        <aside className="nota-lateral" aria-label="Detalhes do nó">
          {!(dadosGrafo && selecionado) && <p className="inspetor-vazio">Selecione um nó no grafo para ver comunidade, centralidades e vizinhos.</p>}
          <AnimatePresence>
            {dadosGrafo && selecionado && <NodePanel graph={dadosGrafo} membership={membership} nodeId={selecionado} onSelect={setSelecionado} />}
          </AnimatePresence>
        </aside>
      </main>
      <aside className="painel" aria-label="Controles do grafo">
        <section className="cartao">
          <Passo n={1} titulo="Dados" ajuda="Conjunto lido do disco." />
          {datasets.status === "carregando" && (
            <p className="nota nota-carregando">
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
              />
              {resumoAtivo.projections.length === 0 ? (
                <p className="nota">nenhuma projeção neste dataset</p>
              ) : (
                <Campo id={ROTULO_PROJECAO[projecaoAtiva ?? ""] ? projecaoAtiva : null}>
                  <Seletor
                    nome="Projeção"
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
              />
              {particoes.length === 0 ? (
                <p className="nota">nenhuma partição desta projeção em disco</p>
              ) : (
                <Campo id={null}>
                  <Seletor
                    nome="Algoritmo de comunidades"
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
                    <b><i>Q</i> = {particao.modularity.toLocaleString("pt-BR", { minimumFractionDigits: 4, maximumFractionDigits: 4 })}</b>
                    <span>modularidade</span>
                    {particao.status !== "ok" && <span>{particao.status}</span>}
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
                      <span className="radio-marca" aria-hidden="true" />
                      {m.nome}
                    </button>
                  ))}
                </div>
              )}
              <p className="opcoes-desc">{DESCRICAO_METRICA[metricaAtiva ?? "igual"]}</p>
            </section>
          </>
        )}

      </aside>


      <footer className="rodape">
        <span>Repositório do TCC: <a href={URL_REPOSITORIO} target="_blank" rel="noopener noreferrer"
          aria-label="Repositório do TCC no GitHub (abre em nova aba)">luctmc/TCC.bipartite-network-analysis</a></span>
        <span>TCC · Grupo 16 · UniAnchieta</span>
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

function Passo(props: { n: number; titulo: string; ajuda: string }) {
  return (
    <header className="passo">
      <span className="passo-num" aria-hidden="true">
        {props.n}
      </span>
      <div className="passo-texto">
        <h2>{props.titulo}</h2>
        <p>{props.ajuda}</p>
      </div>
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

function Marca() {
  return <svg viewBox="0 0 32 16" width="32" height="16" aria-hidden="true">
    <circle cx="5" cy="8" r="4.5" fill="#56B4E9" />
    <path d="M16 3 21 12.5H11Z" fill="#E69F00" />
    <rect x="23" y="3.5" width="8.5" height="8.5" rx="2" fill="#009E73" />
  </svg>;
}

const DESCRICAO_METRICA: Record<string, string> = {
  igual: "Igual: todos os nós têm o mesmo tamanho.",
  degree: "Grau: quantos vizinhos o nó tem.",
  betweenness: "Intermediação: quanto o nó faz ponte entre grupos.",
  eigenvector: "Autovetor: quanto os vizinhos do nó também são centrais.",
};

/** Barra flutuante de zoom: aproximar, afastar e centralizar o grafo. */
function ControlesZoom(props: {
  aoAproximar: () => void;
  aoAfastar: () => void;
  aoCentralizar: () => void;
}) {
  const traco = (filhos: React.ReactNode) => (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {filhos}
    </svg>
  );
  return (
    <div className="zoom-controles" role="group" aria-label="Zoom do grafo">
      <button type="button" onClick={props.aoAproximar} aria-label="Aproximar o grafo" title="Aproximar (+)">
        {traco(<path d="M12 5v14M5 12h14" />)}
      </button>
      <button type="button" onClick={props.aoAfastar} aria-label="Afastar o grafo" title="Afastar (−)">
        {traco(<path d="M5 12h14" />)}
      </button>
      <button type="button" onClick={props.aoCentralizar} aria-label="Centralizar o grafo" title="Centralizar (0)">
        {traco(
          <>
            <path d="M4 9V5h4M20 9V5h-4M4 15v4h4M20 15v4h-4" />
          </>,
        )}
      </button>
    </div>
  );
}

function BotaoTema({ tema, onAlternar }: { tema: Tema; onAlternar: () => void }) {
  const claro = tema === "light";
  return (
    <button
      type="button"
      className="tema-botao"
      aria-pressed={claro}
      aria-label="Alternar tema claro e escuro"
      title={claro ? "Usar o modo escuro" : "Usar o modo claro"}
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
      Tema
    </button>
  );
}

function StatusApi({ estado }: { estado: Estado<HealthResponse> }) {
  if (estado.status !== "pronto") {
    return (
      <span className="status-pilula status-off">
        <span className="status-ponto" aria-hidden="true" />
        API offline
      </span>
    );
  }
  return (
    <div className="status-pilula">
      <span className="status-ponto" aria-hidden="true" />
      <span className="status-versao">API v{estado.dados.version}</span>
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

function Vazio({ children, tipo }: {
  children: React.ReactNode;
  tipo: "vazio" | "carregando" | "erro";
}) {
  return <div className={`vazio vazio-${tipo}`} role={tipo === "erro" ? "alert" : "status"}
    aria-live={tipo === "erro" ? undefined : "polite"}>
    <h2>{tipo === "vazio" ? "Nenhuma figura ainda" : tipo === "carregando" ? "Carregando a projeção…" : "A API não respondeu"}</h2>
    <p>{children}</p>
    {tipo === "carregando" && <span className="fio" aria-hidden="true"><span /></span>}
  </div>;
}
