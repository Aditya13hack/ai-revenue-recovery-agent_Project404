import { useState } from 'react';
import { useCases } from '../hooks/useApi';
import type { Case } from '../types';

interface CaseListProps {
  onSelectCase: (id: string) => void;
  selectedCaseId: string | null;
}

export default function CaseList({ onSelectCase, selectedCaseId }: CaseListProps) {
  const [outcome, setOutcome] = useState('');
  const [channel, setChannel] = useState('');
  const [page, setPage] = useState(1);
  
  const { data, loading } = useCases({ outcome, channel, page, per_page: 20 });

  const getChannelBadge = (ch: string | null) => {
    switch (ch) {
      case 'voice': return 'bg-blue-900 text-blue-300';
      case 'sms': case 'whatsapp': return 'bg-green-900 text-green-300';
      case 'silent_retry': return 'bg-gray-700 text-gray-300';
      case 'human_escalation': return 'bg-red-900 text-red-300';
      default: return 'bg-gray-700 text-gray-300';
    }
  };

  const getOutcomeBadge = (out: string | null) => {
    switch (out) {
      case 'recovered': return 'bg-green-900/50 text-green-400 border border-green-800';
      case 'partially_recovered': return 'bg-yellow-900/50 text-yellow-400 border border-yellow-800';
      case 'escalated': return 'bg-orange-900/50 text-orange-400 border border-orange-800';
      case 'unresolved': return 'bg-red-900/50 text-red-400 border border-red-800';
      case 'do_not_contact': return 'bg-red-900/50 text-red-400 border border-red-800';
      default: return 'bg-gray-800 text-gray-400 border border-gray-700';
    }
  };

  return (
    <div className="bg-gray-950 text-gray-200">
      <div className="p-4 border-b border-gray-800 flex gap-4 bg-gray-900">
        <select 
          className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500"
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
          className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500"
          value={channel}
          onChange={(e) => { setChannel(e.target.value); setPage(1); }}
        >
          <option value="">All Channels</option>
          <option value="voice">Voice</option>
          <option value="sms">SMS</option>
          <option value="silent_retry">Silent Retry</option>
          <option value="human_escalation">Human Escalation</option>
        </select>

        {data && <span className="text-gray-500 text-sm self-center ml-auto">{data.total} total cases</span>}
      </div>

      <div>
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading cases...</div>
        ) : (
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-gray-900 sticky top-0 z-10 border-b border-gray-800 shadow-sm">
              <tr>
                <th className="px-4 py-3 font-medium text-gray-400">ID</th>
                <th className="px-4 py-3 font-medium text-gray-400">Customer</th>
                <th className="px-4 py-3 font-medium text-gray-400">Amount</th>
                <th className="px-4 py-3 font-medium text-gray-400">Type</th>
                <th className="px-4 py-3 font-medium text-gray-400">Channel</th>
                <th className="px-4 py-3 font-medium text-gray-400">Outcome</th>
                <th className="px-4 py-3 font-medium text-gray-400">Recovered</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {data?.cases.map((c: Case) => (
                <tr 
                  key={c.id} 
                  onClick={() => onSelectCase(c.id)}
                  className={`cursor-pointer hover:bg-gray-800 transition-colors ${selectedCaseId === c.id ? 'bg-gray-800' : ''}`}
                >
                  <td className="px-4 py-3 text-blue-400 font-mono text-xs">{c.id}</td>
                  <td className="px-4 py-3 font-medium">{c.customer_name}</td>
                  <td className="px-4 py-3">Rs.{c.payment_amount.toLocaleString()}</td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{c.payment_type}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getChannelBadge(c.assigned_channel)}`}>
                      {c.assigned_channel || 'pending'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2.5 py-1 rounded text-xs font-medium ${getOutcomeBadge(c.outcome)}`}>
                      {c.outcome || 'pending'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-green-400 font-medium">Rs.{c.amount_recovered.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="p-4 border-t border-gray-800 flex justify-between items-center bg-gray-900 text-sm">
        <div className="text-gray-400">
          Page {data?.page || 1} | Showing {data?.cases.length || 0} of {data?.total || 0}
        </div>
        <div className="flex gap-2">
          <button 
            disabled={page === 1} 
            onClick={() => setPage(p => p - 1)}
            className="px-3 py-1 bg-gray-800 rounded border border-gray-700 disabled:opacity-50 hover:bg-gray-700"
          >
            Prev
          </button>
          <button 
            disabled={data ? (page * 20 >= data.total) : true}
            onClick={() => setPage(p => p + 1)}
            className="px-3 py-1 bg-gray-800 rounded border border-gray-700 disabled:opacity-50 hover:bg-gray-700"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
