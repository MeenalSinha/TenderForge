import React, { useState } from 'react';
import {
  BookOpen,
  Search,
  Plus,
  FileText,
  Tag,
  Copy,
  CheckCircle2,
  Filter
} from 'lucide-react';

interface KnowledgeLibraryViewProps {
  knowledgeAssets?: any[];
}

export const KnowledgeLibraryView: React.FC<KnowledgeLibraryViewProps> = ({
  knowledgeAssets = [],
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const defaultAssets = [
    {
      id: 'kn-1',
      title: 'DoD IL6 Secret Hardware Security Enclave Narrative',
      category: 'Technical Architecture',
      version: 'v3.2',
      snippet: 'Our hardware-isolated security enclaves meet the rigorous cryptographic boundaries mandated by DISA STIG guidelines for Secret enclave workloads...',
      tags: ['DoD', 'IL6', 'Secret', 'Security'],
    },
    {
      id: 'kn-2',
      title: 'FedRAMP High Continuous Monitoring & Vulnerability Remediation SLA',
      category: 'Security Governance',
      version: 'v2.0',
      snippet: 'Automated vulnerability scanning using CIS Benchmarks with guaranteed 24-hour patching for critical CVEs and 7-day for high CVEs...',
      tags: ['FedRAMP High', 'SLA', 'Vulnerability', 'Patching'],
    },
    {
      id: 'kn-3',
      title: 'Tactical Edge Micro-Kubernetes DDIL Resiliency Architecture',
      category: 'Technical Architecture',
      version: 'v1.4',
      snippet: 'Autonomous edge node clusters engineered to operate continuously during disconnected, intermittent, or limited bandwidth (DDIL) tactical scenarios...',
      tags: ['Tactical Edge', 'Kubernetes', 'DDIL', 'Resiliency'],
    },
    {
      id: 'kn-4',
      title: 'Air Force Cloud One Multi-Region Modernization Case Study ($14.2M)',
      category: 'Past Performance',
      version: 'v4.1',
      snippet: 'Comprehensive migration of 42 legacy mission-critical applications to dual-region secure cloud architecture with zero operational downtime...',
      tags: ['USAF', 'Cloud One', 'Case Study', 'Past Performance'],
    },
  ];

  const items = knowledgeAssets.length > 0 ? knowledgeAssets : defaultAssets;

  const filtered = items.filter(
    (a: any) =>
      a.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (a.category && a.category.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard?.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-cyan-400" />
            Organizational Knowledge & Boilerplate Library
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Curated repository of reusable proposal narratives, past performance write-ups, and certified technical boilerplate.
          </p>
        </div>
        <button
          onClick={() => alert('New Knowledge Asset: Add standardized boilerplate narrative.')}
          className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
        >
          <Plus className="w-3.5 h-3.5" /> Create Knowledge Asset
        </button>
      </div>

      {/* Search Input */}
      <div className="bg-navy-850 p-3 rounded-xl border border-navy-700/60 flex items-center">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search boilerplate, narratives, or case studies..."
            className="w-full pl-9 pr-3 py-1.5 bg-navy-950 border border-navy-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      {/* Knowledge Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((item: any) => (
          <div
            key={item.id}
            className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl shadow-lg flex flex-col justify-between space-y-3 hover:border-navy-700 transition"
          >
            <div>
              <div className="flex items-start justify-between gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 font-semibold">
                  {item.category || 'Architecture'}
                </span>
                <span className="text-[10px] font-mono text-slate-400">{item.version || 'v1.0'}</span>
              </div>
              <h3 className="font-bold text-sm text-white mt-1.5 leading-snug">{item.title}</h3>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed line-clamp-3 font-sans">
                {item.snippet || item.content_body}
              </p>
            </div>

            <div className="pt-3 border-t border-navy-700/60 flex items-center justify-between text-xs">
              <div className="flex flex-wrap gap-1">
                {(item.tags || []).map((t: string) => (
                  <span key={t} className="text-[10px] font-mono text-slate-400 bg-navy-950 px-1.5 py-0.5 rounded">
                    #{t}
                  </span>
                ))}
              </div>

              <button
                onClick={() => handleCopy(item.id, item.snippet || item.content_body)}
                className="px-2.5 py-1 bg-navy-900 hover:bg-navy-800 text-cyan-400 hover:text-cyan-300 rounded-lg text-xs font-medium border border-navy-700 flex items-center gap-1 transition"
              >
                {copiedId === item.id ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" /> Copy Text
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
