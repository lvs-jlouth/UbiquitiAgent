export type DeviceType = 'gateway' | 'switch' | 'ap' | 'other';
export type DeviceStatus = 'online' | 'offline' | 'unknown';

export interface Device {
  id: number;
  mac: string;
  name: string;
  device_type: DeviceType;
  model: string;
  firmware_version: string | null;
  ip_address: string | null;
  status: DeviceStatus;
  site_id: string | null;
  last_seen: string | null;
  created_at: string;
  updated_at: string;
}

export interface DeviceStats {
  total: number;
  online: number;
  offline: number;
  unknown: number;
  by_type: Record<DeviceType, number>;
}
