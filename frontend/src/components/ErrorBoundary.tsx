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
        <div className="vazio">
          Não foi possível desenhar este grafo.
          <br />
          <span className="dim">{this.state.erro.message}</span>
        </div>
      );
    }
    return this.props.children;
  }
}
