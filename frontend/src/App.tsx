import { useState } from 'react';
import MetricsPanel from './components/MetricsPanel';
import CaseList from './components/CaseList';
import CaseDetail from './components/CaseDetail';
import GraphVisualizer from './components/GraphVisualizer';
import './App.css';

type DataMode = 'all' | 'synthetic' | 'live';

function App() {
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [showGraph, setShowGraph] = useState(false);
  const [dataMode, setDataMode] = useState<DataMode>('all');

  return (
    <div className="min-h-screen bg-gray-950 font-sans text-gray-200">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center justify-between sticky top-0 z-30 shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd"></path>
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-gray-100 flex items-center gap-2">
              AI Revenue Recovery Agent
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-900/60 text-blue-400 border border-blue-700/50">Track 03</span>
            </h1>
            <p className="text-xs text-gray-400">Razorpay AI Buildathon 2026 • Deterministic Control Plane Architecture</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowGraph(true)}
            className="flex items-center gap-2 px-3.5 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold rounded-lg shadow-lg shadow-blue-500/20 transition-all hover:scale-105 active:scale-95"
          >
            <span>⚡</span>
            <span>View LangGraph Pipeline</span>
          </button>
          <span className="text-xs text-gray-500 font-mono hidden md:inline">SQLite • Groq • Edge-TTS</span>
        </div>
      </header>

      {/* Data Mode Toggle Bar */}
      <div className="bg-gray-900/80 border-b border-gray-800 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-1 border border-gray-700">
            <button
              onClick={() => setDataMode('all')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-all ${
                dataMode === 'all'
                  ? 'bg-purple-600 text-white shadow-md shadow-purple-500/20'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
              }`}
            >
              🌐 All Cases
            </button>
            <button
              onClick={() => setDataMode('live')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-all flex items-center gap-1.5 ${
                dataMode === 'live'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/20'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${dataMode === 'live' ? 'bg-white animate-pulse' : 'bg-emerald-500'}`}></span>
              Live Razorpay
            </button>
            <button
              onClick={() => setDataMode('synthetic')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-all ${
                dataMode === 'synthetic'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
              }`}
            >
              📊 Synthetic Benchmark
            </button>
          </div>

          <div className="text-[11px] text-gray-500 hidden md:block">
            {dataMode === 'live' && 'Showing only real Razorpay webhook cases (RZP-*, LIVE-*)'}
            {dataMode === 'synthetic' && 'Showing only generated benchmark cases (CASE-*)'}
            {dataMode === 'all' && 'Showing all cases from both sources'}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Top Metrics Row */}
        <section>
          <MetricsPanel dataMode={dataMode} />
        </section>

        {/* Case Explorer Section */}
        <section className="bg-gray-900 border border-gray-800 rounded-xl shadow-xl">
          <div className="p-4 border-b border-gray-800 bg-gray-900/80 flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-gray-100">
                {dataMode === 'live' ? '🟢 Live Razorpay Recovery Cases' : dataMode === 'synthetic' ? '📊 Synthetic Benchmark Cases' : 'All Recovery Cases'}
              </h2>
              <p className="text-xs text-gray-400">Click any row to inspect the real-time AI decision audit timeline & voice call</p>
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
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-xs transition-opacity animate-fade-in">
          <div className="w-full max-w-xl bg-gray-900 h-full shadow-2xl border-l border-gray-800 flex flex-col">
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
    </div>
  );
}

export default App;
