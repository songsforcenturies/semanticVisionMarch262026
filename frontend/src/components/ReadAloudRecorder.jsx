import React, { useState, useRef, useCallback, useEffect } from 'react';
import { recordingsAPI } from '@/lib/api';
import { Mic, MicOff, Video, Square, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

const ReadAloudRecorder = ({ studentId, narrativeId, chapterNumber, onRecordingComplete }) => {
  const [mode, setMode] = useState('audio');
  const [recording, setRecording] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [mediaBlob, setMediaBlob] = useState(null);
  const [result, setResult] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);

  useEffect(() => () => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop());
  }, []);

  const startRecording = useCallback(async () => {
    try {
      chunksRef.current = [];
      setMediaBlob(null);
      setResult(null);
      setElapsed(0);

      const constraints = mode === 'video'
        ? { audio: true, video: { facingMode: 'user', width: 640, height: 480 } }
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
        setMediaBlob(blob);
        stream.getTracks().forEach(t => t.stop());
      };

      recorder.start(1000);
      setRecording(true);
      timerRef.current = setInterval(() => setElapsed(p => p + 1), 1000);
    } catch (err) {
      toast.error('Could not access microphone/camera. Please grant permission.');
    }
  }, [mode]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    }
  }, [recording]);

  const uploadAndAnalyze = useCallback(async () => {
    if (!mediaBlob) return;
    setAnalyzing(true);
    try {
      const ext = mode === 'video' ? 'webm' : 'webm';
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

  const fmt = (s) => `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;

  const ScoreBar = ({ label, value, color }) => (
    <div className="mb-2">
      <div className="flex justify-between text-xs font-bold mb-1">
        <span>{label}</span><span>{value}%</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  );

  return (
    <div className="border-2 border-gray-200 rounded-xl p-4 bg-white" data-testid="read-aloud-recorder">
      {/* Mode selector */}
      <div className="flex items-center gap-2 mb-3">
        <button onClick={() => !recording && setMode('audio')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${mode === 'audio' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600'}`}
          data-testid="mode-audio-btn">
          <Mic size={14} /> Audio Only
        </button>
        <button onClick={() => !recording && setMode('video')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${mode === 'video' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600'}`}
          data-testid="mode-video-btn">
          <Video size={14} /> Audio + Video
        </button>
      </div>

      {/* Recording controls */}
      <div className="flex items-center gap-3">
        {!recording && !mediaBlob && (
          <button onClick={startRecording}
            className="flex items-center gap-2 px-5 py-2.5 bg-red-500 text-white font-bold rounded-xl hover:bg-red-600 transition-all"
            data-testid="start-recording-btn">
            <Mic size={18} /> Start Reading Aloud
          </button>
        )}
        {recording && (
          <>
            <button onClick={stopRecording}
              className="flex items-center gap-2 px-5 py-2.5 bg-gray-800 text-white font-bold rounded-xl hover:bg-black transition-all animate-pulse"
              data-testid="stop-recording-btn">
              <Square size={18} /> Stop Recording
            </button>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <span className="text-sm font-mono font-bold">{fmt(elapsed)}</span>
            </div>
          </>
        )}
        {mediaBlob && !result && (
          <div className="flex items-center gap-3">
            <button onClick={uploadAndAnalyze} disabled={analyzing}
              className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-all disabled:opacity-50"
              data-testid="analyze-btn">
              {analyzing ? <><Loader2 size={18} className="animate-spin" /> Analyzing...</> : <><CheckCircle size={18} /> Analyze Diction</>}
            </button>
            <button onClick={() => { setMediaBlob(null); setElapsed(0); }}
              className="px-3 py-2.5 text-sm font-bold text-gray-500 hover:text-gray-800 transition-all"
              data-testid="re-record-btn">
              Re-record
            </button>
          </div>
        )}
      </div>

      {/* Preview */}
      {mediaBlob && !result && (
        <div className="mt-3">
          {mode === 'video' ? (
            <video src={URL.createObjectURL(mediaBlob)} controls className="rounded-lg w-full max-h-48" data-testid="video-preview" />
          ) : (
            <audio src={URL.createObjectURL(mediaBlob)} controls className="w-full" data-testid="audio-preview" />
          )}
        </div>
      )}

      {/* Results */}
      {result && result.diction_scores && (
        <div className="mt-4 p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl" data-testid="diction-results">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle size={20} className="text-emerald-600" />
            <h4 className="text-sm font-black uppercase">Diction Analysis</h4>
          </div>
          <div className="text-center mb-4">
            <div className="text-4xl font-black text-indigo-600" data-testid="overall-score">{result.diction_scores.overall}%</div>
            <div className="text-xs font-bold text-gray-500 uppercase">Overall Score</div>
          </div>
          <ScoreBar label="Pronunciation" value={result.diction_scores.pronunciation} color="#6366f1" />
          <ScoreBar label="Fluency" value={result.diction_scores.fluency} color="#8b5cf6" />
          <ScoreBar label="Completeness" value={result.diction_scores.completeness} color="#06b6d4" />
          <ScoreBar label="Prosody" value={result.diction_scores.prosody} color="#f59e0b" />
          <div className="mt-3 text-xs text-gray-500">
            {result.diction_scores.words_matched}/{result.diction_scores.words_in_source} words matched
          </div>
        </div>
      )}
    </div>
  );
};

export default ReadAloudRecorder;
