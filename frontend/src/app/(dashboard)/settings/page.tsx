import type { Metadata } from "next";

import { SettingsView } from "@/features/dashboard";

export const metadata: Metadata = {
  title: "Settings",
};

/** User settings page. */
export default function SettingsPage() {
  return <SettingsView />;
}
