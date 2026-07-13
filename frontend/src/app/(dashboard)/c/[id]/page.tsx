import { ChatWindow } from "@/features/chat";

interface ConversationPageProps {
  params: Promise<{ id: string }>;
}

/** Conversation page — loads chat by id from the URL. */
export default async function ConversationPage({ params }: ConversationPageProps) {
  const { id } = await params;
  return <ChatWindow conversationId={id} />;
}
