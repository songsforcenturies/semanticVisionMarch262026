import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { studentAPI, narrativeAPI } from '@/lib/api';
import { toast } from 'sonner';
import { BrutalCard, BrutalButton, BrutalBadge } from '@/components/brutal';
import { TrendingUp, BookOpen, Clock, Target, ChevronLeft, Award, BarChart3, Brain, Download, Printer, CalendarDays, Timer, Activity, Eye, X } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  AreaChart, Area
} from 'recharts';

const CHART_COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899'];

const StatCard = ({ label, value, sub, icon: Icon, color = 'indigo' }) => {
  const bgMap = { indigo: 'bg-indigo-50', amber: 'bg-amber-50', emerald: 'bg-emerald-50', rose: 'bg-rose-50' };
  const textMap = { indigo: 'text-indigo-600', amber: 'text-amber-600', emerald: 'text-emerald-600', rose: 'text-rose-600' };
  return (
    <div className={`${bgMap[color]} border-4 border-black p-5 brutal-shadow-sm`} data-testid={`stat-${label.toLowerCase().replace(/\s/g, '-')}`}>
      <div className="flex items-center gap-2 mb-2">
        {Icon && <Icon size={18} className={textMap[color]} />}
        <p className="font-bold text-xs uppercase text-gray-600">{label}</p>
      </div>
      <p className="text-3xl font-black">{value}</p>
      {sub && <p className="text-sm font-medium text-gray-500 mt-1">{sub}</p>}
    </div>
  );
};

const EmptyState = ({ message }) => (
  <div className="text-center py-10 border-4 border-dashed border-gray-300 bg-gray-50">
    <BarChart3 size={40} className="mx-auto mb-3 text-gray-400" />
    <p className="text-lg font-bold text-gray-500">{message}</p>
    <p className="text-sm text-gray-400 mt-1">Data will appear here once the student starts learning</p>
  </div>
);

const formatTime = (seconds) => {
  if (!seconds) return '0m';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
};

