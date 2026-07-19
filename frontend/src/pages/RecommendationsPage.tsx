import { useCallback, useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { RecommendationList } from '../components/recommendations/RecommendationList';
import { RecommendationDetail } from '../components/recommendations/RecommendationDetail';
import {
  fetchRecommendations,
  updateRecommendationStatus,
} from '../api/recommendations';
import { extractErrorMessage } from '../api/client';
import type { Recommendation, RecommendationStatus } from '../types';

export function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Recommendation | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setRecommendations(await fetchRecommendations());
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleStatus = async (id: number, status: RecommendationStatus) => {
    try {
      const updated = await updateRecommendationStatus(id, status);
      setRecommendations((prev) => prev.map((r) => (r.id === id ? updated : r)));
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSelected(null);
    }
  };

  return (
    <>
      <PageHeader
        title="Recommendations"
        description="AI-generated recommendations to optimize and secure your network"
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
        <Alert variant="error" className="mb-4" title="Failed to load recommendations">
          {error}
        </Alert>
      )}

      <RecommendationList
        recommendations={recommendations}
        isLoading={isLoading}
        onSelect={setSelected}
      />
      <RecommendationDetail
        recommendation={selected}
        onClose={() => setSelected(null)}
        onUpdateStatus={handleStatus}
      />
    </>
  );
}

export default RecommendationsPage;
