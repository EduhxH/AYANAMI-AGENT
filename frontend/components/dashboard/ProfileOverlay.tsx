"use client";

import { useEffect, useRef, useState } from "react";
import { Camera, CheckCircle2, AlertCircle, User } from "lucide-react";

import { Overlay } from "@/components/ui/overlay";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getAuthErrorMessage } from "@/context/AuthContext";
import {
  preferencesApi,
  type UserPreferences,
} from "@/lib/preferences";

export function ProfileOverlay({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [prefs, setPrefs] = useState<UserPreferences | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setError("");
    setSuccess("");
    preferencesApi
      .get()
      .then((data) => {
        setPrefs(data);
        setDisplayName(data.display_name);
      })
      .catch((err) => setError(getAuthErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [open]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);
    try {
      const updated = await preferencesApi.update({ display_name: displayName });
      setPrefs(updated);
      setSuccess("Perfil actualizado com sucesso.");
    } catch (err) {
      setError(getAuthErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function uploadFile(file: File) {
    if (!file.type.startsWith("image/")) {
      setError("Ficheiro deve ser uma imagem.");
      return;
    }
    setUploading(true);
    setError("");
    setSuccess("");
    try {
      const updated = await preferencesApi.uploadAvatar(file);
      setPrefs(updated);
      setSuccess("Avatar actualizado.");
    } catch (err) {
      setError(getAuthErrorMessage(err));
    } finally {
      setUploading(false);
    }
  }

  function handleFileInput(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) uploadFile(file);
  }

  const avatarSrc = prefs ? preferencesApi.resolveAvatarUrl(prefs.avatar_url) : "";
  const initials = displayName
    ? displayName.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()
    : "?";

  return (
    <Overlay open={open} onClose={onClose} title="Editar perfil" zIndex={60}>
      {loading ? (
        <div className="flex items-center gap-3 py-8 justify-center text-muted">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          <span className="text-sm">A carregar...</span>
        </div>
      ) : (
        <form onSubmit={handleSave} className="space-y-6">

          {/* Avatar upload zone */}
          <div className="flex flex-col items-center gap-4">
            <div
              className={[
                "group relative h-24 w-24 cursor-pointer rounded-full transition-all duration-300",
                dragOver ? "scale-105 ring-2 ring-accent ring-offset-2 ring-offset-[var(--bg-elevated)]" : "",
              ].join(" ")}
              onClick={() => fileRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
            >
              {/* Avatar image or placeholder */}
              <div className="h-24 w-24 overflow-hidden rounded-full border-2 border-theme bg-[var(--bg-input)]">
                {avatarSrc ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={avatarSrc}
                    alt="Avatar"
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center bg-accent-muted text-xl font-semibold text-accent">
                    {initials}
                  </div>
                )}
              </div>

              {/* Hover overlay */}
              <div className="absolute inset-0 flex items-center justify-center rounded-full bg-black/60 opacity-0 transition-opacity group-hover:opacity-100">
                {uploading ? (
                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                ) : (
                  <Camera className="h-5 w-5 text-white" />
                )}
              </div>
            </div>

            {/* Hidden real input */}
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="sr-only"
              disabled={uploading}
              onChange={handleFileInput}
            />

            {/* Upload hint */}
            <div className="text-center">
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                disabled={uploading}
                className="text-sm font-medium text-accent hover:text-accent-hover transition-colors disabled:opacity-50"
              >
                {uploading ? "A carregar..." : "Alterar foto"}
              </button>
              <p className="mt-0.5 text-xs text-muted">
                PNG, JPG ou GIF · Arrasta ou clica
              </p>
            </div>
          </div>

          {/* Divider */}
          <div className="border-t border-theme" />

          {/* Display name */}
          <div className="space-y-2">
            <Label htmlFor="profile-name" className="text-sm font-medium text-primary flex items-center gap-2">
              <User className="h-3.5 w-3.5 text-muted" />
              Nome de exibição
            </Label>
            <Input
              id="profile-name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="border-theme bg-[var(--bg-input)] text-primary"
              placeholder="Como o agente te trata"
            />
            <p className="text-xs text-muted">
              Este nome aparece nas respostas do agente.
            </p>
          </div>

          {/* Feedback */}
          {success && (
            <div className="flex items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3">
              <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />
              <p className="text-sm text-emerald-400">{success}</p>
            </div>
          )}
          {error && (
            <div className="flex items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3">
              <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          <Button type="submit" disabled={saving} className="w-full">
            {saving ? (
              <span className="flex items-center gap-2">
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
                A guardar...
              </span>
            ) : (
              "Guardar perfil"
            )}
          </Button>
        </form>
      )}
    </Overlay>
  );
}
