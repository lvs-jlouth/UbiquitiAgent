import { RadialBar, RadialBarChart, PolarAngleAxis, ResponsiveContainer } from 'recharts';
import { Activity } from 'lucide-react';
import { Card } from '../ui/Card';

interface NetworkHealthCardProps {
  score: number;
  onlineDevices: number;
  totalDevices: number;
}

function healthColor(score: number): string {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#eab308';
  if (score >= 40) return '#f97316';
  return '#ef4444';
}

function healthLabel(score: number): string {
  if (score >= 80) return 'Healthy';
  if (score >= 60) return 'Fair';
  if (score >= 40) return 'Degraded';
  return 'Critical';
}

export function NetworkHealthCard({
  score,
  onlineDevices,
  totalDevices,
}: NetworkHealthCardProps) {
  const clamped = Math.max(0, Math.min(100, Math.round(score)));
  const color = healthColor(clamped);
  const data = [{ name: 'health', value: clamped, fill: color }];

  return (
    <Card className="p-5" as="section">
      <div className="flex items-center gap-2">
        <Activity className="h-5 w-5 text-brand-600 dark:text-brand-400" aria-hidden="true" />
        <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">
          Network Health
        </h3>
      </div>
      <div className="mt-2 flex items-center gap-4">
        <div className="relative h-32 w-32 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              innerRadius="72%"
              outerRadius="100%"
              data={data}
              startAngle={90}
              endAngle={-270}
            >
              <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
              <RadialBar background dataKey="value" cornerRadius={12} />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {clamped}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">/ 100</span>
          </div>
        </div>
        <div>
          <p className="text-lg font-semibold" style={{ color }}>
            {healthLabel(clamped)}
          </p>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {onlineDevices} of {totalDevices} devices online
          </p>
        </div>
      </div>
    </Card>
  );
}

export default NetworkHealthCard;
