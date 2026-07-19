import { useCallback, useEffect, useState } from 'react';
import { fetchEvents, acknowledgeEvent } from '../api/events';
import { extractErrorMessage } from '../api/client';
import type { Event } from '../types';

interface UseEventsResult {
  events: Event[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  acknowledge: (id: number) => Promise<void>;
}

export function useEvents(): UseEventsResult {
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchEvents();
      setEvents(data);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const acknowledge = useCallback(async (id: number) => {
    const updated = await acknowledgeEvent(id);
    setEvents((prev) => prev.map((e) => (e.id === id ? updated : e)));
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { events, isLoading, error, refresh: load, acknowledge };
}
