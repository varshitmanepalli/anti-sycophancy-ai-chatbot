"use client";

/**
 * Chat input field with send button.
 */

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  // TODO: implement controlled input and submit handler
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
      }}
    >
      <input type="text" placeholder="Type a message…" disabled={disabled} />
      <button type="submit" disabled={disabled}>
        Send
      </button>
    </form>
  );
}
