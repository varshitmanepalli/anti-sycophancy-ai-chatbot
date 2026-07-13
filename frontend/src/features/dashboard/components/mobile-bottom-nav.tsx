"use client";

import { History } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/utils";

import { MOBILE_BOTTOM_NAV } from "../data/nav";

interface MobileBottomNavProps {
  onOpenHistory?: () => void;
  className?: string;
}

/** Fixed bottom tab bar for mobile dashboard navigation. */
export function MobileBottomNav({ onOpenHistory, className }: MobileBottomNavProps) {
  const pathname = usePathname();

  return (
    <nav
      className={cn(
        "fixed inset-x-0 bottom-0 z-40 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80",
        "pb-safe px-safe tap-highlight-none",
        className,
      )}
      aria-label="Mobile navigation"
    >
      <div className="mx-auto flex h-16 max-w-lg items-stretch justify-around">
        {MOBILE_BOTTOM_NAV.map((item) => {
          const isActive = item.match?.(pathname) ?? pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex min-w-[4.5rem] flex-1 flex-col items-center justify-center gap-1 touch-manipulation",
                "text-[10px] font-medium transition-colors",
                isActive ? "text-primary" : "text-muted-foreground",
              )}
              aria-current={isActive ? "page" : undefined}
            >
              <span
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-xl transition-colors",
                  isActive && "bg-primary/10",
                )}
              >
                <Icon className="h-5 w-5" strokeWidth={isActive ? 2.25 : 1.75} />
              </span>
              {item.label}
            </Link>
          );
        })}

        <button
          type="button"
          onClick={onOpenHistory}
          className={cn(
            "flex min-w-[4.5rem] flex-1 flex-col items-center justify-center gap-1 touch-manipulation",
            "text-[10px] font-medium text-muted-foreground transition-colors",
          )}
          aria-label="Open conversation history"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-xl">
            <History className="h-5 w-5" strokeWidth={1.75} />
          </span>
          History
        </button>
      </div>
    </nav>
  );
}
