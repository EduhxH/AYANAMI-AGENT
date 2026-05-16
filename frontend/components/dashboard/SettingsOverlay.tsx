"use client";

import { useEffect, useState } from "react";
import { GitBranch, Mail, UserRound, CheckCircle2, AlertCircle } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";

import { Overlay } from "@/components/ui/overlay";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { getAuthErrorMessage, useAuth } from "@/context/AuthContext";
import { useDashboardUI } from "@/context/DashboardUIContext";
import { api } from "@/lib/api";
import { preferencesApi } from "@/lib/preferences";

const sectionVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.07, duration: 0.45, ease: [0.16, 1, 0.3, 1] },
  }),
};

export function SettingsOverlay() {
  const { settingsOpen, closeSettings, openProfile } = useDashboardUI();
  const { user, refreshUser } = useAuth();
  const searchParams = useSearchParams();

  const [instructions, setInstructions] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loadingGithub, setLoadingGithub] = useState(false);
  const [loadingGoogle, setLoadingGoogle] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!settingsOpen) return;
    setLoading(true);
    preferencesApi
      .get()
      .then((p) => {
        setInstructions(p.agent_instructions);
        setDisplayName(p.display_name);
      })
      .catch((err) => setError(getAuthErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [settingsOpen]);

  useEffect(() => {
    const status = searchParams.get("status");
    const oauth = searchParams.get("oauth");
    const message = searchParams.get("message");
    if (status === "success" && oauth) {
      setSuccess(
        oauth === "google"
          ? "Gmail ligado com sucesso!"
          : "GitHub ligado com sucesso!"
      );
      refreshUser();
    } else if (status === "error") {
      setError(message ?? "Falha ao ligar conta.");
    }
  }, [searchParams, refreshUser]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      await preferencesApi.update({
        agent_instructions: instructions,
        display_name: displayName,
      });
      setSuccess("Definições guardadas.");
    } catch (err) {
      setError(getAuthErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function connectGithub() {
    setLoadingGithub(true);
    try {
      const { url } = await api.getGithubAuthUrl();
      window.location.href = url;
    } catch (err) {
      setError(getAuthErrorMessage(err));
      setLoadingGithub(false);
    }
  }

  async function connectGoogle() {
    setLoadingGoogle(true);
    try {
      const { url } = await api.getGoogleAuthUrl();
      window.location.href = url;
    } catch (err) {
      setError(getAuthErrorMessage(err));
      setLoadingGoogle(false);
    }
  }

  return (
    <Overlay open={settingsOpen} onClose={closeSettings} title="Definições" zIndex={55}>
      {loading ? (
        <div className="flex items-center gap-3 py-8 justify-center text-muted">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          <span className="text-sm">A carregar...</span>
        </div>
      ) : (
        <form onSubmit={handleSave} className="space-y-8">

          {/* Section: Conta */}
          <motion.section
            className="space-y-3"
            custom={0}
            initial="hidden"
            animate="visible"
            variants={sectionVariants}
          >
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">
              Conta
            </h3>
            <button
              type="button"
              onClick={openProfile}
              className="flex w-full items-center gap-3 rounded-xl border border-theme bg-[var(--bg-input)] p-3 text-left transition-all hover:border-accent/40 hover:bg-accent-muted/30"
            >
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent-muted text-sm font-medium text-accent">
                <UserRound className="h-4 w-4" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-medium text-primary">
                  {displayName || user?.email?.split("@")[0] || "Perfil"}
                </span>
                <span className="block truncate text-xs text-muted">
                  {user?.email}
                </span>
              </span>
              <span className="text-xs font-medium text-accent">Editar →</span>
            </button>
          </motion.section>

          {/* Section: Agent instructions */}
          <motion.section
            className="space-y-2"
            custom={1}
            initial="hidden"
            animate="visible"
            variants={sectionVariants}
          >
            <Label htmlFor="agent-instructions" className="text-primary">
              Instruções do agente
            </Label>
            <textarea
              id="agent-instructions"
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              rows={4}
              className="w-full rounded-xl border border-theme bg-[var(--bg-input)] px-4 py-3 text-sm text-primary placeholder:text-muted focus:outline-none focus:ring-1 focus:ring-accent transition-colors resize-none"
              placeholder="Ex: Responde sempre em português."
            />
            <p className="text-xs text-muted">
              O agente segue estas instruções em todas as conversas.
            </p>
          </motion.section>

          {/* Section: Connections */}
          <motion.section
            className="space-y-3"
            custom={2}
            initial="hidden"
            animate="visible"
            variants={sectionVariants}
          >
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">
              Ligações
            </h3>
            <ConnectionRow
              icon={GitBranch}
              label="GitHub"
              connected={!!user?.has_github}
              detail={
                user?.has_github
                  ? user.github_username
                    ? `@${user.github_username}`
                    : "Ligado"
                  : "Não ligado"
              }
              loading={loadingGithub}
              onConnect={connectGithub}
            />
            <ConnectionRow
              icon={Mail}
              label="Gmail"
              connected={!!user?.has_google}
              detail={user?.has_google ? "Ligado" : "Não ligado"}
              loading={loadingGoogle}
              onConnect={connectGoogle}
            />
          </motion.section>

          {/* Feedback */}
          {success && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3"
            >
              <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />
              <p className="text-sm text-emerald-400">{success}</p>
            </motion.div>
          )}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3"
            >
              <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
              <p className="text-sm text-red-400">{error}</p>
            </motion.div>
          )}

          <motion.div
            custom={3}
            initial="hidden"
            animate="visible"
            variants={sectionVariants}
          >
            <Button type="submit" disabled={saving} className="w-full">
              {saving ? (
                <span className="flex items-center gap-2">
                  <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  A guardar...
                </span>
              ) : (
                "Guardar definições"
              )}
            </Button>
          </motion.div>
        </form>
      )}
    </Overlay>
  );
}

function ConnectionRow({
  icon: Icon,
  label,
  connected,
  detail,
  loading,
  onConnect,
}: {
  icon: typeof GitBranch;
  label: string;
  connected: boolean;
  detail: string;
  loading: boolean;
  onConnect: () => void;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-theme bg-[var(--bg-input)] px-4 py-3 transition-colors hover:border-theme-strong">
      <div className="flex items-center gap-3">
        <span
          className={[
            "flex h-8 w-8 items-center justify-center rounded-lg",
            connected ? "bg-accent-muted text-accent" : "bg-[var(--bg-elevated)] text-muted",
          ].join(" ")}
        >
          <Icon className="h-4 w-4" />
        </span>
        <div>
          <p className="text-sm font-medium text-primary">{label}</p>
          <p className={["text-xs", connected ? "text-accent" : "text-muted"].join(" ")}>
            {detail}
          </p>
        </div>
      </div>
      <Button
        type="button"
        size="sm"
        variant={connected ? "secondary" : "default"}
        disabled={connected || loading}
        onClick={onConnect}
        className="shrink-0"
      >
        {loading ? (
          <span className="flex items-center gap-1.5">
            <span className="h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" />
          </span>
        ) : connected ? (
          "Ligado ✓"
        ) : (
          "Ligar"
        )}
      </Button>
    </div>
  );
}
