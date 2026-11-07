import React, { useState } from 'react';
import {
  DollarSign,
  Calculator,
  Layers,
  ArrowRight,
  Plus,
  CheckCircle2
} from 'lucide-react';
import { Tender } from '../../types';

interface FinancialBOQViewProps {
  activeTender?: Tender;
  onNavigateTab: (tabId: string) => void;
}

export const FinancialBOQView: React.FC<FinancialBOQViewProps> = ({
  activeTender,
  onNavigateTab,
}) => {
  const [selectedScenario, setSelectedScenario] = useState<'base' | 'conservative' | 'aggressive'>('base');

  const boqItems = [
    {
      id: 'boq-1',
      code: 'CLIN-0001',
      description: 'Core Federated Cloud Command Hub Setup & DISA Integration',
      unit: 'Month',
      qty: 12,
      unitPrice: 125000.0,
      total: 1500000.0,
    },
    {
      id: 'boq-2',
      code: 'CLIN-0002',
      description: 'DoD IL6 Secret Hardware Security Enclaves (Dual Region)',
      unit: 'Enclave',
      qty: 2,
      unitPrice: 650000.0,
      total: 1300000.0,
    },
    {
      id: 'boq-3',
      code: 'CLIN-0003',
      description: 'NIST SP 800-207 Zero Trust Ingress/Egress Edge Gateways',
      unit: 'Gateway Cluster',
      qty: 4,
      unitPrice: 225000.0,
      total: 900000.0,
    },
    {
      id: 'boq-4',
      code: 'CLIN-0004',
      description: '24/7/365 US Citizen TS/SCI Cleared SOC Operations Support',
      unit: 'Month',
      qty: 12,
      unitPrice: 85416.67,
      total: 1025000.0,
    },
  ];

  const baseTotal = 4725000.0;
  const conservativeTotal = baseTotal * 1.15; // $5,433,750
  const aggressiveTotal = baseTotal * 0.95;   // $4,488,750

  const currentPrice =
    selectedScenario === 'conservative'
      ? conservativeTotal
      : selectedScenario === 'aggressive'
      ? aggressiveTotal
      : baseTotal;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-cyan-400" />
            Financial BOQ & Multi-Scenario Pricing Workspace
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic bill-of-quantities calculation using Python Decimal precision with multi-scenario sensitivity modeling.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigateTab('proposal')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            Insert into Proposal <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Multi-Scenario Modeling Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Scenario 1: Base */}
        <div
          onClick={() => setSelectedScenario('base')}
          className={`p-5 rounded-2xl border transition cursor-pointer shadow-lg ${
            selectedScenario === 'base'
              ? 'bg-navy-800 border-cyan-400 ring-1 ring-cyan-400/40'
              : 'bg-navy-850 border-navy-700/60 hover:border-navy-700'
          }`}
        >
          <div className="flex justify-between items-center text-xs">
            <span className="font-mono text-slate-400">Baseline Cost Model</span>
            {selectedScenario === 'base' && (
              <span className="text-cyan-400 text-[10px] font-bold uppercase font-mono">Active</span>
            )}
          </div>
          <div className="text-2xl font-bold text-white font-mono mt-1.5">
            ${baseTotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Exact unburdened engineering & infrastructure cost.
          </div>
        </div>

        {/* Scenario 2: Conservative */}
        <div
          onClick={() => setSelectedScenario('conservative')}
          className={`p-5 rounded-2xl border transition cursor-pointer shadow-lg ${
            selectedScenario === 'conservative'
              ? 'bg-navy-800 border-emerald-400 ring-1 ring-emerald-400/40'
              : 'bg-navy-850 border-navy-700/60 hover:border-navy-700'
          }`}
        >
          <div className="flex justify-between items-center text-xs">
            <span className="font-mono text-emerald-400">Conservative Margin (+15%)</span>
            {selectedScenario === 'conservative' && (
              <span className="text-emerald-400 text-[10px] font-bold uppercase font-mono">Active</span>
            )}
          </div>
          <div className="text-2xl font-bold text-emerald-400 font-mono mt-1.5">
            ${conservativeTotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            High-margin pricing buffer for defense contract contingency.
          </div>
        </div>

        {/* Scenario 3: Aggressive */}
        <div
          onClick={() => setSelectedScenario('aggressive')}
          className={`p-5 rounded-2xl border transition cursor-pointer shadow-lg ${
            selectedScenario === 'aggressive'
              ? 'bg-navy-800 border-amber-400 ring-1 ring-amber-400/40'
              : 'bg-navy-850 border-navy-700/60 hover:border-navy-700'
          }`}
        >
          <div className="flex justify-between items-center text-xs">
            <span className="font-mono text-amber-400">Aggressive Price (-5%)</span>
            {selectedScenario === 'aggressive' && (
              <span className="text-amber-400 text-[10px] font-bold uppercase font-mono">Active</span>
            )}
          </div>
          <div className="text-2xl font-bold text-amber-400 font-mono mt-1.5">
            ${aggressiveTotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Competitive bid pricing for best-value source selections.
          </div>
        </div>
      </div>

      {/* BOQ Line Items Table */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl overflow-hidden shadow-lg">
        <div className="p-4 bg-navy-900/80 border-b border-navy-700/60 flex items-center justify-between">
          <h3 className="font-bold text-sm text-white">Bill of Quantities (CLIN Breakdown)</h3>
          <span className="text-xs font-mono text-cyan-400 font-semibold">
            Evaluated Subtotal: ${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })} USD
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900 text-slate-400 border-b border-navy-700/60">
              <tr>
                <th className="p-3.5">CLIN / Item</th>
                <th className="p-3.5">Description</th>
                <th className="p-3.5">Unit</th>
                <th className="p-3.5 text-center">Qty</th>
                <th className="p-3.5 text-right">Unit Rate (USD)</th>
                <th className="p-3.5 text-right">Total Price (USD)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-700/40 text-slate-300">
              {boqItems.map((item) => (
                <tr key={item.id} className="hover:bg-navy-800/60 transition">
                  <td className="p-3.5 font-mono font-bold text-cyan-400">
                    {item.code}
                  </td>
                  <td className="p-3.5 font-semibold text-white max-w-sm">
                    {item.description}
                  </td>
                  <td className="p-3.5 text-slate-400 font-mono">
                    {item.unit}
                  </td>
                  <td className="p-3.5 text-center font-mono font-bold text-slate-200">
                    {item.qty}
                  </td>
                  <td className="p-3.5 text-right font-mono text-slate-300">
                    ${item.unitPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="p-3.5 text-right font-mono font-bold text-emerald-400">
                    ${item.total.toLocaleString('en-US', { minimumFractionDigits: 2 })}
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
