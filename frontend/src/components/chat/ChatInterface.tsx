import { useEffect, useRef } from 'react';
import { Bot, Trash2 } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { useChat } from '../../hooks/useChat';

export function ChatInterface() {
  const { messages, isTyping, error, sendMessage, clearConversation } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, isTyping]);

  return (
    <div className="flex h-[calc(100vh-10rem)] flex-col overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-800 text-white dark:bg-gray-700">
            <Bot className="h-5 w-5" aria-hidden="true" />
          </span>
          <div className="leading-tight">
            <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              AI Operations Assistant
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {isTyping ? 'Analyzing…' : 'Online'}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={clearConversation}
          className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
          aria-label="Clear conversation"
        >
          <Trash2 className="h-4 w-4" aria-hidden="true" />
          <span className="hidden sm:inline">Clear</span>
        </button>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 space-y-4 overflow-y-auto p-4 scrollbar-thin"
        role="log"
        aria-live="polite"
        aria-label="Conversation history"
      >
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isTyping && (
          <div className="flex items-center gap-3" aria-label="Assistant is typing">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-800 text-white dark:bg-gray-700">
              <Bot className="h-4 w-4" aria-hidden="true" />
            </span>
            <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-gray-100 px-4 py-3 dark:bg-gray-800">
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.3s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.15s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
            </div>
          </div>
        )}
      </div>

      {error && (
        <p className="px-4 py-1 text-center text-xs text-red-500" role="status">
          {error}
        </p>
      )}

      <ChatInput onSend={sendMessage} disabled={isTyping} />
    </div>
  );
}

export default ChatInterface;
