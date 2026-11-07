import React, { useState } from 'react';
import {
  Share2,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Plus,
  Clock
} from 'lucide-react';

interface ProcurementSourcesViewProps {
  sources?: any[];
}

export const ProcurementSourcesView: React.FC<ProcurementSourcesViewProps> = ({
  sources = [],
}) => {
  const [syncing, setSyncing] = useState<string | null>(null);

  const defaultSources = [
    {
      id: 'src-1',
      name: 'System for Award Management (SAM.gov)',
      connector_type: 'US Federal API',
      region: 'North America / Federal',
      status: 'ACTIVE',
      last_sync_at: '12m ago',
      records_synced: 1420,
      sync_interval_hours: 1,
    },
    {
      id: 'src-2',
      name: 'Tenders Electronic Daily (TED Europa)',
      connector_type: 'EU TED XML Feed',
      region: 'European Union',
      status: 'ACTIVE',
      last_sync_at: '45m ago',
      records_synced: 890,
      sync_interval_hours: 2,
    },
    {
      id: 'src-3',
      name: 'Government e-Marketplace (GeM)',
      connector_type: 'GeM Portal Crawler',
      region: 'Asia-Pacific / India',
      status: 'ACTIVE',
      last_sync_at: '1h ago',
      records_synced: 640,
      sync_interval_hours: 4,
    },
    {
      id: 'src-4',
      name: 'UK Find a Tender Service (FTS)',
      connector_type: 'UK Cabinet Office API',
      region: 'United Kingdom',
      status: 'ACTIVE',
      last_sync_at: '2h ago',
      records_synced: 320,
      sync_interval_hours: 4,
    },
  ];

  const items = sources.length > 0 ? sources : defaultSources;

  const handleSync = (id: string) => {
    setSyncing(id);
    setTimeout(() => {
      setSyncing(null);
    }, 1500);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Share2 className="w-5 h-5 text-cyan-400" />
            Procurement Source Connectors & Feed Ingestion
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Automated integrations with global procurement portals, e-tendering gateways, and government public registries.
          </p>
        </div>
        <button
          onClick={() => alert('Add Connector: Enter portal endpoint and API credentials.')}
          className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
        >
          <Plus className="w-3.5 h-3.5" /> Connect Portal Feed
        </button>
      </div>

      {/* Sources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map((src: any) => (
          <div
            key={src.id}
            className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg flex flex-col justify-between space-y-4 hover:border-navy-700 transition"
          >
            <div>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-bold text-sm text-white">{src.name}</h3>
                  <span className="text-[11px] font-mono text-cyan-400 font-semibold">{src.connector_type}</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> {src.status || 'ACTIVE'}
                </span>
              </div>

              <div className="text-xs text-slate-300 mt-2 font-mono">
                Jurisdiction: <span className="text-white">{src.region}</span>
              </div>
            </div>

            <div className="pt-3 border-t border-navy-700/60 flex items-center justify-between text-xs font-mono">
              <div className="text-slate-400">
                <span>Last Sync: {src.last_sync_at || 'Just now'}</span>
                <span className="block text-[10px] text-slate-500">
                  {src.records_synced || 0} notices ingested
                </span>
              </div>
              <button
                onClick={() => handleSync(src.id)}
                disabled={syncing === src.id}
                className="px-3 py-1.5 bg-navy-900 hover:bg-navy-800 text-cyan-400 hover:text-cyan-300 rounded-lg border border-navy-700 flex items-center gap-1.5 transition disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${syncing === src.id ? 'animate-spin' : ''}`} />
                {syncing === src.id ? 'Syncing...' : 'Sync Now'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

