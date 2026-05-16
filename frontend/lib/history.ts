import type { QueryHistoryItem, QueryResponse } from "./types";

const HISTORY_KEY = "dev_agent_query_history";

export function loadHistory(): QueryHistoryItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? (JSON.parse(raw) as QueryHistoryItem[]) : [];
  } catch {
    return [];
  }
}

export function saveQueryToHistory(response: QueryResponse): void {
  const agents = response.results.map((r) => r.agent);
  const item: QueryHistoryItem = {
    id: crypto.randomUUID(),
    query: response.query,
    summary: response.summary,
    agents,
    timestamp: new Date().toISOString(),
    results: response.results,
  };
  const existing = loadHistory();
  localStorage.setItem(
    HISTORY_KEY,
    JSON.stringify([item, ...existing].slice(0, 50))
  );
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event("ayanami-history-updated"));
  }
}
