"use client";

import { PanelLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useChatStore } from "@/stores";

/** Mobile sidebar toggle button. */
export function SidebarToggle() {
  const toggleSidebar = useChatStore((s) => s.toggleSidebar);
  return (
    <Button variant="ghost" size="icon" onClick={toggleSidebar} aria-label="Toggle sidebar">
      <PanelLeft className="h-4 w-4" />
    </Button>
  );
}
