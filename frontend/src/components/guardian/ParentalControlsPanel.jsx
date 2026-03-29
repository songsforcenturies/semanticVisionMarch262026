import React, { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { parentalControlsAPI } from '@/lib/api';
import api from '@/lib/api';
import { BrutalCard, BrutalButton } from '@/components/brutal';
import { Shield, Mic, Video, Clock, ToggleLeft, ToggleRight, ChevronDown, ChevronUp, Save, Headphones, BookOpen, Music, Image, Volume2, Sparkles, Globe } from 'lucide-react';
import { toast } from 'sonner';

const STORY_LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'zh', label: 'Chinese' },
  { value: 'hi', label: 'Hindi' },
  { value: 'ar', label: 'Arabic' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'ru', label: 'Russian' },
  { value: 'ja', label: 'Japanese' },
  { value: 'de', label: 'German' },
  { value: 'ko', label: 'Korean' },
];

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
  const [illustrationsEnabled, setIllustrationsEnabled] = useState(false);
  const [illustrationStyle, setIllustrationStyle] = useState('storybook');
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [storyLanguage, setStoryLanguage] = useState('en');
  const [lifeCharacters, setLifeCharacters] = useState([]);
  const [lifeLessons, setLifeLessons] = useState([]);

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
      setIllustrationsEnabled(studentData.illustrations_enabled || false);
      setIllustrationStyle(studentData.illustration_style || 'storybook');
      setTtsEnabled(studentData.tts_enabled !== false);
      setStoryLanguage(studentData.language || 'en');
      setLifeCharacters(studentData.life_characters || []);
      setLifeLessons(studentData.life_lessons || []);
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
      illustrations_enabled: illustrationsEnabled,
      illustration_style: illustrationStyle,
      tts_enabled: ttsEnabled,
      language: storyLanguage,
      life_characters: lifeCharacters,
      life_lessons: lifeLessons,
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

          {/* Story Language */}
          <div className="mt-4 mb-3">
            <p className="text-xs font-bold uppercase mb-2" style={{ color: '#6366f1' }}>
              <Globe size={14} className="inline mr-1" style={{ verticalAlign: 'middle' }} />
              Story Language
            </p>
            <p className="text-xs mb-2" style={{ color: '#8c8780' }}>
              Choose the language for generated stories
            </p>
            <select
              value={storyLanguage}
              onChange={(e) => setStoryLanguage(e.target.value)}
              className="w-full px-3 py-2 rounded-md text-sm font-bold"
              style={{ background: '#fff', border: '1px solid rgba(0,0,0,0.15)', color: '#2d2a26' }}
              data-testid="story-language-select"
            >
              {STORY_LANGUAGE_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Story Enhancements */}
          <div className="mt-4 mb-3">
            <p className="text-xs font-bold uppercase mb-2" style={{ color: '#6366f1' }}>
              <Sparkles size={14} className="inline mr-1" style={{ verticalAlign: 'middle' }} />
              Story Enhancements
            </p>

            {/* Enable AI Illustrations */}
            <div className="flex items-start justify-between gap-3 py-3" style={{ borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
              <div className="flex items-start gap-2.5 flex-1 min-w-0">
                <Image size={16} className="mt-0.5 flex-shrink-0" style={{ color: '#6366f1' }} />
                <div>
                  <p className="text-sm font-bold" style={{ color: '#2d2a26' }}>Enable AI Illustrations</p>
                  <p className="text-xs mt-0.5" style={{ color: '#8c8780' }}>Generate visual scene descriptions for each chapter</p>
                </div>
              </div>
              <button onClick={() => setIllustrationsEnabled(!illustrationsEnabled)} className="flex-shrink-0 mt-0.5"
                data-testid="toggle-illustrations">
                {illustrationsEnabled ? (
                  <ToggleRight size={28} style={{ color: '#6366f1' }} />
                ) : (
                  <ToggleLeft size={28} style={{ color: '#b0aba4' }} />
                )}
              </button>
            </div>

            {/* Illustration Style */}
            {illustrationsEnabled && (
              <div className="py-3" style={{ borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
                <div className="flex items-start gap-2.5">
                  <Image size={16} className="mt-0.5 flex-shrink-0" style={{ color: '#6366f1' }} />
                  <div className="flex-1">
                    <p className="text-sm font-bold" style={{ color: '#2d2a26' }}>Illustration Style</p>
                    <p className="text-xs mt-0.5" style={{ color: '#8c8780' }}>Choose the visual style for story illustrations</p>
                    <div className="grid grid-cols-3 gap-1.5 mt-2">
                      {[
                        { value: 'watercolor', label: 'Watercolor' },
                        { value: 'cartoon', label: 'Cartoon' },
                        { value: 'realistic', label: 'Realistic' },
                        { value: 'storybook', label: 'Storybook' },
                        { value: 'anime', label: 'Anime' },
                      ].map(opt => (
                        <button key={opt.value}
                          onClick={() => setIllustrationStyle(opt.value)}
                          className="px-3 py-2 rounded-md text-xs font-bold transition-all text-center"
                          style={{
                            background: illustrationStyle === opt.value ? '#6366f1' : '#eae6f2',
                            color: illustrationStyle === opt.value ? '#fff' : '#4338ca',
                            border: `1px solid ${illustrationStyle === opt.value ? '#6366f1' : 'rgba(99,102,241,0.2)'}`,
                          }}
                          data-testid={`illustration-style-${opt.value}`}>
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Enable Read-Aloud (TTS) */}
            <div className="flex items-start justify-between gap-3 py-3" style={{ borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
              <div className="flex items-start gap-2.5 flex-1 min-w-0">
                <Volume2 size={16} className="mt-0.5 flex-shrink-0" style={{ color: '#6366f1' }} />
                <div>
                  <p className="text-sm font-bold" style={{ color: '#2d2a26' }}>Enable Read-Aloud (Text-to-Speech)</p>
                  <p className="text-xs mt-0.5" style={{ color: '#8c8780' }}>Show the TTS audio player by default in the story reader</p>
                </div>
              </div>
              <button onClick={() => setTtsEnabled(!ttsEnabled)} className="flex-shrink-0 mt-0.5"
                data-testid="toggle-tts">
                {ttsEnabled ? (
                  <ToggleRight size={28} style={{ color: '#6366f1' }} />
                ) : (
                  <ToggleLeft size={28} style={{ color: '#b0aba4' }} />
                )}
              </button>
            </div>
          </div>

          {/* ===== TDJAKES OPTION: Life Characters & Lessons ===== */}
          <div className="mt-6 pt-4" style={{ borderTop: '3px solid #e8e5de' }}>
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={18} style={{ color: '#D4A853' }} />
              <h4 className="font-black text-sm uppercase" style={{ color: '#2d2a26' }}>Life Characters & Lessons (TDJakes Option)</h4>
            </div>
            <p className="text-xs mb-4" style={{ color: '#8c8780' }}>
              Add real people in your child's life and life lessons you want woven into stories. The AI will deliver your wisdom through trusted story characters — so your child absorbs the lesson naturally.
            </p>

            {/* Characters */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-bold uppercase" style={{ color: '#6366f1' }}>People in {studentName}'s Life</p>
                <button onClick={() => setLifeCharacters([...lifeCharacters, { id: Date.now().toString(), name: '', relationship: 'classmate', relationship_type: 'neutral', description: '', influence_level: 'medium' }])}
                  className="text-[10px] font-bold px-2 py-1 rounded bg-indigo-100 text-indigo-700 hover:bg-indigo-200">
                  + Add Person
                </button>
              </div>
              {lifeCharacters.map((char, idx) => (
                <div key={char.id || idx} className="p-3 rounded-lg mb-2" style={{ background: '#f5f3ee', border: '1px solid #e8e5de' }}>
                  <div className="flex gap-2 mb-2">
                    <input value={char.name} onChange={(e) => { const c = [...lifeCharacters]; c[idx].name = e.target.value; setLifeCharacters(c); }}
                      placeholder="Name" className="flex-1 px-2 py-1.5 rounded text-sm border border-gray-300 font-bold" />
                    <select value={char.relationship} onChange={(e) => { const c = [...lifeCharacters]; c[idx].relationship = e.target.value; setLifeCharacters(c); }}
                      className="px-2 py-1.5 rounded text-xs border border-gray-300">
                      <option value="brother_sister">Brother/Sister</option>
                      <option value="best_friend">Best Friend</option>
                      <option value="classmate">Classmate</option>
                      <option value="bully">Bully</option>
                      <option value="teacher">Teacher</option>
                      <option value="coach">Coach</option>
                      <option value="neighbor">Neighbor</option>
                      <option value="cousin">Cousin</option>
                      <option value="online_friend">Online Friend</option>
                      <option value="other">Other</option>
                    </select>
                    <button onClick={() => setLifeCharacters(lifeCharacters.filter((_, i) => i !== idx))}
                      className="text-red-500 text-xs font-bold hover:text-red-700">✕</button>
                  </div>
                  <div className="flex gap-2 mb-2">
                    {['positive', 'neutral', 'negative'].map(t => (
                      <button key={t} onClick={() => { const c = [...lifeCharacters]; c[idx].relationship_type = t; setLifeCharacters(c); }}
                        className={`px-2 py-1 rounded text-[10px] font-bold ${char.relationship_type === t ? (t === 'positive' ? 'bg-emerald-500 text-white' : t === 'negative' ? 'bg-red-500 text-white' : 'bg-gray-500 text-white') : 'bg-gray-100 text-gray-500'}`}>
                        {t === 'positive' ? '😊 Positive' : t === 'negative' ? '😟 Challenge' : '😐 Neutral'}
                      </button>
                    ))}
                    <select value={char.influence_level} onChange={(e) => { const c = [...lifeCharacters]; c[idx].influence_level = e.target.value; setLifeCharacters(c); }}
                      className="px-2 py-1 rounded text-[10px] border border-gray-300 ml-auto">
                      <option value="low">Low influence</option>
                      <option value="medium">Medium influence</option>
                      <option value="high">High influence</option>
                    </select>
                  </div>
                  <textarea value={char.description} onChange={(e) => { const c = [...lifeCharacters]; c[idx].description = e.target.value; setLifeCharacters(c); }}
                    placeholder="Brief description (e.g., 'A boy in SJ's class who teases him about reading')"
                    className="w-full px-2 py-1.5 rounded text-xs border border-gray-300 resize-none" rows={2} />
                </div>
              ))}
              {lifeCharacters.length === 0 && <p className="text-xs italic" style={{ color: '#b0aba4' }}>No characters added yet</p>}
            </div>

            {/* Life Lessons */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-bold uppercase" style={{ color: '#D4A853' }}>Life Lessons to Embed in Stories</p>
                <button onClick={() => setLifeLessons([...lifeLessons, { id: Date.now().toString(), topic: '', character_name: '', problem: '', parent_solution: '', delivery_method: 'story_moral', active: true }])}
                  className="text-[10px] font-bold px-2 py-1 rounded bg-amber-100 text-amber-700 hover:bg-amber-200">
                  + Add Lesson
                </button>
              </div>
              {lifeLessons.map((lesson, idx) => (
                <div key={lesson.id || idx} className="p-3 rounded-lg mb-2" style={{ background: 'rgba(212,168,83,0.06)', border: '1px solid rgba(212,168,83,0.2)' }}>
                  <div className="flex gap-2 mb-2">
                    <input value={lesson.topic} onChange={(e) => { const l = [...lifeLessons]; l[idx].topic = e.target.value; setLifeLessons(l); }}
                      placeholder="Topic (e.g., Dealing with bullies)" className="flex-1 px-2 py-1.5 rounded text-sm border border-gray-300 font-bold" />
                    <select value={lesson.character_name} onChange={(e) => { const l = [...lifeLessons]; l[idx].character_name = e.target.value; setLifeLessons(l); }}
                      className="px-2 py-1.5 rounded text-xs border border-gray-300">
                      <option value="">Related to...</option>
                      {lifeCharacters.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
                      <option value="general">General life lesson</option>
                    </select>
                    <button onClick={() => setLifeLessons(lifeLessons.filter((_, i) => i !== idx))}
                      className="text-red-500 text-xs font-bold hover:text-red-700">✕</button>
                  </div>
                  <textarea value={lesson.problem} onChange={(e) => { const l = [...lifeLessons]; l[idx].problem = e.target.value; setLifeLessons(l); }}
                    placeholder="The problem (e.g., Marcus teases SJ about reading and calls him a nerd)"
                    className="w-full px-2 py-1.5 rounded text-xs border border-gray-300 resize-none mb-2" rows={2} />
                  <textarea value={lesson.parent_solution} onChange={(e) => { const l = [...lifeLessons]; l[idx].parent_solution = e.target.value; setLifeLessons(l); }}
                    placeholder="Your solution — what you want your child to learn (e.g., Stand tall, look them in the eye, and say 'I'm proud of being smart.' Then walk away.)"
                    className="w-full px-2 py-1.5 rounded text-xs border border-gray-300 resize-none mb-2" rows={3}
                    style={{ background: 'rgba(212,168,83,0.08)' }} />
                  <div className="flex items-center gap-2">
                    <select value={lesson.delivery_method} onChange={(e) => { const l = [...lifeLessons]; l[idx].delivery_method = e.target.value; setLifeLessons(l); }}
                      className="px-2 py-1.5 rounded text-[10px] border border-gray-300 flex-1">
                      <option value="mentor_character">Through a wise mentor character</option>
                      <option value="friend_advice">Through a friend's advice</option>
                      <option value="story_moral">Through the story's events</option>
                      <option value="inner_voice">As an inner realization</option>
                    </select>
                    <button onClick={() => { const l = [...lifeLessons]; l[idx].active = !l[idx].active; setLifeLessons(l); }}
                      className={`px-2 py-1 rounded text-[10px] font-bold ${lesson.active ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-200 text-gray-500'}`}>
                      {lesson.active ? '✓ Active' : 'Inactive'}
                    </button>
                  </div>
                </div>
              ))}
              {lifeLessons.length === 0 && <p className="text-xs italic" style={{ color: '#b0aba4' }}>No lessons added yet. Add a life lesson and it will be woven into every story.</p>}
            </div>
          </div>

          <div className="mt-4">
            <BrutalButton variant="indigo" size="sm" fullWidth onClick={handleSave}
              disabled={saveMutation.isPending || saveStudentMutation.isPending}
              className="flex items-center justify-center gap-2"
              data-testid={`save-controls-${studentId}`}>
              <Save size={14} />
              {(saveMutation.isPending || saveStudentMutation.isPending) ? 'Saving...' : 'Save All Settings'}
            </BrutalButton>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParentalControlsPanel;
