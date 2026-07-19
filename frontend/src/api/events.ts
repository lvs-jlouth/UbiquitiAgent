import { apiClient } from './client';
import type { Event, EventStats } from '../types';

export async function fetchEvents(): Promise<Event[]> {
  const { data } = await apiClient.get<Event[]>('/events');
  return data;
}

export async function fetchEventStats(): Promise<EventStats> {
  const { data } = await apiClient.get<EventStats>('/events/stats');
  return data;
}

export async function acknowledgeEvent(id: number): Promise<Event> {
  const { data } = await apiClient.post<Event>(`/events/${id}/acknowledge`);
  return data;
}
