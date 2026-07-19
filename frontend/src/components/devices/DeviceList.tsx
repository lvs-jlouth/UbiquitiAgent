import { DataTable, type Column } from '../ui/DataTable';
import { StatusIndicator } from '../ui/StatusIndicator';
import { Badge } from '../ui/Badge';
import { formatRelative } from '../../utils/format';
import type { Device } from '../../types';

interface DeviceListProps {
  devices: Device[];
  isLoading?: boolean;
  onSelect?: (device: Device) => void;
}

const TYPE_LABELS: Record<Device['device_type'], string> = {
  gateway: 'Gateway',
  switch: 'Switch',
  ap: 'Access Point',
  other: 'Other',
};

export function DeviceList({ devices, isLoading, onSelect }: DeviceListProps) {
  const columns: Column<Device>[] = [
    {
      key: 'name',
      header: 'Name',
      sortable: true,
      sortValue: (d) => d.name.toLowerCase(),
      render: (d) => (
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100">{d.name}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{d.mac}</p>
        </div>
      ),
    },
    {
      key: 'device_type',
      header: 'Type',
      sortable: true,
      sortValue: (d) => d.device_type,
      render: (d) => <Badge variant="neutral">{TYPE_LABELS[d.device_type]}</Badge>,
    },
    {
      key: 'model',
      header: 'Model',
      sortable: true,
      sortValue: (d) => d.model,
    },
    {
      key: 'ip_address',
      header: 'IP Address',
      render: (d) => d.ip_address ?? '—',
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      sortValue: (d) => d.status,
      render: (d) => <StatusIndicator status={d.status} />,
    },
    {
      key: 'last_seen',
      header: 'Last Seen',
      sortable: true,
      sortValue: (d) => (d.last_seen ? new Date(d.last_seen).getTime() : 0),
      render: (d) => formatRelative(d.last_seen),
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={devices}
      rowKey={(d) => d.id}
      isLoading={isLoading}
      onRowClick={onSelect}
      emptyMessage="No devices found"
      caption="List of network devices"
    />
  );
}

export default DeviceList;
