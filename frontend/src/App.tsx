import { useState } from 'react';
import MetricsPanel from './components/MetricsPanel';
import CaseList from './components/CaseList';
import CaseDetail from './components/CaseDetail';
import './App.css';

function App() {
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col font-sans text-gray-200">
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
        <div className="flex items-center gap-4">
          <span className="text-xs text-gray-500 font-mono">SQLite DB • Groq Llama/Qwen • Edge-TTS</span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Top Metrics Row */}
        <section>
          <MetricsPanel />
        </section>

        {/* Case Explorer Section */}
        <section className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-gray-800 bg-gray-900/80 flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-gray-100">Live Recovery Cases</h2>
              <p className="text-xs text-gray-400">Click any row to inspect the real-time AI decision audit timeline & voice call</p>
            </div>
          </div>
          <CaseList 
            onSelectCase={setSelectedCaseId} 
            selectedCaseId={selectedCaseId} 
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
    </div>
  );
}

export default App;
