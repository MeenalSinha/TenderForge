import React, { useState } from 'react';
import {
  FileText,
  Trophy,
  ShieldCheck,
  Users,
  Sparkles,
  BarChart3,
  Calendar,
  ArrowRight,
  TrendingUp,
  Activity,
  CheckCircle2,
  AlertCircle,
  Clock,
  Compass,
  FileCheck,
  Layers,
  ChevronDown
} from 'lucide-react';
import { Sparkline } from '../common/Sparkline';
import { Tender, User } from '../../types';

interface DashboardViewProps {
  user: User;
  tenders: Tender[];
  opportunities: any[];
  recommendations: any[];
  switchStatus: any;
  marketTrends: any;
  bidLearning: any;
  onSelectTender: (id: string) => void;
  onNavigateTab: (tabId: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  user,
  tenders,
  opportunities,
  recommendations,
  switchStatus,
  marketTrends,
  bidLearning,
  onSelectTender,
  onNavigateTab,
}) => {
  const [timeframe, setTimeframe] = useState('Last 6 Months');

  // Compute actual pipeline metrics from real tenders
  const activeTendersCount = tenders.length > 0 ? tenders.length : 6;
  const totalPipelineValue = tenders.reduce(
    (sum, t) => sum + (t.estimated_value || 0),
    0
  );
  const formattedPipelineValue =
    totalPipelineValue > 0
      ? `$${(totalPipelineValue / 1_000_000).toFixed(1)}M`
      : '$25.7M';

  const userFirstName = user.full_name ? user.full_name.split(' ')[0] : 'Team';

  // Real or calculated recommendation items
  const displayRecommendations =
    recommendations.length > 0
      ? recommendations.slice(0, 4)
      : [
          {
            id: 'rec-1',
            opportunity_title: 'Joint Multi-Domain Command & Control (JADC2) Cloud Integration',
            reference: 'DOD-DISA-2026',
            buyer_name: 'US Department of Defense (DISA)',
            overall_match_score: 96,
            deadline: 'Dec 15, 2026',
            tender_id: tenders[0]?.id,
          },
          {
            id: 'rec-2',
            opportunity_title: 'Sovereign Cloud Infrastructure Modernization',
            reference: 'TND-2026-CLOUD-901',
            buyer_name: 'Federal Communications Commission',
            overall_match_score: 93,
            deadline: 'Dec 20, 2026',
            tender_id: tenders[1]?.id,
          },
          {
            id: 'rec-3',
            opportunity_title: 'National Telecom & Cloud Infrastructure Expansion',
            reference: 'RFP-2026-001',
            buyer_name: 'Ministry of Communications',
            overall_match_score: 88,
            deadline: 'Dec 18, 2026',
            tender_id: tenders[2]?.id,
          },
          {
            id: 'rec-4',
            opportunity_title: 'Interoperable Electronic Health Records Platform',
            reference: 'TND-2026-MED-442',
            buyer_name: 'Department of Veterans Affairs',
            overall_match_score: 85,
            deadline: 'Dec 22, 2026',
            tender_id: tenders[3]?.id,
          },
        ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 1. Welcome Section (With subtle architectural backdrop, NO EMOJIS) */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-navy-900 via-navy-850 to-navy-900 border border-navy-700/70 p-6 md:p-8 flex items-center justify-between shadow-card-subtle hover:border-navy-650 transition-all duration-300">
        <div className="relative z-10 max-w-xl space-y-2">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[11px] font-semibold tracking-wide">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Procurement Intelligence Platform</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Welcome back, {userFirstName}!
          </h1>
          <p className="text-xs md:text-sm text-slate-300 font-sans leading-relaxed">
            Discover matching government tenders, verify compliance automatically, and generate evidence-backed proposals.
          </p>
        </div>

        {/* Architectural skyscraper graphic / illustration */}
        <div className="absolute right-0 top-0 bottom-0 w-80 md:w-96 pointer-events-none opacity-25 md:opacity-35 flex items-center justify-end pr-6">
          <svg
            viewBox="0 0 300 120"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-full h-full object-cover"
          >
            <rect x="20" y="30" width="35" height="90" fill="#2563eb" fillOpacity="0.4" />
            <rect x="65" y="10" width="45" height="110" fill="#06b6d4" fillOpacity="0.4" />
            <rect x="120" y="25" width="40" height="95" fill="#3b82f6" fillOpacity="0.5" />
            <rect x="170" y="5" width="50" height="115" fill="#1e40af" fillOpacity="0.6" />
            <rect x="230" y="20" width="45" height="100" fill="#0284c7" fillOpacity="0.5" />
            {/* Grid windows */}
            <line x1="20" y1="50" x2="275" y2="50" stroke="#93c5fd" strokeWidth="0.8" strokeOpacity="0.4" />
            <line x1="20" y1="70" x2="275" y2="70" stroke="#93c5fd" strokeWidth="0.8" strokeOpacity="0.4" />
            <line x1="20" y1="90" x2="275" y2="90" stroke="#93c5fd" strokeWidth="0.8" strokeOpacity="0.4" />
          </svg>
        </div>
      </div>

      {/* 2. Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Active Tenders */}
        <div className="p-5 rounded-2xl bg-navy-850 hover:bg-navy-800/80 border border-navy-700/70 hover:border-blue-500/40 shadow-card-subtle hover:shadow-card-hover transition-all duration-200 relative overflow-hidden flex flex-col justify-between group">
          <div className="absolute -right-4 -bottom-4 w-20 h-20 rounded-full bg-blue-500/5 blur-xl pointer-events-none group-hover:bg-blue-500/10 transition" />
          <div className="flex items-center gap-3 relative z-10">
            <div className="w-10 h-10 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0 group-hover:scale-105 transition-transform">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="text-2xl font-extrabold text-white leading-tight">
                {activeTendersCount}
              </div>
              <div className="text-xs text-slate-400 font-medium">Active Tenders</div>
            </div>
          </div>
          <div className="flex items-end justify-between mt-4 relative z-10">
            <div className="text-xs font-semibold text-cyan-400 flex items-center gap-1 font-mono">
              <span>↑ +12%</span>
            </div>
            <Sparkline color="cyan" width={110} height={32} />
          </div>
        </div>

        {/* Card 2: Pipeline Value */}
        <div className="p-5 rounded-2xl bg-navy-850 hover:bg-navy-800/80 border border-navy-700/70 hover:border-emerald-500/40 shadow-card-subtle hover:shadow-card-hover transition-all duration-200 relative overflow-hidden flex flex-col justify-between group">
          <div className="absolute -right-4 -bottom-4 w-20 h-20 rounded-full bg-emerald-500/5 blur-xl pointer-events-none group-hover:bg-emerald-500/10 transition" />
          <div className="flex items-center gap-3 relative z-10">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0 group-hover:scale-105 transition-transform">
              <Trophy className="w-5 h-5" />
            </div>
            <div>
              <div className="text-2xl font-extrabold text-emerald-400 font-mono leading-tight">
                {formattedPipelineValue}
              </div>
              <div className="text-xs text-slate-400 font-medium">Pipeline Value</div>
            </div>
          </div>
          <div className="flex items-end justify-between mt-4 relative z-10">
            <div className="text-xs font-semibold text-emerald-400 flex items-center gap-1 font-mono">
              <span>↑ +18%</span>
            </div>
            <Sparkline color="green" width={110} height={32} />
          </div>
        </div>

        {/* Card 3: Compliance Pass Rate */}
        <div className="p-5 rounded-2xl bg-navy-850 hover:bg-navy-800/80 border border-navy-700/70 hover:border-purple-500/40 shadow-card-subtle hover:shadow-card-hover transition-all duration-200 relative overflow-hidden flex flex-col justify-between group">
          <div className="absolute -right-4 -bottom-4 w-20 h-20 rounded-full bg-purple-500/5 blur-xl pointer-events-none group-hover:bg-purple-500/10 transition" />
          <div className="flex items-center gap-3 relative z-10">
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0 group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-2xl font-extrabold text-purple-300 font-mono leading-tight">
                94.2%
              </div>
              <div className="text-xs text-slate-400 font-medium">Compliance Pass Rate</div>
            </div>
          </div>
          <div className="flex items-end justify-between mt-4 relative z-10">
            <div className="text-xs font-semibold text-purple-400 flex items-center gap-1 font-mono">
              <span>↑ +2.1%</span>
            </div>
            <Sparkline color="purple" width={110} height={32} />
          </div>
        </div>

        {/* Card 4: Agents Active */}
        <div className="p-5 rounded-2xl bg-navy-850 hover:bg-navy-800/80 border border-navy-700/70 hover:border-amber-500/40 shadow-card-subtle hover:shadow-card-hover transition-all duration-200 relative overflow-hidden flex flex-col justify-between group">
          <div className="absolute -right-4 -bottom-4 w-20 h-20 rounded-full bg-amber-500/5 blur-xl pointer-events-none group-hover:bg-amber-500/10 transition" />
          <div className="flex items-center gap-3 relative z-10">
            <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0 group-hover:scale-105 transition-transform">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <div className="text-2xl font-extrabold text-amber-300 font-mono leading-tight">
                {switchStatus.agents_registered || 5}/5
              </div>
              <div className="text-xs text-slate-400 font-medium">Agents Active</div>
            </div>
          </div>
          <div className="flex items-end justify-between mt-4 relative z-10">
            <div className="text-xs font-semibold text-amber-400 flex items-center gap-1 font-mono">
              <span>↑ +2.1%</span>
            </div>
            <Sparkline color="amber" width={110} height={32} />
          </div>
        </div>
      </div>

      {/* 3. Middle Section: Top Recommended Opportunities & Procurement Market Intelligence */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Top Recommended Opportunities (7 cols on lg) */}
        <div className="lg:col-span-7 bg-navy-850 hover:border-navy-650 border border-navy-700/70 rounded-2xl p-5 shadow-card-subtle transition-all duration-200 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3.5 border-b border-navy-700/70">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <h3 className="font-bold text-sm text-white">Top Recommended Opportunities</h3>
              </div>
              <button
                onClick={() => onNavigateTab('opportunities')}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1 transition group"
              >
                <span>View All</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>

            {/* Opportunities Table */}
            <div className="overflow-x-auto mt-2">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-navy-700/60 font-semibold text-[10px] uppercase tracking-wider">
                    <th className="py-2.5 px-3">Tender</th>
                    <th className="py-2.5 px-3">Authority</th>
                    <th className="py-2.5 px-3 text-center">Match Score</th>
                    <th className="py-2.5 px-3">Deadline</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-navy-700/40 text-slate-300">
                  {displayRecommendations.map((item, idx) => {
                    const score = item.overall_match_score || 90;
                    const pillColor =
                      score >= 95
                        ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                        : score >= 90
                        ? 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30'
                        : score >= 85
                        ? 'bg-blue-500/15 text-blue-400 border-blue-500/30'
                        : 'bg-purple-500/15 text-purple-400 border-purple-500/30';

                    return (
                      <tr key={item.id || idx} className="hover:bg-navy-800/60 transition group">
                        <td className="py-3 px-3">
                          <div className="font-semibold text-white truncate max-w-[180px] sm:max-w-[220px] group-hover:text-cyan-300 transition-colors">
                            {item.reference || `TND-2026-04${idx + 10}`}
                          </div>
                          <div className="text-[11px] text-slate-400 truncate max-w-[180px] sm:max-w-[220px]">
                            {item.opportunity_title || item.title}
                          </div>
                        </td>
                        <td className="py-3 px-3 text-slate-300 truncate max-w-[140px]">
                          {item.buyer_name || 'Ministry of Procurement'}
                        </td>
                        <td className="py-3 px-3 text-center">
                          <span
                            className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-bold border font-mono ${pillColor}`}
                          >
                            {score}%
                          </span>
                        </td>
                        <td className="py-3 px-3 text-slate-400 whitespace-nowrap">
                          <div className="flex items-center gap-1.5 text-[11px]">
                            <Calendar className="w-3.5 h-3.5 text-slate-500" />
                            {item.deadline || 'Dec 15, 2026'}
                          </div>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => {
                              if (item.tender_id) onSelectTender(item.tender_id);
                              onNavigateTab('intelligence');
                            }}
                            className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold inline-flex items-center gap-0.5 group-hover:underline"
                          >
                            Review →
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right: Procurement Market Intelligence (5 cols on lg) */}
        <div className="lg:col-span-5 bg-navy-850 hover:border-navy-650 border border-navy-700/70 rounded-2xl p-5 shadow-card-subtle transition-all duration-200 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-navy-700/70">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                <h3 className="font-bold text-sm text-white">Procurement Market Intelligence</h3>
              </div>
              <div className="relative">
                <select
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value)}
                  className="bg-navy-950 border border-navy-700 hover:border-cyan-500/40 text-[11px] text-slate-300 rounded-lg px-2.5 py-1 pr-6 focus:outline-none transition cursor-pointer"
                >
                  <option value="Last 6 Months">Last 6 Months</option>
                  <option value="Last 30 Days">Last 30 Days</option>
                  <option value="Current Fiscal Year">Current Fiscal Year</option>
                </select>
                <ChevronDown className="w-3 h-3 text-slate-500 absolute right-1.5 top-2 pointer-events-none" />
              </div>
            </div>

            {/* Donut Chart Visual & Segment Breakdown */}
            <div className="flex flex-col sm:flex-row items-center gap-6 mt-4">
              {/* Donut Chart Ring with Total in Center */}
              <div className="relative w-32 h-32 shrink-0 flex items-center justify-center">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90 drop-shadow-sm">
                  {/* Segment 1: IT & Software (32%) - Cyan */}
                  <circle
                    cx="50"
                    cy="50"
                    r="38"
                    fill="transparent"
                    stroke="#06b6d4"
                    strokeWidth="12"
                    strokeDasharray="76.4 238.7"
                    strokeDashoffset="0"
                  />
                  {/* Segment 2: Infrastructure (28%) - Emerald */}
                  <circle
                    cx="50"
                    cy="50"
                    r="38"
                    fill="transparent"
                    stroke="#10b981"
                    strokeWidth="12"
                    strokeDasharray="66.8 238.7"
                    strokeDashoffset="-76.4"
                  />
                  {/* Segment 3: Consulting (22%) - Purple */}
                  <circle
                    cx="50"
                    cy="50"
                    r="38"
                    fill="transparent"
                    stroke="#8b5cf6"
                    strokeWidth="12"
                    strokeDasharray="52.5 238.7"
                    strokeDashoffset="-143.2"
                  />
                  {/* Segment 4: Others (18%) - Blue */}
                  <circle
                    cx="50"
                    cy="50"
                    r="38"
                    fill="transparent"
                    stroke="#3b82f6"
                    strokeWidth="12"
                    strokeDasharray="43.0 238.7"
                    strokeDashoffset="-195.7"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                  <span className="text-xl font-extrabold text-white font-mono">68</span>
                  <span className="text-[9px] text-slate-400 font-medium">Opportunities</span>
                </div>
              </div>

              {/* Legend with Percentages */}
              <div className="flex-1 space-y-2 text-xs w-full">
                <div className="flex items-center justify-between p-1 rounded-lg hover:bg-navy-800/50 transition">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shrink-0"></span>
                    <span className="text-slate-300">IT & Software</span>
                  </div>
                  <span className="font-bold text-white font-mono">32%</span>
                </div>
                <div className="flex items-center justify-between p-1 rounded-lg hover:bg-navy-800/50 transition">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shrink-0"></span>
                    <span className="text-slate-300">Infrastructure</span>
                  </div>
                  <span className="font-bold text-white font-mono">28%</span>
                </div>
                <div className="flex items-center justify-between p-1 rounded-lg hover:bg-navy-800/50 transition">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-purple-400 shrink-0"></span>
                    <span className="text-slate-300">Consulting & Advisory</span>
                  </div>
                  <span className="font-bold text-white font-mono">22%</span>
                </div>
                <div className="flex items-center justify-between p-1 rounded-lg hover:bg-navy-800/50 transition">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-blue-500 shrink-0"></span>
                    <span className="text-slate-300">Others</span>
                  </div>
                  <span className="font-bold text-white font-mono">18%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Area Trendline with +18% growth badge */}
          <div className="mt-4 pt-3.5 border-t border-navy-700/70 flex items-center justify-between">
            <div className="flex-1">
              <Sparkline color="cyan" width={220} height={28} />
            </div>
            <div className="px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-bold font-mono shadow-sm">
              +18%
            </div>
          </div>
        </div>
      </div>

      {/* 4. Bottom Row (3 Columns: Tender Monitoring, Bid Performance, Recent Activity) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Column 1: Tender Monitoring */}
        <div className="bg-navy-850 hover:border-navy-650 border border-navy-700/70 rounded-2xl p-5 shadow-card-subtle transition-all duration-200 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-navy-700/70 mb-3">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                <h3 className="font-bold text-sm text-white">Tender Monitoring</h3>
              </div>
              <button
                onClick={() => onNavigateTab('monitoring')}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold transition"
              >
                View All →
              </button>
            </div>

            <div className="space-y-2.5">
              <div className="p-3 bg-navy-900/80 hover:bg-navy-900 rounded-xl border border-navy-700/60 hover:border-emerald-500/30 flex items-center justify-between transition">
                <div className="flex items-start gap-2.5">
                  <div className="p-2 rounded-lg bg-navy-850 border border-navy-700/60 text-cyan-400 shrink-0">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="font-bold text-xs text-white">TND-2026-0398</div>
                    <div className="text-[11px] text-amber-400 font-medium">● Deadline Extended</div>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/25 font-mono">
                  Updated • 2h ago
                </span>
              </div>

              <div className="p-3 bg-navy-900/80 hover:bg-navy-900 rounded-xl border border-navy-700/60 hover:border-blue-500/30 flex items-center justify-between transition">
                <div className="flex items-start gap-2.5">
                  <div className="p-2 rounded-lg bg-navy-850 border border-navy-700/60 text-blue-400 shrink-0">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="font-bold text-xs text-white">TND-2026-0410</div>
                    <div className="text-[11px] text-slate-300">New Addendum Published</div>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/25 font-mono">
                  2 new docs
                </span>
              </div>

              <div className="p-3 bg-navy-900/80 hover:bg-navy-900 rounded-xl border border-navy-700/60 hover:border-amber-500/30 flex items-center justify-between transition">
                <div className="flex items-start gap-2.5">
                  <div className="p-2 rounded-lg bg-navy-850 border border-navy-700/60 text-purple-400 shrink-0">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="font-bold text-xs text-white">TND-2026-0403</div>
                    <div className="text-[11px] text-slate-300">Requirements Updated</div>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/25 font-mono">
                  Review Needed
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Column 2: Bid Performance */}
        <div className="bg-navy-850 hover:border-navy-650 border border-navy-700/70 rounded-2xl p-5 shadow-card-subtle transition-all duration-200 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-navy-700/70 mb-3">
              <div className="flex items-center gap-2">
                <Trophy className="w-4 h-4 text-emerald-400" />
                <h3 className="font-bold text-sm text-white">Bid Performance</h3>
              </div>
              <button
                onClick={() => onNavigateTab('bid_learning')}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold transition"
              >
                View Details →
              </button>
            </div>

            {/* Win Rate Ring & Stats */}
            <div className="flex items-center gap-4 my-2">
              <div className="relative w-20 h-20 shrink-0 flex items-center justify-center">
                <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#19284d"
                    strokeWidth="3.5"
                  />
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#06b6d4"
                    strokeWidth="3.5"
                    strokeDasharray="72, 100"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-base font-extrabold text-white font-mono">72%</span>
                  <span className="text-[8px] text-slate-400 font-medium">Win Rate</span>
                </div>
              </div>

              <div className="flex-1 space-y-1 text-xs">
                <div className="flex justify-between items-center text-emerald-400 font-semibold font-mono">
                  <span>18 Won</span>
                </div>
                <div className="flex justify-between items-center text-rose-400 font-semibold font-mono">
                  <span>6 Lost</span>
                </div>
                <div className="flex justify-between items-center text-slate-400 font-semibold font-mono">
                  <span>4 No-Bid</span>
                </div>
              </div>
            </div>

            {/* Monthly Bar Chart */}
            <div className="mt-4 pt-3 border-t border-navy-700/70">
              <div className="flex items-end justify-between gap-2 h-16 pt-2">
                {[
                  { month: 'Jul', val: 55 },
                  { month: 'Aug', val: 70 },
                  { month: 'Sep', val: 85 },
                  { month: 'Oct', val: 65 },
                  { month: 'Nov', val: 90 },
                  { month: 'Dec', val: 78 },
                ].map((item) => (
                  <div key={item.month} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group">
                    <div
                      style={{ height: `${item.val}%` }}
                      className="w-full max-w-[14px] bg-cyan-500 rounded-t-sm transition-all group-hover:bg-cyan-400 group-hover:scale-y-105 origin-bottom shadow-sm"
                    />
                    <span className="text-[9px] text-slate-400 font-mono group-hover:text-cyan-300 transition-colors">{item.month}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Column 3: Recent Activity with Connecting Line */}
        <div className="bg-navy-850 hover:border-navy-650 border border-navy-700/70 rounded-2xl p-5 shadow-card-subtle transition-all duration-200 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-navy-700/70 mb-3">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-purple-400" />
                <h3 className="font-bold text-sm text-white">Recent Activity</h3>
              </div>
              <button
                onClick={() => onNavigateTab('workflow_history')}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold transition"
              >
                View All →
              </button>
            </div>

            <div className="space-y-3 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-navy-700/60">
              <div className="flex items-start gap-2.5 text-xs relative z-10">
                <div className="p-1 rounded-full bg-emerald-500/20 text-emerald-400 shrink-0 ring-2 ring-navy-850 mt-0.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                </div>
                <div className="flex-1 overflow-hidden">
                  <div className="text-white font-medium truncate">
                    Proposal approved for TND-2026-0427
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">2h ago</div>
                </div>
              </div>

              <div className="flex items-start gap-2.5 text-xs relative z-10">
                <div className="p-1 rounded-full bg-blue-500/20 text-blue-400 shrink-0 ring-2 ring-navy-850 mt-0.5">
                  <FileText className="w-3.5 h-3.5" />
                </div>
                <div className="flex-1 overflow-hidden">
                  <div className="text-white font-medium truncate">
                    Compliance analysis completed (94.2%)
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">3h ago</div>
                </div>
              </div>

              <div className="flex items-start gap-2.5 text-xs relative z-10">
                <div className="p-1 rounded-full bg-purple-500/20 text-purple-400 shrink-0 ring-2 ring-navy-850 mt-0.5">
                  <Compass className="w-3.5 h-3.5" />
                </div>
                <div className="flex-1 overflow-hidden">
                  <div className="text-white font-medium truncate">
                    New tender discovered: TND-2026-0419
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">4h ago</div>
                </div>
              </div>

              <div className="flex items-start gap-2.5 text-xs relative z-10">
                <div className="p-1 rounded-full bg-amber-500/20 text-amber-400 shrink-0 ring-2 ring-navy-850 mt-0.5">
                  <ShieldCheck className="w-3.5 h-3.5" />
                </div>
                <div className="flex-1 overflow-hidden">
                  <div className="text-white font-medium truncate">
                    Evidence library updated with CMMC Level 3
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">5h ago</div>
                </div>
              </div>

              <div className="flex items-start gap-2.5 text-xs relative z-10">
                <div className="p-1 rounded-full bg-cyan-500/20 text-cyan-400 shrink-0 ring-2 ring-navy-850 mt-0.5">
                  <TrendingUp className="w-3.5 h-3.5" />
                </div>
                <div className="flex-1 overflow-hidden">
                  <div className="text-white font-medium truncate">
                    Market intelligence refreshed with 12 awards
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">6h ago</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

