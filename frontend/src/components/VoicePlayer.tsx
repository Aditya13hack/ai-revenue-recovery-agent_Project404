import { useRef, useState, useEffect } from 'react';

interface VoicePlayerProps {
  caseId: string;
}

export default function VoicePlayer({ caseId }: VoicePlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    setHasError(false);
    setIsPlaying(false);
    setMessage(null);

    // Fetch the transcript message
    fetch(`/api/cases/${caseId}/message`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.message) {
          setMessage(data.message);
        }
      })
      .catch(() => {});

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.load();
    }
  }, [caseId]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play()
        .then(() => setIsPlaying(true))
        .catch((err) => {
          console.error("Audio playback error:", err);
          setHasError(true);
        });
    }
  };

  const handleRetry = () => {
    setHasError(false);
    if (audioRef.current) {
      audioRef.current.load();
      audioRef.current.play()
        .then(() => setIsPlaying(true))
        .catch(() => setHasError(true));
    }
  };

  return (
    <div className="bg-gradient-to-br from-indigo-50/80 via-white to-purple-50/60 border border-indigo-100 rounded-2xl p-4.5 shadow-xs mb-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
            Hinglish Voice Recovery Call
          </h4>
        </div>
        <span className="text-[11px] font-mono text-indigo-700 bg-indigo-100/70 px-2 py-0.5 rounded-md border border-indigo-200 font-semibold">
          Edge-TTS Neural Audio (hi-IN)
        </span>
      </div>

      {/* Message Transcript */}
      {message && (
        <div className="mb-3.5 p-3.5 bg-white/90 border border-indigo-100/80 rounded-xl shadow-2xs">
          <div className="flex items-center gap-1.5 mb-1.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
              AI Agent Script
            </span>
          </div>
          <p className="text-xs text-slate-700 leading-relaxed italic">
            "{message}"
          </p>
        </div>
      )}

      {hasError ? (
        <div className="space-y-2">
          <div className="text-amber-800 text-xs bg-amber-50 border border-amber-200 p-3 rounded-xl flex items-center justify-between shadow-2xs">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 shrink-0 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>Audio generation delayed. Click retry to load.</span>
            </div>
            <button
              onClick={handleRetry}
              className="px-3 py-1 text-xs bg-amber-100 hover:bg-amber-200 text-amber-900 font-semibold rounded-lg border border-amber-300 transition"
            >
              Retry
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-2.5">
          <div className="flex items-center gap-3">
            <button 
              onClick={togglePlay}
              className="w-10 h-10 flex items-center justify-center bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white rounded-full transition-all shadow-md shadow-indigo-200 shrink-0 hover:scale-105 active:scale-95"
              title={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-5 h-5 ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
              )}
            </button>
            
            <audio 
              ref={audioRef} 
              src={`/api/cases/${caseId}/audio`} 
              onEnded={() => setIsPlaying(false)}
              onPause={() => setIsPlaying(false)}
              onPlay={() => setIsPlaying(true)}
              onError={() => setHasError(true)}
              className="w-full h-8"
              controls
              controlsList="nodownload"
            />
          </div>
          <p className="text-[11px] text-slate-400 italic">
            * Real-time neural voice synthesis generated from the LLM's custom proposal.
          </p>
        </div>
      )}
    </div>
  );
}
