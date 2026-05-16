"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  createEmptyConversation,
  getActiveConversationId,
  loadConversations,
  saveConversations,
  setActiveConversationId,
  titleFromMessages,
  type Conversation,
} from "@/lib/conversations";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface ChatContextValue {
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: ChatMessage[];
  activeConversation: Conversation | null;
  addMessage: (msg: Omit<ChatMessage, "id" | "timestamp">) => ChatMessage;
  newChat: () => void;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveId] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const loaded = loadConversations();
    let activeId = getActiveConversationId();
    if (loaded.length && (!activeId || !loaded.some((c) => c.id === activeId))) {
      activeId = loaded[0].id;
    }
    if (!loaded.length) {
      const fresh = createEmptyConversation();
      loaded.push(fresh);
      activeId = fresh.id;
    }
    setConversations(loaded);
    setActiveId(activeId);
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated) {
      saveConversations(conversations);
      setActiveConversationId(activeConversationId);
    }
  }, [conversations, activeConversationId, hydrated]);

  const activeConversation = useMemo(
    () => conversations.find((c) => c.id === activeConversationId) ?? null,
    [conversations, activeConversationId]
  );

  const messages = activeConversation?.messages ?? [];

  const updateConversation = useCallback(
    (id: string, updater: (c: Conversation) => Conversation) => {
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? updater(c) : c))
      );
    },
    []
  );

  const addMessage = useCallback(
    (msg: Omit<ChatMessage, "id" | "timestamp">) => {
      const entry: ChatMessage = {
        ...msg,
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
      };

      setConversations((prev) => {
        let convId = activeConversationId;
        let list = [...prev];

        if (!convId || !list.some((c) => c.id === convId)) {
          const fresh = createEmptyConversation();
          list = [fresh, ...list];
          convId = fresh.id;
          setActiveId(convId);
        }

        return list.map((c) => {
          if (c.id !== convId) return c;
          const messages = [...c.messages, entry];
          return {
            ...c,
            messages,
            title:
              c.title === "Novo chat" && msg.role === "user"
                ? titleFromMessages(messages)
                : c.title,
            updatedAt: entry.timestamp,
          };
        });
      });

      return entry;
    },
    [activeConversationId]
  );

  const newChat = useCallback(() => {
    const fresh = createEmptyConversation();
    setConversations((prev) => [fresh, ...prev]);
    setActiveId(fresh.id);
  }, []);

  const selectConversation = useCallback((id: string) => {
    setActiveId(id);
  }, []);

  const deleteConversation = useCallback(
    (id: string) => {
      setConversations((prev) => {
        const next = prev.filter((c) => c.id !== id);
        const list = next.length ? next : [createEmptyConversation()];
        if (activeConversationId === id) {
          setActiveId(list[0].id);
        }
        return list;
      });
    },
    [activeConversationId]
  );

  const value = useMemo(
    () => ({
      conversations,
      activeConversationId,
      messages,
      activeConversation,
      addMessage,
      newChat,
      selectConversation,
      deleteConversation,
    }),
    [
      conversations,
      activeConversationId,
      messages,
      activeConversation,
      addMessage,
      newChat,
      selectConversation,
      deleteConversation,
    ]
  );

  return (
    <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
  );
}

export function useChat() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChat must be used within ChatProvider");
  return ctx;
}
