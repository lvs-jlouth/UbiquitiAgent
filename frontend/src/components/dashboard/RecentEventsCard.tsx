import { Link } from 'react-router-dom';
import { Bell } from 'lucide-react';
import { Card, CardHeader } from '../ui/Card';
import { Badge, severityToVariant } from '../ui/Badge';
import { formatRelative } from '../../utils/format';
import type { Event } from '../../types';

interface RecentEventsCardProps {
  events: Event[];
  limit?: number;
}

export function RecentEventsCard({ events, limit = 6 }: RecentEventsCardProps) {
  const recent = [...events]
    .sort(
      (a, b) =>
        new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime()
    )
    .slice(0, limit);

  return (
    <Card as="section">
      <CardHeader
        title="Recent Events"
        icon={<Bell className="h-5 w-5" aria-hidden="true" />}
        action={
          <Link
            to="/events"
            className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
          >
            View all
          </Link>
        }
      />
      <ul className="divide-y divide-gray-100 dark:divide-gray-800" aria-live="polite">
        {recent.length === 0 ? (
          <li className="px-5 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
            No recent events.
          </li>
        ) : (
          recent.map((event) => (
            <li key={event.id} className="flex items-start gap-3 px-5 py-3">
              <Badge variant={severityToVariant(event.severity)}>{event.severity}</Badge>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-gray-800 dark:text-gray-200">
                  {event.message}
                </p>
                <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
                  <span className="capitalize">{event.category}</span> &middot;{' '}
                  {formatRelative(event.occurred_at)}
                </p>
              </div>
            </li>
          ))
        )}
      </ul>
    </Card>
  );
}

export default RecentEventsCard;
