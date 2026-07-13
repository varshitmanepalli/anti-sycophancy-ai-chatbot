"use client";

import { PanelLeft } from "lucide-react";
import { usePathname } from "next/navigation";

import { ModeToggle } from "@/features/chat";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { queryKeys } from "@/config";
import { useIsMobile, useOnlineStatus } from "@/hooks";
import { checkHealth } from "@/services";
import { useChatStore, useReasoningPanelStore } from "@/stores";
import { cn } from "@/utils";
import { useQuery } from "@tanstack/react-query";

import { getPageTitle } from "../data/nav";
import { UserMenu } from "./user-menu";
import { ThemeToggle } from "@/components/layout/theme-toggle";

interface DashboardHeaderProps {
  title?: string;
  className?: string;
  onOpenHistory?: () => void;
}

/** Top navigation bar for the dashboard. */
export function DashboardHeader({ title, className, onOpenHistory }: DashboardHeaderProps) {
  const isMobile = useIsMobile();
  const isOnline = useOnlineStatus();
  const pathname = usePathname();
  const toggleSidebar = useChatStore((s) => s.toggleSidebar);
  const chatMode = useChatStore((s) => s.chatMode);
  const lastConfidence = useReasoningPanelStore((s) => s.lastConfidence);

  const { data: health, isError, refetch, isFetching } = useQuery({
    queryKey: queryKeys.health.liveness(),
    queryFn: checkHealth,
    refetchInterval: 30_000,
    retry: 1,
  });

  const isBackendOnline = health?.status === "ok";
  const showOffline = !isOnline || isError || !isBackendOnline;

  const pageTitle = title ?? getPageTitle(pathname);
  const isChatRoute = pathname === "/chat" || pathname.startsWith("/c/");

  return (
    <header
      className={cn(
        "flex h-14 shrink-0 items-center justify-between border-b bg-background/80 px-3 backdrop-blur sm:px-4",
        "supports-[backdrop-filter]:bg-background/60",
        className,
      )}
    >
      <div className="flex min-w-0 items-center gap-1.5 sm:gap-2">
        {isMobile && (
          <Button
            variant="ghost"
            size="iconTouch"
            onClick={onOpenHistory ?? toggleSidebar}
            aria-label="Open menu and history"
            className="shrink-0 touch-manipulation"
          >
            <PanelLeft className="h-5 w-5" />
          </Button>
        )}
        <h1 className="truncate text-sm font-semibold tracking-tight">{pageTitle}</h1>
        {isMobile && isChatRoute && chatMode === "reasoning" && lastConfidence !== null && (
          <Badge variant={lastConfidence >= 0.7 ? "success" : "warning"} className="shrink-0 text-[10px]">
            {Math.round(lastConfidence * 100)}%
          </Badge>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-0.5 sm:gap-2">
        {!isMobile && isChatRoute && chatMode === "reasoning" && lastConfidence !== null && (
          <Badge variant={lastConfidence >= 0.7 ? "success" : "warning"} className="hidden sm:inline-flex">
            {Math.round(lastConfidence * 100)}% confidence
          </Badge>
        )}
        <Badge
          variant={showOffline ? "outline" : "success"}
          className={cn(
            "hidden sm:inline-flex",
            isError && "cursor-pointer",
          )}
          onClick={isError ? () => void refetch() : undefined}
          title={isError ? "Click to retry connection" : undefined}
        >
          {!isOnline ? "Offline" : isBackendOnline ? "Online" : isError ? "Unreachable" : "Offline"}
          {isFetching && isError && "…"}
        </Badge>
        {isChatRoute && <ModeToggle mobile={isMobile} />}
        {!isMobile && <ThemeToggle />}
        {!isMobile && <UserMenu />}
      </div>
    </header>
  );
}
