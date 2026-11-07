import React from 'react';
import {
  Activity,
  Bell,
  Clock,
  Shield,
  CheckCircle2,
  AlertTriangle,
  Camera,
  ArrowRight
} from 'lucide-react';
import { Tender } from '../../types';

interface TenderMonitoringViewProps {
  activeTender?: Tender;
  onNavigateTab: (tabId: string) => void;
}

export const TenderMonitoringView: React.FC<TenderMonitoringViewProps> = ({
  activeTender,
  onNavigateTab,
}) => {
  const subscriptions = [
    {
      id: 'sub-1',
      tender_ref: 'DOD-DISA-2026',
      title: 'Joint Multi-Domain Command & Control (JADC2) Cloud Integration',
      frequency: 'Every 30 minutes',
      notify_channels: ['email', 'in_app', 'switch_war_room'],
      last_check: '8m ago',
      status: 'MONITORING',
      detected_amendments: 2,
    },
    {
      id: 'sub-2',
      tender_ref: 'TND-2026-CLOUD-901',
      title: 'Pursuit: Sovereign Cloud Infrastructure Modernization',
      frequency: 'Every 60 minutes',
      notify_channels: ['email', 'in_app'],
      last_check: '15m ago',
      status: 'MONITORING',
      detected_amendments: 1,
    },
    {
      id: 'sub-3',
      tender_ref: 'RFP-2026-001',
      title: 'National Telecom & Cloud Infrastructure',
      frequency: 'Every 120 minutes',
      notify_channels: ['in_app'],
      last_check: '32m ago',
      status: 'MONITORING',
      detected_amendments: 0,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            Active Tender Monitoring & Live Polling
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Automated crawler subscriptions, corrigendum polling, deadline extensions, and notification alerts.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('amendments')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Inspect Amendments <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Monitoring Subscriptions Table */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900/90 text-slate-400 border-b border-navy-700/60">
              <tr>
                <th className="p-3.5">Monitored Pursuit</th>
                <th className="p-3.5">Polling Cadence</th>
                <th className="p-3.5">Notification Channels</th>
                <th className="p-3.5">Last Verified Check</th>
                <th className="p-3.5">Detected Amendments</th>
                <th className="p-3.5 text-right">Monitoring Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-700/40 text-slate-300">
              {subscriptions.map((sub) => (
                <tr key={sub.id} className="hover:bg-navy-800/60 transition">
                  <td className="p-3.5 max-w-sm">
                    <div className="font-bold text-white text-xs">{sub.tender_ref}</div>
                    <div className="text-[11px] text-slate-400 truncate mt-0.5">{sub.title}</div>
                  </td>
                  <td className="p-3.5 font-mono text-cyan-400">
                    {sub.frequency}
                  </td>
                  <td className="p-3.5">
                    <div className="flex gap-1">
                      {sub.notify_channels.map((ch) => (
                        <span key={ch} className="px-2 py-0.5 rounded text-[10px] font-mono bg-navy-900 border border-navy-750 text-slate-300">
                          {ch}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="p-3.5 text-slate-400 font-mono">
                    {sub.last_check}
                  </td>
                  <td className="p-3.5 font-mono font-bold text-amber-400">
                    {sub.detected_amendments} Corrigenda
                  </td>
                  <td className="p-3.5 text-right">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 inline-flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> {sub.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
