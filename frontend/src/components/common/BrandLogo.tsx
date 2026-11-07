import React from 'react';

interface BrandLogoProps {
  collapsed?: boolean;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({ collapsed = false }) => {
  return (
    <div className="flex items-center gap-3">
      {/* Precision Dual-Wave Mark inspired by the reference design */}
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-navy-800 to-navy-900 border border-blue-900/50 flex items-center justify-center shadow-lg shadow-black/40 shrink-0">
        <svg
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-5 h-5"
        >
          <path
            d="M6 16C10 10 16 22 22 14"
            stroke="url(#brand-cyan-grad)"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <path
            d="M10 20C14 14 20 26 26 18"
            stroke="url(#brand-blue-grad)"
            strokeWidth="2.7"
            strokeLinecap="round"
          />
          <defs>
            <linearGradient id="brand-cyan-grad" x1="6" y1="10" x2="22" y2="22" gradientUnits="userSpaceOnUse">
              <stop stopColor="#22d3ee" />
              <stop offset="1" stopColor="#0284c7" />
            </linearGradient>
            <linearGradient id="brand-blue-grad" x1="10" y1="14" x2="26" y2="26" gradientUnits="userSpaceOnUse">
              <stop stopColor="#38bdf8" />
              <stop offset="1" stopColor="#2563eb" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {!collapsed && (
        <div className="overflow-hidden">
          <div className="font-bold text-[15px] text-white tracking-tight leading-tight">
            TenderForge
          </div>
          <div className="text-[10px] text-slate-400 font-sans tracking-tight truncate mt-0.5">
            From Tender to Trustworthy Proposal
          </div>
        </div>
      )}
    </div>
  );
};

