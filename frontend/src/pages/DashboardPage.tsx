import { Link } from 'react-router-dom';
import { Router, Users, ShieldAlert, ClipboardList, RefreshCw } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { NetworkHealthCard } from '../components/dashboard/NetworkHealthCard';
import { DeviceStatusCard } from '../components/dashboard/DeviceStatusCard';
import { SecuritySummaryCard } from '../components/dashboard/SecuritySummaryCard';
import { RecentEventsCard } from '../components/dashboard/RecentEventsCard';
import { useDevices } from '../hooks/useDevices';
import { useClients } from '../hooks/useClients';
import { useEvents } from '../hooks/useEvents';
import { useAudits } from '../hooks/useAudits';
import type { ReactNode } from 'react';

interface StatCardProps {
  label: string;
  value: ReactNode;
  icon: ReactNode;
  accent: string;
  to: string;
}

function StatCard({ label, value, icon, accent, to }: StatCardProps) {
  return (
    <Link to={to} className="block focus:outline-none">
      <Card className="p-5 transition-shadow hover:shadow-md">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
            <p className="mt-1 text-3xl font-bold text-gray-900 dark:text-gray-100">
              {value}
            </p>
          </div>
          <span className={`flex h-12 w-12 items-center justify-center rounded-xl ${accent}`}>
            {icon}
          </span>
        </div>
      </Card>
    </Link>
  );
}

export function DashboardPage() {
  const devices = useDevices();
  const clients = useClients();
  const events = useEvents();
  const audits = useAudits();

  const isLoading =
    devices.isLoading && clients.isLoading && events.isLoading && audits.isLoading;
  const error = devices.error ?? clients.error ?? events.error ?? audits.error;

  const onlineDevices = devices.devices.filter((d) => d.status === 'online').length;
  const totalDevices = devices.devices.length;
  const onlineClients = clients.clients.filter((c) => c.is_online).length;
  const openFindings = audits.findings.filter((f) => f.status === 'open');
  const criticalEvents = events.events.filter(
    (e) => e.severity === 'critical' || e.severity === 'high'
  ).length;

  const healthScore =
    totalDevices === 0
      ? 100
      : Math.round(
          (onlineDevices / totalDevices) * 100 -
            openFindings.filter((f) => f.severity === 'critical').length * 8 -
            openFindings.filter((f) => f.severity === 'high').length * 4
        );

  const refreshAll = () => {
    void devices.refresh();
    void clients.refresh();
    void events.refresh();
    void audits.refresh();
  };

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Real-time overview of your UniFi network operations"
        actions={
          <Button
            variant="secondary"
            onClick={refreshAll}
            leftIcon={<RefreshCw className="h-4 w-4" aria-hidden="true" />}
          >
            Refresh
          </Button>
        }
      />

      {error && (
        <Alert variant="warning" className="mb-4" title="Some data could not be loaded">
          {error}
        </Alert>
      )}

      {isLoading ? (
        <LoadingSpinner fullPage label="Loading dashboard" />
      ) : (
        <div className="space-y-6">
          <section
            aria-label="Summary statistics"
            className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"
          >
            <StatCard
              label="Devices Online"
              value={`${onlineDevices}/${totalDevices}`}
              to="/devices"
              icon={<Router className="h-6 w-6 text-brand-600 dark:text-brand-400" />}
              accent="bg-brand-50 dark:bg-brand-950/60"
            />
            <StatCard
              label="Clients Connected"
              value={onlineClients}
              to="/clients"
              icon={<Users className="h-6 w-6 text-green-600 dark:text-green-400" />}
              accent="bg-green-50 dark:bg-green-950/60"
            />
            <StatCard
              label="Security Alerts"
              value={criticalEvents}
              to="/events"
              icon={<ShieldAlert className="h-6 w-6 text-red-600 dark:text-red-400" />}
              accent="bg-red-50 dark:bg-red-950/60"
            />
            <StatCard
              label="Audit Findings"
              value={openFindings.length}
              to="/audit"
              icon={<ClipboardList className="h-6 w-6 text-amber-600 dark:text-amber-400" />}
              accent="bg-amber-50 dark:bg-amber-950/60"
            />
          </section>

          <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <NetworkHealthCard
              score={healthScore}
              onlineDevices={onlineDevices}
              totalDevices={totalDevices}
            />
            <DeviceStatusCard devices={devices.devices} />
            <SecuritySummaryCard findings={audits.findings} />
          </section>

          <section>
            <RecentEventsCard events={events.events} />
          </section>
        </div>
      )}
    </>
  );
}

export default DashboardPage;
