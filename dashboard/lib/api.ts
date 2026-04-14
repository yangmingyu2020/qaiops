const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8765";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

// -- Types --

export interface LogItem {
  id: string;
  tool_name: string;
  model_name: string | null;
  project_id: string | null;
  directory: string | null;
  prompt_text: string;
  response_text: string | null;
  input_tokens: number;
  output_tokens: number;
  total_cost: number;
  latency_ms: number | null;
  status_code: number;
  error_message: string | null;
  tags: string[] | null;
  created_at: string;
}

export interface LogListResponse {
  items: LogItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface DailyStats {
  date: string;
  tool_name: string;
  total_requests: number;
  total_tokens: number;
  total_cost: number;
}

export interface ProjectStats {
  project_id: string | null;
  tool_name: string;
  request_count: number;
  total_tokens: number;
  total_cost: number;
  avg_latency_ms: number | null;
  last_used_at: string | null;
}

export interface TopCostItem {
  id: string;
  tool_name: string;
  model_name: string | null;
  project_id: string | null;
  prompt_text: string;
  total_cost: number;
  input_tokens: number;
  output_tokens: number;
  created_at: string;
}

export interface HeatmapItem {
  date: string;
  project_id: string | null;
  total_tokens: number;
  total_cost: number;
  request_count: number;
}

export interface AlertItem {
  id: string;
  tool_name: string;
  model_name: string | null;
  project_id: string | null;
  prompt_text: string;
  total_tokens: number;
  total_cost: number;
  created_at: string;
}

// -- API Functions --

export async function fetchLogs(params?: {
  page?: number;
  size?: number;
  tool_name?: string;
  project_id?: string;
  search?: string;
}): Promise<LogListResponse> {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  if (params?.size) query.set("size", String(params.size));
  if (params?.tool_name) query.set("tool_name", params.tool_name);
  if (params?.project_id) query.set("project_id", params.project_id);
  if (params?.search) query.set("search", params.search);

  const qs = query.toString();
  return fetchApi<LogListResponse>(`/api/v1/logs${qs ? `?${qs}` : ""}`);
}

export async function fetchLog(id: string): Promise<LogItem> {
  return fetchApi<LogItem>(`/api/v1/logs/${id}`);
}

export async function fetchDailyStats(days = 30, tool_name?: string): Promise<DailyStats[]> {
  const query = new URLSearchParams({ days: String(days) });
  if (tool_name) query.set("tool_name", tool_name);
  return fetchApi<DailyStats[]>(`/api/v1/stats/daily?${query}`);
}

export async function fetchProjectStats(): Promise<ProjectStats[]> {
  return fetchApi<ProjectStats[]>("/api/v1/stats/projects");
}

export async function fetchTopCosts(limit = 10): Promise<TopCostItem[]> {
  return fetchApi<TopCostItem[]>(`/api/v1/stats/top-costs?limit=${limit}`);
}

export async function fetchHeatmap(days = 30): Promise<HeatmapItem[]> {
  return fetchApi<HeatmapItem[]>(`/api/v1/stats/heatmap?days=${days}`);
}

export async function fetchAlerts(threshold = 10000, limit = 50): Promise<AlertItem[]> {
  return fetchApi<AlertItem[]>(`/api/v1/stats/alerts?threshold=${threshold}&limit=${limit}`);
}

export async function fetchHealth(): Promise<{ status: string; version: string }> {
  return fetchApi("/health");
}
