/**
 * Shared UI primitives (buttons, loaders, etc.).
 */

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
}

export function LoadingSpinner({ size = "md" }: LoadingSpinnerProps) {
  return <div data-size={size} aria-label="Loading" />;
}
