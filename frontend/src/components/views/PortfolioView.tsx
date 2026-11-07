import React, { useState } from 'react';
import {
  Briefcase,
  Search,
  Plus,
  Calendar,
  ExternalLink,
  ChevronRight,
  Filter,
  CheckCircle2,
  Clock,
  Building
} from 'lucide-react';
import { Tender } from '../../types';

interface PortfolioViewProps {
  tenders: Tender[];
  activeTenderId: string | null;
  onSelectTender: (id: string) => void;
  onNavigateTab: (tabId: string) => void;
}

export const PortfolioView: React.FC<PortfolioViewProps> = ({
  tenders,
  activeTenderId,
  onSelectTender,
  onNavigateTab,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredTenders = tenders.filter((t) => {
    const matchesSearch =
      t.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (t.reference_number && t.reference_number.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (t.issuing_authority && t.issuing_authority.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus =
      statusFilter === 'ALL' || (t.status && t.status.toUpperCase().includes(statusFilter));
    return matchesSearch && matchesStatus;
  });

  const getStageBadge = (status?: string) => {
    const s = (status || 'OPPORTUNITY').toUpperCase();
    if (s.includes('SUBMITTED') || s.includes('WON') || s.includes('APPROVED')) {
      return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
    }
    if (s.includes('PREPARATION') || s.includes('PROPOSAL') || s.includes('DRAFT')) {
      return 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30';
    }
    if (s.includes('REVIEW') || s.includes('DECISION')) {
      return 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30';
    }
    return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-cyan-400" />
            Tender Portfolio Management
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Active pursuit volume, multi-workspace pipeline distribution, and lifecycle stage progression.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigateTab('opportunities')}
            className="px-3.5 py-2 bg-navy-800 hover:bg-navy-750 border border-navy-700 rounded-xl text-xs font-semibold text-slate-200 flex items-center gap-1.5 transition"
          >
            <Search className="w-3.5 h-3.5 text-cyan-400" />
            Discover New Tenders
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
            placeholder="Search by title, reference, or authority..."
            className="w-full pl-9 pr-3 py-1.5 bg-navy-950 border border-navy-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-navy-950 border border-navy-700 text-xs text-white rounded-lg px-2.5 py-1.5 focus:outline-none"
          >
            <option value="ALL">All Lifecycle Stages</option>
            <option value="OPPORTUNITY">Opportunity / Ingested</option>
            <option value="PREPARATION">In Preparation / Drafting</option>
            <option value="REVIEW">In Review / Audit</option>
            <option value="APPROVED">Approved / Submitted</option>
          </select>
        </div>
      </div>

      {/* Portfolio Table */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900/90 text-slate-400 border-b border-navy-700/60">
              <tr>
                <th className="p-3.5">Reference & Title</th>
                <th className="p-3.5">Issuing Authority</th>
                <th className="p-3.5">Category</th>
                <th className="p-3.5">Est. Value (USD)</th>
                <th className="p-3.5">Submission Deadline</th>
                <th className="p-3.5">Lifecycle Stage</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-700/40 text-slate-300">
              {filteredTenders.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-400">
                    No matching tenders found in organizational workspace.
                  </td>
                </tr>
              ) : (
                filteredTenders.map((t) => {
                  const isSelected = t.id === activeTenderId;
                  return (
                    <tr
                      key={t.id}
                      className={`hover:bg-navy-800/60 transition cursor-pointer ${
                        isSelected ? 'bg-navy-800/40 border-l-4 border-cyan-400' : ''
                      }`}
                      onClick={() => onSelectTender(t.id)}
                    >
                      <td className="p-3.5">
                        <div className="font-bold text-white flex items-center gap-1.5">
                          {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />}
                          {t.reference_number || 'TND-2026'}
                        </div>
                        <div className="text-[11px] text-slate-400 max-w-sm truncate mt-0.5">
                          {t.title}
                        </div>
                      </td>
                      <td className="p-3.5 text-slate-300">
                        <div className="flex items-center gap-1.5">
                          <Building className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                          <span className="truncate max-w-[180px]">{t.issuing_authority || 'Defense Procurement'}</span>
                        </div>
                      </td>
                      <td className="p-3.5 font-mono text-[11px] text-slate-400">
                        {t.procurement_category || 'Cloud & IT'}
                      </td>
                      <td className="p-3.5 font-mono font-semibold text-emerald-400">
                        ${(t.estimated_value || 0).toLocaleString()} {t.currency || 'USD'}
                      </td>
                      <td className="p-3.5 text-slate-400 whitespace-nowrap">
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-3.5 h-3.5 text-slate-500" />
                          {t.submission_deadline
                            ? new Date(t.submission_deadline).toLocaleDateString()
                            : 'Open Deadline'}
                        </div>
                      </td>
                      <td className="p-3.5">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border uppercase tracking-wider ${getStageBadge(
                            t.status
                          )}`}
                        >
                          {t.status || 'Active'}
                        </span>
                      </td>
                      <td className="p-3.5 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectTender(t.id);
                            onNavigateTab('intelligence');
                          }}
                          className="px-2.5 py-1 bg-navy-800 hover:bg-navy-750 text-cyan-400 hover:text-cyan-300 rounded-lg text-xs font-medium border border-navy-700/80 inline-flex items-center gap-1"
                        >
                          Open Workspace <ChevronRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
