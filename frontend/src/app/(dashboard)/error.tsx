"use client";

import { useEffect } from "react";

import { ErrorPage } from "@/components/feedback";

interface DashboardErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/** Dashboard route error boundary. */
export default function DashboardError({ error, reset }: DashboardErrorProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <ErrorPage
      variant="error"
      title="Dashboard unavailable"
      message={error.message || "We couldn't load this page. Please try again."}
      onRetry={reset}
    />
  );
}
