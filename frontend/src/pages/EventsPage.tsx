import { useMemo, useState } from 'react';
import { Check, RefreshCw } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { Badge, severityToVariant } from '../components/ui/Badge';
import { DataTable, type Column } from '../components/ui/DataTable';
import { useEvents } from '../hooks/useEvents';
import { formatRelative, titleCase } from '../utils/format';
import type { Event, Severity } from '../types';

const SEVERITIES: (Severity | 'all')[] = ['all', 'critical', 'high', 'medium', 'low', 'info'];

export function EventsPage() {
  const { events, isLoading, error, refresh, acknowledge } = useEvents();
  const [filter, setFilter] = useState<Severity | 'all'>('all');

  const filtered = useMemo(
    () => (filter === 'all' ? events : events.filter((e) => e.severity === filter)),
    [events, filter]
  );

  const columns: Column<Event>[] = [
    {
      key: 'severity',
      header: 'Severity',
      sortable: true,
      sortValue: (e) => e.severity,
      render: (e) => <Badge variant={severityToVariant(e.severity)}>{e.severity}</Badge>,
    },
    {
      key: 'message',
      header: 'Message',
      render: (e) => (
        <span className="text-gray-800 dark:text-gray-200">{e.message}</span>
      ),
    },
    {
      key: 'category',
      header: 'Category',
      sortable: true,
      sortValue: (e) => e.category,
      render: (e) => <Badge variant="neutral">{titleCase(e.category)}</Badge>,
    },
    {
      key: 'source',
      header: 'Source',
      render: (e) => e.source ?? '—',
    },
    {
      key: 'occurred_at',
      header: 'Occurred',
      sortable: true,
      sortValue: (e) => new Date(e.occurred_at).getTime(),
      render: (e) => formatRelative(e.occurred_at),
    },
    {
      key: 'actions',
      header: 'Ack',
      align: 'right',
      render: (e) =>
        e.acknowledged ? (
          <Badge variant="success">Acknowledged</Badge>
        ) : (
          <Button
            size="sm"
            variant="ghost"
            leftIcon={<Check className="h-3.5 w-3.5" aria-hidden="true" />}
            onClick={(evt) => {
              evt.stopPropagation();
              void acknowledge(e.id);
            }}
            aria-label={`Acknowledge event: ${e.message}`}
          >
            Ack
          </Button>
        ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Events"
        description="Network events, alerts, and system notifications"
        actions={
          <Button
            variant="secondary"
            onClick={() => void refresh()}
            leftIcon={<RefreshCw className="h-4 w-4" aria-hidden="true" />}
          >
            Refresh
          </Button>
        }
      />

      {error && (
        <Alert variant="error" className="mb-4" title="Failed to load events">
          {error}
        </Alert>
      )}

      <div
        className="mb-4 flex flex-wrap gap-2"
        role="group"
        aria-label="Filter events by severity"
      >
        {SEVERITIES.map((severity) => (
          <button
            key={severity}
            type="button"
            onClick={() => setFilter(severity)}
            aria-pressed={filter === severity}
            className={
              filter === severity
                ? 'rounded-full bg-brand-600 px-3 py-1 text-sm font-medium text-white'
                : 'rounded-full border border-gray-300 px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800'
            }
          >
            {severity === 'all' ? 'All' : titleCase(severity)}
          </button>
        ))}
      </div>

      <DataTable
        columns={columns}
        data={filtered}
        rowKey={(e) => e.id}
        isLoading={isLoading}
        emptyMessage="No events match the selected filter"
        caption="List of network events"
        pageSize={15}
      />
    </>
  );
}

export default EventsPage;
