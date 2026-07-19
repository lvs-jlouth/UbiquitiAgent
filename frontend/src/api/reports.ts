import { apiClient } from './client';

export interface ReportSummary {
  generated_at: string;
  device_count: number;
  client_count: number;
  open_findings: number;
  critical_findings: number;
  pending_approvals: number;
  network_health_score: number;
}

export interface Report {
  id: number;
  title: string;
  report_type: string;
  format: string;
  created_at: string;
  url: string | null;
}

export async function fetchReportSummary(): Promise<ReportSummary> {
  const { data } = await apiClient.get<ReportSummary>('/reports/summary');
  return data;
}

export async function fetchReports(): Promise<Report[]> {
  const { data } = await apiClient.get<Report[]>('/reports');
  return data;
}

export async function generateReport(reportType: string): Promise<Report> {
  const { data } = await apiClient.post<Report>('/reports', {
    report_type: reportType,
  });
  return data;
}
