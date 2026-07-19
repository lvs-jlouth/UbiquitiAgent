import { Modal } from '../ui/Modal';
import { StatusIndicator } from '../ui/StatusIndicator';
import { Badge } from '../ui/Badge';
import { formatBytes, formatDate, formatRelative } from '../../utils/format';
import type { Client } from '../../types';

interface ClientDetailProps {
  client: Client | null;
  onClose: () => void;
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 py-2">
      <dt className="text-sm text-gray-500 dark:text-gray-400">{label}</dt>
      <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">{value}</dd>
    </div>
  );
}

export function ClientDetail({ client, onClose }: ClientDetailProps) {
  if (!client) return null;
  const title = client.name ?? client.hostname ?? client.mac;

  return (
    <Modal isOpen={!!client} onClose={onClose} title={title} size="md">
      <div className="mb-4 flex items-center justify-between">
        <StatusIndicator status={client.is_online ? 'online' : 'offline'} />
        <div className="flex gap-2">
          <Badge variant="neutral">{client.connection_type}</Badge>
          {client.is_guest && <Badge variant="warning">Guest</Badge>}
        </div>
      </div>
      <dl className="divide-y divide-gray-100 dark:divide-gray-800">
        <Row label="MAC Address" value={client.mac} />
        <Row label="Hostname" value={client.hostname ?? '—'} />
        <Row label="IP Address" value={client.ip_address ?? '—'} />
        <Row label="SSID" value={client.ssid ?? '—'} />
        <Row label="VLAN" value={client.vlan ?? '—'} />
        <Row
          label="Signal"
          value={client.signal_strength != null ? `${client.signal_strength} dBm` : '—'}
        />
        <Row label="Operating System" value={client.os_name ?? '—'} />
        <Row label="Received" value={formatBytes(client.rx_bytes)} />
        <Row label="Transmitted" value={formatBytes(client.tx_bytes)} />
        <Row label="First Seen" value={formatDate(client.first_seen)} />
        <Row label="Last Seen" value={formatRelative(client.last_seen)} />
      </dl>
    </Modal>
  );
}

export default ClientDetail;
