"use client";

import { Suspense, useState } from "react";

import { AnimePanel } from "@/components/dashboard/AnimePanel";
import { ProfileOverlay } from "@/components/dashboard/ProfileOverlay";
import { SettingsOverlay } from "@/components/dashboard/SettingsOverlay";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { DashboardUIProvider, useDashboardUI } from "@/context/DashboardUIContext";

function DashboardShellInner({ children }: { children: React.ReactNode }) {
  const [animeOpen, setAnimeOpen] = useState(false);
  const { profileOpen, closeProfile } = useDashboardUI();

  return (
    <div className="flex min-h-screen bg-main md:flex-row">
      <Sidebar onEasterEgg={() => setAnimeOpen(true)} />
      <div className="flex min-w-0 flex-1 flex-col">{children}</div>
      <Suspense fallback={null}>
        <SettingsOverlay />
      </Suspense>
      <ProfileOverlay open={profileOpen} onClose={closeProfile} />
      <AnimePanel open={animeOpen} onClose={() => setAnimeOpen(false)} />
    </div>
  );
}

export function DashboardShell({ children }: { children: React.ReactNode }) {
  return (
    <DashboardUIProvider>
      <DashboardShellInner>{children}</DashboardShellInner>
    </DashboardUIProvider>
  );
}
