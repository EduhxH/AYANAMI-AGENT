"use client";

import { useMemo, useState, useEffect } from "react";
import {
  ChevronLeft,
  ChevronRight,
  LogOut,
  MessageSquare,
  MessageSquarePlus,
  Search,
  Settings,
  Trash2,
} from "lucide-react";

import { BrandLogo } from "@/components/dashboard/BrandLogo";
import { EasterEggButton } from "@/components/dashboard/EasterEggButton";
import { ThemeToggle } from "@/components/dashboard/ThemeToggle";
import { useAuth } from "@/context/AuthContext";
import { useChat } from "@/context/ChatContext";
import { useDashboardUI } from "@/context/DashboardUIContext";
import { groupConversationsByDate } from "@/lib/conversation-groups";
import { preferencesApi } from "@/lib/preferences";
import { cn } from "@/lib/utils";

export function Sidebar({
  onEasterEgg,
}: {
  onEasterEgg: () => void;
}) {
  const { user, logout } = useAuth();
  const {
    conversations,
    activeConversationId,
    newChat,
    selectConversation,
    deleteConversation,
  } = useChat();
  const { sidebarCollapsed, toggleSidebar, openSettings } = useDashboardUI();
  const [avatarUrl, setAvatarUrl] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    preferencesApi
      .get()
      .then((p) => setAvatarUrl(preferencesApi.resolveAvatarUrl(p.avatar_url)))
      .catch(() => setAvatarUrl(""));
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return conversations;
    return conversations.filter((c) => c.title.toLowerCase().includes(q));
  }, [conversations, search]);

  const groups = useMemo(
    () => groupConversationsByDate(filtered),
    [filtered]
  );

  const w = sidebarCollapsed ? "md:w-[60px]" : "md:w-[280px]";

  return (
    <aside
      className={cn(
        "flex h-screen shrink-0 flex-col border-r border-theme bg-sidebar transition-[width] duration-200 overflow-hidden",
        "w-full md:sticky md:top-0",
        w
      )}
    >
      {/* Header */}
      <div className={cn(
        "flex items-center border-b border-theme px-3 py-3",
        sidebarCollapsed ? "justify-center" : "justify-between gap-2"
      )}>
        {!sidebarCollapsed && (
          <BrandLogo variant="full" className="h-10 w-auto shrink-0" priority />
        )}
        {/* Toggle button — always visible, never overflows */}
        <button
          type="button"
          onClick={toggleSidebar}
          aria-label={sidebarCollapsed ? "Expandir barra" : "Recolher barra"}
          className="hidden shrink-0 rounded-lg p-2 text-secondary hover:bg-[var(--bg-elevated)] hover:text-primary md:inline-flex"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      </div>

      <nav className="flex flex-col gap-0.5 px-2 pt-2">
        <SidebarItem
          icon={MessageSquarePlus}
          label="Novo chat"
          collapsed={sidebarCollapsed}
          onClick={newChat}
        />
        {!sidebarCollapsed && (
          <div className="relative px-1 py-1">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Pesquisar chats..."
              className="w-full rounded-lg border border-theme bg-[var(--bg-input)] py-2 pl-9 pr-3 text-xs text-primary placeholder:text-muted focus:outline-none focus:ring-1 focus:ring-accent"
            />
          </div>
        )}
      </nav>

      {!sidebarCollapsed && (
        <div className="mt-3 flex-1 overflow-y-auto px-2 pb-2">
          {groups.length === 0 ? (
            <p className="px-3 py-2 text-xs text-muted">Sem conversas ainda</p>
          ) : (
            groups.map((group) => (
              <div key={group.label} className="mb-4">
                <p className="px-3 py-1 text-[11px] font-medium uppercase tracking-wide text-muted">
                  {group.label}
                </p>
                <ul className="space-y-0.5">
                  {group.items.map((conv) => {
                    const active = conv.id === activeConversationId;
                    return (
                      <li key={conv.id} className="group relative">
                        <button
                          type="button"
                          onClick={() => selectConversation(conv.id)}
                          className={cn(
                            "flex w-full items-start gap-2 rounded-lg px-3 py-2.5 text-left transition-colors",
                            active
                              ? "bg-accent-muted text-primary"
                              : "text-secondary hover:bg-[var(--bg-elevated)] hover:text-primary"
                          )}
                        >
                          <MessageSquare
                            className={cn(
                              "mt-0.5 h-4 w-4 shrink-0",
                              active ? "text-accent" : "text-muted"
                            )}
                          />
                          <span className="min-w-0 flex-1">
                            <span className="block truncate text-sm font-medium">
                              {conv.title}
                            </span>
                            {conv.messages.length > 0 && (
                              <span className="mt-0.5 block truncate text-[11px] text-muted">
                                {conv.messages[conv.messages.length - 1].content}
                              </span>
                            )}
                          </span>
                        </button>
                        {conversations.length > 1 && (
                          <button
                            type="button"
                            aria-label="Apagar conversa"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteConversation(conv.id);
                            }}
                            className="absolute right-2 top-1/2 hidden -translate-y-1/2 rounded p-1 text-muted hover:bg-red-500/10 hover:text-red-400 group-hover:block"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))
          )}
        </div>
      )}

      {/* Footer */}
      <div className="mt-auto space-y-1 border-t border-theme p-2">
        <EasterEggButton collapsed={sidebarCollapsed} onActivate={onEasterEgg} />
        <ThemeToggle
          className={cn("w-full", sidebarCollapsed && "justify-center px-2")}
        />
        <SidebarItem
          icon={Settings}
          label="Definições"
          collapsed={sidebarCollapsed}
          onClick={openSettings}
        />
        <button
          type="button"
          onClick={openSettings}
          className={cn(
            "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left transition-colors hover:bg-[var(--bg-elevated)]",
            sidebarCollapsed && "justify-center px-2"
          )}
        >
          {avatarUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={avatarUrl}
              alt=""
              className="h-8 w-8 shrink-0 rounded-full object-cover"
            />
          ) : (
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent-muted text-xs font-medium text-accent">
              {user?.email?.[0]?.toUpperCase() ?? "A"}
            </span>
          )}
          {!sidebarCollapsed && (
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-medium text-primary">
                {user?.email?.split("@")[0]}
              </span>
              <span className="block truncate text-xs text-muted">
                {user?.email}
              </span>
            </span>
          )}
        </button>
        <SidebarItem
          icon={LogOut}
          label="Sair"
          collapsed={sidebarCollapsed}
          onClick={() => {
            logout();
            window.location.href = "/auth/login";
          }}
          className="text-muted hover:text-red-400"
        />
      </div>
    </aside>
  );
}

function SidebarItem({
  icon: Icon,
  label,
  collapsed,
  onClick,
  className,
}: {
  icon: typeof Search;
  label: string;
  collapsed: boolean;
  onClick: () => void;
  className?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={collapsed ? label : undefined}
      className={cn(
        "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-secondary transition-colors hover:bg-[var(--bg-elevated)] hover:text-primary",
        collapsed && "justify-center px-2",
        className
      )}
    >
      <Icon className="h-4 w-4 shrink-0" />
      {!collapsed && <span className="flex-1 text-left">{label}</span>}
    </button>
  );
}
