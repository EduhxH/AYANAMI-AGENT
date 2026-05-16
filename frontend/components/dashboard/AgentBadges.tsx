import { Bot, GitBranch, Mail, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { AgentType } from "@/lib/types";

const config: Record<
  AgentType,
  { label: string; icon: typeof GitBranch; variant: "default" | "success" | "warning" }
> = {
  github: { label: "GitHub", icon: GitBranch, variant: "default" },
  email: { label: "Email", icon: Mail, variant: "success" },
  anime: { label: "Anime", icon: Sparkles, variant: "warning" },
  general: { label: "Geral", icon: Bot, variant: "default" },
};

export function AgentBadges({ agents }: { agents: AgentType[] }) {
  if (!agents.length) return null;

  return (
    <div className="flex flex-wrap gap-2">
      <span className="text-xs text-gray-500">Agentes activos:</span>
      {agents.map((a) => {
        const c = config[a];
        return (
          <Badge key={a} variant={c.variant} className="gap-1">
            <c.icon className="h-3 w-3" />
            {c.label}
          </Badge>
        );
      })}
    </div>
  );
}
