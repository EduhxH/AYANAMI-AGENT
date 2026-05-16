"use client";

import { ArrowUp, GitBranch, Mail, Plus, Search } from "lucide-react";
import { BrandLogo } from "@/components/dashboard/BrandLogo";

/** Static frame of the real chat UI — same tokens and components as the dashboard. */
export function ChatScreenshot() {
  return (
    <div className="mx-auto w-full max-w-5xl overflow-hidden rounded-2xl border border-theme bg-main shadow-[0_32px_80px_rgba(0,0,0,0.4)]">
      <div className="flex" style={{ minHeight: "520px" }}>
        {/* Sidebar mock */}
        <aside className="hidden w-[200px] shrink-0 border-r border-theme bg-sidebar p-4 sm:flex sm:flex-col">
          <BrandLogo variant="full" className="mb-6 h-9 w-auto" />
          <p className="text-[11px] font-medium uppercase tracking-wide text-muted">Hoje</p>
          <p className="mt-2 truncate rounded-lg bg-accent-muted px-2 py-1.5 text-xs font-medium text-primary">
            Analisa os PRs abertos...
          </p>
        </aside>

        {/* Main chat area */}
        <main className="relative flex flex-1 flex-col">
          {/* Empty state center */}
          <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 pb-32 pt-10">
            <BrandLogo variant="full" className="h-20 w-auto opacity-90" />
            <p className="text-center text-sm italic text-secondary">
              One prompt to rule them all… while they ride it.
            </p>
            <div className="mt-2 flex flex-wrap justify-center gap-2">
              {[
                { icon: GitBranch, label: "Analisar GitHub" },
                { icon: Mail, label: "Verificar emails" },
                { icon: Search, label: "Pesquisar na web" },
              ].map((c) => (
                <span
                  key={c.label}
                  className="inline-flex items-center gap-1.5 rounded-full border border-theme bg-elevated px-3 py-1.5 text-xs text-secondary"
                >
                  <c.icon className="h-3 w-3" />
                  {c.label}
                </span>
              ))}
            </div>
          </div>

          {/* Assistant reply bubble */}
          <div className="absolute bottom-24 left-6 right-6 mx-auto max-w-lg rounded-2xl border border-theme bg-[var(--bubble-assistant)] p-4 text-left shadow-lg">
            <p className="text-xs leading-relaxed text-primary">
              Encontrei 3 pull requests abertos no repositório principal. O PR
              #42 precisa de revisão urgente — conflitos de merge em{" "}
              <code className="text-accent">api/routes.py</code>. Nos emails, 2
              mensagens marcadas como prioritárias hoje.
            </p>
          </div>

          {/* Input bar */}
          <footer className="border-t border-theme bg-[var(--bg-input)] p-3">
            <div className="mx-auto flex max-w-lg items-center gap-2 rounded-full border border-theme-strong bg-elevated px-3 py-2">
              <Plus className="h-4 w-4 shrink-0 text-muted" />
              <span className="flex-1 text-xs text-muted">O que queres saber?</span>
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-accent text-[var(--bg-main)]">
                <ArrowUp className="h-3.5 w-3.5" />
              </span>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}
