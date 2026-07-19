import { apiClient } from './client';
import type { ChatRequest, ChatResponse } from '../types';

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>('/agent/chat', request);
  return data;
}
