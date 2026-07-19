import clsx from 'clsx';
import type { ReactNode } from 'react';

export type BadgeVariant =
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'
  | 'info'
  | 'online'
  | 'offline'
  | 'unknown'
  | 'neutral'
  | 'success'
  | 'warning';

const VARIANT_STYLES: Record<BadgeVariant, string> = {
  critical: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300',
  high: 'bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-300',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-300',
  low: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300',
  info: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
  online: 'bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300',
  offline: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300',
  unknown: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
  neutral: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
  success: 'bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300',
  warning: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300',
};

interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  className?: string;
}

export function Badge({ variant = 'neutral', children, className }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize',
        VARIANT_STYLES[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function severityToVariant(severity: string): BadgeVariant {
  switch (severity) {
    case 'critical':
    case 'high':
    case 'medium':
    case 'low':
    case 'info':
      return severity;
    default:
      return 'neutral';
  }
}

export default Badge;
