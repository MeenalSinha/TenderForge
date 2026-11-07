import React, { useState } from 'react';
import {
  Library,
  Search,
  Plus,
  FileText,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Lock,
  Filter
} from 'lucide-react';
import { EvidenceItem } from '../../types';

interface EvidenceLibraryViewProps {
  evidenceItems?: EvidenceItem[];
  onUploadEvidence?: (file: File) => void;
}

export const EvidenceLibraryView: React.FC<EvidenceLibraryViewProps> = ({
  evidenceItems = [],
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');

  const defaultVault = [
    {
      id: 'ev-1',
      title: 'FedRAMP High Authorization Package (ATO)',
      evidence_type: 'Certification',
      document: 'FedRAMP_High_ATO_Package_2025.pdf',
      freshness_status: 'Fresh' as const,
      valid_until: '2027-12-31',
      checksum_sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    },
    {
      id: 'ev-2',
      title: 'DoD Impact Level 6 (IL6) Provisional Authorization',
      evidence_type: 'Security Accreditation',
      document: 'DoD_IL6_Provisional_Authorization_Package.pdf',
      freshness_status: 'Fresh' as const,
      valid_until: '2027-06-30',
      checksum_sha256: '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
    },
    {
      id: 'ev-3',
      title: 'NIST SP 800-207 Zero Trust Security Evaluation',
      evidence_type: 'Audit Report',
      document: 'Mandiant_Zero_Trust_Evaluation_v2.pdf',
      freshness_status: 'Fresh' as const,
      valid_until: '2026-11-30',
      checksum_sha256: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
    },
    {
      id: 'ev-4',
      title: 'ISO/IEC 27001:2022 Information Security Management',
      evidence_type: 'Certification',
      document: 'ISO_27001_2022_Certified_Certificate.pdf',
      freshness_status: 'Fresh' as const,
      valid_until: '2028-04-15',
      checksum_sha256: '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
    },
    {
      id: 'ev-5',
      title: 'US Air Force Cloud One Migration ($14.2M) CPARS',
      evidence_type: 'Past Performance',
      document: 'CPARS_USAF_CloudOne_Exceptional_Rating.pdf',
      freshness_status: 'Fresh' as const,
      valid_until: '2029-01-01',
      checksum_sha256: '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
    },
    {
      id: 'ev-6',
      title: 'CMMC Level 3 Cyber Hygiene Assessment',
      evidence_type: 'Security Accreditation',
      document: 'CMMC_Level_3_Third_Party_Certificate.pdf',
      freshness_status: 'Fresh' as const,
      valid_until: '2027-08-20',
      checksum_sha256: '8f9e0d1c2b3a4f5e6d7c8b9a0f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6b7a8f9e',
    },
  ];

  const items = evidenceItems.length > 0 ? evidenceItems : defaultVault;

  const filtered = items.filter((item: any) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.evidence_type && item.evidence_type.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = typeFilter === 'ALL' || item.evidence_type === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Library className="w-5 h-5 text-cyan-400" />
            Enterprise Evidence Library & Corporate Vault
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Verified corporate credentials, certifications, audits, and past performance records indexed by @EvidenceResearcher.
          </p>
        </div>
        <button
          onClick={() => alert('Add Evidence dialog: Upload document with automated SHA-256 integrity hashing.')}
          className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
        >
          <Plus className="w-3.5 h-3.5" /> Upload Evidence Asset
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-navy-850 p-3 rounded-xl border border-navy-700/60">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search vault by title or credential..."
            className="w-full pl-9 pr-3 py-1.5 bg-navy-950 border border-navy-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-navy-950 border border-navy-700 text-xs text-white rounded-lg px-2.5 py-1.5 focus:outline-none"
          >
            <option value="ALL">All Asset Types</option>
            <option value="Certification">Certifications</option>
            <option value="Security Accreditation">Security Accreditations</option>
            <option value="Audit Report">Audit Reports</option>
            <option value="Past Performance">Past Performance</option>
          </select>
        </div>
      </div>

      {/* Vault Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((item: any) => (
          <div
            key={item.id}
            className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl hover:border-navy-700 transition shadow-lg flex flex-col justify-between space-y-4"
          >
            <div className="space-y-2">
              <div className="flex items-start justify-between gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 font-semibold">
                  {item.evidence_type}
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono text-emerald-400 bg-emerald-500/15 border border-emerald-500/30 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Fresh
                </span>
              </div>
              <h4 className="font-bold text-sm text-white leading-snug">{item.title}</h4>
              <div className="text-[11px] text-slate-400 font-mono truncate flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                {item.document || `${item.title.replace(/\s+/g, '_')}.pdf`}
              </div>
            </div>

            <div className="pt-3 border-t border-navy-700/60 text-xs space-y-1.5">
              <div className="flex justify-between items-center text-slate-400">
                <span>Valid Until:</span>
                <span className="font-mono text-slate-200">{item.valid_until || '2028-12-31'}</span>
              </div>
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-500">
                <span className="truncate max-w-[160px]">
                  SHA-256: {item.checksum_sha256?.slice(0, 16) || 'e3b0c44298fc1c...'}...
                </span>
                <span className="text-emerald-400 font-bold flex items-center gap-0.5">
                  <Lock className="w-2.5 h-2.5" /> Verified
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
