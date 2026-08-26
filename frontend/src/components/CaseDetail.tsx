import { useCaseDetail, useTimeline } from '../hooks/useApi';
import CaseTimeline from './CaseTimeline';
import VoicePlayer from './VoicePlayer';

interface CaseDetailProps {
  id: string;
  onClose: () => void;
}

export default function CaseDetail({ id, onClose }: CaseDetailProps) {
  const { data: caseData, loading: caseLoading } = useCaseDetail(id);
  const { data: timelineData, loading: timelineLoading } = useTimeline(id);

  if (caseLoading || timelineLoading) {
    return (
      <div className="h-full bg-gray-900 p-6 animate-pulse">
        <div className="h-8 bg-gray-800 rounded w-1/3 mb-6"></div>
        <div className="space-y-4">
          <div className="h-24 bg-gray-800 rounded"></div>
          <div className="h-64 bg-gray-800 rounded"></div>
        </div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        Case not found
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col overflow-hidden relative">
      <button 
        onClick={onClose}
        className="absolute top-4 right-4 text-gray-500 hover:text-gray-300 z-10 p-1"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>

      <div className="p-6 border-b border-gray-800 bg-gray-900 shrink-0">
        <div className="text-xs text-blue-400 font-mono mb-1">{caseData.id}</div>
        <h2 className="text-2xl font-bold text-gray-100 mb-1">{caseData.customer_name}</h2>
        <p className="text-gray-500 text-sm mb-4">{caseData.failure_reason} | {caseData.risk_profile}</p>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-800 p-3 rounded border border-gray-700">
            <div className="text-xs text-gray-500 uppercase">Amount</div>
            <div className="text-lg font-medium text-gray-200">Rs.{caseData.payment_amount.toLocaleString()}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded border border-gray-700">
            <div className="text-xs text-gray-500 uppercase">Recovered</div>
            <div className="text-lg font-medium text-green-400">Rs.{caseData.amount_recovered.toLocaleString()}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded border border-gray-700">
            <div className="text-xs text-gray-500 uppercase">Channel</div>
            <div className="text-sm font-medium text-gray-300">{caseData.assigned_channel || 'N/A'}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded border border-gray-700">
            <div className="text-xs text-gray-500 uppercase">Outcome</div>
            <div className="text-sm font-medium text-gray-300">{caseData.outcome || 'Pending'}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded border border-gray-700">
            <div className="text-xs text-gray-500 uppercase">Type</div>
            <div className="text-sm font-medium text-gray-300">{caseData.payment_type}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded border border-gray-700">
            <div className="text-xs text-gray-500 uppercase">Tier</div>
            <div className="text-sm font-medium text-gray-300">{caseData.value_tier}</div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 bg-gray-950">
        {caseData.assigned_channel === 'voice' && <VoicePlayer caseId={id} />}
        
        {timelineData && <CaseTimeline events={timelineData.events} />}
      </div>
    </div>
  );
}
