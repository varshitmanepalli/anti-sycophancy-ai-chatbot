"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

import { Logo } from "@/components/layout/logo";
import { SidebarNavItem } from "@/components/motion";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { ROUTES } from "@/config";
import { getInitials, useAuthStore } from "@/stores";
import { cn } from "@/utils";

import { DASHBOARD_NAV } from "../data/nav";
import { ConversationHistory } from "@/features/conversation-history";

interface DashboardSidebarProps {
  className?: string;
  onNavigate?: () => void;
}

/** Dashboard sidebar with navigation, conversation history, and user footer. */
export function DashboardSidebar({ className, onNavigate }: DashboardSidebarProps) {
  const pathname = usePathname();
  const profile = useAuthStore((s) => s.profile);

  return (
    <aside
      className={cn(
        "flex h-full w-72 flex-col border-r bg-sidebar text-sidebar-foreground",
        className,
      )}
    >
      <div className="p-4">
        <Link href={ROUTES.dashboard.chat} onClick={onNavigate}>
          <Logo />
        </Link>
      </div>

      <nav className="space-y-0.5 px-3" aria-label="Dashboard">
        {DASHBOARD_NAV.map((item) => {
          const isActive = item.match?.(pathname) ?? pathname === item.href;
          return (
            <SidebarNavItem
              key={item.href}
              href={item.href}
              label={item.label}
              icon={item.icon}
              isActive={isActive}
              onNavigate={onNavigate}
            />
          );
        })}
      </nav>

      <Separator className="my-3 bg-sidebar-border" />

      <div className="px-3 pb-1">
        <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
          History
        </p>
      </div>

      <ConversationHistory onNavigate={onNavigate} />

      <Separator className="bg-sidebar-border" />

      <motion.div whileTap={{ scale: 0.98 }}>
        <Link
          href={ROUTES.dashboard.profile}
          onClick={onNavigate}
          className="flex min-h-11 items-center gap-3 p-4 transition-colors hover:bg-sidebar-accent/40 active:bg-sidebar-accent/60 touch-manipulation"
        >
          <Avatar className="h-9 w-9">
            <AvatarFallback className="text-xs font-medium">
              {getInitials(profile.name)}
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{profile.name}</p>
            <p className="truncate text-xs text-muted-foreground">{profile.email}</p>
          </div>
        </Link>
      </motion.div>
    </aside>
  );
}
