"use client";

import { AlertCircle, Loader2 } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useId, useRef, useState } from "react";

import { cn } from "@/utils";

interface MarkdownMermaidProps {
  chart: string;
  className?: string;
}

/** Render Mermaid diagrams from fenced ```mermaid blocks. */
export function MarkdownMermaid({ chart, className }: MarkdownMermaidProps) {
  const id = useId().replace(/:/g, "");
  const containerRef = useRef<HTMLDivElement>(null);
  const { resolvedTheme } = useTheme();
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function renderDiagram() {
      setStatus("loading");
      setErrorMessage(null);

      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: resolvedTheme === "dark" ? "dark" : "default",
          securityLevel: "strict",
          fontFamily: "inherit",
        });

        const { svg } = await mermaid.render(`mermaid-${id}`, chart.trim());

        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
          setStatus("ready");
        }
      } catch (error) {
        if (!cancelled) {
          setStatus("error");
          setErrorMessage(
            error instanceof Error ? error.message : "Failed to render diagram",
          );
        }
      }
    }

    void renderDiagram();

    return () => {
      cancelled = true;
    };
  }, [chart, id, resolvedTheme]);

  return (
    <div
      className={cn(
        "markdown-mermaid my-4 overflow-hidden rounded-lg border bg-muted/20",
        className,
      )}
    >
      <div className="border-b bg-muted/40 px-3 py-1.5 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
        Diagram
      </div>

      <div className="relative min-h-[120px] p-3 sm:p-4">
        {status === "loading" && (
          <div className="flex items-center justify-center gap-2 py-8 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Rendering diagram…
          </div>
        )}

        {status === "error" && (
          <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              <p className="font-medium">Mermaid render error</p>
              <p className="mt-1 text-xs opacity-90">{errorMessage}</p>
            </div>
          </div>
        )}

        <div
          ref={containerRef}
          className={cn(
            "overflow-x-auto [&_svg]:mx-auto [&_svg]:max-w-full [&_svg]:h-auto",
            status !== "ready" && "hidden",
          )}
          aria-hidden={status !== "ready"}
        />
      </div>
    </div>
  );
}
