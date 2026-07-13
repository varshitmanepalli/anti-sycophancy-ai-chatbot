import { Sparkles } from "lucide-react";

import { APP_NAME } from "@/config";

/** App logo mark for header and sidebar. */
export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
        <Sparkles className="h-4 w-4" />
      </div>
      {!compact && (
        <div className="flex flex-col">
          <span className="text-sm font-semibold leading-none">{APP_NAME}</span>
          <span className="text-[10px] text-muted-foreground">Anti-sycophancy AI</span>
        </div>
      )}
    </div>
  );
}
