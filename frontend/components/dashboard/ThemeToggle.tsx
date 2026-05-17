"use client";

import { Moon, Sun } from "lucide-react";
import { useCallback, useMemo } from "react";

import { useTheme } from "@/context/ThemeContext";
import { cn } from "@/lib/utils";

function playThemeToggleSound() {
  if (typeof window === "undefined" || !window.AudioContext) return;

  const audioContext = new window.AudioContext();
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();

  oscillator.type = "triangle";
  oscillator.frequency.value = 520;
  gain.gain.value = 0.09;

  oscillator.connect(gain);
  gain.connect(audioContext.destination);

  oscillator.start();
  oscillator.stop(audioContext.currentTime + 0.08);

  gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.08);
  oscillator.onended = () => audioContext.close();
}

export function ThemeToggle({ className }: { className?: string }) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  const icon = useMemo(
    () => (isDark ? <Sun className="h-4 w-4 shrink-0" /> : <Moon className="h-4 w-4 shrink-0" />),
    [isDark]
  );

  const handleClick = useCallback(() => {
    playThemeToggleSound();
    toggleTheme();
  }, [toggleTheme]);

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-label={isDark ? "Ativar tema claro" : "Ativar tema escuro"}
      className={cn(
        "flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-secondary transition-colors hover:bg-[var(--bg-elevated)] hover:text-primary",
        className
      )}
    >
      {icon}
      <span className="truncate">{isDark ? "Claro" : "Escuro"}</span>
    </button>
  );
}
