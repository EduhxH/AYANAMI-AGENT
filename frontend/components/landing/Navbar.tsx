"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Bot } from "lucide-react";

import { Button } from "@/components/ui/button";

const links = [
  { href: "#features", label: "Agentes" },
  { href: "#demo", label: "Demo" },
  { href: "#cta", label: "Começar" },
];

export function Navbar() {
  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.65, ease: [0.16, 1, 0.3, 1], delay: 0.8 }}
      className="fixed inset-x-0 top-0 z-[9999] flex h-[52px] items-center justify-center border-b border-black/10 bg-white/80 backdrop-blur-xl"
    >
      <div className="flex w-full max-w-[1080px] items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-6 w-6 items-center justify-center rounded-md bg-brand text-white">
            <Bot className="h-3.5 w-3.5" />
          </span>
          <span className="text-[15px] font-semibold tracking-tight text-foreground">
            Dev Agent
          </span>
        </Link>

        <ul className="hidden items-center gap-7 md:flex">
          {links.map((l) => (
            <li key={l.href}>
              <a
                href={l.href}
                className="text-[13px] text-muted transition-colors hover:text-foreground"
              >
                {l.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/auth/login">Login</Link>
          </Button>
          <Button size="sm" asChild>
            <Link href="/auth/register">Começar grátis</Link>
          </Button>
        </div>
      </div>
    </motion.nav>
  );
}
