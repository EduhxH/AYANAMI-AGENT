"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Bot, ChevronDown } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/motion/Reveal";

export function Hero() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-surface px-6 pb-20 pt-[100px] text-center">
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[800px] w-[800px] -translate-x-1/2 -translate-y-[55%] rounded-full bg-[radial-gradient(circle,rgba(0,113,227,0.07)_0%,transparent_70%)]" />
      <div
        className="pointer-events-none absolute inset-0 opacity-60"
        style={{
          backgroundImage:
            "linear-gradient(rgba(0,113,227,.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,113,227,.03) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
          maskImage:
            "radial-gradient(ellipse 70% 60% at 50% 40%, black, transparent)",
        }}
      />

      <Reveal>
        <span className="mb-5 inline-flex items-center gap-2 rounded-pill border border-brand/20 bg-brand/10 px-3.5 py-1.5 text-xs font-medium text-brand">
          <span className="h-1.5 w-1.5 animate-pulse-soft rounded-full bg-brand" />
          Multi-agente · GitHub · Gmail · IA
        </span>
      </Reveal>

      <Reveal delay={0.1}>
        <motion.div
          className="mb-6 flex h-[100px] w-[100px] items-center justify-center rounded-3xl bg-[var(--accent-muted)] text-primary"
          initial={{ scale: 0.8, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <Bot className="h-12 w-12" />
        </motion.div>
      </Reveal>

      <Reveal delay={0.15}>
        <p className="mb-2 text-[17px] font-semibold text-brand">Dev Agent</p>
        <h1 className="text-balance text-[clamp(2.75rem,7.5vw,5.5rem)] font-bold leading-[1.03] tracking-tight text-foreground">
          O teu assistente
          <span className="mt-1 block font-light italic text-brand">
            Always Shipping.
          </span>
        </h1>
      </Reveal>

      <Reveal delay={0.25}>
        <p className="mx-auto mt-4 max-w-[480px] text-lg font-light leading-relaxed text-muted">
          Orquestra agentes de IA para analisar repositórios GitHub, processar
          emails e responder às tuas queries — tudo num só lugar.
        </p>
      </Reveal>

      <Reveal delay={0.35} className="mt-9">
        <div className="flex flex-wrap items-center justify-center gap-3">
          <Button size="lg" asChild>
            <Link href="/auth/register">Começar grátis</Link>
          </Button>
          <Button variant="secondary" size="lg" asChild>
            <a href="#demo">
              Ver em ação
              <ChevronDown className="h-4 w-4" />
            </a>
          </Button>
        </div>
        <p className="mt-5 text-xs text-subtle">
          GitHub · Gmail · Groq · Sem cartão de crédito
        </p>
      </Reveal>
    </section>
  );
}
