import { useState } from 'react';

interface GraphVisualizerProps {
  onClose: () => void;
}

type PathType = 'all' | 'happy' | 'silent' | 'escalate' | 'blocked';

export default function GraphVisualizer({ onClose }: GraphVisualizerProps) {
  const [selectedPath, setSelectedPath] = useState<PathType>('all');
  const [activeNode, setActiveNode] = useState<string | null>(null);

  const nodes = [
    {
      id: 'detect',
      name: '1. Detect Node',
      type: 'Ingestion',
      badge: 'SQLite / Webhook',
      color: 'border-blue-300 bg-blue-50/70 text-blue-900',
      glow: 'shadow-blue-500/10 ring-4 ring-blue-100',
      description: 'Captures failed transaction payload from Razorpay Webhook or Batch Dataset. Extracts amount, failure reason, and customer tier into CaseContext.',
      inputs: 'Razorpay payment.failed payload or Case record',
      outputs: 'CaseContext (Pydantic object)',
    },
    {
      id: 'diagnose',
      name: '2. Diagnose Node',
      type: 'Analysis',
      badge: 'Root Cause',
      color: 'border-purple-300 bg-purple-50/70 text-purple-900',
      glow: 'shadow-purple-500/10 ring-4 ring-purple-100',
      description: 'Calculates risk score (0.0–1.0) based on overdue amount, payment method (UPI vs EMI vs Sub), and failure code.',
      inputs: 'CaseContext',
      outputs: 'Diagnosis payload + Risk Assessment',
    },
    {
      id: 'triage',
      name: '3. Triage Node',
      type: 'Routing Engine',
      badge: 'Conditional Branching',
      color: 'border-cyan-300 bg-cyan-50/70 text-cyan-900',
      glow: 'shadow-cyan-500/10 ring-4 ring-cyan-100',
      description: 'Decides delivery channel: Voice Call (High Value), WhatsApp/SMS (Low Value), Silent Retry (Bank Timeout), or Immediate Escalation (Prior Refusal).',
      inputs: 'CaseContext + Risk Assessment',
      outputs: 'ChannelType + Routing Decision',
    },
    {
      id: 'reason',
      name: '4. Reason Node',
      type: 'LLM Reasoning',
      badge: 'Groq Llama/Qwen',
      color: 'border-amber-300 bg-amber-50/70 text-amber-900',
      glow: 'shadow-amber-500/10 ring-4 ring-amber-100',
      description: 'Groq Compound LLM analyzes customer profile and formulates a structured Hinglish action proposal (discount, extension, retry date).',
      inputs: 'CaseContext + Conversation History',
      outputs: 'ActionProposal (structured JSON)',
    },
    {
      id: 'validate',
      name: '5. Validate Node',
      type: 'Control Plane',
      badge: '8 Hard Stopping Rules',
      color: 'border-emerald-300 bg-emerald-50/70 text-emerald-900',
      glow: 'shadow-emerald-500/10 ring-4 ring-emerald-100',
      description: 'Deterministic policy engine verifies DNC list, caps discounts to 15%, limits extensions to 7 days, checks campaign budget, and blocks hallucinations.',
      inputs: 'ActionProposal + MerchantPolicyConfig + BudgetTracker',
      outputs: 'ControlPlaneDecision (EXECUTE / MODIFY / BLOCK / ESCALATE)',
    },
    {
      id: 'execute',
      name: '6. Execute Node',
      type: 'Action Layer',
      badge: 'Razorpay + DB',
      color: 'border-indigo-300 bg-indigo-50/70 text-indigo-900',
      glow: 'shadow-indigo-500/10 ring-4 ring-indigo-100',
      description: 'Executes approved action: consumes campaign budget, creates Razorpay Payment Link, triggers edge-tts neural voice, and updates case.',
      inputs: 'ControlPlaneDecision (EXECUTE or MODIFY)',
      outputs: 'Executed transaction details + Budget consumption',
    },
    {
      id: 'measure',
      name: '7. Measure Node',
      type: 'Audit & Metrics',
      badge: 'ROI Calculation',
      color: 'border-teal-300 bg-teal-50/70 text-teal-900',
      glow: 'shadow-teal-500/10 ring-4 ring-teal-100',
      description: 'Calculates recovered revenue, logs full audit event trail with cryptographic timestamps, and updates campaign batch metrics.',
      inputs: 'Final state from Execute or Early Exit',
      outputs: 'BatchMetrics + Complete Case Timeline',
    },
  ];

  const isNodeActive = (nodeId: string) => {
    if (selectedPath === 'all') return true;
    if (selectedPath === 'happy') {
      return ['detect', 'diagnose', 'triage', 'reason', 'validate', 'execute', 'measure'].includes(nodeId);
    }
    if (selectedPath === 'silent') {
      return ['detect', 'diagnose', 'triage', 'execute', 'measure'].includes(nodeId);
    }
    if (selectedPath === 'escalate') {
      return ['detect', 'diagnose', 'triage', 'measure'].includes(nodeId);
    }
    if (selectedPath === 'blocked') {
      return ['detect', 'diagnose', 'triage', 'reason', 'validate', 'measure'].includes(nodeId);
    }
    return true;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white border border-slate-200/80 rounded-3xl w-full max-w-6xl shadow-2xl overflow-hidden my-auto">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-200 bg-gradient-to-r from-slate-50 via-white to-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-600 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-200">
              ⚡
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h2 className="text-lg font-bold text-slate-900">LangGraph Orchestration Pipeline</h2>
                <span className="text-xs font-semibold px-2.5 py-0.5 bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200">
                  Compiled StateGraph v0.2
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium mt-0.5">
                Deterministic Control Loop: Detect → Diagnose → Triage → LLM Reason → Policy Validate → Execute → Measure
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 p-2 rounded-xl hover:bg-slate-100 transition"
          >
            ✕
          </button>
        </div>

        {/* Path Filter Tabs */}
        <div className="px-6 py-3 bg-slate-50/80 border-b border-slate-200 flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 mr-2">
            Execution Pathway:
          </span>
          <button
            onClick={() => setSelectedPath('all')}
            className={`px-3.5 py-1.5 text-xs rounded-xl font-semibold transition ${
              selectedPath === 'all'
                ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-200'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            🌐 Complete Topology
          </button>
          <button
            onClick={() => setSelectedPath('happy')}
            className={`px-3.5 py-1.5 text-xs rounded-xl font-semibold transition ${
              selectedPath === 'happy'
                ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-200'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            🟢 Standard Voice/SMS Recovery
          </button>
          <button
            onClick={() => setSelectedPath('silent')}
            className={`px-3.5 py-1.5 text-xs rounded-xl font-semibold transition ${
              selectedPath === 'silent'
                ? 'bg-cyan-600 text-white shadow-sm shadow-cyan-200'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            🔄 Silent Retry (Bypasses LLM)
          </button>
          <button
            onClick={() => setSelectedPath('blocked')}
            className={`px-3.5 py-1.5 text-xs rounded-xl font-semibold transition ${
              selectedPath === 'blocked'
                ? 'bg-amber-600 text-white shadow-sm shadow-amber-200'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            🛡️ Control Plane Blocked / Capped
          </button>
          <button
            onClick={() => setSelectedPath('escalate')}
            className={`px-3.5 py-1.5 text-xs rounded-xl font-semibold transition ${
              selectedPath === 'escalate'
                ? 'bg-rose-600 text-white shadow-sm shadow-rose-200'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            🚨 Human Escalation (Prior Refusal)
          </button>
        </div>

        {/* Visual Graph Area */}
        <div className="p-8 overflow-x-auto bg-slate-50/40">
          <div className="min-w-[900px] flex items-center justify-between relative py-6">
            
            {/* Connecting Background Line */}
            <div className="absolute top-1/2 left-6 right-6 h-1 bg-slate-200 -translate-y-1/2 z-0"></div>

            {/* Nodes */}
            {nodes.map((node) => {
              const active = isNodeActive(node.id);
              const isSelected = activeNode === node.id;

              return (
                <div 
                  key={node.id}
                  onClick={() => setActiveNode(node.id)}
                  className={`relative z-10 flex flex-col items-center cursor-pointer transition-all duration-300 ${
                    active ? 'opacity-100 scale-100' : 'opacity-30 grayscale scale-95'
                  }`}
                >
                  <div 
                    className={`w-28 h-28 rounded-2xl border-2 flex flex-col items-center justify-center p-3 text-center transition-all ${
                      node.color
                    } ${isSelected ? 'scale-105 ' + node.glow : 'hover:scale-105 shadow-xs'}`}
                  >
                    <span className="text-[10px] uppercase font-bold tracking-wider opacity-80">
                      {node.type}
                    </span>
                    <h4 className="text-xs font-black mt-1 text-slate-900">
                      {node.name.split('.')[1]}
                    </h4>
                    <span className="text-[9px] font-mono mt-1 px-1.5 py-0.5 bg-white/80 border border-black/5 rounded font-medium">
                      {node.badge}
                    </span>
                  </div>

                  {/* Pulsing indicator */}
                  {active && (
                    <span className="w-2 h-2 rounded-full bg-indigo-500 mt-2.5 animate-ping"></span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Node Details Drawer */}
        {activeNode && (
          <div className="px-6 py-4 bg-slate-50 border-t border-slate-200">
            {(() => {
              const n = nodes.find((x) => x.id === activeNode)!;
              return (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="md:col-span-2">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-bold text-slate-900">{n.name}</span>
                      <span className="text-xs font-mono font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                        {n.type}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed font-medium">
                      {n.description}
                    </p>
                  </div>
                  <div className="text-xs space-y-1.5 bg-white p-3 rounded-xl border border-slate-200 shadow-2xs">
                    <div>
                      <span className="text-slate-400 font-bold uppercase text-[10px]">Inputs: </span>
                      <p className="text-slate-700 font-mono text-[11px] mt-0.5">{n.inputs}</p>
                    </div>
                    <div className="pt-1 border-t border-slate-100">
                      <span className="text-slate-400 font-bold uppercase text-[10px]">Outputs: </span>
                      <p className="text-slate-700 font-mono text-[11px] mt-0.5">{n.outputs}</p>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* Footer */}
        <div className="p-4 bg-white border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 font-medium">
          <span>💡 Click any node above to inspect its inputs, outputs, and internal logic.</span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-semibold transition shadow-xs"
          >
            Close Diagram
          </button>
        </div>

      </div>
    </div>
  );
}
