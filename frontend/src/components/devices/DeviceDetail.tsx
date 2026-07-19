import { Modal } from '../ui/Modal';
import { StatusIndicator } from '../ui/StatusIndicator';
import { Badge } from '../ui/Badge';
import { formatDate, formatRelative } from '../../utils/format';
import type { Device } from '../../types';

interface DeviceDetailProps {
  device: Device | null;
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

export function DeviceDetail({ device, onClose }: DeviceDetailProps) {
  if (!device) return null;

  return (
    <Modal isOpen={!!device} onClose={onClose} title={device.name} size="md">
      <div className="mb-4 flex items-center justify-between">
        <StatusIndicator status={device.status} />
        <Badge variant="neutral">{device.device_type}</Badge>
      </div>
      <dl className="divide-y divide-gray-100 dark:divide-gray-800">
        <Row label="MAC Address" value={device.mac} />
        <Row label="Model" value={device.model} />
        <Row label="Firmware" value={device.firmware_version ?? '—'} />
        <Row label="IP Address" value={device.ip_address ?? '—'} />
        <Row label="Site" value={device.site_id ?? '—'} />
        <Row label="Last Seen" value={formatRelative(device.last_seen)} />
        <Row label="First Registered" value={formatDate(device.created_at)} />
        <Row label="Updated" value={formatDate(device.updated_at)} />
      </dl>
    </Modal>
  );
}

export default DeviceDetail;
