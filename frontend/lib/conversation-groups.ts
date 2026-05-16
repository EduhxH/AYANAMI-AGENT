import type { Conversation } from "@/lib/conversations";

export interface ConversationGroup {
  label: string;
  items: Conversation[];
}

function isToday(date: Date): boolean {
  const now = new Date();
  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  );
}

export function groupConversationsByDate(
  conversations: Conversation[]
): ConversationGroup[] {
  const sorted = [...conversations].sort(
    (a, b) =>
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );

  const today: Conversation[] = [];
  const previous: Conversation[] = [];

  for (const c of sorted) {
    if (isToday(new Date(c.updatedAt))) today.push(c);
    else previous.push(c);
  }

  const groups: ConversationGroup[] = [];
  if (today.length) groups.push({ label: "Hoje", items: today });
  if (previous.length) groups.push({ label: "Anteriormente", items: previous });
  return groups;
}
