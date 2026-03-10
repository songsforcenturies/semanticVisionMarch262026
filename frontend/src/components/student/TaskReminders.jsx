import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { remindersAPI } from '@/lib/api';
import { BookOpen, Clock, Mic, Award, AlertTriangle, ChevronRight, Sparkles } from 'lucide-react';

const C = {
  card: '#1A2236', cream: '#F8F5EE', muted: '#94A3B8', gold: '#D4A853',
};

const iconMap = {
  incomplete_story: BookOpen,
  inactivity: Clock,
  recording_due: Mic,
  spelling_contest: Award,
};

const colorMap = {
  high: { bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.2)', icon: '#EF4444', text: '#FCA5A5' },
  medium: { bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.2)', icon: '#F59E0B', text: '#FCD34D' },
  low: { bg: 'rgba(99,102,241,0.08)', border: 'rgba(99,102,241,0.2)', icon: '#818CF8', text: '#A5B4FC' },
};

const TaskReminders = ({ studentId, onOpenStory, onOpenSpelling }) => {
  const { data } = useQuery({
    queryKey: ['student-reminders', studentId],
    queryFn: async () => (await remindersAPI.getStudentReminders(studentId)).data,
    enabled: !!studentId,
    refetchInterval: 60000,
  });

  const reminders = data?.reminders || [];
  if (reminders.length === 0) return null;

  return (
    <div className="mb-4 sm:mb-6" data-testid="task-reminders">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles size={16} style={{ color: C.gold }} />
        <h3 className="text-sm font-bold uppercase" style={{ color: C.gold }}>
          Your Tasks ({reminders.length})
        </h3>
      </div>
      <div className="space-y-2">
        {reminders.slice(0, 5).map((r) => {
          const Icon = iconMap[r.type] || AlertTriangle;
          const colors = colorMap[r.priority] || colorMap.low;
          return (
            <button key={r.id}
              onClick={() => {
                if (r.type === 'spelling_contest' && onOpenSpelling) onOpenSpelling();
                else if (r.narrative_id && onOpenStory) onOpenStory(r.narrative_id);
              }}
              className="w-full flex items-center gap-3 p-3 rounded-xl text-left transition-all hover:scale-[1.01]"
              style={{ background: colors.bg, border: `1px solid ${colors.border}` }}
              data-testid={`reminder-${r.id}`}>
              <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ background: `${colors.border}` }}>
                <Icon size={16} style={{ color: colors.icon }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold truncate" style={{ color: C.cream }}>{r.title}</p>
                <p className="text-xs truncate" style={{ color: C.muted }}>{r.message}</p>
              </div>
              {r.progress !== undefined && (
                <div className="w-12 text-center flex-shrink-0">
                  <p className="text-xs font-bold" style={{ color: colors.text }}>
                    {Math.round(r.progress * 100)}%
                  </p>
                </div>
              )}
              <ChevronRight size={14} style={{ color: C.muted }} className="flex-shrink-0" />
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default TaskReminders;
