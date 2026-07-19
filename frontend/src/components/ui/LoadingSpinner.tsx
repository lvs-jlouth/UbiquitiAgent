import clsx from 'clsx';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  className?: string;
  fullPage?: boolean;
}

const SIZES = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-10 w-10',
};

export function LoadingSpinner({
  size = 'md',
  label = 'Loading',
  className,
  fullPage = false,
}: LoadingSpinnerProps) {
  const spinner = (
    <div
      className={clsx('flex flex-col items-center justify-center gap-2', className)}
      role="status"
      aria-live="polite"
    >
      <Loader2
        className={clsx('animate-spin text-brand-600 dark:text-brand-400', SIZES[size])}
        aria-hidden="true"
      />
      <span className="sr-only">{label}</span>
    </div>
  );

  if (fullPage) {
    return (
      <div className="flex min-h-[50vh] w-full items-center justify-center">
        {spinner}
      </div>
    );
  }
  return spinner;
}

export default LoadingSpinner;
