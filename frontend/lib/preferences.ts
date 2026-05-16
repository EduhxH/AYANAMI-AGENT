import { ApiError } from "./api";

export interface UserPreferences {
  user_id: string;
  display_name: string;
  avatar_url: string;
  agent_instructions: string;
  created_at: string;
  updated_at: string;
}

export interface UserPreferencesUpdate {
  display_name?: string;
  avatar_url?: string;
  agent_instructions?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function preferencesRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const { getToken } = await import("./token");
  const headers = new Headers(options.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_URL}/api/preferences${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let message = res.statusText;
    try {
      const body = await res.json();
      message = body?.detail || message;
    } catch {
      /* ignore */
    }
    throw new ApiError(message, res.status);
  }

  return res.json() as Promise<T>;
}

export const preferencesApi = {
  get: () => preferencesRequest<UserPreferences>(""),

  update: (data: UserPreferencesUpdate) =>
    preferencesRequest<UserPreferences>("", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),

  uploadAvatar: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return preferencesRequest<UserPreferences>("/avatar", {
      method: "POST",
      body: form,
    });
  },

  resolveAvatarUrl: (avatar_url: string) => {
    if (!avatar_url) return "";
    if (avatar_url.startsWith("http")) return avatar_url;
    return `${API_URL}${avatar_url}`;
  },
};
