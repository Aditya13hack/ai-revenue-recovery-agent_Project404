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
      <div className="h-full bg-white p-6 animate-pulse space-y-4">
        <div className="h-6 bg-slate-100 rounded w-1/4"></div>
        <div className="h-8 bg-slate-100 rounded w-1/2"></div>
        <div className="grid grid-cols-2 gap-3 mt-4">
          <div className="h-16 bg-slate-100 rounded-xl"></div>
          <div className="h-16 bg-slate-100 rounded-xl"></div>
        </div>
        <div className="h-64 bg-slate-100 rounded-xl mt-6"></div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="h-full flex items-center justify-center text-slate-400 bg-white">
        Case not found
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col overflow-hidden relative bg-white text-slate-800">
      {/* Close Button */}
      <button 
        onClick={onClose}
        className="absolute top-5 right-5 text-slate-400 hover:text-slate-700 z-10 p-1.5 rounded-xl hover:bg-slate-100 transition"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>

      {/* Header & Metadata Cards */}
      <div className="p-6 border-b border-slate-200/80 bg-gradient-to-b from-slate-50/80 to-white shrink-0">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-xs font-mono font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-200">
            {caseData.id}
          </span>
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            {caseData.payment_type}
          </span>
        </div>

        <h2 className="text-2xl font-black text-slate-900 tracking-tight">{caseData.customer_name}</h2>
        <p className="text-slate-500 text-xs font-medium mt-0.5 mb-4">
          Reason: <strong className="text-slate-700">{caseData.failure_reason}</strong> • Risk: <strong className="text-slate-700">{caseData.risk_profile}</strong>
        </p>
        
        <div className="grid grid-cols-2 gap-2.5">
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80 shadow-2xs">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Amount Due</div>
            <div className="text-lg font-black text-slate-900">₹{caseData.payment_amount.toLocaleString()}</div>
          </div>
          <div className="bg-emerald-50/70 p-3 rounded-xl border border-emerald-200/80 shadow-2xs">
            <div className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider">Recovered</div>
            <div className="text-lg font-black text-emerald-600">₹{caseData.amount_recovered.toLocaleString()}</div>
          </div>
          <div className="bg-white p-2.5 rounded-xl border border-slate-200/80 shadow-2xs">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Channel</div>
            <div className="text-xs font-bold text-indigo-600 uppercase mt-0.5">{caseData.assigned_channel || 'N/A'}</div>
          </div>
          <div className="bg-white p-2.5 rounded-xl border border-slate-200/80 shadow-2xs">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Outcome</div>
            <div className="text-xs font-bold text-emerald-600 uppercase mt-0.5">{caseData.outcome || 'Pending'}</div>
          </div>
        </div>
      </div>

      {/* Main Drawer Scroll Area */}
      <div className="flex-1 overflow-y-auto p-5 bg-slate-50/60 space-y-4">
        {caseData.assigned_channel === 'voice' && <VoicePlayer caseId={id} />}
        
        {timelineData && <CaseTimeline events={timelineData.events} />}
      </div>
    </div>
  );
}
