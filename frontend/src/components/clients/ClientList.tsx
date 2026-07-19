import { DataTable, type Column } from '../ui/DataTable';
import { StatusIndicator } from '../ui/StatusIndicator';
import { Badge } from '../ui/Badge';
import { formatBytes, formatRelative } from '../../utils/format';
import type { Client } from '../../types';

interface ClientListProps {
  clients: Client[];
  isLoading?: boolean;
  onSelect?: (client: Client) => void;
}

export function ClientList({ clients, isLoading, onSelect }: ClientListProps) {
  const columns: Column<Client>[] = [
    {
      key: 'name',
      header: 'Client',
      sortable: true,
      sortValue: (c) => (c.name ?? c.hostname ?? c.mac).toLowerCase(),
      render: (c) => (
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100">
            {c.name ?? c.hostname ?? 'Unknown'}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{c.mac}</p>
        </div>
      ),
    },
    {
      key: 'ip_address',
      header: 'IP Address',
      render: (c) => c.ip_address ?? '—',
    },
    {
      key: 'connection_type',
      header: 'Connection',
      sortable: true,
      sortValue: (c) => c.connection_type,
      render: (c) => (
        <Badge variant="neutral">
          {c.connection_type}
          {c.ssid ? ` · ${c.ssid}` : ''}
        </Badge>
      ),
    },
    {
      key: 'is_guest',
      header: 'Guest',
      render: (c) =>
        c.is_guest ? <Badge variant="warning">Guest</Badge> : <span>—</span>,
    },
    {
      key: 'traffic',
      header: 'Traffic (Rx / Tx)',
      align: 'right',
      render: (c) => `${formatBytes(c.rx_bytes)} / ${formatBytes(c.tx_bytes)}`,
    },
    {
      key: 'is_online',
      header: 'Status',
      sortable: true,
      sortValue: (c) => (c.is_online ? 1 : 0),
      render: (c) => (
        <StatusIndicator status={c.is_online ? 'online' : 'offline'} />
      ),
    },
    {
      key: 'last_seen',
      header: 'Last Seen',
      sortable: true,
      sortValue: (c) => (c.last_seen ? new Date(c.last_seen).getTime() : 0),
      render: (c) => formatRelative(c.last_seen),
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={clients}
      rowKey={(c) => c.id}
      isLoading={isLoading}
      onRowClick={onSelect}
      emptyMessage="No clients found"
      caption="List of connected clients"
    />
  );
}

export default ClientList;
