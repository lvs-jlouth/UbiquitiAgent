export type ConnectionType = 'wired' | 'wireless';

export interface Client {
  id: number;
  mac: string;
  hostname: string | null;
  name: string | null;
  ip_address: string | null;
  connection_type: ConnectionType;
  is_online: boolean;
  is_guest: boolean;
  device_id: number | null;
  ssid: string | null;
  vlan: number | null;
  signal_strength: number | null;
  rx_bytes: number;
  tx_bytes: number;
  os_name: string | null;
  first_seen: string | null;
  last_seen: string | null;
  created_at: string;
  updated_at: string;
}

export interface ClientStats {
  total: number;
  online: number;
  guests: number;
  wired: number;
  wireless: number;
}
