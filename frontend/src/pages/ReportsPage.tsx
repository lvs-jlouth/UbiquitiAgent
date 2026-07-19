import { useCallback, useEffect, useState } from 'react';
import { FileText, Download, Plus, Activity } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import {
  fetchReportSummary,
  fetchReports,
  generateReport,
  type Report,
  type ReportSummary,
} from '../api/reports';
import { extractErrorMessage } from '../api/client';
import { formatDate, titleCase } from '../utils/format';

const REPORT_TYPES = ['network_health', 'security_audit', 'client_activity'];

export function ReportsPage() {
  const [summary, setSummary] = useState<ReportSummary | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [summaryData, reportData] = await Promise.allSettled([
        fetchReportSummary(),
        fetchReports(),
      ]);
      if (summaryData.status === 'fulfilled') setSummary(summaryData.value);
      if (reportData.status === 'fulfilled') setReports(reportData.value);
      if (summaryData.status === 'rejected' && reportData.status === 'rejected') {
        setError(extractErrorMessage(summaryData.reason));
      }
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleGenerate = async (reportType: string) => {
    setGenerating(reportType);
    setError(null);
    try {
      const report = await generateReport(reportType);
      setReports((prev) => [report, ...prev]);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setGenerating(null);
    }
  };

  const stats: { label: string; value: string | number }[] = summary
    ? [
        { label: 'Devices', value: summary.device_count },
        { label: 'Clients', value: summary.client_count },
        { label: 'Open Findings', value: summary.open_findings },
        { label: 'Critical Findings', value: summary.critical_findings },
        { label: 'Pending Approvals', value: summary.pending_approvals },
        { label: 'Health Score', value: `${summary.network_health_score}/100` },
      ]
    : [];

  return (
    <>
      <PageHeader
        title="Reports"
        description="Generate and download operational reports"
      />

      {error && (
        <Alert variant="warning" className="mb-4" title="Reports unavailable">
          {error}
        </Alert>
      )}

      {isLoading ? (
        <LoadingSpinner fullPage label="Loading reports" />
      ) : (
        <div className="space-y-6">
          {summary && (
            <Card as="section">
              <CardHeader
                title="Operational Summary"
                description={`Generated ${formatDate(summary.generated_at)}`}
                icon={<Activity className="h-5 w-5" aria-hidden="true" />}
              />
              <dl className="grid grid-cols-2 gap-4 p-5 sm:grid-cols-3 lg:grid-cols-6">
                {stats.map((stat) => (
                  <div key={stat.label}>
                    <dt className="text-xs text-gray-500 dark:text-gray-400">
                      {stat.label}
                    </dt>
                    <dd className="mt-1 text-xl font-bold text-gray-900 dark:text-gray-100">
                      {stat.value}
                    </dd>
                  </div>
                ))}
              </dl>
            </Card>
          )}

          <section aria-label="Generate report">
            <h3 className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">
              Generate a report
            </h3>
            <div className="flex flex-wrap gap-3">
              {REPORT_TYPES.map((type) => (
                <Button
                  key={type}
                  variant="secondary"
                  isLoading={generating === type}
                  onClick={() => void handleGenerate(type)}
                  leftIcon={<Plus className="h-4 w-4" aria-hidden="true" />}
                >
                  {titleCase(type)}
                </Button>
              ))}
            </div>
          </section>

          <Card as="section">
            <CardHeader
              title="Generated Reports"
              icon={<FileText className="h-5 w-5" aria-hidden="true" />}
            />
            <ul className="divide-y divide-gray-100 dark:divide-gray-800">
              {reports.length === 0 ? (
                <li className="px-5 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                  No reports generated yet.
                </li>
              ) : (
                reports.map((report) => (
                  <li
                    key={report.id}
                    className="flex items-center justify-between gap-4 px-5 py-3"
                  >
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {report.title || titleCase(report.report_type)}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {report.format?.toUpperCase()} &middot;{' '}
                        {formatDate(report.created_at)}
                      </p>
                    </div>
                    {report.url && (
                      <a
                        href={report.url}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
                        aria-label={`Download ${report.title || report.report_type}`}
                      >
                        <Download className="h-4 w-4" aria-hidden="true" />
                        Download
                      </a>
                    )}
                  </li>
                ))
              )}
            </ul>
          </Card>
        </div>
      )}
    </>
  );
}

export default ReportsPage;
