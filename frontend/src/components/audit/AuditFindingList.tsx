import { DataTable, type Column } from '../ui/DataTable';
import { Badge, severityToVariant, type BadgeVariant } from '../ui/Badge';
import { formatRelative, titleCase } from '../../utils/format';
import type { AuditFinding, FindingStatus } from '../../types';

interface AuditFindingListProps {
  findings: AuditFinding[];
  isLoading?: boolean;
  onSelect?: (finding: AuditFinding) => void;
}

const STATUS_VARIANT: Record<FindingStatus, BadgeVariant> = {
  open: 'warning',
  acknowledged: 'info',
  resolved: 'success',
  suppressed: 'neutral',
};

export function AuditFindingList({ findings, isLoading, onSelect }: AuditFindingListProps) {
  const columns: Column<AuditFinding>[] = [
    {
      key: 'severity',
      header: 'Severity',
      sortable: true,
      sortValue: (f) => f.severity,
      render: (f) => <Badge variant={severityToVariant(f.severity)}>{f.severity}</Badge>,
    },
    {
      key: 'title',
      header: 'Finding',
      sortable: true,
      sortValue: (f) => f.title.toLowerCase(),
      render: (f) => (
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100">{f.title}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{f.rule_id}</p>
        </div>
      ),
    },
    {
      key: 'category',
      header: 'Category',
      sortable: true,
      sortValue: (f) => f.category,
      render: (f) => <Badge variant="neutral">{titleCase(f.category)}</Badge>,
    },
    {
      key: 'affected_resource',
      header: 'Resource',
      render: (f) => f.affected_resource ?? '—',
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      sortValue: (f) => f.status,
      render: (f) => <Badge variant={STATUS_VARIANT[f.status]}>{f.status}</Badge>,
    },
    {
      key: 'detected_at',
      header: 'Detected',
      sortable: true,
      sortValue: (f) => new Date(f.detected_at).getTime(),
      render: (f) => formatRelative(f.detected_at),
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={findings}
      rowKey={(f) => f.id}
      isLoading={isLoading}
      onRowClick={onSelect}
      emptyMessage="No audit findings. Run an audit to scan your network."
      caption="List of audit findings"
    />
  );
}

export default AuditFindingList;
