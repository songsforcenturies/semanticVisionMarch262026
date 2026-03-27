import React, { useState, useRef, useCallback, useEffect } from 'react';
import { recordingsAPI } from '@/lib/api';
import { Mic, MicOff, Video, Square, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

const C = {
  card: '#1A2236', cream: '#F8F5EE', muted: '#94A3B8',
  gold: '#D4A853', teal: '#38BDF8',
};

const ReadAloudRecorder = ({ studentId, narrativeId, chapterNumber, onRecordingComplete, requiredMode = null }) => {
  const [mode, setMode] = useState(requiredMode === 'video_required' || requiredMode === 'both_required' ? 'video' : 'audio');
  const [recording, setRecording] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [mediaBlob, setMediaBlob] = useState(null);
  const [mediaBlobUrl, setMediaBlobUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [chunksSaved, setChunksSaved] = useState(0);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const autoSaveRef = useRef(null);

  // Auto-save chunks every 15 seconds to prevent data loss
  const saveChunkLocally = useCallback(() => {
    if (chunksRef.current.length === 0) return;
    try {
      const blob = new Blob([...chunksRef.current], { type: mode === 'video' ? 'video/webm' : 'audio/webm' });
      const key = `sv_recording_${studentId}_${narrativeId}_${chapterNumber}`;
      // Store as array buffer in sessionStorage for recovery
      const reader = new FileReader();
      reader.onload = () => {
        try {
          sessionStorage.setItem(key, reader.result);
          setChunksSaved(prev => prev + 1);
        } catch (e) {
          // sessionStorage might be full, that's ok
          console.warn('Could not auto-save chunk:', e);
        }
      };
      reader.readAsDataURL(blob);
    } catch (e) {
      console.warn('Chunk save failed:', e);
    }
  }, [mode, studentId, narrativeId, chapterNumber]);

  useEffect(() => () => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (autoSaveRef.current) clearInterval(autoSaveRef.current);
    if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop());
    if (mediaBlobUrl) URL.revokeObjectURL(mediaBlobUrl);
  }, []);

  const startRecording = useCallback(async () => {
    try {
      chunksRef.current = [];
      if (mediaBlobUrl) URL.revokeObjectURL(mediaBlobUrl);
      setMediaBlob(null);
      setMediaBlobUrl(null);
      setResult(null);
      setElapsed(0);

      const constraints = mode === 'video'
        ? { audio: true, video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } } }
        : { audio: true };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      const mimeType = mode === 'video'
        ? (MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus') ? 'video/webm;codecs=vp9,opus' : 'video/webm')
        : (MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm');

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        const url = URL.createObjectURL(blob);
        setMediaBlob(blob);
        setMediaBlobUrl(url);
        stream.getTracks().forEach(t => t.stop());
      };

      recorder.start(1000);
      setRecording(true);
      setChunksSaved(0);
      timerRef.current = setInterval(() => setElapsed(p => p + 1), 1000);
      // Auto-save every 15 seconds
      autoSaveRef.current = setInterval(() => saveChunkLocally(), 15000);
    } catch (err) {
      toast.error('Could not access microphone/camera. Please grant permission.');
    }
  }, [mode, mediaBlobUrl, saveChunkLocally]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
      if (autoSaveRef.current) { clearInterval(autoSaveRef.current); autoSaveRef.current = null; }
      // Final save
      saveChunkLocally();
    }
  }, [recording, saveChunkLocally]);

  const uploadAndAnalyze = useCallback(async () => {
    if (!mediaBlob) return;
    setAnalyzing(true);
    try {
      const ext = 'webm';
      const file = new File([mediaBlob], `recording.${ext}`, { type: mediaBlob.type });
      const formData = new FormData();
      formData.append('file', file);
      formData.append('student_id', studentId);
      formData.append('narrative_id', narrativeId);
      formData.append('chapter_number', String(chapterNumber));
      formData.append('recording_type', mode);

      const uploadRes = await recordingsAPI.upload(formData);
      const recordingId = uploadRes.data.id;
      toast.success('Recording uploaded! Analyzing diction...');

      const analysisRes = await recordingsAPI.analyze(recordingId);
      setResult(analysisRes.data);
      toast.success('Diction analysis complete!');
      if (onRecordingComplete) onRecordingComplete(analysisRes.data);
    } catch (err) {
      toast.error('Upload or analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  }, [mediaBlob, studentId, narrativeId, chapterNumber, mode, onRecordingComplete]);

  const handleReRecord = () => {
    if (mediaBlobUrl) URL.revokeObjectURL(mediaBlobUrl);
    setMediaBlob(null);
    setMediaBlobUrl(null);
    setElapsed(0);
  };

  const fmt = (s) => `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;

  const ScoreBar = ({ label, value, color }) => (
    <div className="mb-2">
      <div className="flex justify-between text-xs font-bold mb-1" style={{ color: C.cream }}>
        <span>{label}</span><span>{value}%</span>
      </div>
      <div className="h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.1)' }}>
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  );

  return (
    <div className="rounded-xl p-3 sm:p-4" data-testid="read-aloud-recorder"
      style={{ background: C.card, border: '1px solid rgba(255,255,255,0.1)' }}>
      {/* Mode selector */}
      {requiredMode !== 'video_required' && requiredMode !== 'audio_required' && (
        <div className="flex items-center gap-2 mb-3">
          <button onClick={() => !recording && setMode('audio')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all"
            style={{
              background: mode === 'audio' ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.04)',
              color: mode === 'audio' ? '#818CF8' : C.muted,
              border: mode === 'audio' ? '1px solid rgba(99,102,241,0.3)' : '1px solid rgba(255,255,255,0.08)',
            }}
            data-testid="mode-audio-btn">
            <Mic size={14} /> Audio
          </button>
          <button onClick={() => !recording && setMode('video')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all"
            style={{
              background: mode === 'video' ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.04)',
              color: mode === 'video' ? '#818CF8' : C.muted,
              border: mode === 'video' ? '1px solid rgba(99,102,241,0.3)' : '1px solid rgba(255,255,255,0.08)',
            }}
            data-testid="mode-video-btn">
            <Video size={14} /> Video
          </button>
        </div>
      )}
      {requiredMode === 'video_required' && (
        <div className="flex items-center gap-2 mb-3 px-3 py-2 rounded-lg" style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)' }}>
          <Video size={16} style={{ color: '#818CF8' }} />
          <span className="text-xs font-bold" style={{ color: '#818CF8' }}>Audio & Video recording required by parent</span>
        </div>
      )}
      {requiredMode === 'audio_required' && (
        <div className="flex items-center gap-2 mb-3 px-3 py-2 rounded-lg" style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)' }}>
          <Mic size={16} style={{ color: '#818CF8' }} />
          <span className="text-xs font-bold" style={{ color: '#818CF8' }}>Audio recording required by parent</span>
        </div>
      )}

      {/* Recording controls */}
      <div className="flex items-center gap-3 flex-wrap">
        {!recording && !mediaBlob && (
          <button onClick={startRecording}
            className="flex items-center gap-2 px-4 py-2.5 font-bold rounded-xl text-sm transition-all"
            style={{ background: 'rgba(239,68,68,0.15)', color: '#EF4444', border: '1px solid rgba(239,68,68,0.3)' }}
            data-testid="start-recording-btn">
            <Mic size={16} /> Start Reading Aloud
          </button>
        )}
        {recording && (
          <>
            <button onClick={stopRecording}
              className="flex items-center gap-2 px-4 py-2.5 font-bold rounded-xl text-sm transition-all animate-pulse"
              style={{ background: 'rgba(255,255,255,0.1)', color: C.cream, border: '1px solid rgba(255,255,255,0.2)' }}
              data-testid="stop-recording-btn">
              <Square size={16} /> Stop
            </button>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <span className="text-sm font-mono font-bold" style={{ color: C.cream }}>{fmt(elapsed)}</span>
              {chunksSaved > 0 && (
                <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: 'rgba(52,211,153,0.15)', color: '#34D399' }}>
                  Auto-saved
                </span>
              )}
            </div>
          </>
        )}
        {mediaBlob && !result && (
          <div className="flex items-center gap-2 flex-wrap">
            <button onClick={uploadAndAnalyze} disabled={analyzing}
              className="flex items-center gap-2 px-4 py-2.5 font-bold rounded-xl text-sm transition-all disabled:opacity-50"
              style={{ background: 'rgba(52,211,153,0.15)', color: '#34D399', border: '1px solid rgba(52,211,153,0.3)' }}
              data-testid="analyze-btn">
              {analyzing ? <><Loader2 size={16} className="animate-spin" /> Analyzing...</> : <><CheckCircle size={16} /> Analyze Diction</>}
            </button>
            <button onClick={handleReRecord}
              className="px-3 py-2.5 text-xs font-bold transition-all"
              style={{ color: C.muted }}
              data-testid="re-record-btn">
              Re-record
            </button>
          </div>
        )}
      </div>

      {/* Preview */}
      {mediaBlobUrl && !result && (
        <div className="mt-3">
          {mode === 'video' ? (
            <video src={mediaBlobUrl} controls playsInline preload="metadata"
              className="rounded-lg w-full max-h-48 bg-black" data-testid="video-preview" />
          ) : (
            <audio src={mediaBlobUrl} controls preload="metadata" className="w-full" data-testid="audio-preview" />
          )}
        </div>
      )}

      {/* Results */}
      {result && result.diction_scores && (
        <div className="mt-4 p-4 rounded-xl" data-testid="diction-results"
          style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)' }}>
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle size={18} style={{ color: '#34D399' }} />
            <h4 className="text-xs font-black uppercase" style={{ color: C.cream }}>Diction Analysis</h4>
          </div>
          <div className="text-center mb-4">
            <div className="text-3xl sm:text-4xl font-black" style={{ color: '#818CF8' }} data-testid="overall-score">{result.diction_scores.overall}%</div>
            <div className="text-xs font-bold uppercase" style={{ color: C.muted }}>Overall Score</div>
          </div>
          <ScoreBar label="Pronunciation" value={result.diction_scores.pronunciation} color="#6366f1" />
          <ScoreBar label="Fluency" value={result.diction_scores.fluency} color="#8b5cf6" />
          <ScoreBar label="Completeness" value={result.diction_scores.completeness} color="#06b6d4" />
          <ScoreBar label="Prosody" value={result.diction_scores.prosody} color="#f59e0b" />
          <div className="mt-3 text-xs" style={{ color: C.muted }}>
            {result.diction_scores.words_matched}/{result.diction_scores.words_in_source} words matched
          </div>
        </div>
      )}
    </div>
  );
};

export default ReadAloudRecorder;
