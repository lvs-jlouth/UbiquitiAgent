import { apiClient } from './client';
import type { Recommendation, RecommendationStatus } from '../types';

export async function fetchRecommendations(): Promise<Recommendation[]> {
  const { data } = await apiClient.get<Recommendation[]>('/recommendations');
  return data;
}

export async function fetchRecommendation(id: number): Promise<Recommendation> {
  const { data } = await apiClient.get<Recommendation>(`/recommendations/${id}`);
  return data;
}

export async function updateRecommendationStatus(
  id: number,
  status: RecommendationStatus
): Promise<Recommendation> {
  const { data } = await apiClient.patch<Recommendation>(
    `/recommendations/${id}`,
    { status }
  );
  return data;
}
