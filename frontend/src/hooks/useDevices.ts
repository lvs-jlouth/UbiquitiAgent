import { useCallback, useEffect, useState } from 'react';
import { fetchDevices, fetchDevice } from '../api/devices';
import { extractErrorMessage } from '../api/client';
import type { Device } from '../types';

interface UseDevicesResult {
  devices: Device[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useDevices(): UseDevicesResult {
  const [devices, setDevices] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchDevices();
      setDevices(data);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { devices, isLoading, error, refresh: load };
}

interface UseDeviceResult {
  device: Device | null;
  isLoading: boolean;
  error: string | null;
}

export function useDevice(id: number | null): UseDeviceResult {
  const [device, setDevice] = useState<Device | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id == null) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);
    fetchDevice(id)
      .then((data) => {
        if (!cancelled) setDevice(data);
      })
      .catch((err) => {
        if (!cancelled) setError(extractErrorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  return { device, isLoading, error };
}
