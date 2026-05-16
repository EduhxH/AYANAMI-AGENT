const items = [
  "GitHub Agent",
  "Email Agent",
  "Orchestrator",
  "Groq LLM",
  "OAuth",
  "Multi-agente",
  "Anime Easter Egg",
];

export function Ticker() {
  const track = [...items, ...items];
  return (
    <div className="overflow-hidden bg-brand py-3.5">
      <div className="flex w-max animate-ticker whitespace-nowrap">
        {track.map((item, i) => (
          <span
            key={`${item}-${i}`}
            className="px-8 text-[13px] font-medium uppercase tracking-wide text-white after:ml-8 after:opacity-60 after:content-['·']"
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}
