import { useCallback, useEffect, useState } from 'react';
import { fetchFindings, runAudit, updateFindingStatus } from '../api/audits';
import { extractErrorMessage } from '../api/client';
import type { AuditFinding, FindingStatus } from '../types';

interface UseAuditsResult {
  findings: AuditFinding[];
  isLoading: boolean;
  error: string | null;
  isRunning: boolean;
  refresh: () => Promise<void>;
  triggerAudit: () => Promise<void>;
  setStatus: (id: number, status: FindingStatus) => Promise<void>;
}

export function useAudits(): UseAuditsResult {
  const [findings, setFindings] = useState<AuditFinding[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchFindings();
      setFindings(data);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const triggerAudit = useCallback(async () => {
    setIsRunning(true);
    setError(null);
    try {
      await runAudit();
      await load();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsRunning(false);
    }
  }, [load]);

  const setStatus = useCallback(async (id: number, status: FindingStatus) => {
    const updated = await updateFindingStatus(id, status);
    setFindings((prev) => prev.map((f) => (f.id === id ? updated : f)));
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { findings, isLoading, error, isRunning, refresh: load, triggerAudit, setStatus };
}
