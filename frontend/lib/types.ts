export type AgentType = "github" | "email" | "anime" | "general";

export interface User {
  id: string;
  email: string;
  verified: boolean;
  github_username?: string | null;
  has_github: boolean;
  has_google: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface MessageResponse {
  message: string;
}

export interface OAuthUrlResponse {
  url: string;
}

export interface AgentResult {
  agent: AgentType;
  success: boolean;
  data: Record<string, unknown>;
  error?: string | null;
}

export interface QueryResponse {
  query: string;
  results: AgentResult[];
  summary: string;
}

export interface AnimeRecommendation {
  title: string;
  reason: string;
  technical_parallel: string;
  rating: number;
}

export interface AnimeRecommendResponse {
  recommendation?: {
    recommendations: AnimeRecommendation[];
  };
  recommendations?: AnimeRecommendation[];
}

export interface AnimeSuggestResponse {
  critique: string;
  approved: boolean;
  score: number;
}

export interface UserPreferences {
  user_id: string;
  display_name: string;
  avatar_url: string;
  agent_instructions: string;
  created_at: string;
  updated_at: string;
}

export interface QueryHistoryItem {
  id: string;
  query: string;
  summary: string;
  agents: AgentType[];
  timestamp: string;
  results: AgentResult[];
}
