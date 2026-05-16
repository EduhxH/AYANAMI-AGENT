import type { ChatMessage } from "@/context/ChatContext";

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

const CONVERSATIONS_KEY = "ayanami_conversations";
const ACTIVE_KEY = "ayanami_active_conversation";
const LEGACY_MESSAGES_KEY = "ayanami_chat_messages";

export function loadConversations(): Conversation[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(CONVERSATIONS_KEY);
    if (raw) return JSON.parse(raw) as Conversation[];

    const legacy = localStorage.getItem(LEGACY_MESSAGES_KEY);
    if (legacy) {
      const messages = JSON.parse(legacy) as ChatMessage[];
      if (messages.length) {
        const conv: Conversation = {
          id: crypto.randomUUID(),
          title: titleFromMessages(messages),
          messages,
          createdAt: messages[0]?.timestamp ?? new Date().toISOString(),
          updatedAt:
            messages[messages.length - 1]?.timestamp ??
            new Date().toISOString(),
        };
        saveConversations([conv]);
        setActiveConversationId(conv.id);
        localStorage.removeItem(LEGACY_MESSAGES_KEY);
        return [conv];
      }
    }
    return [];
  } catch {
    return [];
  }
}

export function saveConversations(conversations: Conversation[]): void {
  try {
    localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));
  } catch {
    /* ignore */
  }
}

export function getActiveConversationId(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(ACTIVE_KEY);
  } catch {
    return null;
  }
}

export function setActiveConversationId(id: string | null): void {
  try {
    if (id) localStorage.setItem(ACTIVE_KEY, id);
    else localStorage.removeItem(ACTIVE_KEY);
  } catch {
    /* ignore */
  }
}

export function titleFromMessages(messages: ChatMessage[]): string {
  const firstUser = messages.find((m) => m.role === "user");
  if (!firstUser) return "Novo chat";
  const t = firstUser.content.trim();
  return t.length > 42 ? `${t.slice(0, 42)}…` : t;
}

export function createEmptyConversation(): Conversation {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    title: "Novo chat",
    messages: [],
    createdAt: now,
    updatedAt: now,
  };
}
