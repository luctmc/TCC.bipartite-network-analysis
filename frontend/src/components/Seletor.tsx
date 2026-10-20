/**
 * Seletor próprio (listbox) — acabamento da C-05.
 *
 * O menu aberto de um `<select>` é o popup nativo do sistema, que destoa do
 * tema. Este componente desenha o gatilho e o painel no tema e segue o padrão
 * WAI-ARIA "select-only combobox": o foco fica no gatilho, e a opção ativa é
 * apontada por `aria-activedescendant`.
 *
 * Teclado: setas, Home/End, PageUp/PageDown, Enter ou Espaço para escolher,
 * Esc para fechar (o foco continua no gatilho), digitar para buscar. Clique
 * fora fecha.
 *
 * **Não muda o fluxo:** `onChange` recebe o mesmo `value` que o `<select>`
 * recebia. Um `<select>` nativo, oculto e sincronizado, continua no DOM — é por
 * ele que `scripts/capture.mjs` escolhe as cenas, e ele cobre ferramentas que
 * leem controles de formulário.
 */

import {
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent,
} from "react";
import { createPortal } from "react-dom";

export interface OpcaoSeletor {
  value: string;
  /** Texto principal da opção. */
  rotulo: string;
  /** Id técnico, mostrado em mono como informação secundária. */
  id?: string;
}

interface SeletorProps {
  /** Nome acessível do controle. */
  nome: string;
  value: string;
  opcoes: OpcaoSeletor[];
  onChange: (valor: string) => void;
  titulo?: string;
}

/** Tempo sem digitar até a busca por prefixo recomeçar. */
const BUSCA_MS = 700;

/** Altura máxima do painel e folga até a borda da janela. */
const ALTURA_MAX_PX = 256;
const FOLGA_PX = 8;
/** Largura mínima do painel em telas estreitas, onde o gatilho divide a linha. */
const LARGURA_MIN_ESTREITA_PX = 256;

/** Onde o painel fica, em px da janela (posição fixa, fora de qualquer área com scroll). */
interface Posicao {
  left: number;
  width: number;
  maxHeight: number;
  /** Abre para cima quando embaixo não cabe. */
  acima: boolean;
  /** Distância da borda: do topo (abre para baixo) ou da base (abre para cima). */
  borda: number;
}

