import React, { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { parentalControlsAPI } from '@/lib/api';
import api from '@/lib/api';
import { BrutalCard, BrutalButton } from '@/components/brutal';
import { Shield, Mic, Video, Clock, ToggleLeft, ToggleRight, ChevronDown, ChevronUp, Save, Headphones, BookOpen, Music } from 'lucide-react';
import { toast } from 'sonner';

const LEARNING_SUPPORT_OPTIONS = [
  { value: 'dyslexia', label: 'Dyslexia' },
  { value: 'visual_processing', label: 'Visual Processing' },
  { value: 'adhd', label: 'ADHD' },
  { value: 'esl_ell', label: 'ESL/ELL' },
  { value: 'other', label: 'Other' },
];

const ParentalControlsPanel = ({ studentId, studentName }) => {
  const queryClient = useQueryClient();
  const [expanded, setExpanded] = useState(false);
  const [controls, setControls] = useState(null);
  const [assessmentMode, setAssessmentMode] = useState('written');
  const [accessibilityNeeds, setAccessibilityNeeds] = useState([]);
  const [forceMedia, setForceMedia] = useState(false);
  const [mediaIntegrationCount, setMediaIntegrationCount] = useState(2);

  const { data: savedControls } = useQuery({
    queryKey: ['parental-controls', studentId],
    queryFn: async () => (await parentalControlsAPI.get(studentId)).data,
    enabled: !!studentId,
  });

  // Fetch student data for assessment_mode and accessibility_needs
  const { data: studentData } = useQuery({
    queryKey: ['student', studentId],
    queryFn: async () => (await api.get(`/students/${studentId}`)).data,
    enabled: !!studentId,
  });

  useEffect(() => {
    if (savedControls) setControls(savedControls);
  }, [savedControls]);

  useEffect(() => {
    if (studentData) {
      setAssessmentMode(studentData.assessment_mode || 'written');
      setAccessibilityNeeds(studentData.accessibility_needs || []);
      setForceMedia(studentData.force_media_in_stories || false);
      setMediaIntegrationCount(studentData.media_integration_count ?? 2);
    }
  }, [studentData]);

  const saveMutation = useMutation({
    mutationFn: (data) => parentalControlsAPI.update(studentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['parental-controls', studentId]);
      toast.success(`Reading rules updated for ${studentName}`);
    },
    onError: () => toast.error('Failed to save rules'),
  });

  const saveStudentMutation = useMutation({
    mutationFn: (data) => api.patch(`/students/${studentId}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['student', studentId]);
    },
    onError: () => toast.error('Failed to save assessment settings'),
  });

  const handleSave = () => {
    if (controls) saveMutation.mutate(controls);
    // Also save assessment mode, accessibility needs, and media settings to the student record
    saveStudentMutation.mutate({
      assessment_mode: assessmentMode,
      accessibility_needs: accessibilityNeeds,
      force_media_in_stories: forceMedia,
      media_integration_count: mediaIntegrationCount,
    });
  };

  const toggleAccessibilityNeed = (need) => {
    setAccessibilityNeeds((prev) =>
      prev.includes(need) ? prev.filter((n) => n !== need) : [...prev, need]
    );
  };

  if (!controls) return null;

  const Toggle = ({ label, desc, value, onChange, icon: Icon }) => (
    <div className="flex items-start justify-between gap-3 py-3" style={{ borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
      <div className="flex items-start gap-2.5 flex-1 min-w-0">
        <Icon size={16} className="mt-0.5 flex-shrink-0" style={{ color: '#6366f1' }} />
        <div>
          <p className="text-sm font-bold" style={{ color: '#2d2a26' }}>{label}</p>
          <p className="text-xs mt-0.5" style={{ color: '#8c8780' }}>{desc}</p>
        </div>
      </div>
      <button onClick={() => onChange(!value)} className="flex-shrink-0 mt-0.5"
        data-testid={`toggle-${label.toLowerCase().replace(/\s+/g, '-')}`}>
        {value ? (
          <ToggleRight size={28} style={{ color: '#6366f1' }} />
        ) : (
          <ToggleLeft size={28} style={{ color: '#b0aba4' }} />
        )}
      </button>
    </div>
  );

  return (
    <div className="mt-3" data-testid={`parental-controls-${studentId}`}>
      <button onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm font-bold transition-all"
        style={{ background: '#eae6f2', color: '#4338ca', border: '1px solid rgba(99,102,241,0.2)' }}
        data-testid={`expand-controls-${studentId}`}>
        <div className="flex items-center gap-2">
          <Shield size={14} />
          Reading Rules
        </div>
        {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {expanded && (
        <div className="mt-2 p-4 rounded-lg" style={{ background: '#f5f3ee', border: '1px solid rgba(0,0,0,0.08)' }}>
          {/* Recording Mode */}
          <div className="mb-3">
            <p className="text-xs font-bold uppercase mb-2" style={{ color: '#6366f1' }}>Recording Requirement</p>
            <div className="grid grid-cols-2 gap-1.5">
              {[
                { value: 'none', label: 'None', desc: 'No recording required' },
                { value: 'audio_video', label: 'Audio & Video', desc: 'Student reads aloud on camera with microphone' },
                { value: 'audio_only', label: 'Audio Only', desc: 'Student reads aloud with microphone only' },
              ].map(opt => (
                <button key={opt.value}
                  onClick={() => setControls({ ...controls, recording_mode: opt.value })}
                  className="px-3 py-2 rounded-md text-xs font-bold transition-all text-left"
                  style={{
                    background: controls.recording_mode === opt.value ? '#6366f1' : '#eae6f2',
                    color: controls.recording_mode === opt.value ? '#fff' : '#4338ca',
                    border: `1px solid ${controls.recording_mode === opt.value ? '#6366f1' : 'rgba(99,102,241,0.2)'}`,
                  }}
                  data-testid={`recording-mode-${opt.value}`}>
                  {opt.label}
                  <span className="block text-[10px] font-normal mt-0.5" style={{
                    color: controls.recording_mode === opt.value ? 'rgba(255,255,255,0.7)' : '#8c8780',
                  }}>{opt.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Chapter Threshold */}
          <div className="py-3" style={{ borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
            <div className="flex items-start gap-2.5">
              <Clock size={16} className="mt-0.5 flex-shrink-0" style={{ color: '#6366f1' }} />
              <div className="flex-1">
                <p className="text-sm font-bold" style={{ color: '#2d2a26' }}>Chapter Threshold</p>
                <p className="text-xs mt-0.5" style={{ color: '#8c8780' }}>
                  Require recording after this many chapters (0 = every chapter)
                </p>
                <input type="number" min="0" max="5" value={controls.chapter_threshold}
                  onChange={(e) => setControls({ ...controls, chapter_threshold: parseInt(e.target.value) || 0 })}
                  className="mt-2 w-20 px-3 py-1.5 rounded-md text-sm font-bold text-center"
                  style={{ background: '#fff', border: '1px solid rgba(0,0,0,0.15)', color: '#2d2a26' }}
                  data-testid="chapter-threshold-input" />
              </div>
            </div>
          </div>

          <Toggle
            label="Auto-Start Recording"
            desc="Recording starts automatically when chapter opens"
            value={controls.auto_start_recording}
            onChange={(v) => setControls({ ...controls, auto_start_recording: v })}
            icon={Mic}
          />

          <Toggle
            label="Require Confirmation"
            desc="Student must confirm before they can proceed"
            value={controls.require_confirmation}
            onChange={(v) => setControls({ ...controls, require_confirmation: v })}
            icon={Shield}
          />

          <Toggle
            label="Allow Skip"
            desc="Student can skip recording and continue reading"
            value={controls.can_skip_recording}
            onChange={(v) => setControls({ ...controls, can_skip_recording: v })}
            icon={Video}
          />

          {/* Assessment Mode */}
          <div className="mt-4 mb-3">
            <p className="text-xs font-bold uppercase mb-2" style={{ color: '#6366f1' }}>
              <Headphones size={14} className="inline mr-1" style={{ verticalAlign: 'middle' }} />
              Assessment Mode
            </p>
            <div className="grid grid-cols-3 gap-1.5">
              {[
                { value: 'written', label: 'Written (default)', desc: 'Type answers' },
                { value: 'oral', label: 'Oral (speak answers)', desc: 'Speak answers aloud' },
                { value: 'both', label: 'Both (written + oral)', desc: 'Written and spoken' },
              ].map(opt => (
                <button key={opt.value}
                  onClick={() => setAssessmentMode(opt.value)}
                  className="px-3 py-2 rounded-md text-xs font-bold transition-all text-left"
                  style={{
                    background: assessmentMode === opt.value ? '#6366f1' : '#eae6f2',
                    color: assessmentMode === opt.value ? '#fff' : '#4338ca',
                    border: `1px solid ${assessmentMode === opt.value ? '#6366f1' : 'rgba(99,102,241,0.2)'}`,
                  }}
                  data-testid={`assessment-mode-${opt.value}`}>
                  {opt.label}
                  <span className="block text-[10px] font-normal mt-0.5" style={{
                    color: assessmentMode === opt.value ? 'rgba(255,255,255,0.7)' : '#8c8780',
                  }}>{opt.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Learning Support */}
          <div className="mb-3">
            <p className="text-xs font-bold uppercase mb-2" style={{ color: '#6366f1' }}>
              <BookOpen size={14} className="inline mr-1" style={{ verticalAlign: 'middle' }} />
              Learning Support
            </p>
            <div className="flex flex-wrap gap-2">
              {LEARNING_SUPPORT_OPTIONS.map(opt => (
                <label key={opt.value}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold cursor-pointer transition-all"
                  style={{
                    background: accessibilityNeeds.includes(opt.value) ? '#6366f1' : '#eae6f2',
                    color: accessibilityNeeds.includes(opt.value) ? '#fff' : '#4338ca',
                    border: `1px solid ${accessibilityNeeds.includes(opt.value) ? '#6366f1' : 'rgba(99,102,241,0.2)'}`,
                  }}
                  data-testid={`accessibility-${opt.value}`}>
                  <input
                    type="checkbox"
                    checked={accessibilityNeeds.includes(opt.value)}
                    onChange={() => toggleAccessibilityNeed(opt.value)}
                    className="sr-only"
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>

          {/* Learning Through Songs & Media */}
          <div className="mt-4 mb-3">
            <p className="text-xs font-bold uppercase mb-2" style={{ color: '#6366f1' }}>
              <Music size={14} className="inline mr-1" style={{ verticalAlign: 'middle' }} />
              Learning Through Songs & Media
            </p>
            <div className="flex items-start justify-between gap-3 py-3" style={{ borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
              <div className="flex items-start gap-2.5 flex-1 min-w-0">
                <Music size={16} className="mt-0.5 flex-shrink-0" style={{ color: '#6366f1' }} />
                <div>
                  <p className="text-sm font-bold" style={{ color: '#2d2a26' }}>Force songs/media in every story</p>
                  <p className="text-xs mt-0.5" style={{ color: '#8c8780' }}>When enabled, songs and media will always be included in generated stories</p>
                </div>
              </div>
              <button onClick={() => setForceMedia(!forceMedia)} className="flex-shrink-0 mt-0.5"
                data-testid="toggle-force-media">
                {forceMedia ? (
                  <ToggleRight size={28} style={{ color: '#6366f1' }} />
                ) : (
                  <ToggleLeft size={28} style={{ color: '#b0aba4' }} />
                )}
              </button>
            </div>
            <div className="py-3" style={{ borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
              <div className="flex items-start gap-2.5">
                <Music size={16} className="mt-0.5 flex-shrink-0" style={{ color: '#6366f1' }} />
                <div className="flex-1">
                  <p className="text-sm font-bold" style={{ color: '#2d2a26' }}>Number of song/media integrations per story</p>
                  <p className="text-xs mt-0.5" style={{ color: '#8c8780' }}>
                    How many songs or media references to include (1-5)
                  </p>
                  <input type="number" min="1" max="5" value={mediaIntegrationCount}
                    onChange={(e) => setMediaIntegrationCount(Math.max(1, Math.min(5, parseInt(e.target.value) || 1)))}
                    className="mt-2 w-20 px-3 py-1.5 rounded-md text-sm font-bold text-center"
                    style={{ background: '#fff', border: '1px solid rgba(0,0,0,0.15)', color: '#2d2a26' }}
                    data-testid="media-integration-count-input" />
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4">
            <BrutalButton variant="indigo" size="sm" fullWidth onClick={handleSave}
              disabled={saveMutation.isPending || saveStudentMutation.isPending}
              className="flex items-center justify-center gap-2"
              data-testid={`save-controls-${studentId}`}>
              <Save size={14} />
              {(saveMutation.isPending || saveStudentMutation.isPending) ? 'Saving...' : 'Save Reading Rules'}
            </BrutalButton>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParentalControlsPanel;
