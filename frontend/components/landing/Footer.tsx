import Link from "next/link";
import { Bot } from "lucide-react";

const cols = [
  {
    title: "Produto",
    links: [
      { href: "#features", label: "Agentes" },
      { href: "#demo", label: "Demo" },
      { href: "/auth/register", label: "Registar" },
    ],
  },
  {
    title: "Conta",
    links: [
      { href: "/auth/login", label: "Login" },
      { href: "/dashboard", label: "Dashboard" },
      { href: "/dashboard/settings", label: "Definições" },
    ],
  },
  {
    title: "Stack",
    links: [
      { href: "#", label: "Next.js 14" },
      { href: "#", label: "FastAPI" },
      { href: "#", label: "Groq" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "#", label: "Privacidade" },
      { href: "#", label: "Termos" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="bg-dark text-white/45">
      <div className="mx-auto max-w-[1080px] border-b border-white/10 px-6 py-10">
        <div className="mb-6 flex items-center gap-2">
          <span className="flex h-5 w-5 items-center justify-center rounded-md bg-brand/80 text-white opacity-70">
            <Bot className="h-3 w-3" />
          </span>
          <span className="text-sm font-semibold text-white/50">Dev Agent</span>
        </div>
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {cols.map((col) => (
            <div key={col.title}>
              <h5 className="mb-3 text-xs font-semibold text-white/90">
                {col.title}
              </h5>
              {col.links.map((l) => (
                <Link
                  key={l.label}
                  href={l.href}
                  className="mb-2 block text-xs transition-colors hover:text-white/75"
                >
                  {l.label}
                </Link>
              ))}
            </div>
          ))}
        </div>
      </div>
      <div className="mx-auto flex max-w-[1080px] flex-wrap justify-between gap-2 px-6 py-4 text-xs">
        <p>© 2026 Dev Agent. Todos os direitos reservados.</p>
        <p>Projeto multi-agente para developers.</p>
      </div>
    </footer>
  );
}
