"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, ChevronDown, GitBranch, Mail, Search, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

import { BrandLogo } from "@/components/dashboard/BrandLogo";
import { ThemeToggle } from "@/components/dashboard/ThemeToggle";
import { ChatScreenshot } from "@/components/landing/ChatScreenshot";
import { LandingFooter } from "@/components/landing/LandingFooter";
import { PageCurtain, Reveal } from "@/components/motion/Reveal";
import { getToken } from "@/lib/token";

const TICKER = [
  "GitHub Agent",
  "Gmail Agent",
  "Multi-agente",
  "AYANAMI AGENT",
  "One prompt",
  "Rei Ayanami blue",
  "Respostas directas",
];

const FEATURES = [
  {
    icon: GitBranch,
    title: "GitHub",
    body: "Analisa PRs, repos e prioriza o que importa — sem sair do chat.",
  },
  {
    icon: Mail,
    title: "Gmail",
    body: "Resume emails urgentes e liga o contexto às tuas tarefas.",
  },
  {
    icon: Search,
    title: "Pesquisa",
    body: "Um prompt orquestra agentes e devolve uma resposta limpa.",
  },
];

export function WelcomeLanding() {
  const [enterHref, setEnterHref] = useState("/auth/login");

  useEffect(() => {
    if (getToken()) setEnterHref("/dashboard");
  }, []);

  return (
  <>
    <PageCurtain />
    <section className="min-h-screen bg-main text-primary">
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.65, ease: [0.16, 1, 0.3, 1] }}
        className="fixed inset-x-0 top-0 z-50 flex h-[52px] items-center justify-center border-b border-theme bg-[var(--bg-main)]/80 backdrop-blur-xl"
      >
        <div className="flex w-full max-w-6xl items-center justify-between px-6">
          <Link href="/" className="shrink-0">
            <BrandLogo variant="full" className="h-14 w-auto" priority />
          </Link>
          <div className="flex items-center gap-2 sm:gap-3">
            <ThemeToggle className="rounded-lg border border-theme px-2 py-1.5 text-xs sm:px-3 sm:text-sm" />
            <Link
              href={enterHref}
              className="inline-flex items-center gap-1.5 rounded-pill bg-accent px-4 py-2 text-xs font-medium text-[#0a1218] transition-colors hover:bg-accent-hover sm:gap-2 sm:px-5 sm:text-sm"
            >
              Entrar
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </motion.nav>

      <header className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-hero px-6 pb-20 pt-28 text-center">
        <div
          className="hero-bg-circle pointer-events-none absolute h-[800px] w-[800px] rounded-full"
          style={{
            background:
              "radial-gradient(circle, var(--rei-blue-muted) 0%, transparent 70%)",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -55%)",
          }}
        />
        <div className="hero-grid pointer-events-none absolute inset-0 opacity-60" />

        <Reveal>
          <span className="mb-5 inline-flex items-center gap-2 rounded-pill border border-accent/25 bg-accent-muted px-3.5 py-1.5 text-xs font-medium text-accent">
            <span
              className="h-1.5 w-1.5 rounded-full bg-accent"
              style={{ animation: "accentPulse 2s ease-in-out infinite" }}
            />
            Multi-agente · GitHub · Gmail
          </span>
        </Reveal>

        <Reveal delay={0.1}>
          <BrandLogo variant="full" className="mx-auto h-[22rem] w-auto max-w-[700px] md:h-[30rem] md:max-w-[900px] drop-shadow-[0_0_48px_var(--rei-blue-glow)]" priority />
        </Reveal>

        <Reveal delay={0.15}>
          <p className="mt-6 text-lg font-medium text-accent md:text-xl">
            AYANAMI AGENT
          </p>
          <h1 className="mt-3 text-balance text-4xl font-bold tracking-tight md:text-6xl">
            One prompt to rule them all
            <span className="mt-2 block font-light italic text-accent">
              …while they ride it.
            </span>
          </h1>
        </Reveal>

        <Reveal delay={0.25}>
          <p className="mx-auto mt-6 max-w-lg text-base font-light leading-relaxed text-secondary md:text-lg">
            Interface minimalista, respostas directas. Orquestra agentes num
            único chat — como uma conversa de mensagens.
          </p>
        </Reveal>

        <Reveal delay={0.35} className="mt-10 flex flex-wrap justify-center gap-3">
          <Link
            href={enterHref}
            className="inline-flex h-11 items-center gap-2 rounded-pill bg-accent px-7 text-sm font-medium text-[#0a1218] shadow-[0_8px_28px_var(--rei-blue-glow)] transition-all hover:bg-accent-hover hover:-translate-y-0.5"
          >
            Abrir o agente
            <ArrowRight className="h-4 w-4" />
          </Link>
          <a
            href="#demo"
            className="inline-flex h-11 items-center gap-2 rounded-pill border border-accent px-7 text-sm text-accent transition-colors hover:bg-accent-muted"
          >
            Ver interface
            <ChevronDown className="h-4 w-4" />
          </a>
        </Reveal>
      </header>

      <section className="ticker-wrap overflow-hidden bg-accent py-3.5">
        <div className="ticker-track flex whitespace-nowrap">
          {[...TICKER, ...TICKER].map((t, i) => (
            <span
              key={`${t}-${i}`}
              className="mx-8 text-sm font-medium text-[#0a1218]/90"
            >
              {t}
            </span>
          ))}
        </div>
      </section>

      <section id="features" className="scroll-mt-24 bg-main px-6 py-24">
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold text-accent">Funcionalidades</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight md:text-4xl">
            Tudo num só prompt
          </h2>
          <p className="mt-4 text-secondary">
            Agentes especializados, uma interface de chat contínua.
          </p>
        </Reveal>
        <div className="mx-auto mt-14 grid max-w-5xl gap-6 md:grid-cols-3">
          {FEATURES.map((f, i) => (
            <Reveal key={f.title} delay={0.1 * i}>
              <article className="h-full rounded-2xl border border-theme bg-elevated p-6 transition-colors hover:border-accent/40">
                <f.icon className="h-6 w-6 text-accent" />
                <h3 className="mt-4 text-lg font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{f.body}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      <section id="demo" className="scroll-mt-24 bg-hero px-6 py-24">
        <Reveal className="mx-auto mb-12 max-w-xl text-center">
          <p className="text-sm font-semibold text-accent">Interface real</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight">
            Chat como mensagens
          </h2>
          <p className="mt-3 text-secondary">
            Várias conversas na barra lateral. Sobe no histórico de cada uma.
          </p>
        </Reveal>
        <Reveal variant="scale">
          <ChatScreenshot />
        </Reveal>
      </section>

      <section className="relative overflow-hidden bg-main px-6 py-28 text-center">
        <div
          className="pointer-events-none absolute left-1/2 top-1/2 h-[500px] w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full opacity-40"
          style={{
            background:
              "radial-gradient(circle, var(--rei-blue-glow) 0%, transparent 65%)",
          }}
        />
        <Reveal>
          <Sparkles className="mx-auto h-8 w-8 text-accent" />
          <h2 className="mt-6 text-3xl font-bold md:text-4xl">Pronto para entrar?</h2>
          <p className="mx-auto mt-4 max-w-md text-secondary">
            Cria conta ou inicia sessão e continua as tuas conversas onde
            paraste.
          </p>
          <Link
            href={enterHref}
            className="mt-10 inline-flex h-12 items-center gap-2 rounded-pill bg-accent px-10 text-base font-medium text-[#0a1218] shadow-[0_8px_32px_var(--rei-blue-glow)] transition-all hover:bg-accent-hover hover:-translate-y-0.5"
          >
            Começar agora
            <ArrowRight className="h-5 w-5" />
          </Link>
        </Reveal>
      </section>

      <LandingFooter />
    </section>
  </>
  );
}
