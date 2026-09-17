/**
 * Cliente da API.
 *
 * A API é somente leitura (ADR-0004): não há POST, não há cálculo sob
 * demanda. Todo endpoint aqui é um GET sobre artefato já em disco.
 *
 * Rotas de dados ainda respondem 501 enquanto a spec C-04 não fecha —
 * `ApiError.notImplemented` distingue esse caso de um erro de verdade,
 * para que a interface possa dizer "aguardando C-04" em vez de "falhou".
 */

import type {
  CentralityMetric,
  CentralityResponse,
  DatasetListResponse,
  GraphResponse,
  HealthResponse,
  PartitionResponse,
} from "./types";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }

  /** 501: a rota existe, mas a spec que a implementa ainda está aberta. */
  get notImplemented(): boolean {
    return this.status === 501;
  }

  /** 404: dataset, projeção ou partição inexistente sob as raízes da API. */
  get notFound(): boolean {
    return this.status === 404;
  }
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(path, { headers: { Accept: "application/json" } });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // resposta sem corpo JSON: fica o statusText mesmo
    }
    throw new ApiError(response.status, detail);
  }

  return (await response.json()) as T;
}

export const api = {
  health: () => get<HealthResponse>("/health"),

  datasets: () => get<DatasetListResponse>("/datasets"),

  /**
   * Grafo de uma projeção. `partition` e `metrics` pedem que a partição
   * e as centralidades venham embutidas, evitando uma segunda ida ao
   * servidor só para colorir e dimensionar.
   */
  projection: (
    dataset: string,
    projectionId: string,
    options: { partition?: string; metrics?: CentralityMetric[] } = {},
  ) => {
    const params = new URLSearchParams();
    if (options.partition) params.set("partition", options.partition);
    if (options.metrics?.length) params.set("metrics", options.metrics.join(","));
    const query = params.toString();

    return get<GraphResponse>(
      `/datasets/${encodeURIComponent(dataset)}/projections/` +
        `${encodeURIComponent(projectionId)}${query ? `?${query}` : ""}`,
    );
  },

  partition: (dataset: string, artifactId: string) =>
    get<PartitionResponse>(
      `/datasets/${encodeURIComponent(dataset)}/communities/${encodeURIComponent(artifactId)}`,
    ),

  centrality: (dataset: string, projectionId: string, metric: CentralityMetric) =>
    get<CentralityResponse>(
      `/datasets/${encodeURIComponent(dataset)}/centrality/` +
        `${encodeURIComponent(projectionId)}/${metric}`,
    ),
};
