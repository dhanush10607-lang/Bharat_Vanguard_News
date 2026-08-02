'use client';
import { useState, useRef } from 'react';
import { Play, Pause, Volume2 } from 'lucide-react';
import { motion } from 'framer-motion';

export function PodcastPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

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

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-glass p-6 rounded-2xl flex items-center justify-between gap-6"
    >
      <div className="flex items-center gap-4">
        <button 
          onClick={togglePlay}
          className="w-14 h-14 rounded-full bg-primary flex items-center justify-center text-white shadow-lg shadow-primary/30 hover:scale-105 transition-transform"
        >
          {isPlaying ? <Pause size={24} /> : <Play size={24} className="ml-1" />}
        </button>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Volume2 size={16} className="text-primary" />
            <h3 className="font-bold text-lg">Daily Briefing Podcast</h3>
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
        src="/podcast/latest.mp3" 
        onEnded={() => setIsPlaying(false)}
        preload="metadata"
      />
    </motion.div>
  );
}
