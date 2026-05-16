"use client";

import Link from "next/link";
import { Bot } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/motion/Reveal";

export function Cta() {
  return (
    <section
      id="cta"
      className="relative scroll-mt-20 overflow-hidden bg-dark px-6 py-28 text-center"
    >
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[500px] w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,rgba(0,113,227,0.18)_0%,transparent_65%)]" />

      <div className="relative mx-auto max-w-xl">
        <Reveal variant="scale">
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-brand to-blue-600 text-white shadow-xl">
            <Bot className="h-10 w-10" />
          </div>
        </Reveal>
        <Reveal>
          <p className="text-[17px] font-semibold text-[#6bb5ff]">Dev Agent</p>
          <h2 className="mt-2 text-[clamp(2.5rem,5vw,4rem)] font-bold leading-tight tracking-tight text-white">
            Pronto para
            <br />
            começar?
          </h2>
        </Reveal>
        <Reveal delay={0.1}>
          <p className="mx-auto mt-4 max-w-md text-lg font-light leading-relaxed text-white/60">
            Liga GitHub e Gmail, faz a tua primeira query e deixa os agentes
            trabalharem por ti.
          </p>
        </Reveal>
        <Reveal delay={0.2} className="mt-9">
          <div className="flex flex-wrap justify-center gap-3">
            <Button size="lg" asChild>
              <Link href="/auth/register">Começar grátis</Link>
            </Button>
            <Button
              variant="secondary"
              size="lg"
              className="border-white/30 text-white/90 hover:bg-white/10 hover:text-white"
              asChild
            >
              <a href="#demo">Ver demo</a>
            </Button>
          </div>
          <p className="mt-5 text-sm text-white/35">
            API em localhost:8000 · Next.js 14
          </p>
        </Reveal>
      </div>
    </section>
  );
}
