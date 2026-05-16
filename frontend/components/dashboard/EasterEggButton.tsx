"use client";

import { Sparkles } from "lucide-react";

import { cn } from "@/lib/utils";

export function EasterEggButton({
  onActivate,
  collapsed,
}: {
  onActivate: () => void;
  collapsed?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onActivate}
      aria-label="Modo Anime — easter egg"
      className={cn(
        "group flex w-full items-center gap-2 rounded-lg border border-accent/30 bg-accent-muted px-3 py-2.5 text-sm transition-all animate-egg-glow hover:border-accent/50",
        collapsed && "justify-center px-2"
      )}
    >
      <Sparkles className="h-4 w-4 shrink-0 text-accent" />
      {!collapsed && (
        <span className="font-medium text-accent">Modo Anime</span>
      )}
    </button>
  );
}
