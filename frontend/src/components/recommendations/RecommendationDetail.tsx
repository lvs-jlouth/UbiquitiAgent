import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Badge, severityToVariant } from '../ui/Badge';
import { titleCase } from '../../utils/format';
import type { Recommendation, RecommendationStatus } from '../../types';

interface RecommendationDetailProps {
  recommendation: Recommendation | null;
  onClose: () => void;
  onUpdateStatus?: (id: number, status: RecommendationStatus) => void;
}

export function RecommendationDetail({
  recommendation,
  onClose,
  onUpdateStatus,
}: RecommendationDetailProps) {
  if (!recommendation) return null;
  const rec = recommendation;

  const footer =
    onUpdateStatus && rec.status === 'proposed' ? (
      <>
        <Button variant="ghost" onClick={() => onUpdateStatus(rec.id, 'dismissed')}>
          Dismiss
        </Button>
        <Button variant="danger" onClick={() => onUpdateStatus(rec.id, 'rejected')}>
          Reject
        </Button>
        <Button variant="success" onClick={() => onUpdateStatus(rec.id, 'accepted')}>
          Accept
        </Button>
      </>
    ) : undefined;

  return (
    <Modal
      isOpen={!!rec}
      onClose={onClose}
      title={rec.title}
      size="lg"
      footer={footer}
    >
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <Badge variant={severityToVariant(rec.severity)}>{rec.severity}</Badge>
        <Badge variant="neutral">{titleCase(rec.category)}</Badge>
        <Badge variant="info">{rec.status}</Badge>
        {rec.requires_approval && <Badge variant="warning">Approval required</Badge>}
      </div>

      <section className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Summary</h4>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{rec.summary}</p>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Rationale
          </h4>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{rec.rationale}</p>
        </div>

        {rec.impact && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Impact</h4>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{rec.impact}</p>
          </div>
        )}

        {rec.actions.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              Proposed Actions
            </h4>
            <ul className="mt-2 space-y-2">
              {rec.actions.map((action) => (
                <li
                  key={action.id}
                  className="rounded-lg border border-gray-200 p-3 text-sm dark:border-gray-800"
                >
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-gray-700 dark:text-gray-300">{action.description}</p>
                    {action.automated ? (
                      <Badge variant="success">Automated</Badge>
                    ) : (
                      <Badge variant="neutral">Manual</Badge>
                    )}
                  </div>
                  {action.command && (
                    <pre className="mt-2 overflow-x-auto rounded bg-gray-50 p-2 font-mono text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300 scrollbar-thin">
                      {action.command}
                    </pre>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </Modal>
  );
}

export default RecommendationDetail;
