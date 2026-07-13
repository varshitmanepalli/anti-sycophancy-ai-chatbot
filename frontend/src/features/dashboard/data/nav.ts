import {
  MessageSquare,
  Settings,
  User,
  type LucideIcon,
} from "lucide-react";

import { ROUTES } from "@/config";

export interface DashboardNavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  match?: (pathname: string) => boolean;
}

export const DASHBOARD_NAV: DashboardNavItem[] = [
  {
    label: "Chat",
    href: ROUTES.dashboard.chat,
    icon: MessageSquare,
    match: (pathname) =>
      pathname === ROUTES.dashboard.chat || pathname.startsWith("/c/"),
  },
  {
    label: "Profile",
    href: ROUTES.dashboard.profile,
    icon: User,
    match: (pathname) => pathname === ROUTES.dashboard.profile,
  },
  {
    label: "Settings",
    href: ROUTES.dashboard.settings,
    icon: Settings,
    match: (pathname) => pathname === ROUTES.dashboard.settings,
  },
];

/** Bottom tab bar items for mobile dashboard navigation. */
export const MOBILE_BOTTOM_NAV = DASHBOARD_NAV;

export const PAGE_TITLES: Record<string, string> = {
  [ROUTES.dashboard.chat]: "Chat",
  [ROUTES.dashboard.profile]: "Profile",
  [ROUTES.dashboard.settings]: "Settings",
};

export function getPageTitle(pathname: string): string {
  if (pathname.startsWith("/c/")) return "Conversation";
  return PAGE_TITLES[pathname] ?? "Dashboard";
}
