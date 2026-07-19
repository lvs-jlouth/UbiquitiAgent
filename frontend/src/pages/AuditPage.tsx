import { useState } from 'react';
import { PageHeader } from '../components/ui/PageHeader';
import { Alert } from '../components/ui/Alert';
import { Badge } from '../components/ui/Badge';
import { AuditFindingList } from '../components/audit/AuditFindingList';
import { AuditFindingDetail } from '../components/audit/AuditFindingDetail';
import { RunAuditButton } from '../components/audit/RunAuditButton';
import { useAudits } from '../hooks/useAudits';
import type { AuditFinding, Severity } from '../types';

const SEVERITY_ORDER: Severity[] = ['critical', 'high', 'medium', 'low', 'info'];

export function AuditPage() {
  const { findings, isLoading, error, isRunning, triggerAudit, setStatus } = useAudits();
  const [selected, setSelected] = useState<AuditFinding | null>(null);

  const open = findings.filter((f) => f.status === 'open');
  const counts = open.reduce<Record<string, number>>((acc, f) => {
    acc[f.severity] = (acc[f.severity] ?? 0) + 1;
    return acc;
  }, {});

  const handleStatus = (id: number, status: AuditFinding['status']) => {
    void setStatus(id, status);
    setSelected(null);
  };

  return (
    <>
      <PageHeader
        title="Security Audit"
        description="Automated compliance and security findings for your network"
        actions={<RunAuditButton onRun={() => void triggerAudit()} isRunning={isRunning} />}
      />

      {error && (
        <Alert variant="error" className="mb-4" title="Audit error">
          {error}
        </Alert>
      )}

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {open.length} open findings
        </span>
        {SEVERITY_ORDER.map((severity) => (
          <span key={severity} className="inline-flex items-center gap-1.5">
            <Badge variant={severity}>{severity}</Badge>
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-200">
              {counts[severity] ?? 0}
            </span>
          </span>
        ))}
      </div>

      <AuditFindingList findings={findings} isLoading={isLoading} onSelect={setSelected} />
      <AuditFindingDetail
        finding={selected}
        onClose={() => setSelected(null)}
        onUpdateStatus={handleStatus}
      />
    </>
  );
}

export default AuditPage;
