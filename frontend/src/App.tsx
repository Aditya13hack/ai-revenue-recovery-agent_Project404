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

      <header className="bg-white/90 backdrop-blur-md border-b border-slate-200/80 px-6 py-3.5 sticky top-0 z-30 shadow-xs transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center shadow-xs text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="text-base font-bold tracking-tight text-slate-900">
                  AI Revenue Recovery Agent
                </h1>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                  Track 03
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                Deterministic Policy Engine & Autonomous Dunning Pipeline
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setShowSandbox(true)}
              className="flex items-center gap-2 px-3.5 py-1.5 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 shadow-2xs transition-all hover:border-slate-300"
            >
              <svg className="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span>Policy Sandbox</span>
            </button>
            <button
              onClick={() => setShowGraph(true)}
              className="flex items-center gap-2 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-xs transition-all"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7" />
              </svg>
              <span>Pipeline Architecture</span>
            </button>
          </div>
        </div>
      </header>


      <main className="max-w-7xl w-full mx-auto p-6 space-y-6">

        <div className="bg-white p-2 rounded-xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-lg border border-slate-200/60">
            <button
              onClick={() => setDataMode('all')}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-md transition-all ${
                dataMode === 'all'
                  ? 'bg-white text-slate-900 shadow-2xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              All Cases
            </button>
            <button
              onClick={() => setDataMode('live')}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-md transition-all flex items-center gap-1.5 ${
                dataMode === 'live'
                  ? 'bg-white text-emerald-700 shadow-2xs border border-emerald-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${dataMode === 'live' ? 'bg-emerald-500' : 'bg-slate-400'}`}></span>
              Live Razorpay Events
            </button>
            <button
              onClick={() => setDataMode('synthetic')}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-md transition-all ${
                dataMode === 'synthetic'
                  ? 'bg-white text-indigo-700 shadow-2xs border border-indigo-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              Synthetic Benchmark
            </button>
          </div>

          <div className="text-xs text-slate-500 font-medium px-3 flex items-center gap-1.5">
            {dataMode === 'live' && (
              <span className="text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">
                Live Mode: Webhook transactions from Razorpay API
              </span>
            )}
            {dataMode === 'synthetic' && (
              <span className="text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded border border-indigo-200">
                Benchmark Mode: 200 Multi-tier synthetic recovery cases
              </span>
            )}
            {dataMode === 'all' && (
              <span className="text-slate-600 bg-slate-50 px-2.5 py-1 rounded border border-slate-200">
                Aggregate View: Live API Webhooks + Benchmark Evaluations
              </span>
            )}
          </div>
        </div>


        <section>
          <MetricsPanel dataMode={dataMode} />
        </section>


        <section className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">
                {dataMode === 'live' ? 'Live Webhook Cases' : dataMode === 'synthetic' ? 'Synthetic Benchmark Cases' : 'Recovery Case Explorer'}
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Inspect audit trail logs, LLM reasoning proposals, and voice synthesis scripts
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


      {showGraph && (
        <GraphVisualizer onClose={() => setShowGraph(false)} />
      )}


      {showSandbox && (
        <PolicySandbox onClose={() => setShowSandbox(false)} />
      )}
    </div>
  );
}

export default App;
