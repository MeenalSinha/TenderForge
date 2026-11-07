import React, { useState } from 'react';
import {
  Users,
  Plus,
  ShieldCheck,
  UserCheck,
  Mail,
  CheckCircle2
} from 'lucide-react';
import { User } from '../../types';

interface TeamPermissionsViewProps {
  currentUser: User;
}

export const TeamPermissionsView: React.FC<TeamPermissionsViewProps> = ({
  currentUser,
}) => {
  const members = [
    {
      id: 'usr-1',
      full_name: 'Elena Vance (Lead)',
      email: 'admin@tenderforge.com',
      role: 'Admin',
      status: 'ACTIVE',
      lastLogin: 'Active now',
    },
    {
      id: 'usr-2',
      full_name: 'Marcus Brody',
      email: 'author@tenderforge.com',
      role: 'Author',
      status: 'ACTIVE',
      lastLogin: '1h ago',
    },
    {
      id: 'usr-3',
      full_name: 'Dr. Sarah Connor',
      email: 'reviewer@tenderforge.com',
      role: 'Reviewer',
      status: 'ACTIVE',
      lastLogin: '3h ago',
    },
    {
      id: 'usr-4',
      full_name: 'David Chen',
      email: 'approver@tenderforge.com',
      role: 'Approver',
      status: 'ACTIVE',
      lastLogin: 'Yesterday',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-cyan-400" />
            Team Members & Role-Based Access Control (RBAC)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Enforced authorization matrix across 5 tiers: Admin, Approver, Reviewer, Author, and Viewer.
          </p>
        </div>
        <button
          onClick={() => alert('Invite Team Member: Enter work email and assign role.')}
          className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
        >
          <Plus className="w-3.5 h-3.5" /> Invite Teammate
        </button>
      </div>

      {/* Team Table */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900/90 text-slate-400 border-b border-navy-700/60">
              <tr>
                <th className="p-3.5">Team Member</th>
                <th className="p-3.5">Email Address</th>
                <th className="p-3.5">Assigned RBAC Role</th>
                <th className="p-3.5">Last Session</th>
                <th className="p-3.5 text-right">Account Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-700/40 text-slate-300">
              {members.map((m) => (
                <tr key={m.id} className="hover:bg-navy-800/60 transition">
                  <td className="p-3.5 font-bold text-white">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-navy-900 border border-navy-700 flex items-center justify-center text-[10px] font-bold text-cyan-400 font-mono">
                        {m.full_name.slice(0, 2).toUpperCase()}
                      </div>
                      <span>{m.full_name}</span>
                    </div>
                  </td>
                  <td className="p-3.5 font-mono text-slate-300">
                    {m.email}
                  </td>
                  <td className="p-3.5">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                        m.role === 'Admin'
                          ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                          : m.role === 'Approver'
                          ? 'bg-purple-500/15 text-purple-400 border-purple-500/30'
                          : m.role === 'Reviewer'
                          ? 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30'
                          : 'bg-blue-500/15 text-blue-300 border-blue-500/30'
                      }`}
                    >
                      {m.role}
                    </span>
                  </td>
                  <td className="p-3.5 text-slate-400 font-mono text-[11px]">
                    {m.lastLogin}
                  </td>
                  <td className="p-3.5 text-right">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      {m.status}
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

