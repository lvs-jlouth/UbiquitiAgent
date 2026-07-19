import { useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { ClientList } from '../components/clients/ClientList';
import { ClientDetail } from '../components/clients/ClientDetail';
import { useClients } from '../hooks/useClients';
import type { Client } from '../types';

export function ClientsPage() {
  const { clients, isLoading, error, refresh } = useClients();
  const [selected, setSelected] = useState<Client | null>(null);

  return (
    <>
      <PageHeader
        title="Clients"
        description="Devices connected to your UniFi network"
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
        <Alert variant="error" className="mb-4" title="Failed to load clients">
          {error}
        </Alert>
      )}

      <ClientList clients={clients} isLoading={isLoading} onSelect={setSelected} />
      <ClientDetail client={selected} onClose={() => setSelected(null)} />
    </>
  );
}

export default ClientsPage;
