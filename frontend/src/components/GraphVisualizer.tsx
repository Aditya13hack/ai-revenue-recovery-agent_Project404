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
      color: 'border-blue-500 bg-blue-950/40 text-blue-300',
      glow: 'shadow-blue-500/20',
      description: 'Captures failed transaction payload from Razorpay Webhook or Batch Dataset. Extracts amount, failure reason, and customer tier into CaseContext.',
      inputs: 'Razorpay payment.failed payload or Case record',
      outputs: 'CaseContext (Pydantic object)',
    },
    {
      id: 'diagnose',
      name: '2. Diagnose Node',
      type: 'Analysis',
      badge: 'Root Cause',
      color: 'border-purple-500 bg-purple-950/40 text-purple-300',
      glow: 'shadow-purple-500/20',
      description: 'Calculates risk score (0.0–1.0) based on overdue amount, payment method (UPI vs EMI vs Sub), and failure code.',
      inputs: 'CaseContext',
      outputs: 'Diagnosis payload + Risk Assessment',
    },
    {
      id: 'triage',
      name: '3. Triage Node',
      type: 'Routing Engine',
      badge: 'Conditional Branching',
      color: 'border-cyan-500 bg-cyan-950/40 text-cyan-300',
      glow: 'shadow-cyan-500/20',
      description: 'Decides delivery channel: Voice Call (High Value), WhatsApp/SMS (Low Value), Silent Retry (Bank Timeout), or Immediate Escalation (Prior Refusal).',
      inputs: 'CaseContext + Risk Assessment',
      outputs: 'ChannelType + Routing Decision',
    },
    {
      id: 'reason',
      name: '4. Reason Node',
      type: 'LLM Reasoning',
      badge: 'Groq Llama/Qwen',
      color: 'border-amber-500 bg-amber-950/40 text-amber-300',
      glow: 'shadow-amber-500/20',
      description: 'Groq Compound LLM analyzes customer profile and formulates a structured Hinglish action proposal (discount, extension, retry date).',
      inputs: 'CaseContext + Conversation History',
      outputs: 'ActionProposal (structured JSON)',
    },
    {
      id: 'validate',
      name: '5. Validate Node',
      type: 'Control Plane',
      badge: '8 Hard Stopping Rules',
      color: 'border-emerald-500 bg-emerald-950/40 text-emerald-300',
      glow: 'shadow-emerald-500/20',
      description: 'Deterministic policy engine verifies DNC list, caps discounts to 15%, limits extensions to 7 days, checks campaign budget, and blocks hallucinations.',
      inputs: 'ActionProposal + MerchantPolicyConfig + BudgetTracker',
      outputs: 'ControlPlaneDecision (EXECUTE / MODIFY / BLOCK / ESCALATE)',
    },
    {
      id: 'execute',
      name: '6. Execute Node',
      type: 'Action Layer',
      badge: 'Razorpay + DB',
      color: 'border-indigo-500 bg-indigo-950/40 text-indigo-300',
      glow: 'shadow-indigo-500/20',
      description: 'Executes approved action: consumes campaign budget, creates Razorpay Payment Link, triggers edge-tts neural voice, and updates case.',
      inputs: 'ControlPlaneDecision (EXECUTE or MODIFY)',
      outputs: 'Executed transaction details + Budget consumption',
    },
    {
      id: 'measure',
      name: '7. Measure Node',
      type: 'Audit & Metrics',
      badge: 'ROI Calculation',
      color: 'border-teal-500 bg-teal-950/40 text-teal-300',
      glow: 'shadow-teal-500/20',
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-6xl shadow-2xl overflow-hidden my-auto">
        
        {/* Header */}
        <div className="p-6 border-b border-gray-800 bg-gray-950/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 font-bold">
              ⚡
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-gray-100">LangGraph Orchestration Pipeline</h2>
                <span className="text-xs font-mono px-2 py-0.5 bg-blue-950 text-blue-400 rounded-full border border-blue-800">
                  Compiled StateGraph
                </span>
              </div>
              <p className="text-xs text-gray-400">
                Deterministic Control Loop: Detect → Diagnose → Triage → LLM Reason → Policy Validate → Execute → Measure
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-gray-800 transition"
          >
            ✕
          </button>
        </div>

        {/* Path Filter Tabs */}
        <div className="px-6 py-3 bg-gray-900/60 border-b border-gray-800 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-400 mr-2">
            Simulate Execution Pathway:
          </span>
          <button
            onClick={() => setSelectedPath('all')}
            className={`px-3 py-1 text-xs rounded-lg font-medium transition ${
              selectedPath === 'all'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'bg-gray-800 text-gray-400 hover:text-gray-200'
            }`}
          >
            🌐 Complete Topology
          </button>
          <button
            onClick={() => setSelectedPath('happy')}
            className={`px-3 py-1 text-xs rounded-lg font-medium transition ${
              selectedPath === 'happy'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/20'
                : 'bg-gray-800 text-gray-400 hover:text-gray-200'
            }`}
          >
            🟢 Standard Voice/SMS Recovery
          </button>
          <button
            onClick={() => setSelectedPath('silent')}
            className={`px-3 py-1 text-xs rounded-lg font-medium transition ${
              selectedPath === 'silent'
                ? 'bg-cyan-600 text-white shadow-md shadow-cyan-500/20'
                : 'bg-gray-800 text-gray-400 hover:text-gray-200'
            }`}
          >
            🔄 Silent Retry (Bypasses LLM)
          </button>
          <button
            onClick={() => setSelectedPath('blocked')}
            className={`px-3 py-1 text-xs rounded-lg font-medium transition ${
              selectedPath === 'blocked'
                ? 'bg-amber-600 text-white shadow-md shadow-amber-500/20'
                : 'bg-gray-800 text-gray-400 hover:text-gray-200'
            }`}
          >
            🛡️ Control Plane Blocked / Capped
          </button>
          <button
            onClick={() => setSelectedPath('escalate')}
            className={`px-3 py-1 text-xs rounded-lg font-medium transition ${
              selectedPath === 'escalate'
                ? 'bg-rose-600 text-white shadow-md shadow-rose-500/20'
                : 'bg-gray-800 text-gray-400 hover:text-gray-200'
            }`}
          >
            🚨 Human Escalation (Prior Refusal)
          </button>
        </div>

        {/* Visual Graph Area */}
        <div className="p-6 overflow-x-auto">
          <div className="min-w-[900px] flex items-center justify-between relative py-6">
            
            {/* Connecting Background Line */}
            <div className="absolute top-1/2 left-6 right-6 h-1 bg-gray-800 -translate-y-1/2 z-0"></div>

            {/* Nodes */}
            {nodes.map((node) => {
              const active = isNodeActive(node.id);
              const isSelected = activeNode === node.id;

              return (
                <div 
                  key={node.id}
                  onClick={() => setActiveNode(node.id)}
                  className={`relative z-10 flex flex-col items-center cursor-pointer transition-all duration-300 ${
                    active ? 'opacity-100 scale-100' : 'opacity-25 grayscale scale-95'
                  }`}
                >
                  <div 
                    className={`w-28 h-28 rounded-2xl border-2 flex flex-col items-center justify-center p-3 text-center transition-all ${
                      node.color
                    } ${isSelected ? 'ring-4 ring-blue-500/50 scale-105 ' + node.glow : 'hover:scale-105'}`}
                  >
                    <span className="text-[10px] uppercase font-bold tracking-wider opacity-75">
                      {node.type}
                    </span>
                    <h4 className="text-xs font-bold mt-1 text-gray-100">
                      {node.name.split('.')[1]}
                    </h4>
                    <span className="text-[9px] font-mono mt-1 px-1.5 py-0.5 bg-black/40 rounded">
                      {node.badge}
                    </span>
                  </div>

                  {/* Pulsing indicator */}
                  {active && (
                    <span className="w-2.5 h-2.5 rounded-full bg-blue-400 mt-3 animate-ping"></span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Node Details Drawer */}
        {activeNode && (
          <div className="px-6 py-4 bg-gray-950/90 border-t border-gray-800">
            {(() => {
              const n = nodes.find((x) => x.id === activeNode)!;
              return (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="md:col-span-2">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-bold text-gray-100">{n.name}</span>
                      <span className="text-xs font-mono text-blue-400 bg-blue-950 px-2 py-0.5 rounded border border-blue-900">
                        {n.type}
                      </span>
                    </div>
                    <p className="text-xs text-gray-300 leading-relaxed">
                      {n.description}
                    </p>
                  </div>
                  <div className="text-xs space-y-1 bg-gray-900 p-3 rounded-lg border border-gray-800">
                    <div>
                      <span className="text-gray-500 font-medium">Inputs: </span>
                      <span className="text-gray-300 font-mono text-[11px]">{n.inputs}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 font-medium">Outputs: </span>
                      <span className="text-gray-300 font-mono text-[11px]">{n.outputs}</span>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* Footer */}
        <div className="p-4 bg-gray-950 border-t border-gray-800 flex items-center justify-between text-xs text-gray-500">
          <span>💡 Click any node above to inspect its inputs, outputs, and internal logic.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition"
          >
            Close Diagram
          </button>
        </div>

      </div>
    </div>
  );
}
