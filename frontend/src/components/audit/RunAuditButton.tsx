import { Play } from 'lucide-react';
import { Button } from '../ui/Button';

interface RunAuditButtonProps {
  onRun: () => void;
  isRunning: boolean;
}

export function RunAuditButton({ onRun, isRunning }: RunAuditButtonProps) {
  return (
    <Button
      onClick={onRun}
      isLoading={isRunning}
      leftIcon={<Play className="h-4 w-4" aria-hidden="true" />}
      aria-label="Run network audit"
    >
      {isRunning ? 'Running Audit…' : 'Run Audit'}
    </Button>
  );
}

export default RunAuditButton;
