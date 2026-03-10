import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { recordingsAPI, audioBooksAPI } from '@/lib/api';
import { BrutalCard, BrutalBadge } from '@/components/brutal';
import { Mic, Play, Pause, Trash2, Share2, TrendingUp, BarChart3, Clock, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const AudioMemoryTab = () => {
  const queryClient = useQueryClient();
  const [playing, setPlaying] = useState(null);
  const [audioEl, setAudioEl] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState('all');
  const [showProgress, setShowProgress] = useState(null);

  const { data, isLoading } = useQuery({
    queryKey: ['guardian-recordings'],
    queryFn: async () => (await recordingsAPI.getGuardianAll()).data,
  });

  const { data: progressData } = useQuery({
    queryKey: ['diction-progress', showProgress],
    queryFn: async () => (await recordingsAPI.getProgress(showProgress)).data,
    enabled: !!showProgress,
  });

  const deleteMut = useMutation({
    mutationFn: (id) => recordingsAPI.delete(id),
    onSuccess: () => { queryClient.invalidateQueries(['guardian-recordings']); toast.success('Recording deleted'); },
  });

  const contributeMut = useMutation({
    mutationFn: (data) => audioBooksAPI.contribute(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries(['guardian-recordings']);
      toast.success(res.data.status === 'approved' ? 'Shared to Audio Book Collection!' : 'Submitted for admin review!');
    },
  });

  const playRecording = (id) => {
    if (playing === id && audioEl) {
      audioEl.pause();
      setPlaying(null);
      return;
    }
    if (audioEl) audioEl.pause();
    const audio = new Audio(`${API_BASE}/api/recordings/${id}/stream`);
    audio.play();
    audio.onended = () => setPlaying(null);
    setAudioEl(audio);
    setPlaying(id);
  };

  if (isLoading) return (
    <div className="text-center py-16" data-testid="audio-memory-loading">
      <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto mb-3" />
      <p className="font-bold text-gray-500">Loading recordings...</p>
    </div>
  );

  const recordings = data?.recordings || [];
  const students = data?.students || [];
  const filtered = selectedStudent === 'all' ? recordings : recordings.filter(r => r.student_id === selectedStudent);

  return (
    <div className="space-y-6" data-testid="audio-memory-tab">
      <BrutalCard shadow="xl" className="bg-gradient-to-r from-violet-50 to-indigo-50">
        <div className="flex items-center gap-3">
          <Mic size={28} className="text-indigo-600" />
          <div>
            <h2 className="text-2xl font-black uppercase">Audio Memories</h2>
            <p className="text-gray-600 font-medium text-sm">Listen to your children reading their stories. A growing collection of precious moments.</p>
          </div>
        </div>
      </BrutalCard>

      {/* Student filter */}
      {students.length > 1 && (
        <div className="flex gap-2 flex-wrap">
          <button onClick={() => setSelectedStudent('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold ${selectedStudent === 'all' ? 'bg-indigo-600 text-white' : 'bg-gray-100'}`}>
            All Students
          </button>
          {students.map(s => (
            <button key={s.id} onClick={() => setSelectedStudent(s.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold ${selectedStudent === s.id ? 'bg-indigo-600 text-white' : 'bg-gray-100'}`}>
              {s.full_name}
            </button>
          ))}
        </div>
      )}

      {/* Recordings list */}
      {filtered.length === 0 ? (
        <BrutalCard shadow="lg" className="text-center py-12">
          <Mic size={48} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-xl font-black mb-2">No Recordings Yet</h3>
          <p className="text-gray-500 font-medium text-sm">When your child reads a story aloud using the Read Aloud feature, their recordings will appear here.</p>
        </BrutalCard>
      ) : (
        <div className="space-y-3">
          {filtered.map(rec => (
            <BrutalCard key={rec.id} shadow="md" className="hover:shadow-lg transition-shadow" data-testid={`recording-${rec.id}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <button onClick={() => playRecording(rec.id)}
                    className="w-10 h-10 flex-shrink-0 rounded-full bg-indigo-600 text-white flex items-center justify-center hover:bg-indigo-700 transition-all"
                    data-testid={`play-${rec.id}`}>
                    {playing === rec.id ? <Pause size={16} /> : <Play size={16} className="ml-0.5" />}
                  </button>
                  <div className="min-w-0">
                    <p className="font-bold text-sm truncate">{rec.narrative_title || 'Story'}</p>
                    <p className="text-xs text-gray-500">
                      {rec.student_name} (age {rec.student_age}) &middot; Ch. {rec.chapter_number} &middot; {new Date(rec.created_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {rec.diction_scores && (
                    <BrutalBadge variant={rec.diction_scores.overall >= 70 ? 'emerald' : rec.diction_scores.overall >= 40 ? 'amber' : 'red'} size="sm">
                      {rec.diction_scores.overall}%
                    </BrutalBadge>
                  )}
                  {rec.analysis_status === 'pending' && <BrutalBadge variant="amber" size="sm">Pending</BrutalBadge>}
                  {!rec.shared_to_audiobooks && rec.analysis_status === 'completed' && (
                    <button onClick={() => contributeMut.mutate({ recording_id: rec.id, display_name: rec.student_name })}
                      className="p-2 text-gray-400 hover:text-indigo-600 transition-all" title="Share to Audio Book Collection"
                      data-testid={`share-${rec.id}`}>
                      <Share2 size={16} />
                    </button>
                  )}
                  {rec.shared_to_audiobooks && <CheckCircle size={16} className="text-emerald-500" title="Shared" />}
                  <button onClick={() => setShowProgress(showProgress === rec.student_id ? null : rec.student_id)}
                    className="p-2 text-gray-400 hover:text-indigo-600 transition-all" title="View Progress"
                    data-testid={`progress-${rec.student_id}`}>
                    <TrendingUp size={16} />
                  </button>
                  <button onClick={() => { if (window.confirm('Delete this recording?')) deleteMut.mutate(rec.id); }}
                    className="p-2 text-gray-400 hover:text-red-500 transition-all" data-testid={`delete-${rec.id}`}>
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </BrutalCard>
          ))}
        </div>
      )}

      {/* Diction Progress Panel */}
      {showProgress && progressData && (
        <BrutalCard shadow="xl" className="bg-gradient-to-br from-emerald-50 to-teal-50" data-testid="diction-progress-panel">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 size={22} className="text-emerald-600" />
            <h3 className="text-lg font-black uppercase">Diction Progress</h3>
            <button onClick={() => setShowProgress(null)} className="ml-auto text-xs font-bold text-gray-500 hover:text-gray-800">Close</button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
            <div className="text-center p-3 bg-white rounded-lg">
              <p className="text-2xl font-black text-indigo-600">{progressData.total_sessions}</p>
              <p className="text-xs font-bold text-gray-500 uppercase">Sessions</p>
            </div>
            {Object.entries(progressData.improvement || {}).map(([key, val]) => (
              <div key={key} className="text-center p-3 bg-white rounded-lg">
                <p className={`text-2xl font-black ${val >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                  {val >= 0 ? '+' : ''}{val}%
                </p>
                <p className="text-xs font-bold text-gray-500 uppercase">{key}</p>
              </div>
            ))}
          </div>
          {progressData.progress?.length > 0 && (
            <div className="space-y-1">
              {progressData.progress.slice(-10).map((p, i) => (
                <div key={i} className="flex items-center justify-between text-xs p-2 bg-white rounded-lg">
                  <span className="font-medium truncate flex-1">{p.title}</span>
                  <span className="text-gray-500 mx-2">{new Date(p.date).toLocaleDateString()}</span>
                  <span className="font-black text-indigo-600">{p.scores?.overall}%</span>
                </div>
              ))}
            </div>
          )}
        </BrutalCard>
      )}
    </div>
  );
};

export default AudioMemoryTab;
