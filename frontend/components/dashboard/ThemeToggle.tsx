"use client";

import { Moon, Sun } from "lucide-react";

import { useTheme } from "@/context/ThemeContext";
import { cn } from "@/lib/utils";

export function ThemeToggle({ className }: { className?: string }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={theme === "dark" ? "Ativar tema claro" : "Ativar tema escuro"}
      className={cn(
        "flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-secondary transition-colors hover:bg-[var(--bg-elevated)] hover:text-primary",
        className
      )}
    >
      {theme === "dark" ? (
        <Sun className="h-4 w-4 shrink-0" />
      ) : (
        <Moon className="h-4 w-4 shrink-0" />
      )}
      <span className="truncate">{theme === "dark" ? "Claro" : "Escuro"}</span>
    </button>
  );
}
