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

export interface GraphResponse {
  dataset: string;
  projection_id: string;
  spec: Record<string, unknown>;
  nodes: GraphNode[];
  edges: GraphEdge[];
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
