"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getAuthErrorMessage } from "@/context/AuthContext";
import { api } from "@/lib/api";
import type { AnimeRecommendation, AnimeSuggestResponse } from "@/lib/types";

function extractRecommendations(data: {
  recommendation?: { recommendations: AnimeRecommendation[] };
  recommendations?: AnimeRecommendation[];
}): AnimeRecommendation[] {
  if (data.recommendations?.length) return data.recommendations;
  return data.recommendation?.recommendations ?? [];
}

export function AnimePanel({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [loading, setLoading] = useState(false);
  const [recs, setRecs] = useState<AnimeRecommendation[]>([]);
  const [title, setTitle] = useState("");
  const [reason, setReason] = useState("");
  const [critique, setCritique] = useState<AnimeSuggestResponse | null>(null);
  const [error, setError] = useState("");

  async function loadRecommendations() {
    setError("");
    setLoading(true);
    try {
      const data = await api.animeRecommend();
      setRecs(extractRecommendations(data));
    } catch (err) {
      setError(getAuthErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function submitSuggestion(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.animeSuggest(title, reason);
      setCritique(res);
    } catch (err) {
      setError(getAuthErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-40 bg-[var(--overlay)]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.aside
            className="fixed bottom-0 right-0 top-0 z-50 flex w-full max-w-md flex-col border-l border-theme bg-elevated p-6 text-primary shadow-[var(--shadow-soft)] md:top-0"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 28, stiffness: 280 }}
          >
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-accent" />
                <h2 className="text-lg font-semibold">Modo Anime</h2>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="rounded-full p-2 hover:bg-white/10"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <Button
              type="button"
              variant="secondary"
              className="mb-4 border-accent/40 text-accent"
              disabled={loading}
              onClick={loadRecommendations}
            >
              {loading ? "A carregar..." : "Obter recomendações"}
            </Button>

            <div className="flex-1 space-y-4 overflow-y-auto">
              {recs.map((r) => (
                <div
                  key={r.title}
                  className="rounded-xl border border-theme bg-accent-muted p-4"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold">{r.title}</h3>
                    <span className="text-sm text-accent">
                      ★ {r.rating}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-secondary">{r.reason}</p>
                  <p className="mt-2 text-xs text-muted">
                    {r.technical_parallel}
                  </p>
                </div>
              ))}

              <form onSubmit={submitSuggestion} className="space-y-3 border-t border-white/10 pt-4">
                <p className="text-sm font-medium text-accent">
                  Sugere um anime
                </p>
                <div className="space-y-2">
                  <Label htmlFor="anime-title" className="text-primary">
                    Título
                  </Label>
                  <Input
                    id="anime-title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="border-theme bg-[var(--bg-input)] text-primary"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="anime-reason" className="text-white/80">
                    Porquê?
                  </Label>
                  <Input
                    id="anime-reason"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    className="border-theme bg-[var(--bg-input)] text-primary"
                    required
                  />
                </div>
                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full"
                >
                  Enviar sugestão
                </Button>
              </form>

              {critique && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-xl border border-theme bg-[var(--bg-input)] p-4"
                >
                  <p className="text-xs text-accent">
                    {critique.approved ? "Aprovado" : "Rejeitado"} · Score{" "}
                    {critique.score}
                  </p>
                  <p className="mt-2 text-sm leading-relaxed">{critique.critique}</p>
                </motion.div>
              )}

              {error && (
                <p className="text-sm text-red-300">{error}</p>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
