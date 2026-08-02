'use client';
import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, ListVideo, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function PodcastPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [currentPodcast, setCurrentPodcast] = useState<any>(null);
  const [showPlaylist, setShowPlaylist] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    // Fetch the history JSON
    fetch('/podcast/podcast_history.json?t=' + Date.now())
      .then(res => res.json())
      .then(data => {
        if (data && data.length > 0) {
          setHistory(data);
          setCurrentPodcast(data[0]);
        }
      })
      .catch(err => console.error("Could not load podcast history", err));
  }, []);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const selectPodcast = (podcast: any) => {
    setCurrentPodcast(podcast);
    setIsPlaying(true);
    setShowPlaylist(false);
    setTimeout(() => {
      if (audioRef.current) audioRef.current.play();
    }, 100);
  };

  return (
    <div className="flex flex-col gap-2">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-glass p-6 rounded-2xl flex items-center justify-between gap-6 relative z-10"
      >
        <div className="flex items-center gap-4">
          <button 
            onClick={togglePlay}
            className="w-14 h-14 rounded-full bg-primary flex items-center justify-center text-white shadow-lg shadow-primary/30 hover:scale-105 transition-transform"
          >
            {isPlaying ? <Pause size={24} /> : <Play size={24} className="ml-1" />}
          </button>
          <div>
            <div className="flex items-center gap-2 mb-1 cursor-pointer hover:opacity-80" onClick={() => setShowPlaylist(!showPlaylist)}>
              <Volume2 size={16} className="text-primary" />
              <h3 className="font-bold text-lg flex items-center gap-1">
                {currentPodcast ? currentPodcast.title : "Daily Briefing Podcast"}
                {history.length > 1 && <ChevronDown size={16} className="text-text-muted mt-0.5" />}
              </h3>
            </div>
            <p className="text-sm text-text-muted">Auto-generated top headlines via AI Voice</p>
          </div>
        </div>
        
        {/* Visualizer animation when playing */}
        <div className="hidden sm:flex items-center gap-1 h-8">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              animate={{ height: isPlaying ? ["20%", "100%", "30%"] : "20%" }}
              transition={{ repeat: Infinity, duration: 0.8, delay: i * 0.1 }}
              className="w-1.5 bg-primary/60 rounded-full"
              style={{ height: "20%" }}
            />
          ))}
        </div>

        <audio 
          ref={audioRef} 
          src={currentPodcast ? `/podcast/${currentPodcast.filename}` : "/podcast/latest.mp3"}
          onEnded={() => setIsPlaying(false)}
          preload="metadata"
        />
      </motion.div>

      {/* Playlist Dropdown */}
      <AnimatePresence>
        {showPlaylist && history.length > 1 && (
          <motion.div
            initial={{ opacity: 0, height: 0, y: -20 }}
            animate={{ opacity: 1, height: 'auto', y: 0 }}
            exit={{ opacity: 0, height: 0, y: -20 }}
            className="card-glass rounded-xl overflow-hidden mt-[-1rem] pt-6 z-0"
          >
            <div className="px-6 pb-4 pt-2 border-t border-border/30 max-h-48 overflow-y-auto">
              <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">Previous Broadcasts</h4>
              <div className="space-y-2">
                {history.map((podcast, idx) => (
                  <button
                    key={idx}
                    onClick={() => selectPodcast(podcast)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between ${
                      currentPodcast?.filename === podcast.filename 
                        ? 'bg-primary/10 text-primary font-medium' 
                        : 'hover:bg-surface-2 text-text-secondary'
                    }`}
                  >
                    <span>{podcast.title}</span>
                    {currentPodcast?.filename === podcast.filename && isPlaying && (
                      <Volume2 size={14} className="animate-pulse" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
