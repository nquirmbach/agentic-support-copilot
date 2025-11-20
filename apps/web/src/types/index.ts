export interface ProcessRequest {
  request_text: string;
}

export interface Source {
  id: string;
  title: string;
  content: string;
  similarity_score: number;
}

export interface AgentStep {
  agent_name: string;
  step_name: string;
  input: any;
  output: any;
  duration_ms: number;
  timestamp: string;
}

export interface Metrics {
  latency_ms: number;
  token_usage: number;
}

export interface ProcessResponse {
  answer: string;
  sources: Source[];
  trace: AgentStep[];
  metrics: Metrics;
}
