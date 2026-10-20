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

import { useEffect, useId, useRef, useState, type KeyboardEvent, type ReactNode } from "react";

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
  icone: ReactNode;
  titulo?: string;
}

/** Tempo sem digitar até a busca por prefixo recomeçar. */
const BUSCA_MS = 700;

export function Seletor({ nome, value, opcoes, onChange, icone, titulo }: SeletorProps) {
  const base = useId();
  const [aberto, setAberto] = useState(false);
  const [ativo, setAtivo] = useState(0);
  const raiz = useRef<HTMLDivElement>(null);
  const lista = useRef<HTMLUListElement>(null);
  const busca = useRef({ texto: "", timer: 0 });

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
    if (opcao) onChange(opcao.value);
    fechar();
  };

  // Clique fora fecha.
  useEffect(() => {
    if (!aberto) return;
    const fora = (event: PointerEvent) => {
      if (!raiz.current?.contains(event.target as Node)) setAberto(false);
    };
    document.addEventListener("pointerdown", fora);
    return () => document.removeEventListener("pointerdown", fora);
  }, [aberto]);

  // A opção ativa sempre fica visível dentro do painel.
  useEffect(() => {
    if (!aberto) return;
    lista.current?.children[ativo]?.scrollIntoView({ block: "nearest" });
  }, [aberto, ativo]);

  useEffect(() => () => window.clearTimeout(busca.current.timer), []);

  /** Digitar leva à primeira opção cujo texto começa pelo que foi digitado. */
  const buscar = (tecla: string) => {
    window.clearTimeout(busca.current.timer);
    busca.current.texto += tecla.toLowerCase();
    busca.current.timer = window.setTimeout(() => (busca.current.texto = ""), BUSCA_MS);
    const texto = busca.current.texto;
    const comeca = (o: OpcaoSeletor) =>
      o.rotulo.toLowerCase().startsWith(texto) || o.value.toLowerCase().startsWith(texto);
    // Uma tecla só repetida avança entre as opções que começam por ela.
    const partida = texto.length === 1 ? (aberto ? ativo : indiceSelecionado) + 1 : 0;
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
        <span className="seletor-icone" aria-hidden="true">
          {icone}
        </span>
        <span className="seletor-valor">{selecionada?.rotulo ?? value}</span>
        <svg className="seletor-seta" viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M3 4.5 6 7.5 9 4.5" />
        </svg>
      </button>

      {aberto && (
        <ul className="seletor-painel" id={`${base}-lista`} role="listbox" aria-label={nome} ref={lista}>
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
        </ul>
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
