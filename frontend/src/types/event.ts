export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';

export type EventCategory =
  | 'security'
  | 'connectivity'
  | 'performance'
  | 'configuration'
  | 'system';

export interface Event {
  id: number;
  event_type: string;
  category: EventCategory;
  severity: Severity;
  message: string;
  source: string | null;
  device_id: number | null;
  client_id: number | null;
  metadata: Record<string, unknown> | null;
  acknowledged: boolean;
  occurred_at: string;
  created_at: string;
}

export interface EventStats {
  total: number;
  by_severity: Record<Severity, number>;
  unacknowledged: number;
}
