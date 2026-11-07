import React from 'react';
import {
  PackageCheck,
  Download,
  FileText,
  FileCheck,
  ShieldCheck,
  CheckCircle2,
  Lock,
  ExternalLink
} from 'lucide-react';
import { Tender } from '../../types';

interface DeliverablesViewProps {
  activeTender?: Tender;
}

export const DeliverablesView: React.FC<DeliverablesViewProps> = ({
  activeTender,
}) => {
  const [downloadSuccess, setDownloadSuccess] = React.useState(false);

  const handleDownload = () => {
    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 4000);
  };
  const deliverables = [
    {
      id: 'deliv-1',
      title: 'Tender Intelligence & Extraction Report',
      format: 'PDF',
      size: '2.4 MB',
      description: 'Extracted clauses, eligibility analysis, and authority profile.',
      sha256: 'a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0',
    },
    {
      id: 'deliv-2',
      title: 'Certified Compliance Matrix',
      format: 'XLSX',
      size: '1.1 MB',
      description: 'Full 14-clause matrix with evidence claim references and gap remediation.',
      sha256: 'b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef01a',
    },
    {
      id: 'deliv-3',
      title: 'Comprehensive Technical Proposal (Vol I & II)',
      format: 'DOCX / PDF',
      size: '8.7 MB',
      description: 'Executive summary, technical cloud mesh architecture, security governance, and BOQ.',
      sha256: 'c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef01a2b',
    },
    {
      id: 'deliv-4',
      title: 'Independent Bid Audit & Integrity Certificate',
      format: 'PDF',
      size: '950 KB',
      description: 'Signed audit certificate with ProofLink validation and ECDSA cryptographic seal.',
      sha256: 'd4e5f67890123456789abcdef0123456789abcdef0123456789abcdef01a2b3c',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <PackageCheck className="w-5 h-5 text-cyan-400" />
            Final Deliverables & Export Bundle
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Complete, publication-ready submission bundle with immutable audit certificates and cryptographic evidence anchors.
          </p>
        </div>
        <button
          onClick={handleDownload}
          className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-semibold flex items-center gap-2 shadow-lg shadow-emerald-950 transition active:scale-95"
        >
          {downloadSuccess ? (
            <>
              <CheckCircle2 className="w-4 h-4 text-white" /> Bundle Manifest Generated
            </>
          ) : (
            <>
              <Download className="w-4 h-4" /> Download Complete ZIP Bundle
            </>
          )}
        </button>
      </div>

      {/* Target Tender Banner */}
      <div className="p-4 bg-navy-850 border border-navy-700/60 rounded-2xl flex items-center justify-between">
        <div>
          <span className="text-[11px] font-mono text-cyan-400 uppercase tracking-wider">
            {activeTender?.reference_number || 'DOD-DISA-2026'}
          </span>
          <h3 className="font-bold text-sm text-white mt-0.5">
            {activeTender?.title || 'Joint Multi-Domain Command & Control (JADC2) Cloud Integration'}
          </h3>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
          Sealed & Ready for Submission
        </span>
      </div>

      {/* Deliverables Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {deliverables.map((item) => (
          <div
            key={item.id}
            className="p-5 bg-navy-850 border border-navy-700/60 rounded-2xl hover:border-navy-700 transition shadow-lg flex flex-col justify-between space-y-4"
          >
            <div>
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-cyan-400 shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-sm text-white">{item.title}</h4>
                    <span className="text-[11px] font-mono text-slate-400">
                      {item.format} • {item.size}
                    </span>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20">
                  Verified
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-2.5 leading-relaxed">
                {item.description}
              </p>
            </div>

            <div className="pt-3 border-t border-navy-700/60 flex items-center justify-between">
              <span className="text-[10px] font-mono text-slate-500 truncate max-w-[200px]">
                SHA-256: {item.sha256.slice(0, 16)}...
              </span>
              <button
                onClick={() => alert(`Downloading ${item.title}...`)}
                className="px-3 py-1 bg-navy-900 hover:bg-navy-800 text-cyan-400 hover:text-cyan-300 text-xs font-semibold rounded-lg border border-navy-700 flex items-center gap-1.5 transition"
              >
                <Download className="w-3.5 h-3.5" /> Download
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

