import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Badge, severityToVariant } from '../ui/Badge';
import { formatDate, titleCase } from '../../utils/format';
import type { AuditFinding, FindingStatus } from '../../types';

interface AuditFindingDetailProps {
  finding: AuditFinding | null;
  onClose: () => void;
  onUpdateStatus?: (id: number, status: FindingStatus) => void;
}

export function AuditFindingDetail({
  finding,
  onClose,
  onUpdateStatus,
}: AuditFindingDetailProps) {
  if (!finding) return null;

  const footer = onUpdateStatus ? (
    <>
      {finding.status !== 'acknowledged' && (
        <Button
          variant="secondary"
          onClick={() => onUpdateStatus(finding.id, 'acknowledged')}
        >
          Acknowledge
        </Button>
      )}
      {finding.status !== 'suppressed' && (
        <Button
          variant="ghost"
          onClick={() => onUpdateStatus(finding.id, 'suppressed')}
        >
          Suppress
        </Button>
      )}
      {finding.status !== 'resolved' && (
        <Button variant="success" onClick={() => onUpdateStatus(finding.id, 'resolved')}>
          Mark Resolved
        </Button>
      )}
    </>
  ) : undefined;

  return (
    <Modal
      isOpen={!!finding}
      onClose={onClose}
      title={finding.title}
      size="lg"
      footer={footer}
    >
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <Badge variant={severityToVariant(finding.severity)}>{finding.severity}</Badge>
        <Badge variant="neutral">{titleCase(finding.category)}</Badge>
        <Badge variant="info">{finding.status}</Badge>
        <span className="text-xs text-gray-400">{finding.rule_id}</span>
      </div>

      <section className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Description
          </h4>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
            {finding.description}
          </p>
        </div>

        {finding.affected_resource && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              Affected Resource
            </h4>
            <p className="mt-1 font-mono text-sm text-gray-600 dark:text-gray-300">
              {finding.affected_resource}
            </p>
          </div>
        )}

        {finding.remediation && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              Recommended Remediation
            </h4>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
              {finding.remediation}
            </p>
          </div>
        )}

        {finding.details && Object.keys(finding.details).length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              Details
            </h4>
            <pre className="mt-1 overflow-x-auto rounded-lg bg-gray-50 p-3 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300 scrollbar-thin">
              {JSON.stringify(finding.details, null, 2)}
            </pre>
          </div>
        )}

        <p className="text-xs text-gray-400">
          Detected {formatDate(finding.detected_at)}
        </p>
      </section>
    </Modal>
  );
}

export default AuditFindingDetail;
