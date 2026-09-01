import { useState } from 'react';
import MetricsPanel from './components/MetricsPanel';
import CaseList from './components/CaseList';
import CaseDetail from './components/CaseDetail';
import GraphVisualizer from './components/GraphVisualizer';
import PolicySandbox from './components/PolicySandbox';
import './App.css';

type DataMode = 'all' | 'synthetic' | 'live';

function App() {
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [showGraph, setShowGraph] = useState(false);
  const [showSandbox, setShowSandbox] = useState(false);
  const [dataMode, setDataMode] = useState<DataMode>('all');

  return (
    <div className="min-h-screen font-sans text-slate-800 antialiased selection:bg-indigo-100 selection:text-indigo-900">
      {/* Top Navigation Bar */}
      <header className="bg-white/85 backdrop-blur-md border-b border-slate-200/80 px-6 py-4 sticky top-0 z-30 shadow-xs transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-blue-600 to-sky-500 flex items-center justify-center shadow-md shadow-indigo-200/60 text-white">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd"></path>
              </svg>
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="text-lg font-bold tracking-tight text-slate-900">
                  AI Revenue Recovery Agent
                </h1>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200/80 shadow-2xs">
                  Razorpay Track 03
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                Deterministic Control Plane & Autonomous Recovery Pipeline
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setShowSandbox(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white text-xs font-semibold rounded-xl shadow-xs shadow-amber-200 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
            >
              <span>🛡️</span>
              <span>Test Policy Sandbox</span>
            </button>
            <button
              onClick={() => setShowGraph(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-indigo-600 via-blue-600 to-teal-600 hover:from-indigo-700 hover:to-teal-700 text-white text-xs font-semibold rounded-xl shadow-xs shadow-indigo-200 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
            >
              <span>⚡</span>
              <span>View LangGraph Pipeline</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Mode Switcher Bar */}
        <div className="bg-white/80 backdrop-blur-md p-2 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-1.5 p-1 bg-slate-100/90 rounded-xl border border-slate-200/60">
            <button
              onClick={() => setDataMode('all')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                dataMode === 'all'
                  ? 'bg-white text-indigo-700 shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              🌐 All Cases
            </button>
            <button
              onClick={() => setDataMode('live')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 ${
                dataMode === 'live'
                  ? 'bg-white text-emerald-700 shadow-xs border border-emerald-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${dataMode === 'live' ? 'bg-emerald-500 animate-ping' : 'bg-emerald-500'}`}></span>
              Live Razorpay Events
            </button>
            <button
              onClick={() => setDataMode('synthetic')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                dataMode === 'synthetic'
                  ? 'bg-white text-blue-700 shadow-xs border border-blue-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              📊 Synthetic Benchmark
            </button>
          </div>

          <div className="text-xs text-slate-500 font-medium px-3 flex items-center gap-1.5">
            {dataMode === 'live' && (
              <span className="text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200/80">
                🟢 Live Mode: Webhook transactions from Razorpay Sandbox API
              </span>
            )}
            {dataMode === 'synthetic' && (
              <span className="text-blue-700 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-200/80">
                📊 Benchmark Mode: 200 Multi-tier synthetic recovery cases
              </span>
            )}
            {dataMode === 'all' && (
              <span className="text-slate-600 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200">
                🌐 Aggregate View: Real API webhooks + Benchmark evaluations
              </span>
            )}
          </div>
        </div>

        {/* Top Metrics Row */}
        <section>
          <MetricsPanel dataMode={dataMode} />
        </section>

        {/* Case Explorer Section */}
        <section className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="p-5 border-b border-slate-200/80 bg-gradient-to-r from-slate-50/80 via-white to-slate-50/80 flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <span>{dataMode === 'live' ? '🟢 Live Webhook Cases' : dataMode === 'synthetic' ? '📊 Synthetic Benchmark Cases' : 'Recovery Case Explorer'}</span>
                <span className="text-xs font-normal text-slate-400">| Real-time Audit & Voice Synthesis</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Click any case to inspect the live audit trail, Groq AI Hinglish reasoning, and Edge-TTS voice call
              </p>
            </div>
          </div>
          <CaseList 
            onSelectCase={setSelectedCaseId} 
            selectedCaseId={selectedCaseId}
            dataMode={dataMode}
          />
        </section>
      </main>

      {/* Slide-over Case Detail Modal */}
      {selectedCaseId && (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/30 backdrop-blur-xs transition-opacity animate-fade-in">
          <div className="w-full max-w-xl bg-white h-full shadow-2xl border-l border-slate-200 flex flex-col">
            <CaseDetail 
              id={selectedCaseId} 
              onClose={() => setSelectedCaseId(null)} 
            />
          </div>
        </div>
      )}

      {/* Interactive LangGraph Architecture Visualizer Modal */}
      {showGraph && (
        <GraphVisualizer onClose={() => setShowGraph(false)} />
      )}

      {/* Interactive Policy Sandbox & Guardrail Simulator Modal */}
      {showSandbox && (
        <PolicySandbox onClose={() => setShowSandbox(false)} />
      )}
    </div>
  );
}

export default App;
