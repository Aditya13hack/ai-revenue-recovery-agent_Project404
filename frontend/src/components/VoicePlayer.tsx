import { useRef, useState, useEffect } from 'react';

interface VoicePlayerProps {
  caseId: string;
}

export default function VoicePlayer({ caseId }: VoicePlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    setHasError(false);
    setIsPlaying(false);
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

  return (
    <div className="bg-gray-900/90 border border-blue-900/40 rounded-xl p-4 mb-6 shadow-lg">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse"></span>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-200">
            Hinglish Voice Recovery Call
          </h4>
        </div>
        <span className="text-xs font-mono text-blue-400 bg-blue-950/60 px-2 py-0.5 rounded border border-blue-800/40">
          Edge-TTS Neural Audio
        </span>
      </div>

      {hasError ? (
        <div className="text-amber-400/90 text-xs bg-amber-950/40 border border-amber-800/50 p-3 rounded-lg flex items-center gap-2">
          <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>Audio call recording unavailable for this channel type.</span>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <button 
              onClick={togglePlay}
              className="w-10 h-10 flex items-center justify-center bg-blue-600 hover:bg-blue-500 text-white rounded-full transition-all shadow-md shadow-blue-600/30 shrink-0"
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
          <p className="text-[11px] text-gray-400 italic">
            * Simulated Indian fintech customer interaction in natural Hinglish.
          </p>
        </div>
      )}
    </div>
  );
}