export function Seletor({ nome, value, opcoes, onChange, titulo }: SeletorProps) {
  const base = useId();
  const [aberto, setAberto] = useState(false);
  const [ativo, setAtivo] = useState(0);
  const raiz = useRef<HTMLDivElement>(null);
  const lista = useRef<HTMLUListElement>(null);
  const busca = useRef({ texto: "", timer: 0 });
  const [posicao, setPosicao] = useState<Posicao | null>(null);

  const indiceSelecionado = Math.max(
    0,
    opcoes.findIndex((o) => o.value === value),
  );
  const selecionada = opcoes[indiceSelecionado];
  const idOpcao = (i: number) => `${base}-opcao-${i}`;

  const abrir = (indice = indiceSelecionado) => {
    setAtivo(indice);
    setAberto(true);
  };
  const fechar = () => setAberto(false);
  const escolher = (i: number) => {
    const opcao = opcoes[i];
    // Reconfirmar a opção já escolhida só fecha o menu: o <select> nativo não
    // disparava onChange nesse caso, e o App reseta a projeção ao trocar de dataset.
    if (opcao && opcao.value !== value) onChange(opcao.value);
    fechar();
  };

  // Clique fora fecha. O painel mora no <body> (portal), então conta como "dentro".
  useEffect(() => {
    if (!aberto) return;
    const fora = (event: PointerEvent) => {
      const alvo = event.target as Node;
      if (!raiz.current?.contains(alvo) && !lista.current?.contains(alvo)) setAberto(false);
    };
    document.addEventListener("pointerdown", fora);
    return () => document.removeEventListener("pointerdown", fora);
  }, [aberto]);

  // O painel tem posição fixa: rolar a página/lateral ou redimensionar o fecha,
  // em vez de deixá-lo solto longe do gatilho. A rolagem da própria lista não conta.
  useEffect(() => {
    if (!aberto) return;
    const aoRolar = (event: Event) => {
      if (lista.current && event.target instanceof Node && lista.current.contains(event.target)) return;
      setAberto(false);
    };
    const aoRedimensionar = () => setAberto(false);
    document.addEventListener("scroll", aoRolar, true);
    window.addEventListener("resize", aoRedimensionar);
    return () => {
      document.removeEventListener("scroll", aoRolar, true);
      window.removeEventListener("resize", aoRedimensionar);
    };
  }, [aberto]);

  // Posiciona o painel antes da pintura: embaixo do gatilho; se não couber e
  // houver mais espaço em cima, abre para cima. A altura se limita ao espaço.
  useLayoutEffect(() => {
    if (!aberto) {
      setPosicao(null);
      return;
    }
    const gatilho = raiz.current?.getBoundingClientRect();
    const painel = lista.current;
    if (!gatilho || !painel) return;
    const abaixo = window.innerHeight - gatilho.bottom - FOLGA_PX;
    const acima = gatilho.top - FOLGA_PX;
    const natural = Math.min(painel.scrollHeight, ALTURA_MAX_PX);
    const paraCima = natural > abaixo && acima > abaixo;
    const espaco = paraCima ? acima : abaixo;
    const largura = Math.max(
      gatilho.width,
      window.innerWidth <= 760 ? Math.min(LARGURA_MIN_ESTREITA_PX, window.innerWidth - 2 * FOLGA_PX) : 0,
    );
    setPosicao({
      left: Math.max(FOLGA_PX, Math.min(gatilho.left, window.innerWidth - largura - FOLGA_PX)),
      width: largura,
      // Nunca passa do espaço do lado escolhido (sem piso): o painel não sai da janela.
      maxHeight: Math.max(0, Math.min(ALTURA_MAX_PX, espaco - 6)),
      acima: paraCima,
      borda: paraCima ? window.innerHeight - gatilho.top + 6 : gatilho.bottom + 6,
    });
  }, [aberto, opcoes.length]);

  // A opção ativa sempre fica visível dentro do painel.
  useEffect(() => {
    if (!aberto) return;
    lista.current?.children[ativo]?.scrollIntoView({ block: "nearest" });
  }, [aberto, ativo]);

  useEffect(() => () => window.clearTimeout(busca.current.timer), []);

  /**
   * Digitar leva à primeira opção cujo texto começa pelo que foi digitado
   * (busca por prefixo, com várias letras). Repetir a MESMA tecla ("a", "a")
   * cicla entre as opções que começam por ela.
   */
  const buscar = (tecla: string) => {
    window.clearTimeout(busca.current.timer);
    busca.current.texto += tecla.toLowerCase();
    busca.current.timer = window.setTimeout(() => (busca.current.texto = ""), BUSCA_MS);
    const digitado = busca.current.texto;
    const repetida = [...digitado].every((letra) => letra === digitado[0]);
    const texto = repetida ? digitado[0] : digitado;
    const comeca = (o: OpcaoSeletor) =>
      o.rotulo.toLowerCase().startsWith(texto) || o.value.toLowerCase().startsWith(texto);
    const atual = aberto ? ativo : indiceSelecionado;
    // Tecla repetida avança a partir da opção atual; prefixo longo a mantém, se ainda casar.
    const partida = repetida ? atual + 1 : atual;
    const ordem = Array.from({ length: opcoes.length }, (_, k) => (partida + k) % opcoes.length);
    const achado = ordem.find((i) => comeca(opcoes[i]));
    if (achado === undefined) return;
    if (aberto) setAtivo(achado);
    else abrir(achado);
  };

  const aoTeclar = (event: KeyboardEvent<HTMLButtonElement>) => {
    const ultimo = opcoes.length - 1;
    const mover = (indice: number) => {
      event.preventDefault();
      if (aberto) setAtivo(Math.min(ultimo, Math.max(0, indice)));
      else abrir(Math.min(ultimo, Math.max(0, indice)));
    };
    switch (event.key) {
      case "ArrowDown":
        return mover(aberto ? ativo + 1 : indiceSelecionado);
      case "ArrowUp":
        return mover(aberto ? ativo - 1 : indiceSelecionado);
      case "Home":
        return mover(0);
      case "End":
        return mover(ultimo);
      case "PageDown":
        return mover(ativo + 10);
      case "PageUp":
        return mover(ativo - 10);
      case "Enter":
      case " ":
        event.preventDefault();
        return aberto ? escolher(ativo) : abrir();
      case "Escape":
        if (aberto) {
          event.preventDefault();
          event.stopPropagation();
          fechar();
        }
        return;
      case "Tab":
        return fechar();
      default:
        if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
          event.preventDefault();
          buscar(event.key);
        }
    }
  };

  return (
    <div className="seletor" ref={raiz}>
      <button
        type="button"
        className="seletor-gatilho"
        role="combobox"
        aria-label={nome}
        aria-haspopup="listbox"
        aria-expanded={aberto}
        aria-controls={`${base}-lista`}
        aria-activedescendant={aberto ? idOpcao(ativo) : undefined}
        title={titulo}
        onClick={(event) => {
          // Safari não foca <button> no clique; sem foco, teclado e Esc não chegam aqui.
          event.currentTarget.focus();
          if (aberto) fechar();
          else abrir();
        }}
        onKeyDown={aoTeclar}
      >
        <span className="seletor-valor">{selecionada?.rotulo ?? value}</span>
        <svg className="seletor-seta" viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M3 4.5 6 7.5 9 4.5" />
        </svg>
      </button>

      {aberto &&
        createPortal(
          <ul
            className="seletor-painel"
            id={`${base}-lista`}
            role="listbox"
            aria-label={nome}
            ref={lista}
            data-acima={posicao?.acima ?? false}
            style={estiloPainel(posicao)}
          >
            {opcoes.map((opcao, i) => (
              <li
                key={opcao.value}
                id={idOpcao(i)}
                role="option"
                aria-selected={opcao.value === value}
                data-ativo={i === ativo}
                className="seletor-opcao"
                // O foco fica no gatilho: nem o mousedown pode roubá-lo.
                onMouseDown={(event) => event.preventDefault()}
                onMouseMove={() => i !== ativo && setAtivo(i)}
                onClick={() => escolher(i)}
              >
                <span className="seletor-textos">
                  <span className="seletor-rotulo">{opcao.rotulo}</span>
                  {opcao.id && <code className="seletor-id">{opcao.id}</code>}
                </span>
                <svg className="seletor-check" viewBox="0 0 14 14" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M2.5 7.5 5.5 10.5 11.5 3.5" />
                </svg>
              </li>
            ))}
          </ul>,
          document.body,
        )}

      {/* Mesmo valor e mesmo onChange de antes, fora da vista e do teclado. */}
      <select
        className="seletor-nativo"
        aria-hidden="true"
        tabIndex={-1}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {opcoes.map((opcao) => (
          <option key={opcao.value} value={opcao.value}>
            {opcao.rotulo}
          </option>
        ))}
      </select>
    </div>
  );
}

/** Estilo em px da janela; até medir, o painel fica invisível (sem piscar fora do lugar). */
function estiloPainel(posicao: Posicao | null): CSSProperties {
  if (!posicao) return { visibility: "hidden", top: 0, left: 0 };
  return {
    left: posicao.left,
    width: posicao.width,
    maxHeight: posicao.maxHeight,
    ...(posicao.acima ? { bottom: posicao.borda } : { top: posicao.borda }),
  };
}
