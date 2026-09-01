import type { TimelineEvent } from '../types';

export default function CaseTimeline({ events }: { events: TimelineEvent[] }) {
  const getEventColor = (type: string) => {
    switch (type) {
      case 'detection': return 'bg-blue-500 ring-4 ring-blue-100';
      case 'diagnosis': return 'bg-purple-500 ring-4 ring-purple-100';
      case 'triage': return 'bg-cyan-500 ring-4 ring-cyan-100';
      case 'proposal': return 'bg-amber-500 ring-4 ring-amber-100';
      case 'control_plane_decision': return 'bg-indigo-500 ring-4 ring-indigo-100';
      case 'execution': return 'bg-emerald-500 ring-4 ring-emerald-100';
      case 'measurement': return 'bg-teal-500 ring-4 ring-teal-100';
      default: return 'bg-slate-400 ring-4 ring-slate-100';
    }
  };

  const getDecisionBadge = (decision?: string | null) => {
    if (!decision) return null;
    switch (decision) {
      case 'EXECUTE': 
        return <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-2 py-0.5 rounded font-bold ml-2">EXECUTE</span>;
      case 'MODIFY': 
        return <span className="bg-amber-50 text-amber-700 border border-amber-200 text-xs px-2 py-0.5 rounded font-bold ml-2">MODIFY</span>;
      case 'ESCALATE': 
        return <span className="bg-orange-50 text-orange-700 border border-orange-200 text-xs px-2 py-0.5 rounded font-bold ml-2">ESCALATE</span>;
      case 'BLOCK': 
        return <span className="bg-rose-50 text-rose-700 border border-rose-200 text-xs px-2 py-0.5 rounded font-bold ml-2">BLOCK</span>;
      default: return null;
    }
  };

  if (!events || events.length === 0) return <div className="p-4 text-slate-400">No events found.</div>;

  return (
    <div className="p-1">
      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-5">Audit Trail & Guardrail Log</h3>
      <div className="relative border-l-2 border-slate-200 ml-3 space-y-5">
        {events.map((event, idx) => (
          <div key={idx} className="relative pl-6">
            <div className={`absolute -left-[9px] top-1.5 w-4 h-4 rounded-full bg-white ${getEventColor(event.event_type)}`}></div>
            
            <div className="flex flex-col">
              <div className="flex items-center flex-wrap gap-2 mb-1">
                <span className="uppercase text-xs font-bold text-slate-700 tracking-wider">
                  {event.event_type}
                </span>
                <span className="text-[11px] text-slate-400 font-mono">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
                {getDecisionBadge(event.decision)}
              </div>
              
              <div className="text-xs text-slate-600 mb-1.5 font-medium leading-relaxed">
                {event.description}
              </div>

              {event.reason && (
                <div className="text-xs bg-amber-50/80 p-2.5 rounded-lg text-amber-900 border-l-2 border-amber-400 mb-2">
                  <strong className="font-semibold">Reason:</strong> {event.reason}
                </div>
              )}

              {event.details && Object.keys(event.details).length > 0 && (
                <details className="text-xs">
                  <summary className="text-indigo-600 font-medium cursor-pointer hover:text-indigo-800 select-none">View State Payload</summary>
                  <pre className="mt-2 bg-slate-900 p-2.5 rounded-xl overflow-x-auto text-emerald-400 border border-slate-800 font-mono text-[11px] leading-tight">
                    {JSON.stringify(event.details, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
