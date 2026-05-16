"use client";

import { useEffect } from "react";
import { X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

export function Overlay({
  open,
  onClose,
  title,
  children,
  className,
  zIndex = 50,
}: {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  className?: string;
  zIndex?: number;
}) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  // Render nothing when closed (AnimatePresence handles exit)
  return (
    <AnimatePresence>
      {open && (
        // Full-screen fixed wrapper — flex centers the panel
        <div
          className="fixed inset-0 flex items-center justify-center p-4"
          style={{ zIndex }}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-[var(--overlay)]"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.22 }}
          />

          {/* Dialog panel — centered by flexbox, no translate */}
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? "overlay-title" : undefined}
            className={cn(
              "relative z-10 flex max-h-[min(90vh,800px)] w-full max-w-[560px] flex-col rounded-2xl border border-theme bg-elevated shadow-2xl overflow-hidden",
              className
            )}
            onClick={(e) => e.stopPropagation()}
            initial={{ opacity: 0, y: 32, scale: 0.96, filter: "blur(4px)" }}
            animate={{ opacity: 1, y: 0,  scale: 1,    filter: "blur(0px)" }}
            exit={{   opacity: 0, y: 20,  scale: 0.97, filter: "blur(2px)" }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            {title && (
              <header className="flex shrink-0 items-center justify-between border-b border-theme bg-elevated px-6 py-4">
                <h2 id="overlay-title" className="text-lg font-semibold text-primary">
                  {title}
                </h2>
                <button
                  type="button"
                  onClick={onClose}
                  aria-label="Fechar painel"
                  className="rounded-lg p-2 text-secondary transition-colors hover:bg-[var(--bg-input)] hover:text-primary"
                >
                  <X className="h-4 w-4" />
                </button>
              </header>
            )}
            <div className="overflow-y-auto px-6 py-5">{children}</div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
