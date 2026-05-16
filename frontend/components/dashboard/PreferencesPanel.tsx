"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getAuthErrorMessage } from "@/context/AuthContext";
import {
  preferencesApi,
  type UserPreferences,
} from "@/lib/preferences";

export function PreferencesPanel() {
  const [prefs, setPrefs] = useState<UserPreferences | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [instructions, setInstructions] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data = await preferencesApi.get();
        setPrefs(data);
        setDisplayName(data.display_name);
        setInstructions(data.agent_instructions);
        setAvatarUrl(data.avatar_url);
      } catch (err) {
        setError(getAuthErrorMessage(err));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);
    try {
      const updated = await preferencesApi.update({
        display_name: displayName,
        agent_instructions: instructions,
        avatar_url: avatarUrl.trim() || undefined,
      });
      setPrefs(updated);
      setSuccess("Preferências guardadas.");
    } catch (err) {
      setError(getAuthErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleAvatarChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");
    setSuccess("");
    setUploading(true);
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

  if (loading) {
    return <p className="text-sm text-gray-500">A carregar preferências...</p>;
  }

  const avatarSrc = prefs
    ? preferencesApi.resolveAvatarUrl(prefs.avatar_url)
    : "";

  return (
    <form onSubmit={handleSave} className="max-w-xl space-y-6">
      <div className="flex items-center gap-4">
        <div className="h-16 w-16 overflow-hidden rounded-full border border-white/10 bg-[#161616]">
          {avatarSrc ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={avatarSrc}
              alt="Avatar"
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-lg text-gray-500">
              ?
            </div>
          )}
        </div>
        <div>
          <Label htmlFor="avatar" className="text-[#f5f5f7]">
            Avatar
          </Label>
          <Input
            id="avatar"
            type="file"
            accept="image/*"
            className="mt-2 text-gray-300"
            disabled={uploading}
            onChange={handleAvatarChange}
          />
          {uploading && (
            <p className="mt-1 text-xs text-gray-500">A enviar...</p>
          )}
          <Input
            className="mt-3 border-white/10 bg-[#161616] text-[#f5f5f7]"
            placeholder="Ou cola URL do avatar (https://...)"
            value={avatarUrl}
            onChange={(e) => setAvatarUrl(e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="display_name" className="text-[#f5f5f7]">
          Nome (como o agente te trata)
        </Label>
        <Input
          id="display_name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          className="border-white/10 bg-[#161616] text-[#f5f5f7]"
          placeholder="Ex: Rei"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="instructions" className="text-[#f5f5f7]">
          Instruções do agente
        </Label>
        <textarea
          id="instructions"
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
          rows={5}
          className="w-full rounded-xl border border-white/10 bg-[#161616] px-4 py-3 text-sm text-[#f5f5f7] placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-brand"
          placeholder="Ex: Responde sempre em português. Foca em backend Python."
        />
      </div>

      {success && <p className="text-sm text-emerald-400">{success}</p>}
      {error && <p className="text-sm text-red-300">{error}</p>}

      <Button type="submit" disabled={saving}>
        {saving ? "A guardar..." : "Guardar preferências"}
      </Button>
    </form>
  );
}
