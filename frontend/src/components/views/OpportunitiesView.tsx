import React, { useState } from 'react';
import {
  Compass,
  Search,
  Filter,
  Building,
  Calendar,
  Sparkles,
  ArrowRight,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { Tender } from '../../types';

interface OpportunitiesViewProps {
  opportunities: any[];
  onPromoteOpportunity?: (opp: any) => void;
  onNavigateTab: (tabId: string) => void;
}

export const OpportunitiesView: React.FC<OpportunitiesViewProps> = ({
  opportunities = [],
  onPromoteOpportunity,
  onNavigateTab,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  const defaultOpps = [
    {
      id: 'opp-1',
      external_id: 'DOD-DISA-2026',
      title: 'Joint Multi-Domain Command & Control (JADC2) Cloud Integration',
      buyer_name: 'US Department of Defense (DISA)',
      procurement_category: 'Cloud & IT Services',
      estimated_budget: 12500000,
      currency: 'USD',
      submission_deadline: '2026-12-15',
      match_score: 96,
      match_status: 'RECOMMENDED',
      canonical_summary: 'Multi-region tactical cloud architecture integration supporting Joint All-Domain Command & Control.',
    },
    {
      id: 'opp-2',
      external_id: 'TND-2026-CLOUD-901',
      title: 'Pursuit: Sovereign Cloud Infrastructure Modernization',
      buyer_name: 'Federal Communications Commission',
      procurement_category: 'Infrastructure',
      estimated_budget: 4850000,
      currency: 'USD',
      submission_deadline: '2026-12-20',
      match_score: 93,
      match_status: 'RECOMMENDED',
      canonical_summary: 'Sovereign cloud migration and tenant isolation for communications compliance databases.',
    },
    {
      id: 'opp-3',
      external_id: 'RFP-2026-001',
      title: 'National Telecom & Cloud Infrastructure Expansion',
      buyer_name: 'Ministry of Communications',
      procurement_category: 'Telecommunications',
      estimated_budget: 3500000,
      currency: 'USD',
      submission_deadline: '2026-12-18',
      match_score: 88,
      match_status: 'QUALIFIED',
      canonical_summary: 'Nationwide broadband and cloud point-of-presence deployment across 14 central regions.',
    },
    {
      id: 'opp-4',
      external_id: 'TND-2026-MED-442',
      title: 'Interoperable Electronic Health Records Platform',
      buyer_name: 'Department of Veterans Affairs',
      procurement_category: 'Healthcare IT',
      estimated_budget: 4850000,
      currency: 'USD',
      submission_deadline: '2026-12-22',
      match_score: 85,
      match_status: 'QUALIFIED',
      canonical_summary: 'HL7 FHIR compliant clinical health record interoperability platform for regional medical centers.',
    },
  ];

  const items = opportunities.length > 0 ? opportunities : defaultOpps;

  const filtered = items.filter((o: any) => {
    const matchesSearch =
      o.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (o.buyer_name && o.buyer_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (o.external_id && o.external_id.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory =
      categoryFilter === 'ALL' || (o.procurement_category && o.procurement_category.includes(categoryFilter));
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Compass className="w-5 h-5 text-cyan-400" />
            Tender Opportunity Discovery & 9-Dimension Matching
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Automated procurement feed crawling, semantic keyword matching, and capabilities fit scoring.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('sources')}
            className="px-3.5 py-2 bg-navy-800 hover:bg-navy-750 border border-navy-700 rounded-xl text-xs font-semibold text-slate-200 flex items-center gap-1.5 transition"
          >
            Manage Source Feeds
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-navy-850 p-3 rounded-xl border border-navy-700/60">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search discovered opportunities..."
            className="w-full pl-9 pr-3 py-1.5 bg-navy-950 border border-navy-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-navy-950 border border-navy-700 text-xs text-white rounded-lg px-2.5 py-1.5 focus:outline-none"
          >
            <option value="ALL">All Sectors</option>
            <option value="Cloud">Cloud & IT</option>
            <option value="Infrastructure">Infrastructure</option>
            <option value="Telecommunications">Telecommunications</option>
            <option value="Healthcare">Healthcare IT</option>
          </select>
        </div>
      </div>

      {/* Opportunities List */}
      <div className="space-y-4">
        {filtered.map((opp: any) => (
          <div
            key={opp.id}
            className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl hover:border-navy-700 transition shadow-lg space-y-3"
          >
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                    {opp.external_id || 'TND-2026'}
                  </span>
                  <span className="text-xs font-semibold text-slate-300">
                    {opp.procurement_category || 'General'}
                  </span>
                </div>
                <h3 className="font-bold text-sm text-white mt-1.5">{opp.title}</h3>
                <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                  <Building className="w-3.5 h-3.5 text-slate-500" />
                  <span>{opp.buyer_name}</span>
                </div>
              </div>

              <div className="flex sm:flex-col items-end gap-2 shrink-0">
                <span className="px-3 py-1 rounded-full text-xs font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  {opp.match_score || 92}% Match Score
                </span>
                <span className="text-xs font-mono font-bold text-white">
                  ${(opp.estimated_budget || 0).toLocaleString()} {opp.currency || 'USD'}
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed font-sans">
              {opp.canonical_summary}
            </p>

            <div className="pt-3 border-t border-navy-700/60 flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 text-slate-400 font-mono">
                <Calendar className="w-3.5 h-3.5 text-slate-500" />
                Deadline: {opp.submission_deadline || 'Dec 15, 2026'}
              </div>

              <button
                onClick={() => {
                  if (onPromoteOpportunity) onPromoteOpportunity(opp);
                  onNavigateTab('portfolio');
                }}
                className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
              >
                Promote to Active Pursuit <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
