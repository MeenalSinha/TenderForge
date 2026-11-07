import React from 'react';
import {
  Bell,
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Building,
  ArrowRight
} from 'lucide-react';
import { Tender } from '../../types';

interface DeadlinesViewProps {
  tenders: Tender[];
  onSelectTender: (id: string) => void;
  onNavigateTab: (tabId: string) => void;
}

export const DeadlinesView: React.FC<DeadlinesViewProps> = ({
  tenders,
  onSelectTender,
  onNavigateTab,
}) => {
  const deadlines = [
    {
      id: 'dl-1',
      tender_ref: 'DOD-DISA-2026',
      title: 'Joint Multi-Domain Command & Control (JADC2) Cloud Integration',
      deadline: '2026-12-15T17:00:00Z',
      daysLeft: 38,
      urgency: 'ON_TRACK',
      phase: 'Final Approval Sealed',
      tender_id: tenders[0]?.id,
    },
    {
      id: 'dl-2',
      tender_ref: 'TND-2026-CLOUD-901',
      title: 'Pursuit: Sovereign Cloud Infrastructure Modernization',
      deadline: '2026-12-20T17:00:00Z',
      daysLeft: 43,
      urgency: 'ON_TRACK',
      phase: 'Proposal Drafting',
      tender_id: tenders[1]?.id,
    },
    {
      id: 'dl-3',
      tender_ref: 'RFP-2026-001',
      title: 'National Telecom & Cloud Infrastructure',
      deadline: '2026-12-18T17:00:00Z',
      daysLeft: 41,
      urgency: 'ON_TRACK',
      phase: 'Analyzed & Mapped',
      tender_id: tenders[2]?.id,
    },
    {
      id: 'dl-4',
      tender_ref: 'TND-2026-MED-442',
      title: 'Interoperable Electronic Health Records Platform',
      deadline: '2026-12-22T17:00:00Z',
      daysLeft: 45,
      urgency: 'ON_TRACK',
      phase: 'Opportunity Evaluated',
      tender_id: tenders[3]?.id,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bell className="w-5 h-5 text-cyan-400" />
            Pursuit Deadlines, Milestones & Urgency Alerts
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Centralized calendar tracking for submission cut-offs, clarification Q&A deadlines, and proposal gates.
          </p>
        </div>
      </div>

      {/* Deadlines Table */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900/90 text-slate-400 border-b border-navy-700/60">
              <tr>
                <th className="p-3.5">Pursuit Reference & Title</th>
                <th className="p-3.5">Submission Deadline</th>
                <th className="p-3.5">Days Remaining</th>
                <th className="p-3.5">Current Stage Status</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-700/40 text-slate-300">
              {deadlines.map((dl) => (
                <tr key={dl.id} className="hover:bg-navy-800/60 transition">
                  <td className="p-3.5 max-w-sm">
                    <div className="font-bold text-white text-xs">{dl.tender_ref}</div>
                    <div className="text-[11px] text-slate-400 truncate mt-0.5">{dl.title}</div>
                  </td>
                  <td className="p-3.5 font-mono text-slate-200">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-cyan-400" />
                      {new Date(dl.deadline).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </div>
                  </td>
                  <td className="p-3.5 font-mono font-bold text-cyan-400">
                    {dl.daysLeft} Days
                  </td>
                  <td className="p-3.5">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      {dl.phase}
                    </span>
                  </td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => {
                        if (dl.tender_id) onSelectTender(dl.tender_id);
                        onNavigateTab('intelligence');
                      }}
                      className="px-2.5 py-1 bg-navy-900 hover:bg-navy-800 text-cyan-400 hover:text-cyan-300 text-xs font-semibold rounded-lg border border-navy-700 inline-flex items-center gap-1 transition"
                    >
                      Open Pursuit <ArrowRight className="w-3 h-3" />
                    </button>
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

