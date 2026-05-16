"use client";

import { GitBranch, Mail, Sparkles } from "lucide-react";

import { Reveal } from "@/components/motion/Reveal";

const features = [
  {
    icon: GitBranch,
    color: "blue",
    eyebrow: "GitHub Agent",
    title: "Analisa repositórios.",
    body: "Pede um review de código, resumo de PRs ou estado do repo. O agente usa a tua conta GitHub ligada.",
    stats: ["Repos", "PRs", "Issues"],
  },
  {
    icon: Mail,
    color: "green",
    eyebrow: "Email Agent",
    title: "Gmail inteligente.",
    body: "Resume threads, prioriza mensagens e responde com contexto do teu inbox — sem sair do dashboard.",
    stats: ["Inbox", "Resumos", "Ações"],
    reverse: true,
  },
  {
    icon: Sparkles,
    color: "purple",
    eyebrow: "Anime Easter Egg",
    title: "Modo secreto.",
    body: "Um botão escondido activa recomendações de anime com justificações técnicas. Porque sim.",
    stats: ["Crítica", "Rating", "Tags"],
    dark: true,
  },
];

const iconBg: Record<string, string> = {
  blue: "bg-brand/10 text-brand",
  green: "bg-emerald-500/10 text-emerald-600",
  purple: "bg-violet-500/10 text-violet-600",
};

export function Features() {
  return (
    <section id="features" className="scroll-mt-20">
      {features.map((f) => (
        <div
          key={f.eyebrow}
          className={`flex min-h-[70vh] items-center justify-center px-6 py-24 ${
            f.dark ? "bg-dark text-white" : f.reverse ? "bg-surface" : "bg-white"
          }`}
        >
          <div
            className={`grid w-full max-w-[1020px] items-center gap-12 lg:gap-20 ${
              f.reverse ? "lg:grid-cols-2" : "lg:grid-cols-2"
            } ${f.reverse ? "[&>*:first-child]:lg:order-2" : ""}`}
          >
            <Reveal variant={f.reverse ? "right" : "left"}>
              <div>
                <div
                  className={`mb-5 flex h-14 w-14 items-center justify-center rounded-2xl ${iconBg[f.color]}`}
                >
                  <f.icon className="h-7 w-7" />
                </div>
                <p className="mb-2 text-sm font-semibold text-brand">{f.eyebrow}</p>
                <h2
                  className={`text-[clamp(2rem,4vw,3.25rem)] font-bold leading-tight tracking-tight ${
                    f.dark ? "text-white" : "text-foreground"
                  }`}
                >
                  {f.title}
                </h2>
                <p
                  className={`mt-4 max-w-md text-lg font-light leading-relaxed ${
                    f.dark ? "text-white/65" : "text-muted"
                  }`}
                >
                  {f.body}
                </p>
                <div className="mt-7 flex flex-wrap gap-3">
                  {f.stats.map((s) => (
                    <span
                      key={s}
                      className={`rounded-2xl border px-6 py-4 text-sm ${
                        f.dark
                          ? "border-white/10 bg-white/5 text-white/80"
                          : "border-black/8 bg-black/[0.04] text-muted"
                      }`}
                    >
                      <span className="block text-2xl font-bold text-brand">{s}</span>
                      agente
                    </span>
                  ))}
                </div>
              </div>
            </Reveal>

            <Reveal variant={f.reverse ? "left" : "right"} delay={0.1}>
              <div
                className={`overflow-hidden rounded-2xl border shadow-2xl ${
                  f.dark
                    ? "border-white/10 bg-[#111]"
                    : "border-black/10 bg-white"
                }`}
              >
                <div className="border-b border-black/5 bg-[#e8e8ed] px-4 py-2.5 flex gap-1.5">
                  <span className="h-3 w-3 rounded-full bg-[#ff5f56]" />
                  <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
                  <span className="h-3 w-3 rounded-full bg-[#28c840]" />
                </div>
                <div className={`p-8 font-mono text-sm ${f.dark ? "text-white/80" : "text-muted"}`}>
                  <p className="text-brand">{">"} query</p>
                  <p className="mt-2 text-foreground">
                    {f.eyebrow === "GitHub Agent"
                      ? "Analisa o último PR do repo main"
                      : f.eyebrow === "Email Agent"
                        ? "Resume os emails não lidos de hoje"
                        : "recommenda anime para mim"}
                  </p>
                  <p className="mt-4 text-emerald-500">✓ agente activado</p>
                </div>
              </div>
            </Reveal>
          </div>
        </div>
      ))}
    </section>
  );
}
