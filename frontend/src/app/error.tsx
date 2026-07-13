"use client";

import { useEffect } from "react";

import { ErrorPage } from "@/components/feedback";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/** Route-level error boundary with retry action. */
export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <ErrorPage
      variant="error"
      message={error.message || undefined}
      onRetry={reset}
    />
  );
}
