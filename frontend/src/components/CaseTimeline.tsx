import type { TimelineEvent } from '../types';

export default function CaseTimeline({ events }: { events: TimelineEvent[] }) {
  const getEventColor = (type: string) => {
    switch (type) {
      case 'detection': return 'bg-blue-500 border-blue-500';
      case 'diagnosis': return 'bg-purple-500 border-purple-500';
      case 'triage': return 'bg-cyan-500 border-cyan-500';
      case 'proposal': return 'bg-yellow-500 border-yellow-500';
      case 'control_plane_decision': return 'bg-orange-500 border-orange-500';
      case 'execution': return 'bg-green-500 border-green-500';
      case 'measurement': return 'bg-gray-500 border-gray-500';
      default: return 'bg-gray-500 border-gray-500';
    }
  };

  const getDecisionBadge = (decision?: string | null) => {
    if (!decision) return null;
    switch (decision) {
      case 'EXECUTE': return <span className="bg-green-900 text-green-300 text-xs px-2 py-0.5 rounded font-bold ml-2">EXECUTE</span>;
      case 'MODIFY': return <span className="bg-yellow-900 text-yellow-300 text-xs px-2 py-0.5 rounded font-bold ml-2">MODIFY</span>;
      case 'ESCALATE': return <span className="bg-orange-900 text-orange-300 text-xs px-2 py-0.5 rounded font-bold ml-2">ESCALATE</span>;
      case 'BLOCK': return <span className="bg-red-900 text-red-300 text-xs px-2 py-0.5 rounded font-bold ml-2">BLOCK</span>;
      default: return null;
    }
  };

  if (!events || events.length === 0) return <div className="p-4 text-gray-500">No events found.</div>;

  return (
    <div className="p-4">
      <h3 className="text-lg font-medium text-gray-200 mb-6">Audit Timeline</h3>
      <div className="relative border-l-2 border-gray-700 ml-3 space-y-6">
        {events.map((event, idx) => (
          <div key={idx} className="relative pl-6">
            <div className={`absolute -left-[9px] top-1.5 w-4 h-4 rounded-full border-2 bg-gray-900 ${getEventColor(event.event_type)}`}></div>
            
            <div className="flex flex-col">
              <div className="flex items-center flex-wrap gap-2 mb-1">
                <span className="uppercase text-xs font-bold text-gray-400 tracking-wider">
                  {event.event_type}
                </span>
                <span className="text-xs text-gray-500 font-mono">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
                {getDecisionBadge(event.decision)}
              </div>
              
              <div className="text-sm text-gray-300 mb-2">
                {event.description}
              </div>

              {event.reason && (
                <div className="text-xs bg-gray-800 p-2 rounded text-gray-400 border-l-2 border-orange-500 mb-2">
                  <strong>Reason:</strong> {event.reason}
                </div>
              )}

              {event.details && Object.keys(event.details).length > 0 && (
                <details className="text-xs">
                  <summary className="text-gray-500 cursor-pointer hover:text-gray-300 select-none">View Details</summary>
                  <pre className="mt-2 bg-gray-950 p-2 rounded overflow-x-auto text-gray-400 border border-gray-800 font-mono">
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
