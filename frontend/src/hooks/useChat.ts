import { useCallback, useState } from 'react';
import { sendChatMessage } from '../api/agent';
import { extractErrorMessage } from '../api/client';
import type { ChatMessage } from '../types';

function createId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

const WELCOME: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  content:
    'Hello, I am your UniFi AI Operations Assistant. Ask me about device health, security posture, recent events, or recommended actions.',
  timestamp: new Date().toISOString(),
};

interface UseChatResult {
  messages: ChatMessage[];
  isTyping: boolean;
  error: string | null;
  sendMessage: (text: string) => Promise<void>;
  clearConversation: () => void;
}

export function useChat(): UseChatResult {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isTyping) return;

      const userMessage: ChatMessage = {
        id: createId(),
        role: 'user',
        content: trimmed,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsTyping(true);
      setError(null);

      try {
        const response = await sendChatMessage({
          message: trimmed,
          conversation_id: conversationId,
        });
        setConversationId(response.conversation_id);
        setMessages((prev) => [
          ...prev,
          {
            id: createId(),
            role: 'assistant',
            content: response.message,
            timestamp: response.created_at ?? new Date().toISOString(),
          },
        ]);
      } catch (err) {
        const message = extractErrorMessage(err);
        setError(message);
        setMessages((prev) => [
          ...prev,
          {
            id: createId(),
            role: 'assistant',
            content: `I was unable to reach the operations backend: ${message}`,
            timestamp: new Date().toISOString(),
            error: true,
          },
        ]);
      } finally {
        setIsTyping(false);
      }
    },
    [conversationId, isTyping]
  );

  const clearConversation = useCallback(() => {
    setMessages([WELCOME]);
    setConversationId(null);
    setError(null);
  }, []);

  return { messages, isTyping, error, sendMessage, clearConversation };
}
