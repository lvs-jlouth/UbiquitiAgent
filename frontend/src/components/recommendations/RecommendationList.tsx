import { Lightbulb } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge, severityToVariant, type BadgeVariant } from '../ui/Badge';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { titleCase } from '../../utils/format';
import type { Recommendation, RecommendationStatus } from '../../types';

interface RecommendationListProps {
  recommendations: Recommendation[];
  isLoading?: boolean;
  onSelect?: (recommendation: Recommendation) => void;
}

const STATUS_VARIANT: Record<RecommendationStatus, BadgeVariant> = {
  proposed: 'info',
  accepted: 'success',
  rejected: 'offline',
  applied: 'success',
  dismissed: 'neutral',
};

export function RecommendationList({
  recommendations,
  isLoading,
  onSelect,
}: RecommendationListProps) {
  if (isLoading) {
    return <LoadingSpinner fullPage label="Loading recommendations" />;
  }

  if (recommendations.length === 0) {
    return (
      <Card className="p-10">
        <div className="flex flex-col items-center gap-2 text-gray-400">
          <Lightbulb className="h-8 w-8" aria-hidden="true" />
          <p className="text-sm">No recommendations available yet.</p>
        </div>
      </Card>
    );
  }

  return (
    <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {recommendations.map((rec) => (
        <li key={rec.id}>
          <Card className="flex h-full flex-col p-5">
            <button
              type="button"
              onClick={() => onSelect?.(rec)}
              className="flex h-full flex-col text-left"
              aria-label={`View recommendation: ${rec.title}`}
            >
              <div className="flex items-start justify-between gap-2">
                <Badge variant={severityToVariant(rec.severity)}>{rec.severity}</Badge>
                <Badge variant={STATUS_VARIANT[rec.status]}>{rec.status}</Badge>
              </div>
              <h3 className="mt-3 text-base font-semibold text-gray-900 dark:text-gray-100">
                {rec.title}
              </h3>
              <p className="mt-1 flex-1 text-sm text-gray-600 dark:text-gray-300">
                {rec.summary}
              </p>
              <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                <Badge variant="neutral">{titleCase(rec.category)}</Badge>
                {rec.effort && <span>Effort: {rec.effort}</span>}
                {rec.requires_approval && (
                  <Badge variant="warning">Approval required</Badge>
                )}
              </div>
            </button>
          </Card>
        </li>
      ))}
    </ul>
  );
}

export default RecommendationList;
