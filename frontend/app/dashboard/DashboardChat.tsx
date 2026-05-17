"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { ArrowUp, GitBranch, Mail, Plus, Search } from "lucide-react";
import { motion } from "framer-motion";

import { BrandLogo } from "@/components/dashboard/BrandLogo";
import { useChat } from "@/context/ChatContext";
import { useDashboardUI } from "@/context/DashboardUIContext";
import { getAuthErrorMessage } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { saveQueryToHistory } from "@/lib/history";
import { preferencesApi } from "@/lib/preferences";
import { cn } from "@/lib/utils";
import { Reveal } from "@/components/motion/Reveal";

const SUGGESTIONS = [
  {
    label: "Analisar GitHub",
    icon: GitBranch,
    query: "Analisa os meus repositórios GitHub e resume o estado actual.",
  },
  {
    label: "Verificar emails",
    icon: Mail,
    query: "Resume os emails mais urgentes de hoje na minha caixa de entrada.",
  },
  {
    label: "Pesquisar na web",
    icon: Search,
    query: "Pesquisa na web as últimas novidades sobre agentes de IA.",
  },
];

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString("pt-PT", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function DashboardChat() {
  const { messages, addMessage, activeConversation } = useChat();
  const { openSettings } = useDashboardUI();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [pendingFile, setPendingFile] = useState<{
    name: string;
    content: string;
    preview: string;
    fileCount: number;
  } | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    preferencesApi
      .get()
      .then((p) => {
        setAvatarUrl(preferencesApi.resolveAvatarUrl(p.avatar_url));
        setDisplayName(p.display_name || "");
      })
      .catch(() => {
        setAvatarUrl("");
        setDisplayName("");
      });
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, activeConversation?.id]);

  async function submit(text: string) {
    const trimmed = text.trim();
    if ((!trimmed && !pendingFile) || loading) return;
    setError("");
    setQuery("");
    setLoading(true);
    document.body.classList.add("waiting");

    const userMessage = pendingFile
      ? `Ficheiro anexado: ${pendingFile.name}${trimmed ? ` — ${trimmed}` : ""}`
      : trimmed;

    const backendQuery = pendingFile
      ? `Ficheiro: ${pendingFile.name}\nConteúdo:\n${pendingFile.content}\n\n${trimmed ||
          "Resume o conteúdo do ficheiro em poucas frases."}`
      : trimmed;

    addMessage({ role: "user", content: userMessage });

    try {
      const res = await api.query(backendQuery);
      addMessage({
        role: "assistant",
        content: res.summary || "Sem resposta.",
      });
      saveQueryToHistory(res);
      window.dispatchEvent(new Event("ayanami-history-updated"));
      setPendingFile(null);
    } catch (err) {
      setError(getAuthErrorMessage(err));
    } finally {
      setLoading(false);
      document.body.classList.remove("waiting");
    }
  }

  const hasMessages = messages.length > 0;
  const chatTitle = activeConversation?.title ?? "Novo chat";

  return (
    <div className="flex h-screen min-w-0 flex-1 flex-col bg-main">
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="flex shrink-0 items-center justify-between border-b border-theme px-4 py-3 md:px-6"
      >
        <div className="min-w-0">
          <h1 className="truncate text-sm font-semibold text-primary md:text-base">
            {chatTitle}
          </h1>
          <p className="text-xs text-muted">
            {hasMessages
              ? `${messages.length} mensagem${messages.length === 1 ? "" : "s"}`
              : "Nova conversa"}
          </p>
        </div>
        <button
          type="button"
          onClick={openSettings}
          className="shrink-0 rounded-full ring-1 ring-[var(--border)] transition-opacity hover:opacity-80"
          aria-label="Abrir definições"
        >
          {avatarUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={avatarUrl}
              alt=""
              className="h-9 w-9 rounded-full object-cover"
            />
          ) : (
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-accent-muted text-sm font-medium text-accent">
              {displayName?.[0]?.toUpperCase() ?? "A"}
            </span>
          )}
        </button>
      </motion.header>

      <div
        ref={scrollRef}
        className={cn(
          "flex flex-1 flex-col overflow-y-auto overscroll-contain px-4 py-4 md:px-8",
          !hasMessages && "justify-center"
        )}
      >
        {!hasMessages ? (
          <EmptyState onSuggestion={submit} />
        ) : (
          <div className="mx-auto flex w-full max-w-2xl flex-col gap-1 pb-4">
            {messages.map((msg, index) => {
              const isUser = msg.role === "user";
              const prev = messages[index - 1];
              const showTime =
                !prev ||
                new Date(msg.timestamp).getTime() -
                  new Date(prev.timestamp).getTime() >
                  5 * 60 * 1000;

              return (
                <div key={msg.id}>
                  {showTime && (
                    <p className="my-4 text-center text-[10px] uppercase tracking-wider text-muted">
                      {formatTime(msg.timestamp)}
                    </p>
                  )}
                  <div
                    className={cn(
                      "mb-2 flex gap-2",
                      isUser ? "flex-row-reverse" : "flex-row"
                    )}
                  >
                    {!isUser ? (
                      <Image
                        src="/brand/logo-icon.png"
                        alt=""
                        width={28}
                        height={28}
                        className="mt-1 h-7 w-7 shrink-0 object-contain"
                      />
                    ) : avatarUrl ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={avatarUrl}
                        alt=""
                        className="mt-1 h-7 w-7 shrink-0 rounded-full object-cover"
                      />
                    ) : (
                      <span className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-muted text-[10px] font-medium text-accent">
                        {displayName?.[0]?.toUpperCase() ?? "Tu"}
                      </span>
                    )}
                    <div
                      className={cn(
                        "max-w-[min(85%,420px)] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-[var(--shadow-soft)]",
                        isUser
                          ? "rounded-br-md bg-[var(--bubble-user)] text-primary border border-[var(--bubble-user-border)]"
                          : "rounded-bl-md border border-theme bg-[var(--bubble-assistant)] text-primary"
                      )}
                    >
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                      <p
                        className={cn(
                          "mt-1 text-[10px]",
                          isUser ? "text-right text-muted" : "text-muted"
                        )}
                      >
                        {formatTime(msg.timestamp)}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
            {loading && (
              <div className="mb-2 flex gap-2">
                <Image
                  src="/brand/logo-icon.png"
                  alt=""
                  width={28}
                  height={28}
                  className="h-7 w-7 object-contain"
                />
                <div className="rounded-2xl rounded-bl-md border border-theme bg-[var(--bubble-assistant)] px-4 py-3">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-accent [animation-delay:0ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-accent [animation-delay:150ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-accent [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} className="h-1 shrink-0" />
          </div>
        )}

        {error && (
          <p className="mx-auto mt-4 max-w-2xl rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {error}
          </p>
        )}
      </div>

      <motion.footer
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="shrink-0 border-t border-theme bg-main px-4 py-4 md:px-8"
      >
        {pendingFile && (
          <div className="mx-auto mb-4 max-w-2xl rounded-2xl border border-theme bg-[#111a23] px-4 py-3 text-sm text-primary">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-semibold">Ficheiro anexado: {pendingFile.name}</p>
                <p className="text-xs text-muted">
                  {pendingFile.fileCount > 1
                    ? `${pendingFile.fileCount} ficheiros extraídos`
                    : "Ficheiro pronto para análise."}
                </p>
              </div>
              <button
                type="button"
                className="self-start rounded-full border border-theme px-3 py-1 text-xs text-accent transition hover:bg-accent-muted hover:text-accent"
                onClick={() => setPendingFile(null)}
              >
                Remover
              </button>
            </div>
            <p className="mt-3 max-h-28 overflow-hidden whitespace-pre-wrap text-[13px] text-muted">
              {pendingFile.preview}
            </p>
          </div>
        )}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submit(query);
          }}
          className="mx-auto max-w-2xl"
        >
          <div className="flex items-end gap-2 rounded-2xl border border-theme-strong bg-[var(--bg-input)] px-2 py-2">
            <button
              type="button"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-muted transition-colors hover:bg-accent-muted hover:text-accent"
              aria-label="Anexar"
              onClick={() => fileRef.current?.click()}
            >
              <Plus className="h-5 w-5" />
            </button>
            <input
              ref={fileRef}
              type="file"
              className="sr-only"
              onChange={async (e) => {
                const f = e.target.files?.[0];
                if (!f) return;
                try {
                  setLoading(true);
                  setError("");
                  const res = await api.uploadFile(f as File);
                  const files = res.files || [];
                  const content = files
                    .map((ff: any) => `${ff.name}\n\n${ff.content}`)
                    .join("\n\n---\n\n");
                  const preview = files
                    .slice(0, 3)
                    .map((ff: any) => `${ff.name}: ${ff.content.slice(0, 180)}`)
                    .join("\n\n");

                  setPendingFile({
                    name: f.name,
                    content: content.slice(0, 4000),
                    preview:
                      files.length > 1
                        ? `${files.length} ficheiros processados. ${preview}`
                        : preview,
                    fileCount: files.length,
                  });
                } catch (err) {
                  setError(getAuthErrorMessage(err));
                } finally {
                  setLoading(false);
                  if (fileRef.current) fileRef.current.value = "";
                }
              }}
            />
            <textarea
              id="chat-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit(query);
                }
              }}
              rows={1}
              placeholder={pendingFile ? "Escreve uma pergunta ou envia para resumir o ficheiro anexado..." : "Escreve uma mensagem..."}
              className="max-h-32 min-h-[44px] flex-1 resize-none bg-transparent py-2.5 text-sm text-primary placeholder:text-muted focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading || (!query.trim() && !pendingFile)}
              aria-label="Enviar"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent text-[#0a1218] transition-opacity disabled:opacity-40"
            >
              <ArrowUp className="h-5 w-5" />
            </button>
          </div>
        </form>
      </motion.footer>
    </div>
  );
}

function EmptyState({ onSuggestion }: { onSuggestion: (q: string) => void }) {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center text-center">
      <Reveal>
        <BrandLogo variant="full" className="h-24 w-auto" priority />
      </Reveal>
      <Reveal delay={0.1}>
        <p className="mt-5 text-sm italic text-secondary">
          One prompt to rule them all… while they ride it.
        </p>
      </Reveal>
      <Reveal delay={0.2} className="mt-8 flex flex-wrap justify-center gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s.label}
            type="button"
            onClick={() => onSuggestion(s.query)}
            className="inline-flex items-center gap-2 rounded-pill border border-theme bg-elevated px-4 py-2 text-sm text-secondary transition-colors hover:border-accent hover:text-accent"
          >
            <s.icon className="h-3.5 w-3.5" />
            {s.label}
          </button>
        ))}
      </Reveal>
    </div>
  );
}
