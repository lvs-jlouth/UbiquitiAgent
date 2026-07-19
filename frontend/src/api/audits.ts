import { apiClient } from './client';
import type { AuditFinding, AuditRun, FindingStatus } from '../types';

export async function fetchFindings(): Promise<AuditFinding[]> {
  const { data } = await apiClient.get<AuditFinding[]>('/audit/findings');
  return data;
}

export async function fetchFinding(id: number): Promise<AuditFinding> {
  const { data } = await apiClient.get<AuditFinding>(`/audit/findings/${id}`);
  return data;
}

export async function updateFindingStatus(
  id: number,
  status: FindingStatus
): Promise<AuditFinding> {
  const { data } = await apiClient.patch<AuditFinding>(`/audit/findings/${id}`, {
    status,
  });
  return data;
}

export async function fetchAuditRuns(): Promise<AuditRun[]> {
  const { data } = await apiClient.get<AuditRun[]>('/audit/runs');
  return data;
}

export async function runAudit(): Promise<AuditRun> {
  const { data } = await apiClient.post<AuditRun>('/audit/runs');
  return data;
}
