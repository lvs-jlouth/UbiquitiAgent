export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'expired' | 'executed';

export type ApprovalRiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface Approval {
  id: number;
  title: string;
  description: string;
  action_type: string;
  risk_level: ApprovalRiskLevel;
  status: ApprovalStatus;
  requested_by: string;
  reviewed_by: string | null;
  recommendation_id: number | null;
  device_id: number | null;
  payload: Record<string, unknown> | null;
  reason: string | null;
  requested_at: string;
  reviewed_at: string | null;
  expires_at: string | null;
  executed_at: string | null;
}

export interface ApprovalDecision {
  reason?: string;
}
