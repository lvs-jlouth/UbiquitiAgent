import { useCallback, useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { ApprovalList } from '../components/approvals/ApprovalList';
import { ApprovalDetail } from '../components/approvals/ApprovalDetail';
import {
  approveApproval,
  fetchApprovals,
  rejectApproval,
} from '../api/approvals';
import { extractErrorMessage } from '../api/client';
import type { Approval } from '../types';

export function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Approval | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setApprovals(await fetchApprovals());
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const applyDecision = async (
    id: number,
    action: (id: number, reason?: string) => Promise<Approval>,
    reason?: string
  ) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const updated = await action(id, reason);
      setApprovals((prev) => prev.map((a) => (a.id === id ? updated : a)));
      setSelected(null);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const pending = approvals.filter((a) => a.status === 'pending').length;

  return (
    <>
      <PageHeader
        title="Approvals"
        description="Review and authorize sensitive network actions"
        actions={
          <Button
            variant="secondary"
            onClick={() => void load()}
            leftIcon={<RefreshCw className="h-4 w-4" aria-hidden="true" />}
          >
            Refresh
          </Button>
        }
      />

      {error && (
        <Alert variant="error" className="mb-4" title="Approval error">
          {error}
        </Alert>
      )}

      {pending > 0 && (
        <Alert variant="warning" className="mb-4">
          {pending} approval request{pending === 1 ? '' : 's'} awaiting your review.
        </Alert>
      )}

      <ApprovalList approvals={approvals} isLoading={isLoading} onSelect={setSelected} />
      <ApprovalDetail
        approval={selected}
        onClose={() => setSelected(null)}
        onApprove={(id, reason) => void applyDecision(id, approveApproval, reason)}
        onReject={(id, reason) => void applyDecision(id, rejectApproval, reason)}
        isSubmitting={isSubmitting}
      />
    </>
  );
}

export default ApprovalsPage;
