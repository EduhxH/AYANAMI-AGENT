import { loadHistory } from "./history";
import type { QueryHistoryItem } from "./types";

export interface HistoryGroup {
  label: string;
  items: QueryHistoryItem[];
}

function isToday(date: Date): boolean {
  const now = new Date();
  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  );
}

export function groupHistoryByDate(): HistoryGroup[] {
  const items = loadHistory();
  const today: QueryHistoryItem[] = [];
  const previous: QueryHistoryItem[] = [];

  for (const item of items) {
    const d = new Date(item.timestamp);
    if (isToday(d)) today.push(item);
    else previous.push(item);
  }

  const groups: HistoryGroup[] = [];
  if (today.length) groups.push({ label: "Hoje", items: today });
  if (previous.length) groups.push({ label: "Anteriormente", items: previous });
  return groups;
}
