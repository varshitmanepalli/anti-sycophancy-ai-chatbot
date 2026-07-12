/**
 * Home page — chat interface entry point.
 *
 * Renders the main chat UI. Business logic and API calls are delegated
 * to components/ and lib/api.ts.
 */
import { ChatWindow } from "@/components/chat/ChatWindow";

export default function HomePage() {
  return (
    <main>
      <h1>Anti-Sycophancy Chatbot</h1>
      <ChatWindow />
    </main>
  );
}
