import clsx from 'clsx';
import type { ReactNode } from 'react';
import { AlertCircle, CheckCircle2, Info, XCircle } from 'lucide-react';

type AlertVariant = 'info' | 'success' | 'warning' | 'error';

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children?: ReactNode;
  className?: string;
}

const CONFIG: Record<
  AlertVariant,
  { container: string; icon: ReactNode; iconColor: string }
> = {
  info: {
    container:
      'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-950/40 dark:border-blue-900 dark:text-blue-200',
    icon: <Info className="h-5 w-5" aria-hidden="true" />,
    iconColor: 'text-blue-500',
  },
  success: {
    container:
      'bg-green-50 border-green-200 text-green-800 dark:bg-green-950/40 dark:border-green-900 dark:text-green-200',
    icon: <CheckCircle2 className="h-5 w-5" aria-hidden="true" />,
    iconColor: 'text-green-500',
  },
  warning: {
    container:
      'bg-amber-50 border-amber-200 text-amber-800 dark:bg-amber-950/40 dark:border-amber-900 dark:text-amber-200',
    icon: <AlertCircle className="h-5 w-5" aria-hidden="true" />,
    iconColor: 'text-amber-500',
  },
  error: {
    container:
      'bg-red-50 border-red-200 text-red-800 dark:bg-red-950/40 dark:border-red-900 dark:text-red-200',
    icon: <XCircle className="h-5 w-5" aria-hidden="true" />,
    iconColor: 'text-red-500',
  },
};

export function Alert({ variant = 'info', title, children, className }: AlertProps) {
  const config = CONFIG[variant];
  return (
    <div
      role="alert"
      className={clsx('flex gap-3 rounded-lg border p-4', config.container, className)}
    >
      <span className={config.iconColor}>{config.icon}</span>
      <div className="text-sm">
        {title && <p className="font-semibold">{title}</p>}
        {children && <div className={clsx(title && 'mt-1')}>{children}</div>}
      </div>
    </div>
  );
}

export default Alert;
