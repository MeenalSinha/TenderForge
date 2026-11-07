import React, { useState } from 'react';
import {
  Settings,
  Shield,
  Save,
  CheckCircle2,
  Lock,
  Zap,
  Server,
  Database
} from 'lucide-react';

interface SettingsViewProps {
  switchStatus: any;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  switchStatus,
}) => {
  const [switchUrl, setSwitchUrl] = useState('http://localhost:8765');
  const [retentionDays, setRetentionDays] = useState('2555'); // 7 years federal compliance
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Settings className="w-5 h-5 text-cyan-400" />
            System Governance & Switch Security Settings
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Enterprise connectivity parameters, Switch broker endpoints, and cryptographic log retention rules.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {saved && (
            <span className="text-xs text-emerald-400 font-medium flex items-center gap-1 animate-fade-in">
              <CheckCircle2 className="w-3.5 h-3.5" /> Settings Saved
            </span>
          )}
          <button
            onClick={handleSave}
            className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            <Save className="w-3.5 h-3.5" /> Save Configuration
          </button>
        </div>
      </div>

      {/* Switch Broker Settings Card */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl p-6 shadow-lg space-y-4">
        <h3 className="font-bold text-sm text-white flex items-center gap-2 pb-3 border-b border-navy-700/60">
          <Zap className="w-4 h-4 text-cyan-400" /> Switch Mesh Integration Broker
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Switch Endpoint URL</label>
            <input
              type="text"
              value={switchUrl}
              onChange={(e) => setSwitchUrl(e.target.value)}
              className="w-full px-3 py-2 bg-navy-950 border border-navy-700 rounded-xl text-white font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Operational Broker Mode</label>
            <div className="px-3 py-2 bg-navy-900 border border-navy-750 rounded-xl text-emerald-400 font-mono flex items-center justify-between">
              <span>{switchStatus.message || 'Internal Agent Broker Mode Active'}</span>
              <span className="text-[10px] bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                Verified
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Compliance & Audit Retention Card */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl p-6 shadow-lg space-y-4">
        <h3 className="font-bold text-sm text-white flex items-center gap-2 pb-3 border-b border-navy-700/60">
          <Database className="w-4 h-4 text-cyan-400" /> Defense Audit Retention & Security Policies
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">FAR/DFARS Audit Log Retention (Days)</label>
            <input
              type="text"
              value={retentionDays}
              onChange={(e) => setRetentionDays(e.target.value)}
              className="w-full px-3 py-2 bg-navy-950 border border-navy-700 rounded-xl text-white font-mono focus:outline-none focus:border-cyan-500"
            />
            <span className="text-[10px] text-slate-500 mt-1 block">Default: 2555 days (7 years federal mandate)</span>
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Database Encryption Standard</label>
            <div className="px-3 py-2 bg-navy-900 border border-navy-750 rounded-xl text-cyan-300 font-mono">
              AES-256-GCM At Rest & TLS 1.3 In Transit
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

