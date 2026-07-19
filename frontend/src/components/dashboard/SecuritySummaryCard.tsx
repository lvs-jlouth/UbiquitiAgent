import { ShieldCheck, ShieldAlert } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import type { AuditFinding, Severity } from '../../types';

interface SecuritySummaryCardProps {
  findings: AuditFinding[];
}

const SEVERITY_ORDER: Severity[] = ['critical', 'high', 'medium', 'low', 'info'];

export function SecuritySummaryCard({ findings }: SecuritySummaryCardProps) {
  const open = findings.filter((f) => f.status === 'open');
  const counts = open.reduce<Record<string, number>>((acc, f) => {
    acc[f.severity] = (acc[f.severity] ?? 0) + 1;
    return acc;
  }, {});

  const hasCritical = (counts.critical ?? 0) > 0 || (counts.high ?? 0) > 0;

  return (
    <Card className="p-5" as="section">
      <div className="flex items-center gap-2">
        {hasCritical ? (
          <ShieldAlert className="h-5 w-5 text-red-500" aria-hidden="true" />
        ) : (
          <ShieldCheck className="h-5 w-5 text-green-500" aria-hidden="true" />
        )}
        <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">
          Security Summary
        </h3>
      </div>

      <p className="mt-3 text-3xl font-bold text-gray-900 dark:text-gray-100">
        {open.length}
        <span className="ml-2 text-sm font-normal text-gray-500 dark:text-gray-400">
          open findings
        </span>
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        {SEVERITY_ORDER.map((severity) => (
          <div key={severity} className="flex items-center gap-1.5">
            <Badge variant={severity}>{severity}</Badge>
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-200">
              {counts[severity] ?? 0}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default SecuritySummaryCard;
