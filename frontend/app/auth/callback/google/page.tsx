"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { AuthShell } from "@/components/auth/AuthShell";
import { getAuthErrorMessage } from "@/context/AuthContext";
import { api } from "@/lib/api";

function GoogleCallbackInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [message, setMessage] = useState("A ligar Gmail...");

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");
    if (!code) {
      setMessage("Código OAuth em falta.");
      return;
    }

    (async () => {
      try {
        const res = await api.googleCallback(code, state ?? undefined);
        setMessage(res.message || "Gmail ligado!");
        setTimeout(() => router.replace("/dashboard/settings"), 1200);
      } catch (err) {
        setMessage(getAuthErrorMessage(err));
      }
    })();
  }, [searchParams, router]);

  return (
    <AuthShell title="Gmail" subtitle="A processar autorização OAuth">
      <p className="text-center text-sm text-muted">{message}</p>
    </AuthShell>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-surface text-muted">
          A processar...
        </div>
      }
    >
      <GoogleCallbackInner />
    </Suspense>
  );
}
