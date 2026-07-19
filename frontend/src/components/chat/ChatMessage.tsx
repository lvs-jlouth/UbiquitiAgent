import clsx from 'clsx';
import { Bot, User } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { parseAiSections, SECTION_STYLES } from '../../utils/chat';
import type { ChatMessage as ChatMessageType } from '../../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

function timeLabel(timestamp: string): string {
  try {
    return format(parseISO(timestamp), 'HH:mm');
  } catch {
    return '';
  }
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end gap-3" role="listitem">
        <div className="max-w-[80%]">
          <div className="rounded-2xl rounded-tr-sm bg-brand-600 px-4 py-2.5 text-sm text-white shadow-sm">
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          </div>
          <p className="mt-1 text-right text-xs text-gray-400">
            {timeLabel(message.timestamp)}
          </p>
        </div>
        <span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300">
          <User className="h-4 w-4" aria-hidden="true" />
        </span>
      </div>
    );
  }

  const sections = parseAiSections(message.content);
  const isStructured =
    sections.length > 1 || (sections[0] && sections[0].key !== 'other');

  return (
    <div className="flex justify-start gap-3" role="listitem">
      <span
        className={clsx(
          'mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
          message.error
            ? 'bg-red-100 text-red-600 dark:bg-red-950 dark:text-red-300'
            : 'bg-gray-800 text-white dark:bg-gray-700'
        )}
      >
        <Bot className="h-4 w-4" aria-hidden="true" />
      </span>
      <div className="max-w-[85%]">
        <div
          className={clsx(
            'rounded-2xl rounded-tl-sm px-4 py-3 text-sm shadow-sm',
            message.error
              ? 'bg-red-50 text-red-800 dark:bg-red-950/60 dark:text-red-200'
              : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100'
          )}
        >
          {isStructured ? (
            <div className="space-y-3">
              {sections.map((section, idx) => {
                const style = SECTION_STYLES[section.key];
                return (
                  <section
                    key={`${section.key}-${idx}`}
                    className={clsx('border-l-2 pl-3', style.border)}
                  >
                    <span
                      className={clsx(
                        'inline-block rounded px-2 py-0.5 text-xs font-semibold uppercase tracking-wide',
                        style.badge
                      )}
                    >
                      {style.label}
                    </span>
                    <ul className="mt-1.5 space-y-1">
                      {section.lines.map((line, lineIdx) => (
                        <li
                          key={lineIdx}
                          className="flex gap-2 text-sm text-gray-700 dark:text-gray-200"
                        >
                          <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-current opacity-60" />
                          <span className="whitespace-pre-wrap break-words">{line}</span>
                        </li>
                      ))}
                    </ul>
                  </section>
                );
              })}
            </div>
          ) : (
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          )}
        </div>
        <p className="mt-1 text-xs text-gray-400">{timeLabel(message.timestamp)}</p>
      </div>
    </div>
  );
}

export default ChatMessage;
