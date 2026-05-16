"use client";

/**
 * Resposta única do agente — sem cards por agente nem JSON bruto.
 */
export function AgentMessage({
  message,
  inline = false,
}: {
  message: string;
  inline?: boolean;
}) {
  if (!message?.trim()) return null;

  if (inline) {
    return (
      <p className="whitespace-pre-wrap text-sm leading-relaxed">{message}</p>
    );
  }

  return (
    <article className="rounded-2xl border border-theme bg-[var(--bubble-assistant)] px-5 py-4">
      <p className="whitespace-pre-wrap text-sm leading-relaxed text-primary">
        {message}
      </p>
    </article>
  );
}
