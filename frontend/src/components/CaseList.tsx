import { useState, useEffect } from 'react';
import { useCases } from '../hooks/useApi';
import type { Case } from '../types';

interface CaseListProps {
  onSelectCase: (id: string) => void;
  selectedCaseId: string | null;
  dataMode: string;
}

export default function CaseList({ onSelectCase, selectedCaseId, dataMode }: CaseListProps) {
  const [outcome, setOutcome] = useState('');
  const [channel, setChannel] = useState('');
  const [page, setPage] = useState(1);
  
  useEffect(() => {
    setPage(1);
  }, [dataMode]);

  const { data, loading } = useCases({ 
    data_mode: dataMode, 
    outcome, 
    channel, 
    page, 
    per_page: 20 
  });

  const getChannelBadge = (ch: string | null) => {
    switch (ch) {
      case 'voice': return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'sms': case 'whatsapp': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'silent_retry': return 'bg-slate-100 text-slate-700 border-slate-200';
      case 'human_escalation': return 'bg-rose-50 text-rose-700 border-rose-200';
      default: return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  const getOutcomeBadge = (out: string | null) => {
    switch (out) {
      case 'recovered': return 'bg-emerald-50 text-emerald-700 border-emerald-200 font-semibold';
      case 'partially_recovered': return 'bg-amber-50 text-amber-700 border-amber-200 font-semibold';
      case 'escalated': return 'bg-orange-50 text-orange-700 border-orange-200 font-semibold';
      case 'unresolved': return 'bg-rose-50 text-rose-700 border-rose-200 font-semibold';
      case 'do_not_contact': return 'bg-rose-50 text-rose-700 border-rose-200 font-semibold';
      default: return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  const isLiveCase = (id: string) => id.startsWith('RZP-') || id.startsWith('LIVE-');

  return (
    <div className="bg-white text-slate-800">
      {/* Filters Toolbar */}
      <div className="p-3.5 border-b border-slate-200 flex flex-wrap gap-4 bg-slate-50/50 items-center justify-between">
        <div className="flex flex-wrap gap-2.5 items-center">
          <select 
            className="bg-white border border-slate-300 text-slate-700 rounded-lg px-3 py-1.5 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-indigo-500 shadow-2xs transition"
            value={outcome}
            onChange={(e) => { setOutcome(e.target.value); setPage(1); }}
          >
            <option value="">All Outcomes</option>
            <option value="recovered">Recovered</option>
            <option value="partially_recovered">Partially Recovered</option>
            <option value="escalated">Escalated</option>
            <option value="unresolved">Unresolved</option>
          </select>

          <select 
            className="bg-white border border-slate-300 text-slate-700 rounded-lg px-3 py-1.5 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-indigo-500 shadow-2xs transition"
            value={channel}
            onChange={(e) => { setChannel(e.target.value); setPage(1); }}
          >
            <option value="">All Channels</option>
            <option value="voice">Voice Call</option>
            <option value="sms">SMS / WhatsApp</option>
            <option value="silent_retry">Silent Retry</option>
            <option value="human_escalation">Human Escalation</option>
          </select>
        </div>

        {data && (
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span>
              Showing <span className="font-semibold text-slate-900">{data.total}</span> {dataMode === 'live' ? 'live Razorpay' : dataMode === 'synthetic' ? 'benchmark' : 'total'} cases
            </span>
          </div>
        )}
      </div>

      {/* Cases Table */}
      <div className="overflow-x-auto">
        {loading ? (
          <div className="p-12 text-center text-slate-400 font-medium animate-pulse">Loading cases...</div>
        ) : data?.cases.length === 0 ? (
          <div className="p-16 text-center text-slate-500 space-y-2">
            <svg className="w-10 h-10 text-slate-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <p className="font-semibold text-slate-700 text-sm">No {dataMode === 'live' ? 'Live Razorpay' : ''} cases found matching your filters.</p>
            {dataMode === 'live' && (
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Trigger a test payment failure via Razorpay checkout to capture an authentic live transaction.
              </p>
            )}
          </div>
        ) : (
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-50 text-slate-500 text-[11px] font-bold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Case ID</th>
                <th className="px-5 py-3">Origin</th>
                <th className="px-5 py-3">Customer</th>
                <th className="px-5 py-3">Amount</th>
                <th className="px-5 py-3">Type</th>
                <th className="px-5 py-3">Channel</th>
                <th className="px-5 py-3">Outcome</th>
                <th className="px-5 py-3">Recovered</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data?.cases.map((c: Case) => {
                const live = isLiveCase(c.id);
                const isSelected = selectedCaseId === c.id;
                return (
                  <tr 
                    key={c.id} 
                    onClick={() => onSelectCase(c.id)}
                    className={`cursor-pointer transition-colors ${
                      isSelected 
                        ? 'bg-indigo-50/70 ring-1 ring-indigo-500/20' 
                        : live
                          ? 'bg-emerald-50/20 hover:bg-emerald-50/40'
                          : 'hover:bg-slate-50'
                    }`}
                  >
                    <td className="px-5 py-3 font-mono text-xs font-semibold text-indigo-600">{c.id}</td>
                    <td className="px-5 py-3">
                      {live ? (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                          LIVE RZP
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                          BENCHMARK
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3 font-medium text-slate-900">{c.customer_name}</td>
                    <td className="px-5 py-3 font-semibold text-slate-900">₹{c.payment_amount.toLocaleString()}</td>
                    <td className="px-5 py-3 text-slate-500 text-xs uppercase font-medium">{c.payment_type}</td>
                    <td className="px-5 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getChannelBadge(c.assigned_channel)}`}>
                        {c.assigned_channel || 'pending'}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs border ${getOutcomeBadge(c.outcome)}`}>
                        {c.outcome || 'pending'}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-emerald-600 font-semibold">₹{c.amount_recovered.toLocaleString()}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination Footer */}
      <div className="p-3.5 border-t border-slate-200 flex justify-between items-center bg-slate-50/50 text-xs">
        <div className="text-slate-500 font-medium">
          Page {data?.page || 1} • Showing {data?.cases.length || 0} of {data?.total || 0} cases
        </div>
        <div className="flex gap-2">
          <button 
            disabled={page === 1} 
            onClick={() => setPage(p => p - 1)}
            className="px-3 py-1 bg-white rounded-lg border border-slate-200 shadow-2xs font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition"
          >
            Previous
          </button>
          <button 
            disabled={data ? (page * 20 >= data.total) : true}
            onClick={() => setPage(p => p + 1)}
            className="px-3 py-1 bg-white rounded-lg border border-slate-200 shadow-2xs font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
