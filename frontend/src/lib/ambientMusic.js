/**
 * Ambient Music Generator using Web Audio API
 * Generates mood-based background music for audio book playback
 */

const MOODS = {
  adventurous: { tempo: 140, baseNote: 60, scale: [0, 2, 4, 5, 7, 9, 11], energy: 0.8, color: 'bright' },
  calm: { tempo: 70, baseNote: 55, scale: [0, 2, 4, 7, 9], energy: 0.3, color: 'warm' },
  mysterious: { tempo: 90, baseNote: 48, scale: [0, 1, 4, 5, 7, 8, 11], energy: 0.5, color: 'dark' },
  joyful: { tempo: 120, baseNote: 62, scale: [0, 2, 4, 5, 7, 9, 11], energy: 0.7, color: 'bright' },
  emotional: { tempo: 80, baseNote: 53, scale: [0, 2, 3, 5, 7, 8, 10], energy: 0.4, color: 'warm' },
  exciting: { tempo: 150, baseNote: 58, scale: [0, 2, 4, 5, 7, 9, 11], energy: 0.9, color: 'bright' },
  peaceful: { tempo: 60, baseNote: 52, scale: [0, 2, 4, 7, 9], energy: 0.2, color: 'warm' },
  inspiring: { tempo: 100, baseNote: 57, scale: [0, 2, 4, 5, 7, 9, 11], energy: 0.6, color: 'bright' },
};

function midiToFreq(midi) {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export class AmbientMusicPlayer {
  constructor() {
    this.ctx = null;
    this.gainNode = null;
    this.playing = false;
    this.timeouts = [];
    this.oscillators = [];
  }

  start(mood = 'calm', volume = 0.15) {
    if (this.playing) this.stop();

    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    this.gainNode = this.ctx.createGain();
    this.gainNode.gain.value = volume;
    this.gainNode.connect(this.ctx.destination);
    this.playing = true;

    const config = MOODS[mood] || MOODS.calm;
    this._playLoop(config);
  }

  _playLoop(config) {
    if (!this.playing) return;

    const beatDuration = 60 / config.tempo;

    // Play a note
    const interval = pickRandom(config.scale);
    const octaveShift = pickRandom([0, 0, 0, 12, -12]);
    const midi = config.baseNote + interval + octaveShift;
    const freq = midiToFreq(midi);

    this._playTone(freq, beatDuration * 2, config.energy * 0.3);

    // Sometimes play a chord (two notes)
    if (Math.random() < 0.4) {
      const interval2 = pickRandom(config.scale);
      const freq2 = midiToFreq(config.baseNote + interval2 + 12);
      this._playTone(freq2, beatDuration * 3, config.energy * 0.15);
    }

    // Pad drone (low background)
    if (Math.random() < 0.15) {
      this._playPad(midiToFreq(config.baseNote - 12), beatDuration * 8, config.energy * 0.1);
    }

    const nextDelay = beatDuration * (1 + Math.random() * 2) * 1000;
    const t = setTimeout(() => this._playLoop(config), nextDelay);
    this.timeouts.push(t);
  }

  _playTone(freq, duration, amplitude) {
    if (!this.ctx || !this.playing) return;

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.value = freq;

    // Soft attack and release
    const now = this.ctx.currentTime;
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(amplitude, now + 0.1);
    gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

    osc.connect(gain);
    gain.connect(this.gainNode);
    osc.start(now);
    osc.stop(now + duration + 0.1);

    this.oscillators.push(osc);
    osc.onended = () => {
      this.oscillators = this.oscillators.filter(o => o !== osc);
    };
  }

  _playPad(freq, duration, amplitude) {
    if (!this.ctx || !this.playing) return;

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'triangle';
    osc.frequency.value = freq;

    const now = this.ctx.currentTime;
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(amplitude, now + 0.5);
    gain.gain.linearRampToValueAtTime(amplitude * 0.7, now + duration * 0.7);
    gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

    osc.connect(gain);
    gain.connect(this.gainNode);
    osc.start(now);
    osc.stop(now + duration + 0.1);
  }

  setVolume(vol) {
    if (this.gainNode) {
      this.gainNode.gain.linearRampToValueAtTime(vol, this.ctx.currentTime + 0.1);
    }
  }

  stop() {
    this.playing = false;
    this.timeouts.forEach(t => clearTimeout(t));
    this.timeouts = [];
    this.oscillators.forEach(o => { try { o.stop(); } catch(e) {} });
    this.oscillators = [];
    if (this.ctx) {
      this.ctx.close().catch(() => {});
      this.ctx = null;
    }
  }

  static getMoods() {
    return Object.keys(MOODS);
  }

  static analyzeMood(text) {
    const lower = text.toLowerCase();
    const keywords = {
      adventurous: ['adventure', 'journey', 'explore', 'brave', 'quest', 'discover', 'travel'],
      exciting: ['race', 'fast', 'exciting', 'amazing', 'incredible', 'wow', 'action'],
      mysterious: ['mystery', 'secret', 'dark', 'hidden', 'strange', 'shadow', 'unknown'],
      joyful: ['happy', 'laugh', 'fun', 'play', 'dance', 'celebrate', 'joy', 'smile'],
      emotional: ['cry', 'love', 'heart', 'miss', 'remember', 'hug', 'tears', 'feel'],
      inspiring: ['dream', 'hope', 'believe', 'achieve', 'grow', 'learn', 'strong', 'courage'],
      peaceful: ['quiet', 'sleep', 'gentle', 'soft', 'nature', 'rest', 'calm', 'breeze'],
      calm: ['think', 'wonder', 'sit', 'look', 'walk', 'pond', 'garden'],
    };

    let bestMood = 'calm';
    let bestScore = 0;

    for (const [mood, words] of Object.entries(keywords)) {
      const score = words.reduce((acc, w) => acc + (lower.includes(w) ? 1 : 0), 0);
      if (score > bestScore) { bestScore = score; bestMood = mood; }
    }

    return bestMood;
  }
}
