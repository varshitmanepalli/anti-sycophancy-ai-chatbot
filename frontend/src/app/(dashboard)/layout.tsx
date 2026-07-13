import { DashboardShell } from "@/features/dashboard";

/** Shared layout for all dashboard routes. */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardShell>{children}</DashboardShell>;
}
