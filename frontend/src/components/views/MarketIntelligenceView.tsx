import React, { useState } from 'react';
import {
  TrendingUp,
  Award,
  DollarSign,
  Building,
  Calendar,
  Filter,
  BarChart3,
  Search
} from 'lucide-react';

interface MarketIntelligenceViewProps {
  marketTrends?: any;
}

export const MarketIntelligenceView: React.FC<MarketIntelligenceViewProps> = ({
  marketTrends,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const awards = [
    {
      id: 'aw-1',
      tender_ref: 'DOD-AF-2025-08',
      buyer_name: 'US Air Force Materiel Command',
      winning_bidder: 'Apex Global Defense & IT Solutions',
      award_amount: 14200000.0,
      currency: 'USD',
      award_date: '2026-08-15',
      category: 'Cloud Modernization',
      status: 'VERIFIED',
    },
    {
      id: 'aw-2',
      tender_ref: 'NAVY-SPAWAR-2025',
      buyer_name: 'Naval Information Warfare Systems Command',
      winning_bidder: 'General Dynamics IT',
      award_amount: 22800000.0,
      currency: 'USD',
      award_date: '2026-09-02',
      category: 'Tactical Mesh Networking',
      status: 'VERIFIED',
    },
    {
      id: 'aw-3',
      tender_ref: 'DISA-ENCLAVE-2026',
      buyer_name: 'Defense Information Systems Agency',
      winning_bidder: 'Leidos Defense Corp',
      award_amount: 9800000.0,
      currency: 'USD',
      award_date: '2026-10-10',
      category: 'IL6 Security Hosting',
      status: 'VERIFIED',
    },
    {
      id: 'aw-4',
      tender_ref: 'DHS-CISA-2026-01',
      buyer_name: 'Cybersecurity & Infrastructure Security Agency',
      winning_bidder: 'Apex Global Defense & IT Solutions',
      award_amount: 8400000.0,
      currency: 'USD',
      award_date: '2026-10-25',
      category: 'Zero Trust Monitoring',
      status: 'VERIFIED',
    },
  ];

  const filtered = awards.filter(
    (a) =>
      a.winning_bidder.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.buyer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.tender_ref.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            Market Intelligence & Public Award Analytics
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Macro-procurement spend analysis, verified public contract awards, and competitive win distributions.
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Total Analyzed Spend</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">$55.2M USD</div>
          <div className="text-[11px] text-emerald-300 mt-0.5">Across 4 Defense & Federal Sectors</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Our Market Capture</div>
          <div className="text-2xl font-bold text-cyan-400 font-mono mt-1">$22.6M USD (41%)</div>
          <div className="text-[11px] text-cyan-300 mt-0.5">Apex Global Defense portfolio</div>
        </div>
        <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-sm">
          <div className="text-[11px] font-mono text-slate-400">Sector Spend Trajectory</div>
          <div className="text-2xl font-bold text-indigo-300 font-mono mt-1">+18.4% YoY</div>
          <div className="text-[11px] text-indigo-400 mt-0.5">Strongest growth in Zero Trust / IL6</div>
        </div>
      </div>

      {/* Search Input */}
      <div className="bg-navy-850 p-3 rounded-xl border border-navy-700/60 flex items-center">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search awards by winner, buyer, or reference..."
            className="w-full pl-9 pr-3 py-1.5 bg-navy-950 border border-navy-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      {/* Awards Table */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900/90 text-slate-400 border-b border-navy-700/60">
              <tr>
                <th className="p-3.5">Tender Reference</th>
                <th className="p-3.5">Procuring Buyer</th>
                <th className="p-3.5">Winning Contractor</th>
                <th className="p-3.5">Award Amount</th>
                <th className="p-3.5">Sector</th>
                <th className="p-3.5">Award Date</th>
                <th className="p-3.5 text-right">Verification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-700/40 text-slate-300">
              {filtered.map((aw) => (
                <tr key={aw.id} className="hover:bg-navy-800/60 transition">
                  <td className="p-3.5 font-bold font-mono text-cyan-400">
                    {aw.tender_ref}
                  </td>
                  <td className="p-3.5 text-slate-200 font-semibold max-w-xs truncate">
                    {aw.buyer_name}
                  </td>
                  <td className="p-3.5 text-white font-medium max-w-xs truncate">
                    {aw.winning_bidder}
                  </td>
                  <td className="p-3.5 font-mono font-bold text-emerald-400">
                    ${aw.award_amount.toLocaleString()} {aw.currency}
                  </td>
                  <td className="p-3.5 text-slate-400 font-mono text-[11px]">
                    {aw.category}
                  </td>
                  <td className="p-3.5 text-slate-400 font-mono text-[11px]">
                    {aw.award_date}
                  </td>
                  <td className="p-3.5 text-right">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      {aw.status}
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

