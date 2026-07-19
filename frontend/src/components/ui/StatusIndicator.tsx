import clsx from 'clsx';
import type { DeviceStatus } from '../../types';

interface StatusIndicatorProps {
  status: DeviceStatus | 'online' | 'offline' | 'unknown';
  label?: string;
  showLabel?: boolean;
  className?: string;
}

const COLORS: Record<string, { dot: string; text: string; ping: string }> = {
  online: {
    dot: 'bg-green-500',
    text: 'text-green-700 dark:text-green-400',
    ping: 'bg-green-400',
  },
  offline: {
    dot: 'bg-red-500',
    text: 'text-red-700 dark:text-red-400',
    ping: 'bg-red-400',
  },
  unknown: {
    dot: 'bg-gray-400',
    text: 'text-gray-600 dark:text-gray-400',
    ping: 'bg-gray-300',
  },
};

export function StatusIndicator({
  status,
  label,
  showLabel = true,
  className,
}: StatusIndicatorProps) {
  const colors = COLORS[status] ?? COLORS.unknown;
  const text = label ?? status;

  return (
    <span className={clsx('inline-flex items-center gap-2', className)}>
      <span className="relative flex h-2.5 w-2.5" aria-hidden="true">
        {status === 'online' && (
          <span
            className={clsx(
              'absolute inline-flex h-full w-full rounded-full opacity-75',
              colors.ping,
              'animate-ping'
            )}
          />
        )}
        <span className={clsx('relative inline-flex h-2.5 w-2.5 rounded-full', colors.dot)} />
      </span>
      {showLabel && (
        <span className={clsx('text-sm font-medium capitalize', colors.text)}>{text}</span>
      )}
      <span className="sr-only">{`Status: ${text}`}</span>
    </span>
  );
}

export default StatusIndicator;
