import type { Severity } from './event';

export type RecommendationStatus =
  | 'proposed'
  | 'accepted'
  | 'rejected'
  | 'applied'
  | 'dismissed';

export type RecommendationCategory =
  | 'security'
  | 'performance'
  | 'reliability'
  | 'cost'
  | 'maintenance';

export interface Recommendation {
  id: number;
  title: string;
  summary: string;
  rationale: string;
  category: RecommendationCategory;
  severity: Severity;
  status: RecommendationStatus;
  impact: string | null;
  effort: 'low' | 'medium' | 'high' | null;
  finding_id: number | null;
  device_id: number | null;
  requires_approval: boolean;
  actions: RecommendationAction[];
  created_at: string;
  updated_at: string;
}

export interface RecommendationAction {
  id: string;
  description: string;
  command: string | null;
  automated: boolean;
}
