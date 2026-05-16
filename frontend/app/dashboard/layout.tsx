"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { useAuth } from "@/context/AuthContext";
import { ChatProvider } from "@/context/ChatContext";
import { useDashboardUI } from "@/context/DashboardUIContext";
import { getToken } from "@/lib/token";

function SettingsQueryOpener() {
  const searchParams = useSearchParams();
  const { openSettings } = useDashboardUI();

  useEffect(() => {
    if (searchParams.get("settings") === "1") openSettings();
  }, [searchParams, openSettings]);

  return null;
}

function DashboardAuthGate({ children }: { children: React.ReactNode }) {
  const { user, loading, refreshUser } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !getToken()) {
      router.replace("/auth/login");
    }
  }, [loading, router]);

  useEffect(() => {
    if (getToken() && !user && !loading) {
      refreshUser().catch(() => router.replace("/auth/login"));
    }
  }, [user, loading, refreshUser, router]);

  if (loading || (!user && getToken())) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-main text-muted">
        A carregar...
      </div>
    );
  }

  if (!user) return null;

  return <>{children}</>;
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ChatProvider>
      <DashboardAuthGate>
        <DashboardShell>
          <Suspense fallback={null}>
            <SettingsQueryOpener />
          </Suspense>
          {children}
        </DashboardShell>
      </DashboardAuthGate>
    </ChatProvider>
  );
}
