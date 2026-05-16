"use client";

import { motion } from "framer-motion";
import { Bot, GitBranch, Mail, Terminal } from "lucide-react";

import { Reveal } from "@/components/motion/Reveal";

export function MockDashboard() {
  return (
    <section id="demo" className="scroll-mt-20 bg-surface px-6 pb-24 pt-4">
      <Reveal className="mx-auto mb-10 max-w-xl text-center">
        <p className="text-sm font-semibold text-brand">Demo</p>
        <h2 className="mt-2 text-3xl font-bold tracking-tight text-foreground md:text-4xl">
          Dashboard em acção
        </h2>
        <p className="mt-3 font-light text-muted">
          O mesmo padrão visual do DriverSync — interface escura, cards e
          resultados dos agentes.
        </p>
      </Reveal>

      <Reveal variant="scale" className="mx-auto max-w-[960px]">
        <motion.div
          className="overflow-hidden rounded-[14px] border border-black/12 shadow-[0_32px_80px_rgba(0,0,0,0.11)]"
          whileHover={{ y: -4 }}
          transition={{ duration: 0.3 }}
        >
          <div className="flex items-center gap-2 border-b border-black/10 bg-[#e0e0e0] px-4 py-2.5">
            <span className="h-3 w-3 rounded-full bg-[#ff5f56]" />
            <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
            <span className="h-3 w-3 rounded-full bg-[#28c840]" />
          </div>

          <div className="flex min-h-[380px] bg-[#111]">
            <aside className="hidden w-[210px] shrink-0 flex-col border-r border-white/10 bg-[#0d0d0d] py-5 sm:flex">
              <div className="flex items-center gap-2 px-4 pb-5">
                <span className="flex h-7 w-7 items-center justify-center rounded-lg border border-brand/30 bg-[#131826]">
                  <Bot className="h-4 w-4 text-brand" />
                </span>
                <span className="text-sm font-semibold text-[#f5f5f7]">
                  Dev Agent
                </span>
              </div>
              <nav className="flex flex-col gap-0.5 px-2">
                {[
                  { label: "Dashboard", on: true },
                  { label: "Histórico", on: false },
                  { label: "Definições", on: false },
                ].map((item) => (
                  <div
                    key={item.label}
                    className={`rounded-lg px-3 py-2 text-xs ${
                      item.on
                        ? "border border-brand/20 bg-brand/15 text-blue-400"
                        : "text-gray-500"
                    }`}
                  >
                    {item.label}
                  </div>
                ))}
              </nav>
              <div className="mt-auto border-t border-white/10 px-4 pt-4">
                <div className="flex items-center gap-2">
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-500 text-xs text-white">
                    D
                  </span>
                  <span className="text-xs text-[#f5f5f7]">Developer</span>
                </div>
              </div>
            </aside>

            <main className="flex-1 p-6 md:p-7">
              <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="text-xl font-medium text-[#f5f5f7]">
                    Dashboard
                  </h3>
                  <p className="text-xs text-gray-500">
                    Pergunta aos teus agentes
                  </p>
                </div>
                <span className="inline-flex items-center gap-1.5 rounded-pill bg-brand px-4 py-2 text-xs font-medium text-white">
                  <Terminal className="h-3.5 w-3.5" />
                  Enviar
                </span>
              </div>

              <div className="mb-4 rounded-xl border border-white/10 bg-[#161616] p-3">
                <p className="font-mono text-xs text-gray-500">
                  Analisa os PRs abertos e resume os emails urgentes...
                </p>
              </div>

              <div className="mb-4 grid gap-3 sm:grid-cols-3">
                {[
                  { label: "GITHUB", value: "2", icon: GitBranch },
                  { label: "EMAIL", value: "5", icon: Mail },
                  { label: "AGENTES", value: "3", icon: Bot },
                ].map((c) => (
                  <div
                    key={c.label}
                    className="rounded-xl border border-white/10 bg-[#161616] p-4"
                  >
                    <p className="text-[9px] tracking-widest text-gray-500">
                      {c.label}
                    </p>
                    <p className="mt-1 text-2xl font-light text-[#f5f5f7]">
                      {c.value}
                    </p>
                    <c.icon className="mt-2 h-4 w-4 text-brand" />
                  </div>
                ))}
              </div>

              <div className="overflow-hidden rounded-xl border border-white/10 bg-[#161616]">
                <div className="grid grid-cols-4 gap-2 border-b border-white/10 px-3 py-2 text-[9px] tracking-widest text-gray-500">
                  <span>AGENTE</span>
                  <span>STATUS</span>
                  <span className="col-span-2">RESULTADO</span>
                </div>
                {[
                  { agent: "GitHub", status: "ok", text: "3 PRs analisados" },
                  { agent: "Email", status: "warn", text: "2 urgentes" },
                ].map((row) => (
                  <div
                    key={row.agent}
                    className="grid grid-cols-4 items-center gap-2 border-b border-white/5 px-3 py-2.5 text-xs last:border-0"
                  >
                    <span className="text-[#f5f5f7]">{row.agent}</span>
                    <span
                      className={
                        row.status === "ok"
                          ? "text-emerald-400"
                          : "text-amber-400"
                      }
                    >
                      {row.status === "ok" ? "OK" : "Atenção"}
                    </span>
                    <span className="col-span-2 text-gray-400">{row.text}</span>
                  </div>
                ))}
              </div>
            </main>
          </div>
        </motion.div>
      </Reveal>
    </section>
  );
}
