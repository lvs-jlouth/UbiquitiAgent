import { apiClient } from './client';
import type { Client, ClientStats } from '../types';

export async function fetchClients(): Promise<Client[]> {
  const { data } = await apiClient.get<Client[]>('/clients');
  return data;
}

export async function fetchClient(id: number): Promise<Client> {
  const { data } = await apiClient.get<Client>(`/clients/${id}`);
  return data;
}

export async function fetchClientStats(): Promise<ClientStats> {
  const { data } = await apiClient.get<ClientStats>('/clients/stats');
  return data;
}
