export * from './device';
export * from './client';
export * from './event';
export * from './audit';
export * from './recommendation';
export * from './approval';
export * from './auth';

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiError {
  detail: string;
  status?: number;
}

export type ChatRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string;
  pending?: boolean;
  error?: boolean;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  created_at: string;
}

export interface ParsedAiSection {
  key: 'facts' | 'observations' | 'risks' | 'recommendations' | 'other';
  title: string;
  lines: string[];
}
