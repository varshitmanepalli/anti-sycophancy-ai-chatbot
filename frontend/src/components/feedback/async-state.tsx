"use client";

import { cn } from "@/utils";

import { EmptyStateView } from "./empty-state-view";
import { ErrorStateView } from "./error-state-view";
import { LoadingSpinner } from "./loading-spinner";

interface AsyncStateProps {
  isLoading?: boolean;
  isError?: boolean;
  isEmpty?: boolean;
  error?: Error | string | null;
  loadingLabel?: string;
  emptyTitle?: string;
  emptyDescription?: string;
  errorTitle?: string;
  onRetry?: () => void;
  retryLoading?: boolean;
  loadingFallback?: React.ReactNode;
  errorFallback?: React.ReactNode;
  emptyFallback?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  minHeight?: string;
}

function resolveMessage(error?: Error | string | null): string | undefined {
  if (!error) return undefined;
  return typeof error === "string" ? error : error.message;
}

/** Switches between loading, error, empty, and content states. */
export function AsyncState({
  isLoading = false,
  isError = false,
  isEmpty = false,
  error,
  loadingLabel = "Loading",
  emptyTitle = "Nothing here yet",
  emptyDescription,
  errorTitle = "Failed to load",
  onRetry,
  retryLoading = false,
  loadingFallback,
  errorFallback,
  emptyFallback,
  children,
  className,
  minHeight = "min-h-[12rem]",
}: AsyncStateProps) {
  if (isLoading) {
    return (
      <div className={cn(minHeight, className)}>
        {loadingFallback ?? <LoadingSpinner centered label={loadingLabel} />}
      </div>
    );
  }

  if (isError) {
    return (
      <div className={cn(minHeight, className)}>
        {errorFallback ?? (
          <ErrorStateView
            title={errorTitle}
            message={resolveMessage(error)}
            onRetry={onRetry}
            retryLoading={retryLoading}
          />
        )}
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className={cn(minHeight, className)}>
        {emptyFallback ?? (
          <EmptyStateView title={emptyTitle} description={emptyDescription} size="sm" />
        )}
      </div>
    );
  }

  return <>{children}</>;
}
