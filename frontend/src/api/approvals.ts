import { apiClient } from './client';
import type { Approval } from '../types';

export async function fetchApprovals(): Promise<Approval[]> {
  const { data } = await apiClient.get<Approval[]>('/approvals');
  return data;
}

export async function fetchApproval(id: number): Promise<Approval> {
  const { data } = await apiClient.get<Approval>(`/approvals/${id}`);
  return data;
}

export async function approveApproval(id: number, reason?: string): Promise<Approval> {
  const { data } = await apiClient.post<Approval>(`/approvals/${id}/approve`, {
    reason,
  });
  return data;
}

export async function rejectApproval(id: number, reason?: string): Promise<Approval> {
  const { data } = await apiClient.post<Approval>(`/approvals/${id}/reject`, {
    reason,
  });
  return data;
}