const StudentProgressDetail = ({ studentId, onBack }) => {
  const queryClient = useQueryClient();
  const [showArchived, setShowArchived] = useState(false);
  const [readingStory, setReadingStory] = useState(null);
  const [readingChapter, setReadingChapter] = useState(1);
  const { data: progress, isLoading } = useQuery({
    queryKey: ['student-progress', studentId],
    queryFn: async () => {
      const res = await studentAPI.getProgress(studentId);
      return res.data;
    },
    enabled: !!studentId,
  });

  const { data: timeLog, isLoading: timeLogLoading } = useQuery({
    queryKey: ['student-time-log', studentId],
    queryFn: async () => {
      const res = await studentAPI.getTimeLog(studentId);
      return res.data;
    },
    enabled: !!studentId,
  });

  const handleExportJSON = () => {
    const token = localStorage.getItem('token');
    const url = studentAPI.getExportUrl(studentId, 'json');
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => res.blob())
      .then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `leximaster_report_${progress?.student?.full_name?.replace(/\s/g, '_') || studentId}.json`;
        a.click();
        URL.revokeObjectURL(a.href);
      });
  };

  const handleExportHTML = () => {
    const token = localStorage.getItem('token');
    const url = studentAPI.getExportUrl(studentId, 'html');
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => res.text())
      .then(html => {
        const w = window.open('', '_blank');
        w.document.write(html);
        w.document.close();
      });
  };

  if (isLoading) return <div className="text-center py-12 text-2xl font-bold">Loading progress...</div>;
  if (!progress) return <div className="text-center py-12 text-2xl font-bold">No data found</div>;

  const { student, reading_stats, vocabulary, assessments, narratives, assigned_banks } = progress;

  const masteryData = [
    { name: 'Mastered', value: vocabulary.mastered_count },
    { name: 'Remaining', value: Math.max(0, vocabulary.biological_target - vocabulary.mastered_count) },
  ];

  const assessmentChartData = assessments.history.map((a, i) => ({
    name: `#${assessments.history.length - i}`,
    accuracy: a.accuracy,
    correct: a.correct,
    total: a.total,
  })).reverse();

  const narrativeStatusData = [
    { name: 'Completed', value: narratives.completed },
    { name: 'In Progress', value: narratives.total - narratives.completed },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-6" data-testid="student-progress-detail">
      {/* Back + Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <BrutalButton variant="default" size="sm" onClick={onBack} className="flex items-center gap-1" data-testid="progress-back-btn">
            <ChevronLeft size={18} /> Back
          </BrutalButton>
          <div>
            <h2 className="text-3xl font-black uppercase">{student.full_name}</h2>
            <p className="text-sm font-medium text-gray-500">
              {student.age ? `Age ${student.age}` : ''}{student.grade_level ? ` · Grade ${student.grade_level}` : ''}
            </p>
          </div>
          {student.agentic_reach_score > 0 && (
            <BrutalBadge variant="indigo" size="lg">Score: {student.agentic_reach_score}</BrutalBadge>
          )}
        </div>
        <div className="flex gap-2">
          <BrutalButton variant="emerald" size="sm" onClick={handleExportJSON} className="flex items-center gap-1" data-testid="export-json-btn">
            <Download size={16} /> Export JSON
          </BrutalButton>
          <BrutalButton variant="indigo" size="sm" onClick={handleExportHTML} className="flex items-center gap-1" data-testid="export-html-btn">
            <Printer size={16} /> Print Report
          </BrutalButton>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Words Mastered" value={vocabulary.mastered_count} sub={`of ${vocabulary.biological_target} target`} icon={Brain} color="indigo" />
        <StatCard label="Reading Time" value={formatTime(reading_stats.total_reading_seconds)} sub={`${reading_stats.sessions_count} sessions`} icon={Clock} color="amber" />
        <StatCard label="Avg WPM" value={reading_stats.average_wpm || '—'} sub={`${reading_stats.total_words_read} total words`} icon={BookOpen} color="emerald" />
        <StatCard label="Assessments" value={assessments.completed} sub={`${assessments.average_accuracy}% avg accuracy`} icon={Award} color="rose" />
      </div>

      {/* Cumulative Time Log */}
      <BrutalCard shadow="lg" data-testid="time-log-section">
        <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
          <Timer size={20} className="text-violet-500" /> Cumulative Time Log
        </h3>
        {timeLogLoading ? (
          <p className="text-gray-500 font-medium py-4 text-center">Loading time data...</p>
        ) : !timeLog || timeLog.total_sessions === 0 ? (
          <EmptyState message="No login sessions recorded yet" />
        ) : (
          <div className="space-y-5">
            {/* Time Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-violet-50 border-4 border-black p-4 brutal-shadow-sm" data-testid="time-total-days">
                <div className="flex items-center gap-2 mb-1">
                  <CalendarDays size={16} className="text-violet-600" />
                  <p className="font-bold text-xs uppercase text-gray-600">Days Active</p>
                </div>
                <p className="text-2xl font-black">{timeLog.total_days_logged_in}</p>
                <p className="text-xs text-gray-500 font-medium">unique days</p>
              </div>
              <div className="bg-violet-50 border-4 border-black p-4 brutal-shadow-sm" data-testid="time-cumulative">
                <div className="flex items-center gap-2 mb-1">
                  <Timer size={16} className="text-violet-600" />
                  <p className="font-bold text-xs uppercase text-gray-600">Total Time</p>
                </div>
                <p className="text-2xl font-black">{timeLog.cumulative_display}</p>
                <p className="text-xs text-gray-500 font-medium">{timeLog.total_sessions} sessions</p>
              </div>
              <div className="bg-violet-50 border-4 border-black p-4 brutal-shadow-sm" data-testid="time-avg-daily">
                <div className="flex items-center gap-2 mb-1">
                  <Activity size={16} className="text-violet-600" />
                  <p className="font-bold text-xs uppercase text-gray-600">Avg / Day</p>
                </div>
                <p className="text-2xl font-black">{timeLog.average_daily_display}</p>
                <p className="text-xs text-gray-500 font-medium">per active day</p>
              </div>
              <div className="bg-violet-50 border-4 border-black p-4 brutal-shadow-sm" data-testid="time-total-sessions">
                <div className="flex items-center gap-2 mb-1">
                  <TrendingUp size={16} className="text-violet-600" />
                  <p className="font-bold text-xs uppercase text-gray-600">Sessions</p>
                </div>
                <p className="text-2xl font-black">{timeLog.total_sessions}</p>
                <p className="text-xs text-gray-500 font-medium">total logins</p>
              </div>
            </div>

            {/* Daily Activity Chart */}
            {timeLog.daily_logs && timeLog.daily_logs.length > 0 && (
              <div>
                <h4 className="font-bold text-sm uppercase text-gray-600 mb-3">Daily Login Hours</h4>
                <div className="h-52" data-testid="time-log-chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={timeLog.daily_logs.slice(-30)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 11, fontWeight: 700 }}
                        tickFormatter={(d) => d.slice(5)}
                      />
                      <YAxis tick={{ fontSize: 11 }} label={{ value: 'Hours', angle: -90, position: 'insideLeft', fontSize: 11, fontWeight: 700 }} />
                      <Tooltip
                        formatter={(v) => [`${v.toFixed(2)} hrs`, 'Time']}
                        labelFormatter={(d) => `Date: ${d}`}
                      />
                      <Bar dataKey="hours" fill="#8b5cf6" stroke="#000" strokeWidth={2} radius={[4, 4, 0, 0]} name="Hours" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        )}
      </BrutalCard>

      {/* Charts Row */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Vocabulary Mastery Pie */}
        <BrutalCard shadow="lg">
          <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
            <Target size={20} className="text-indigo-500" /> Vocabulary Mastery
          </h3>
          {vocabulary.mastered_count > 0 || vocabulary.biological_target > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={masteryData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={4} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                    {masteryData.map((_, idx) => (
                      <Cell key={idx} fill={CHART_COLORS[idx]} stroke="#000" strokeWidth={2} />
                    ))}
                  </Pie>
                  <Legend />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState message="No vocabulary data yet" />
          )}
          {vocabulary.mastery_percentage > 0 && (
            <p className="text-center font-bold mt-2">{vocabulary.mastery_percentage}% of biological target</p>
          )}
        </BrutalCard>

        {/* Assessment Accuracy Chart */}
        <BrutalCard shadow="lg">
          <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
            <Award size={20} className="text-amber-500" /> Assessment History
          </h3>
          {assessmentChartData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={assessmentChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12, fontWeight: 700 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(v) => `${v}%`} />
                  <Bar dataKey="accuracy" fill="#6366f1" stroke="#000" strokeWidth={2} radius={[4, 4, 0, 0]} name="Accuracy %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState message="No assessments completed yet" />
          )}
        </BrutalCard>
      </div>

      {/* Stories Section */}
      <BrutalCard shadow="lg">
        <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
          <BookOpen size={20} className="text-emerald-500" /> Story History
        </h3>
        {narratives.stories.length > 0 ? (
          <div className="space-y-3">
            {narratives.stories.filter(s => s.status !== 'archived' || showArchived).map((story) => (
              <div key={story.id} className={`flex items-center justify-between border-4 p-4 ${story.status === 'archived' ? 'bg-gray-200 border-gray-400 opacity-50' : 'bg-white border-black'}`} data-testid={`story-${story.id}`}>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className={`font-black text-lg ${story.status === 'archived' ? 'line-through text-gray-500' : ''}`}>{story.title}</p>
                    {story.status === 'archived' && (
                      <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 bg-gray-500 text-white rounded">ARCHIVED</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 font-medium">
                    {story.total_word_count} words · {story.chapters_completed}/{story.chapters_total} chapters
                  </p>
                  <p className="text-xs text-gray-400 font-medium mt-1">
                    Created: {story.created_date ? new Date(story.created_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'N/A'}
                    {story.last_read_date ? ` · Last read: ${new Date(story.last_read_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}` : ' · Not read yet'}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                  <BrutalBadge variant={story.status === 'completed' ? 'emerald' : story.status === 'archived' ? 'gray' : 'amber'} size="sm">
                    {story.status}
                  </BrutalBadge>
                  <button onClick={async () => {
                    try {
                      const res = await narrativeAPI.getById(story.id);
                      setReadingStory(res.data);
                      setReadingChapter(1);
                    } catch (err) {
                      toast.error('Failed to load story');
                    }
                  }} className="text-xs font-bold px-3 py-1.5 bg-indigo-500 text-white rounded hover:bg-indigo-600 transition-colors flex items-center gap-1">
                    <Eye size={12} /> Read
                  </button>
                  {story.status === 'archived' ? (
                    <button onClick={async () => {
                      if (!window.confirm('Restore this story? It will be visible to the student again.')) return;
                      await narrativeAPI.unarchive(story.id);
                      story.status = 'active';
                      await queryClient.refetchQueries({ queryKey: ['student-progress', studentId] });
                      toast.success('Story restored');
                    }} className="text-xs font-bold px-3 py-1.5 bg-emerald-500 text-white rounded hover:bg-emerald-600 transition-colors">Restore</button>
                  ) : (
                    <button onClick={async () => {
                      if (!window.confirm('Archive this story?\n\n• Hidden from the student\'s story list\n• Data still available for parents, brands & system analytics\n• Can be restored anytime')) return;
                      await narrativeAPI.archive(story.id);
                      story.status = 'archived';
                      await queryClient.refetchQueries({ queryKey: ['student-progress', studentId] });
                      toast.success('Story archived — hidden from student. Data preserved for parents & analytics.');
                    }} className="text-xs font-bold px-3 py-1.5 bg-gray-700 text-white rounded hover:bg-gray-800 transition-colors">Archive</button>
                  )}
                  <button onClick={async () => {
                    if (!window.confirm('PERMANENTLY delete this story and all related data? This cannot be undone.')) return;
                    await narrativeAPI.delete(story.id);
                    await queryClient.refetchQueries({ queryKey: ['student-progress', studentId] });
                    toast.success('Story permanently deleted');
                  }} className="text-xs font-bold px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 transition-colors">Delete</button>
                </div>
              </div>
            ))}
            <button onClick={() => setShowArchived(!showArchived)} className="text-xs font-bold text-gray-400 hover:text-gray-600 mt-2">
              {showArchived ? 'Hide archived stories' : `Show archived stories (${narratives.stories.filter(s => s.status === 'archived').length})`}
            </button>
          </div>
        ) : (
          <EmptyState message="No stories generated yet" />
        )}
      </BrutalCard>

      {/* Word Banks & Virtues */}
      <div className="grid md:grid-cols-2 gap-6">
        <BrutalCard shadow="lg">
          <h3 className="text-xl font-black uppercase mb-4">Assigned Word Banks</h3>
          {assigned_banks.length > 0 ? (
            <div className="space-y-2">
              {assigned_banks.map((bank) => (
                <div key={bank.id} className="flex items-center justify-between border-2 border-black p-3 bg-indigo-50">
                  <span className="font-bold">{bank.name}</span>
                  <BrutalBadge variant="indigo" size="sm">{bank.total_tokens} words</BrutalBadge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 font-medium">No word banks assigned yet</p>
          )}
        </BrutalCard>

        <BrutalCard shadow="lg">
          <h3 className="text-xl font-black uppercase mb-4">Character Education</h3>
          {student.virtues && student.virtues.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {student.virtues.map((virtue, idx) => (
                <BrutalBadge key={idx} variant="emerald" size="lg">{virtue}</BrutalBadge>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 font-medium">No virtues added yet</p>
          )}
        </BrutalCard>
      </div>

      {/* Recently Mastered Words */}
      {vocabulary.recent_mastered.length > 0 && (
        <BrutalCard shadow="lg">
          <h3 className="text-xl font-black uppercase mb-4">Recently Mastered Words</h3>
          <div className="flex flex-wrap gap-2">
            {vocabulary.recent_mastered.map((word, idx) => (
              <span key={idx} className="px-4 py-2 bg-emerald-100 border-4 border-black font-black text-lg brutal-shadow-sm">
                {word}
              </span>
            ))}
          </div>
        </BrutalCard>
      )}

      {/* Story Reader Modal */}
      {readingStory && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white border-4 border-black max-w-3xl w-full mx-4 max-h-[90vh] flex flex-col shadow-[8px_8px_0_0_rgba(0,0,0,1)]">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b-4 border-black bg-indigo-50">
              <div>
                <h3 className="text-xl font-black uppercase">{readingStory.title}</h3>
                <p className="text-sm font-medium text-gray-500">
                  Chapter {readingChapter} of {readingStory.chapters?.length || 0}
                </p>
              </div>
              <button onClick={() => setReadingStory(null)} className="p-1 hover:bg-indigo-100 border-2 border-black">
                <X size={20} />
              </button>
            </div>

            {/* Chapter Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {readingStory.chapters && readingStory.chapters.length > 0 ? (
                <div>
                  <h4 className="text-lg font-black mb-4">
                    {readingStory.chapters[readingChapter - 1]?.title || `Chapter ${readingChapter}`}
                  </h4>
                  <div className="prose max-w-none text-base leading-relaxed whitespace-pre-wrap">
                    {readingStory.chapters[readingChapter - 1]?.content || 'No content available'}
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 font-medium text-center py-8">No chapters available</p>
              )}
            </div>

            {/* Chapter Navigation */}
            {readingStory.chapters && readingStory.chapters.length > 1 && (
              <div className="flex items-center justify-between p-4 border-t-4 border-black bg-gray-50">
                <BrutalButton
                  variant="default"
                  size="sm"
                  onClick={() => setReadingChapter((c) => Math.max(1, c - 1))}
                  disabled={readingChapter <= 1}
                >
                  Previous
                </BrutalButton>
                <div className="flex gap-1">
                  {readingStory.chapters.map((_, idx) => (
                    <button
                      key={idx}
                      onClick={() => setReadingChapter(idx + 1)}
                      className={`w-8 h-8 text-xs font-black border-2 border-black ${
                        readingChapter === idx + 1
                          ? 'bg-indigo-500 text-white'
                          : 'bg-white hover:bg-indigo-50'
                      }`}
                    >
                      {idx + 1}
                    </button>
                  ))}
                </div>
                <BrutalButton
                  variant="default"
                  size="sm"
                  onClick={() => setReadingChapter((c) => Math.min(readingStory.chapters.length, c + 1))}
                  disabled={readingChapter >= readingStory.chapters.length}
                >
                  Next
                </BrutalButton>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const ProgressTab = () => {
  const { user } = useAuth();
  const [selectedStudentId, setSelectedStudentId] = useState(null);

  const { data: students = [], isLoading } = useQuery({
    queryKey: ['students', user?.id],
    queryFn: async () => {
      const res = await studentAPI.getAll(user?.id);
      return res.data;
    },
    enabled: !!user?.id,
  });

  if (selectedStudentId) {
    return <StudentProgressDetail studentId={selectedStudentId} onBack={() => setSelectedStudentId(null)} />;
  }

  if (isLoading) return <div className="text-center py-12 text-2xl font-bold">Loading...</div>;

  return (
    <div className="space-y-6" data-testid="progress-tab">
      <h2 className="text-3xl font-black uppercase">Student Progress</h2>
      <p className="text-lg font-medium text-gray-600">Select a student to view detailed analytics</p>

      {students.length === 0 ? (
        <BrutalCard shadow="xl" className="text-center py-12">
          <TrendingUp size={48} className="mx-auto mb-4 text-gray-400" />
          <p className="text-2xl font-bold mb-2">No students yet</p>
          <p className="text-lg text-gray-500">Add students from the Students tab to track their progress</p>
        </BrutalCard>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {students.map((student) => (
            <BrutalCard
              key={student.id}
              shadow="lg"
              hover
              className="cursor-pointer transition-transform hover:-translate-y-1"
              onClick={() => setSelectedStudentId(student.id)}
              data-testid={`progress-student-card-${student.id}`}
            >
              <div className="mb-4">
                <h3 className="text-2xl font-black uppercase">{student.full_name}</h3>
                <p className="text-sm font-medium text-gray-500">
                  {student.age ? `Age ${student.age}` : ''}{student.grade_level ? ` · Grade ${student.grade_level}` : ''}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 border-t-4 border-black pt-4">
                <div>
                  <p className="text-xs font-bold uppercase text-gray-600">Mastered</p>
                  <p className="text-2xl font-black">{student.mastered_tokens?.length || 0}</p>
                </div>
                <div>
                  <p className="text-xs font-bold uppercase text-gray-600">Word Banks</p>
                  <p className="text-2xl font-black">{student.assigned_banks?.length || 0}</p>
                </div>
                <div>
                  <p className="text-xs font-bold uppercase text-gray-600">Score</p>
                  <p className="text-2xl font-black">{student.agentic_reach_score || 0}</p>
                </div>
                <div>
                  <p className="text-xs font-bold uppercase text-gray-600">Target</p>
                  <p className="text-2xl font-black">{student.biological_target || 0}</p>
                </div>
              </div>

              <div className="mt-4">
                <BrutalButton variant="indigo" fullWidth size="sm" className="flex items-center justify-center gap-2" data-testid={`view-progress-btn-${student.id}`}>
                  <TrendingUp size={16} /> View Progress
                </BrutalButton>
              </div>
            </BrutalCard>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProgressTab;
