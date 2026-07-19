import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { Router } from 'lucide-react';
import { Card } from '../ui/Card';
import type { Device } from '../../types';

interface DeviceStatusCardProps {
  devices: Device[];
}

const STATUS_COLORS: Record<string, string> = {
  online: '#22c55e',
  offline: '#ef4444',
  unknown: '#a1a1aa',
};

export function DeviceStatusCard({ devices }: DeviceStatusCardProps) {
  const counts = devices.reduce<Record<string, number>>((acc, device) => {
    acc[device.status] = (acc[device.status] ?? 0) + 1;
    return acc;
  }, {});

  const data = (['online', 'offline', 'unknown'] as const)
    .map((status) => ({ name: status, value: counts[status] ?? 0 }))
    .filter((entry) => entry.value > 0);

  const total = devices.length;

  return (
    <Card className="p-5" as="section">
      <div className="flex items-center gap-2">
        <Router className="h-5 w-5 text-brand-600 dark:text-brand-400" aria-hidden="true" />
        <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">
          Device Status
        </h3>
      </div>

      {total === 0 ? (
        <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
          No devices reported yet.
        </p>
      ) : (
        <div className="mt-2 flex items-center gap-4">
          <div className="h-32 w-32 shrink-0">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={38}
                  outerRadius={60}
                  paddingAngle={2}
                >
                  {data.map((entry) => (
                    <Cell key={entry.name} fill={STATUS_COLORS[entry.name]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ borderRadius: 8, fontSize: 12 }}
                  formatter={(value: number, name: string) => [value, name]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="space-y-2 text-sm">
            {(['online', 'offline', 'unknown'] as const).map((status) => (
              <li key={status} className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: STATUS_COLORS[status] }}
                  aria-hidden="true"
                />
                <span className="capitalize text-gray-600 dark:text-gray-300">{status}</span>
                <span className="font-semibold text-gray-900 dark:text-gray-100">
                  {counts[status] ?? 0}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}

export default DeviceStatusCard;
