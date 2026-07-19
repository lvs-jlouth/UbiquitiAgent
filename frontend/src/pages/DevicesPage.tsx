import { useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { DeviceList } from '../components/devices/DeviceList';
import { DeviceDetail } from '../components/devices/DeviceDetail';
import { useDevices } from '../hooks/useDevices';
import type { Device } from '../types';

export function DevicesPage() {
  const { devices, isLoading, error, refresh } = useDevices();
  const [selected, setSelected] = useState<Device | null>(null);

  return (
    <>
      <PageHeader
        title="Devices"
        description="UniFi infrastructure devices across your sites"
        actions={
          <Button
            variant="secondary"
            onClick={() => void refresh()}
            leftIcon={<RefreshCw className="h-4 w-4" aria-hidden="true" />}
          >
            Refresh
          </Button>
        }
      />

      {error && (
        <Alert variant="error" className="mb-4" title="Failed to load devices">
          {error}
        </Alert>
      )}

      <DeviceList devices={devices} isLoading={isLoading} onSelect={setSelected} />
      <DeviceDetail device={selected} onClose={() => setSelected(null)} />
    </>
  );
}

export default DevicesPage;
