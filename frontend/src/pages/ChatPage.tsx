import { PageHeader } from '../components/ui/PageHeader';
import { ChatInterface } from '../components/chat/ChatInterface';

export function ChatPage() {
  return (
    <>
      <PageHeader
        title="AI Assistant"
        description="Ask questions about your network operations, security posture, and recommended actions"
      />
      <ChatInterface />
    </>
  );
}

export default ChatPage;
