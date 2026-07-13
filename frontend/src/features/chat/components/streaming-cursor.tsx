/** Blinking cursor shown while a message is streaming. */
export function StreamingCursor() {
  return (
    <span
      className="ml-0.5 inline-block h-[1.1em] w-[2px] translate-y-[2px] animate-pulse bg-foreground/70"
      aria-hidden
    />
  );
}
