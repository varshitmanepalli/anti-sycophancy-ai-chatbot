"use client";

import { useCallback, useEffect, useState } from "react";

import { OfflineBanner } from "@/components/feedback";
import { AnimatedSheet, PageTransition } from "@/components/motion";
import { useIsMobile, useSwipeEdge } from "@/hooks";
import { useChatStore } from "@/stores";
import { cn } from "@/utils";

import { DashboardHeader } from "./dashboard-header";
import { DashboardSidebar } from "./dashboard-sidebar";
import { MobileBottomNav } from "./mobile-bottom-nav";

interface DashboardShellProps {
  children: React.ReactNode;
  headerTitle?: string;
}

/** Responsive dashboard shell — sidebar, top nav, bottom tabs, and main content. */
export function DashboardShell({ children, headerTitle }: DashboardShellProps) {
  const isMobile = useIsMobile();
  const isSidebarOpen = useChatStore((s) => s.isSidebarOpen);
  const setSidebarOpen = useChatStore((s) => s.setSidebarOpen);
  const [sheetOpen, setSheetOpen] = useState(false);

  const closeSidebar = useCallback(() => {
    setSheetOpen(false);
    if (useChatStore.getState().isSidebarOpen) {
      setSidebarOpen(false);
    }
  }, [setSidebarOpen]);

  const openSidebar = useCallback(() => {
    setSheetOpen(true);
    if (!useChatStore.getState().isSidebarOpen) {
      setSidebarOpen(true);
    }
  }, [setSidebarOpen]);

  const handleSwipeLeft = useCallback(() => {
    if (sheetOpen || useChatStore.getState().isSidebarOpen) {
      closeSidebar();
    }
  }, [sheetOpen, closeSidebar]);

  useEffect(() => {
    // Desktop: sidebar open in store. Mobile: use sheet state only — do not keep
    // flipping isSidebarOpen or Radix onOpenChange will fight the media query.
    if (!isMobile) {
      setSheetOpen(false);
      if (!useChatStore.getState().isSidebarOpen) {
        setSidebarOpen(true);
      }
    }
  }, [isMobile, setSidebarOpen]);

  useSwipeEdge({
    enabled: isMobile,
    onSwipeRight: openSidebar,
    onSwipeLeft: handleSwipeLeft,
  });

  const showDesktopSidebar = !isMobile && isSidebarOpen;

  return (
    <div className="flex h-dvh overflow-hidden bg-background pt-safe">
      {showDesktopSidebar && (
        <div className="hidden shrink-0 md:block">
          <DashboardSidebar />
        </div>
      )}

      {isMobile && (
        <AnimatedSheet
          open={sheetOpen}
          onOpenChange={setSheetOpen}
          side="left"
          className="w-[min(20rem,85vw)]"
          showClose={false}
        >
          <DashboardSidebar onNavigate={closeSidebar} />
        </AnimatedSheet>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <OfflineBanner />
        <DashboardHeader title={headerTitle} onOpenHistory={isMobile ? openSidebar : undefined} />
        <main
          className={cn(
            "flex flex-1 flex-col overflow-hidden",
            isMobile && "pb-bottom-nav",
          )}
        >
          <PageTransition>{children}</PageTransition>
        </main>
      </div>

      {isMobile && <MobileBottomNav onOpenHistory={openSidebar} />}
    </div>
  );
}
