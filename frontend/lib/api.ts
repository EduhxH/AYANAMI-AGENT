import { clearToken, getToken } from "./token";
import type {
  AnimeRecommendResponse,
  AnimeSuggestResponse,
  LoginResponse,
  MessageResponse,
  OAuthUrlResponse,
  QueryResponse,
  User,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    const detail = body?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((d: { msg?: string }) => d.msg || String(d)).join(", ");
    }
    return body?.message || res.statusText;
  } catch {
    return res.statusText || "Erro desconhecido";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth = true
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (auth) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401 && auth) {
    clearToken();
    if (typeof window !== "undefined") {
      window.location.href = "/auth/login";
    }
    throw new ApiError("Sessão expirada. Inicia sessão novamente.", 401);
  }

  if (!res.ok) {
    throw new ApiError(await parseError(res), res.status);
  }

  if (res.status === 204) return {} as T;
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string }>("/health", {}, false),

  register: (email: string, password: string) =>
    request<MessageResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }, false),

  verify: (email: string, code: string) =>
    request<MessageResponse>("/auth/verify", {
      method: "POST",
      body: JSON.stringify({ email, code }),
    }, false),

  login: (email: string, password: string) =>
    request<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }, false),

  me: () => request<User>("/auth/me"),

  getGithubAuthUrl: () => request<OAuthUrlResponse>("/auth/github"),

  getGoogleAuthUrl: () => request<OAuthUrlResponse>("/auth/google"),

  githubCallback: (code: string, state?: string) => {
    const params = new URLSearchParams({ code });
    if (state) params.set("state", state);
    return request<{ message: string; username?: string }>(
      `/auth/callback/github?${params.toString()}`
    );
  },

  googleCallback: (code: string, state?: string) => {
    const params = new URLSearchParams({ code });
    if (state) params.set("state", state);
    return request<MessageResponse>(`/auth/callback/google?${params.toString()}`);
  },

  query: (query: string) =>
    request<QueryResponse>("/query/", {
      method: "POST",
      body: JSON.stringify({ query }),
    }),

  animeRecommend: () => request<AnimeRecommendResponse>("/anime/recommend"),

  animeSuggest: (anime_title: string, reason: string) =>
    request<AnimeSuggestResponse>("/anime/suggest", {
      method: "POST",
      body: JSON.stringify({ anime_title, reason }),
    }),
};
