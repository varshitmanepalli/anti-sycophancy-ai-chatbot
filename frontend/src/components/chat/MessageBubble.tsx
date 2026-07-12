/**
 * Message bubble component — renders a single user or assistant turn.
 */

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
  return (
    <div data-role={role}>
      <strong>{role === "user" ? "You" : "Assistant"}</strong>
      <p>{content}</p>
    </div>
  );
}
