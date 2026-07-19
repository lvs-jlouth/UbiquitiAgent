import { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { formatDate, titleCase } from '../../utils/format';
import type { Approval } from '../../types';

interface ApprovalDetailProps {
  approval: Approval | null;
  onClose: () => void;
  onApprove?: (id: number, reason?: string) => void;
  onReject?: (id: number, reason?: string) => void;
  isSubmitting?: boolean;
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 py-2">
      <dt className="text-sm text-gray-500 dark:text-gray-400">{label}</dt>
      <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">{value}</dd>
    </div>
  );
}

export function ApprovalDetail({
  approval,
  onClose,
  onApprove,
  onReject,
  isSubmitting = false,
}: ApprovalDetailProps) {
  const [reason, setReason] = useState('');

  if (!approval) return null;
  const isPending = approval.status === 'pending';

  const footer =
    isPending && (onApprove || onReject) ? (
      <>
        {onReject && (
          <Button
            variant="danger"
            isLoading={isSubmitting}
            onClick={() => onReject(approval.id, reason || undefined)}
          >
            Reject
          </Button>
        )}
        {onApprove && (
          <Button
            variant="success"
            isLoading={isSubmitting}
            onClick={() => onApprove(approval.id, reason || undefined)}
          >
            Approve
          </Button>
        )}
      </>
    ) : undefined;

  return (
    <Modal
      isOpen={!!approval}
      onClose={onClose}
      title={approval.title}
      size="lg"
      footer={footer}
    >
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <Badge
          variant={
            approval.risk_level === 'critical'
              ? 'critical'
              : approval.risk_level === 'high'
                ? 'high'
                : approval.risk_level === 'medium'
                  ? 'medium'
                  : 'low'
          }
        >
          {approval.risk_level} risk
        </Badge>
        <Badge variant="info">{approval.status}</Badge>
      </div>

      <p className="text-sm text-gray-600 dark:text-gray-300">{approval.description}</p>

      <dl className="mt-4 divide-y divide-gray-100 dark:divide-gray-800">
        <Row label="Action Type" value={titleCase(approval.action_type)} />
        <Row label="Requested By" value={approval.requested_by} />
        <Row label="Requested At" value={formatDate(approval.requested_at)} />
        {approval.reviewed_by && <Row label="Reviewed By" value={approval.reviewed_by} />}
        {approval.reviewed_at && (
          <Row label="Reviewed At" value={formatDate(approval.reviewed_at)} />
        )}
        {approval.expires_at && (
          <Row label="Expires" value={formatDate(approval.expires_at)} />
        )}
        {approval.reason && <Row label="Reason" value={approval.reason} />}
      </dl>

      {approval.payload && Object.keys(approval.payload).length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Payload</h4>
          <pre className="mt-1 overflow-x-auto rounded-lg bg-gray-50 p-3 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300 scrollbar-thin">
            {JSON.stringify(approval.payload, null, 2)}
          </pre>
        </div>
      )}

      {isPending && (onApprove || onReject) && (
        <div className="mt-4">
          <label
            htmlFor="approval-reason"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Decision note (optional)
          </label>
          <textarea
            id="approval-reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={2}
            className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
            placeholder="Add context for this decision…"
          />
        </div>
      )}
    </Modal>
  );
}

export default ApprovalDetail;
