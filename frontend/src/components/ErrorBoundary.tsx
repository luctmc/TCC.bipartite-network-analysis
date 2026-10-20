/**
 * Contém erros de renderização do grafo.
 *
 * Um erro dentro do Cytoscape ou do layout não pode apagar a interface
 * inteira: o painel continua usável e o usuário pode trocar de projeção.
 * `resetKey` limpa o erro quando a seleção muda.
 */

import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  resetKey: string;
  children: ReactNode;
}

interface State {
  erro: Error | null;
  resetKey: string;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { erro: null, resetKey: this.props.resetKey };

  static getDerivedStateFromError(erro: Error): Partial<State> {
    return { erro };
  }

  static getDerivedStateFromProps(props: Props, state: State): Partial<State> | null {
    return props.resetKey !== state.resetKey ? { erro: null, resetKey: props.resetKey } : null;
  }

  componentDidCatch(erro: Error, info: ErrorInfo) {
    console.error("[ErrorBoundary] erro ao desenhar o grafo", erro, info.componentStack);
  }

  render() {
    if (this.state.erro) {
      return (
        <div className="vazio vazio-erro" role="alert">
          <span className="vazio-icone" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 4 3 20h18L12 4Z" />
              <path d="M12 10v4M12 17.2v.1" />
            </svg>
          </span>
          <span className="vazio-texto">
            Não foi possível desenhar este grafo.
            <br />
            <span className="dim">{this.state.erro.message}</span>
          </span>
        </div>
      );
    }
    return this.props.children;
  }
}
