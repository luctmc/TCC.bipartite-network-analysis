/**
 * Espelho dos schemas pydantic de `edugraph/api/schemas.py`.
 *
 * Mudar um schema lá é mudar o contrato com o front: sai em PR com os
 * dois lados juntos. Para conferir se ainda batem:
 *
 *     python -m edugraph api openapi > /tmp/openapi.json
 */

export type NodeKind = "student" | "discipline";
export type CentralityMetric = "degree" | "betweenness" | "eigenvector";
export type RunStatus = "ok" | "timeout" | "skipped";

export interface HealthResponse {
  status: "ok";
  version: string;
  schema_version: string;
  /** Raízes de artefatos que a API está consultando, em ordem. */
  roots: string[];
}

export interface DatasetSummary {
  dataset: string;
  has_bipartite: boolean;
  projections: string[];
  /** Ids no formato `<algoritmo>__<projection_id>`. */
  partitions: string[];
  centralities: string[];
}

export interface DatasetListResponse {
  datasets: DatasetSummary[];
}

export interface GraphNode {
  id: string;
  kind: NodeKind;
  label: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
}

/**
 * O corte de arestas da resposta. Quando `truncated`, a API ficou com as
 * `max_edges` arestas de maior peso e manteve todos os nós.
 */
export interface TruncationInfo {
  truncated: boolean;
  max_edges: number;
  n_nodes: number;
  n_edges_total: number;
  n_edges_returned: number;
  criterion: "top_weight";
}

export interface GraphResponse {
  dataset: string;
  projection_id: string;
  spec: Record<string, unknown>;
  nodes: GraphNode[];
  edges: GraphEdge[];
  truncation: TruncationInfo;
  /** Nó → comunidade, quando a partição foi pedida junto. */
  community?: Record<string, number> | null;
  /** Métrica → (nó → score), quando as centralidades foram pedidas junto. */
  centrality?: Record<string, Record<string, number>> | null;
}

export interface PartitionResponse {
  dataset: string;
  algorithm: string;
  projection_id: string;
  modularity: number;
  n_communities: number;
  runtime_s: number;
  status: RunStatus;
  params: Record<string, unknown>;
  membership: Record<string, number>;
}

export interface CentralityResponse {
  dataset: string;
  projection_id: string;
  metric: CentralityMetric;
  converged: boolean;
  runtime_s: number;
  params: Record<string, unknown>;
  /** Pares [nó, score], já ordenados do maior para o menor. */
  ranking: [string, number][];
}

export interface MetricsResponse {
  dataset: string;
  name: string;
  /** Linhas de `metrics/<name>.csv`; números já convertidos. */
  rows: Record<string, string | number>[];
}
