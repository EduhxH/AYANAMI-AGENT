"use client";

import Link from "next/link";
import { motion } from "framer-motion";

import { BrandLogo } from "@/components/dashboard/BrandLogo";
import { ThemeToggle } from "@/components/dashboard/ThemeToggle";
import { Reveal } from "@/components/motion/Reveal";

export function AuthShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <section className="grid min-h-screen bg-main lg:grid-cols-2">

      {/* ── Left decorative panel (desktop only) ── */}
      <aside className="relative hidden overflow-hidden bg-hero lg:flex lg:flex-col lg:items-center lg:justify-center lg:p-12">
        {/* Ambient glow */}
        <div
          className="hero-bg-circle pointer-events-none absolute h-[700px] w-[700px] rounded-full"
          style={{
            background: "radial-gradient(circle, var(--rei-blue-muted) 0%, transparent 70%)",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
          }}
        />
        <div className="hero-grid pointer-events-none absolute inset-0 opacity-50" />

        {/* Logo — dead center, massive and impactful */}
        <div className="relative z-10 flex flex-col items-center gap-12">
          <Link href="/">
            <BrandLogo
              variant="full"
              className="h-[14rem] w-auto drop-shadow-[0_0_64px_var(--rei-blue-glow)]"
              priority
            />
          </Link>
          <Reveal className="max-w-xs text-center">
            <p className="text-sm font-semibold uppercase tracking-widest text-accent">
              AYANAMI AGENT
            </p>
            <p className="mt-3 text-lg font-bold tracking-tight text-primary">
              One prompt to rule them all
            </p>
            <p className="mt-1 text-base font-light italic text-accent">
              …while they ride it.
            </p>
          </Reveal>
        </div>

        <p className="absolute bottom-6 z-10 text-xs text-muted">Built by Eduardo Carvalho</p>
      </aside>

      {/* ── Right form panel ── */}
      <div className="flex flex-col bg-main">
        {/* Top bar */}
        <header className="flex items-center justify-between border-b border-theme px-6 py-4">
          {/* Mobile: logo left */}
          <Link href="/" className="lg:hidden">
            <BrandLogo
              variant="full"
              className="h-12 w-auto drop-shadow-[0_0_24px_var(--rei-blue-glow)]"
              priority
            />
          </Link>
          <span className="hidden lg:block" />
          <ThemeToggle className="rounded-lg border border-theme px-3 py-2 text-sm" />
        </header>

        {/* Form */}
        <motion.main
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-1 flex-col justify-center px-6 pb-12 pt-8 lg:px-16"
        >
          <article className="mx-auto w-full max-w-md">
            <h1 className="text-2xl font-semibold tracking-tight text-primary">{title}</h1>
            <p className="mt-1.5 text-sm text-secondary">{subtitle}</p>
            <section className="mt-8">{children}</section>
          </article>
        </motion.main>
      </div>
    </section>
  );
}
