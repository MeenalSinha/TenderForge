import React, { useState } from 'react';
import {
  Building,
  Shield,
  Save,
  CheckCircle2,
  Lock,
  Globe,
  Mail,
  MapPin
} from 'lucide-react';
import { Organization, User } from '../../types';

interface OrgProfileViewProps {
  user: User;
  organizations: Organization[];
}

export const OrgProfileView: React.FC<OrgProfileViewProps> = ({
  user,
  organizations,
}) => {
  const [orgName, setOrgName] = useState(organizations[0]?.name || 'Apex Global Defense & IT Solutions');
  const [cageCode, setCageCode] = useState('8X7L2');
  const [dunsNumber, setDunsNumber] = useState('08-941-8842');
  const [samUei, setSamUei] = useState('K9Y8Q7M6P5N4');
  const [facilityClearance, setFacilityClearance] = useState('Top Secret / Sensitive Compartmented Information (TS/SCI)');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-700/60">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Building className="w-5 h-5 text-cyan-400" />
            Enterprise Organization Profile & Compliance Registry
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Government vendor identification, SAM.gov Unique Entity ID (UEI), CAGE codes, and verified security clearances.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {saved && (
            <span className="text-xs text-emerald-400 font-medium flex items-center gap-1 animate-fade-in">
              <CheckCircle2 className="w-3.5 h-3.5" /> Profile Updated
            </span>
          )}
          <button
            onClick={handleSave}
            className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-900/30 transition"
          >
            <Save className="w-3.5 h-3.5" /> Save Profile Details
          </button>
        </div>
      </div>

      {/* Organization Credentials Form */}
      <div className="bg-navy-850 border border-navy-700/60 rounded-2xl p-6 shadow-lg space-y-5">
        <h3 className="font-bold text-sm text-white flex items-center gap-2 pb-3 border-b border-navy-700/60">
          <Shield className="w-4 h-4 text-cyan-400" /> Corporate Entity Credentials
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Legal Entity Name</label>
            <input
              type="text"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              className="w-full px-3 py-2 bg-navy-950 border border-navy-700 rounded-xl text-white focus:outline-none focus:border-cyan-500 font-sans"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1.5">SAM.gov Unique Entity ID (UEI)</label>
            <input
              type="text"
              value={samUei}
              onChange={(e) => setSamUei(e.target.value)}
              className="w-full px-3 py-2 bg-navy-950 border border-navy-700 rounded-xl text-white font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1.5">CAGE / NCAGE Code</label>
            <input
              type="text"
              value={cageCode}
              onChange={(e) => setCageCode(e.target.value)}
              className="w-full px-3 py-2 bg-navy-950 border border-navy-700 rounded-xl text-white font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1.5">DUNS Number</label>
            <input
              type="text"
              value={dunsNumber}
              onChange={(e) => setDunsNumber(e.target.value)}
              className="w-full px-3 py-2 bg-navy-950 border border-navy-700 rounded-xl text-white font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-slate-400 font-medium mb-1.5">Facility Security Clearance (FCL)</label>
            <input
              type="text"
              value={facilityClearance}
              onChange={(e) => setFacilityClearance(e.target.value)}
              className="w-full px-3 py-2 bg-navy-950 border border-navy-700 rounded-xl text-emerald-400 font-mono font-semibold focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

