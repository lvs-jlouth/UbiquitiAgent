import type { Severity } from './event';

export type FindingStatus = 'open' | 'acknowledged' | 'resolved' | 'suppressed';

export type AuditCategory =
  | 'security'
  | 'firmware'
  | 'configuration'
  | 'performance'
  | 'compliance';

export interface AuditFinding {
  id: number;
  audit_run_id: number;
  rule_id: string;
  title: string;
  description: string;
  category: AuditCategory;
  severity: Severity;
  status: FindingStatus;
  affected_resource: string | null;
  device_id: number | null;
  remediation: string | null;
  details: Record<string, unknown> | null;
  detected_at: string;
  created_at: string;
  updated_at: string;
}

export type AuditRunStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface AuditRun {
  id: number;
  status: AuditRunStatus;
  triggered_by: string | null;
  findings_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  started_at: string;
  completed_at: string | null;
  created_at: string;
}
