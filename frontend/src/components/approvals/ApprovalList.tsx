import { DataTable, type Column } from '../ui/DataTable';
import { Badge, type BadgeVariant } from '../ui/Badge';
import { formatRelative, titleCase } from '../../utils/format';
import type { Approval, ApprovalRiskLevel, ApprovalStatus } from '../../types';

interface ApprovalListProps {
  approvals: Approval[];
  isLoading?: boolean;
  onSelect?: (approval: Approval) => void;
}

const RISK_VARIANT: Record<ApprovalRiskLevel, BadgeVariant> = {
  low: 'low',
  medium: 'medium',
  high: 'high',
  critical: 'critical',
};

const STATUS_VARIANT: Record<ApprovalStatus, BadgeVariant> = {
  pending: 'warning',
  approved: 'success',
  rejected: 'offline',
  expired: 'neutral',
  executed: 'success',
};

export function ApprovalList({ approvals, isLoading, onSelect }: ApprovalListProps) {
  const columns: Column<Approval>[] = [
    {
      key: 'title',
      header: 'Request',
      sortable: true,
      sortValue: (a) => a.title.toLowerCase(),
      render: (a) => (
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100">{a.title}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {titleCase(a.action_type)}
          </p>
        </div>
      ),
    },
    {
      key: 'risk_level',
      header: 'Risk',
      sortable: true,
      sortValue: (a) => a.risk_level,
      render: (a) => <Badge variant={RISK_VARIANT[a.risk_level]}>{a.risk_level}</Badge>,
    },
    {
      key: 'requested_by',
      header: 'Requested By',
      render: (a) => a.requested_by,
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      sortValue: (a) => a.status,
      render: (a) => <Badge variant={STATUS_VARIANT[a.status]}>{a.status}</Badge>,
    },
    {
      key: 'requested_at',
      header: 'Requested',
      sortable: true,
      sortValue: (a) => new Date(a.requested_at).getTime(),
      render: (a) => formatRelative(a.requested_at),
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={approvals}
      rowKey={(a) => a.id}
      isLoading={isLoading}
      onRowClick={onSelect}
      emptyMessage="No approval requests"
      caption="List of approval requests"
    />
  );
}

export default ApprovalList;
