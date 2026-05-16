import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AgentResult } from "@/lib/types";

function formatData(data: Record<string, unknown>): string {
  try {
    return JSON.stringify(data, null, 2);
  } catch {
    return String(data);
  }
}

export function ResultCards({
  results,
  summary,
}: {
  results: AgentResult[];
  summary?: string;
}) {
  return (
    <div className="space-y-4">
      {summary && (
        <Card className="border-white/10 bg-[#161616] text-[#f5f5f7]">
          <CardHeader>
            <CardTitle className="text-base text-[#f5f5f7]">Resumo</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-gray-300">{summary}</p>
          </CardContent>
        </Card>
      )}

      {results.map((r) => (
        <Card
          key={`${r.agent}-${r.success}`}
          className={`border-white/10 bg-[#161616] ${
            r.success ? "" : "border-amber-500/30"
          }`}
        >
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm capitalize text-[#f5f5f7]">
              {r.agent} Agent
            </CardTitle>
            <span
              className={`text-xs ${
                r.success ? "text-emerald-400" : "text-amber-400"
              }`}
            >
              {r.success ? "Sucesso" : "Erro"}
            </span>
          </CardHeader>
          <CardContent>
            {r.error ? (
              <p className="text-sm text-amber-300">{r.error}</p>
            ) : (
              <>
                {typeof r.data.highlight === "string" && (
                  <p className="mb-3 text-sm leading-relaxed text-blue-200">
                    {r.data.highlight}
                  </p>
                )}
                <pre className="max-h-64 overflow-auto rounded-lg bg-black/30 p-3 text-xs text-gray-300">
                  {formatData(r.data)}
                </pre>
              </>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
