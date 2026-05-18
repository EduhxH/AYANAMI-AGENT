"use client";

import { useMemo, useState } from "react";
import type { ReactNode } from "react";

const MAX_COLLAPSE_LENGTH = 900;
const MAX_COLLAPSE_LINES = 12;

function truncateMessage(message: string) {
  if (message.length <= MAX_COLLAPSE_LENGTH) return message;
  return message.slice(0, MAX_COLLAPSE_LENGTH).trimEnd() + "...";
}

function parseMessage(message: string): ReactNode[] {
  const lines = message.split("\n");
  const blocks: Array<{ type: string; content: string[] }> = [];
  let currentList: string[] | null = null;
  let currentType = "paragraph";

  const flushList = () => {
    if (currentList) {
      blocks.push({ type: "list", content: currentList });
      currentList = null;
    }
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      flushList();
      currentType = "paragraph";
      continue;
    }

    const headingMatch = trimmed.match(/^\*\*(.+)\*\*$/);
    if (headingMatch) {
      flushList();
      blocks.push({ type: "heading", content: [headingMatch[1].trim()] });
      continue;
    }

    if (/^#+\s+/.test(trimmed)) {
      flushList();
      blocks.push({ type: "heading", content: [trimmed.replace(/^#+\s+/, "")] });
      continue;
    }

    if (/^[-*]\s+/.test(trimmed) || /^\d+\.\s+/.test(trimmed)) {
      if (!currentList) {
        flushList();
        currentList = [];
        currentType = "list";
      }
      currentList.push(trimmed.replace(/^([-*]|\d+\.)\s+/, ""));
      continue;
    }

    if (/^(Fonte|Fontes|Source|Sources|Referência|Referências)[:\s]/i.test(trimmed)) {
      flushList();
      blocks.push({ type: "reference-title", content: [trimmed] });
      continue;
    }

    if (/^https?:\/\//i.test(trimmed) || trimmed.includes("www.")) {
      if (!currentList) {
        flushList();
        currentList = [];
        currentType = "list";
      }
      currentList.push(trimmed);
      continue;
    }

    flushList();
    blocks.push({ type: "paragraph", content: [trimmed] });
  }

  flushList();
  return blocks.map((block, index) => {
    if (block.type === "heading") {
      return (
        <h3 key={index} className="mt-4 text-sm font-semibold text-primary">
          {block.content[0]}
        </h3>
      );
    }

    if (block.type === "list") {
      return (
        <ul key={index} className="ml-5 list-disc space-y-1 text-sm leading-7 text-primary">
          {block.content.map((item, itemIndex) => (
            <li key={itemIndex}>{item}</li>
          ))}
        </ul>
      );
    }

    if (block.type === "reference-title") {
      return (
        <p key={index} className="mt-4 text-xs font-semibold uppercase tracking-wide text-accent">
          {block.content[0]}
        </p>
      );
    }

    return (
      <p key={index} className="mt-3 text-sm leading-7 text-primary">
        {block.content[0]}
      </p>
    );
  });
}

export function AgentMessage({
  message,
  inline = false,
}: {
  message: string;
  inline?: boolean;
}) {
  if (!message?.trim()) return null;

  const shouldCollapse = useMemo(
    () =>
      message.length > MAX_COLLAPSE_LENGTH ||
      message.split("\n").length > MAX_COLLAPSE_LINES,
    [message]
  );

  const [expanded, setExpanded] = useState(false);
  const visibleMessage = shouldCollapse && !expanded ? truncateMessage(message) : message;

  if (inline) {
    return (
      <p className="whitespace-pre-wrap text-sm leading-relaxed">{message}</p>
    );
  }

  return (
    <article className="rounded-2xl border border-theme bg-[var(--bubble-assistant)] px-5 py-4">
      <div className="space-y-2 text-primary">{parseMessage(visibleMessage)}</div>

      {shouldCollapse && (
        <button
          type="button"
          onClick={() => setExpanded((prev) => !prev)}
          className="mt-4 inline-flex items-center rounded-full border border-accent px-3 py-1 text-xs font-semibold text-accent transition hover:bg-accent/10"
        >
          {expanded ? "Ler menos" : "Ler mais"}
        </button>
      )}
    </article>
  );
}
