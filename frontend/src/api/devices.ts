import { apiClient } from './client';
import type { Device, DeviceStats } from '../types';

export async function fetchDevices(): Promise<Device[]> {
  const { data } = await apiClient.get<Device[]>('/devices');
  return data;
}

export async function fetchDevice(id: number): Promise<Device> {
  const { data } = await apiClient.get<Device>(`/devices/${id}`);
  return data;
}

export async function fetchDeviceStats(): Promise<DeviceStats> {
  const { data } = await apiClient.get<DeviceStats>('/devices/stats');
  return data;
}
