import React, { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { parentalControlsAPI } from '@/lib/api';
import { BrutalCard, BrutalButton } from '@/components/brutal';
import { Shield, Mic, Video, Clock, ToggleLeft, ToggleRight, ChevronDown, ChevronUp, Save } from 'lucide-react';
import { toast } from 'sonner';

const ParentalControlsPanel = ({ studentId, studentName }) => {
  const queryClient = useQueryClient();
  const [expanded, setExpanded] = useState(false);
  const [controls, setControls] = useState(null);

  const { data: savedControls } = useQuery({
    queryKey: ['parental-controls', studentId],
    queryFn: async () => (await parentalControlsAPI.get(studentId)).data,
    enabled: !!studentId,
  });

  useEffect(() => {
    if (savedControls) setControls(savedControls);
  }, [savedControls]);

  const saveMutation = useMutation({
    mutationFn: (data) => parentalControlsAPI.update(studentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['parental-controls', studentId]);
      toast.success(`Reading rules updated for ${studentName}`);
    },
    onError: () => toast.error('Failed to save rules'),
  });

  const handleSave = () => {
    if (controls) saveMutation.mutate(controls);
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
                { value: 'optional', label: 'Optional' },
                { value: 'audio_required', label: 'Audio Required' },
                { value: 'video_required', label: 'Video Required' },
                { value: 'both_required', label: 'Both Required' },
              ].map(opt => (
                <button key={opt.value}
                  onClick={() => setControls({ ...controls, recording_mode: opt.value })}
                  className="px-3 py-2 rounded-md text-xs font-bold transition-all"
                  style={{
                    background: controls.recording_mode === opt.value ? '#6366f1' : '#eae6f2',
                    color: controls.recording_mode === opt.value ? '#fff' : '#4338ca',
                    border: `1px solid ${controls.recording_mode === opt.value ? '#6366f1' : 'rgba(99,102,241,0.2)'}`,
                  }}
                  data-testid={`recording-mode-${opt.value}`}>
                  {opt.label}
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

          <div className="mt-4">
            <BrutalButton variant="indigo" size="sm" fullWidth onClick={handleSave}
              disabled={saveMutation.isPending}
              className="flex items-center justify-center gap-2"
              data-testid={`save-controls-${studentId}`}>
              <Save size={14} />
              {saveMutation.isPending ? 'Saving...' : 'Save Reading Rules'}
            </BrutalButton>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParentalControlsPanel;
