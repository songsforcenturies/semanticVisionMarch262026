import React, { useState, useRef, useEffect } from 'react';
import { AmbientMusicPlayer } from '@/lib/ambientMusic';
import { Music, Volume2, VolumeX } from 'lucide-react';

const C = {
  gold: '#D4A853', muted: '#94A3B8', cream: '#F8F5EE',
};

const MusicPlayerWidget = ({ storyText = '', mood: propMood = null, autoPlay = false }) => {
  const [playing, setPlaying] = useState(false);
  const [volume, setVolume] = useState(0.12);
  const [currentMood, setCurrentMood] = useState(propMood || 'calm');
  const playerRef = useRef(null);

  useEffect(() => {
    if (!propMood && storyText) {
      const detected = AmbientMusicPlayer.analyzeMood(storyText);
      setCurrentMood(detected);
    }
  }, [storyText, propMood]);

  useEffect(() => {
    if (autoPlay && !playing) {
      handlePlay();
    }
    return () => { if (playerRef.current) playerRef.current.stop(); };
  }, []);

  const handlePlay = () => {
    if (playing) {
      playerRef.current?.stop();
      setPlaying(false);
    } else {
      const p = new AmbientMusicPlayer();
      p.start(currentMood, volume);
      playerRef.current = p;
      setPlaying(true);
    }
  };

  const handleVolumeChange = (e) => {
    const v = parseFloat(e.target.value);
    setVolume(v);
    playerRef.current?.setVolume(v);
  };

  const handleMoodChange = (mood) => {
    setCurrentMood(mood);
    if (playing) {
      playerRef.current?.stop();
      const p = new AmbientMusicPlayer();
      p.start(mood, volume);
      playerRef.current = p;
    }
  };

  const moods = AmbientMusicPlayer.getMoods();

  return (
    <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-xl" data-testid="music-player"
      style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)' }}>
      <button onClick={handlePlay}
        className="w-7 h-7 flex items-center justify-center rounded-full transition-all"
        style={{
          background: playing ? 'rgba(212,168,83,0.25)' : 'rgba(255,255,255,0.08)',
          color: playing ? C.gold : C.muted,
        }}
        data-testid="music-toggle-btn">
        {playing ? <Volume2 size={13} /> : <Music size={13} />}
      </button>

      {playing && (
        <input type="range" min="0" max="0.4" step="0.01" value={volume}
          onChange={handleVolumeChange}
          className="w-14 h-1 accent-amber-500" data-testid="music-volume" />
      )}

      <select value={currentMood} onChange={(e) => handleMoodChange(e.target.value)}
        className="text-xs font-bold bg-transparent border-none outline-none cursor-pointer"
        style={{ color: C.muted }}
        data-testid="music-mood-select">
        {moods.map(m => (
          <option key={m} value={m} style={{ background: '#1A2236', color: '#F8F5EE' }}>
            {m.charAt(0).toUpperCase() + m.slice(1)}
          </option>
        ))}
      </select>
    </div>
  );
};

export default MusicPlayerWidget;
