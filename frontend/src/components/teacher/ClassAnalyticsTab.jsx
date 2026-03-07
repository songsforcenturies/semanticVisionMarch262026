import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { classroomAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalBadge } from '@/components/brutal';
import { BarChart3, Users, Award, Clock, ChevronLeft, Trophy } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

const formatTime = (seconds) => {
  if (!seconds) return '0m';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
};

const ClassAnalyticsTab = () => {
  const [selectedSessionId, setSelectedSessionId] = useState(null);

  const { data: sessions = [], isLoading: sessionsLoading } = useQuery({
    queryKey: ['classroom-sessions'],
    queryFn: async () => (await classroomAPI.getAll()).data,
  });

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['session-analytics', selectedSessionId],
    queryFn: async () => (await classroomAPI.analytics(selectedSessionId)).data,
    enabled: !!selectedSessionId,
  });

  if (selectedSessionId && analytics) {
    const { session, students, class_summary } = analytics;

    const leaderboardData = students.map(s => ({
      name: s.name.length > 12 ? s.name.slice(0, 12) + '...' : s.name,
      'Words Mastered': s.words_mastered,
      'Avg Accuracy': s.avg_accuracy,
    }));

    return (
      <div className="space-y-6" data-testid="class-analytics-detail">
        <div className="flex items-center gap-4">
          <BrutalButton variant="default" size="sm" onClick={() => setSelectedSessionId(null)} data-testid="analytics-back-btn">
            <ChevronLeft size={18} className="mr-1" /> Back
          </BrutalButton>
          <h2 className="text-3xl font-black uppercase">{session.title}</h2>
          <BrutalBadge variant={session.status === 'active' ? 'emerald' : 'default'} size="lg">{session.status}</BrutalBadge>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-indigo-50 border-4 border-black p-5 brutal-shadow-sm" data-testid="stat-students">
            <div className="flex items-center gap-2 mb-2">
              <Users size={18} className="text-indigo-600" />
              <p className="font-bold text-xs uppercase text-gray-600">Students</p>
            </div>
            <p className="text-3xl font-black">{session.student_count}</p>
          </div>
          <div className="bg-amber-50 border-4 border-black p-5 brutal-shadow-sm" data-testid="stat-avg-accuracy">
            <div className="flex items-center gap-2 mb-2">
              <Award size={18} className="text-amber-600" />
              <p className="font-bold text-xs uppercase text-gray-600">Avg Accuracy</p>
            </div>
            <p className="text-3xl font-black">{class_summary.avg_accuracy}%</p>
          </div>
          <div className="bg-emerald-50 border-4 border-black p-5 brutal-shadow-sm" data-testid="stat-total-mastered">
            <div className="flex items-center gap-2 mb-2">
              <Trophy size={18} className="text-emerald-600" />
              <p className="font-bold text-xs uppercase text-gray-600">Total Mastered</p>
            </div>
            <p className="text-3xl font-black">{class_summary.total_words_mastered}</p>
          </div>
          <div className="bg-rose-50 border-4 border-black p-5 brutal-shadow-sm" data-testid="stat-avg-reading">
            <div className="flex items-center gap-2 mb-2">
              <Clock size={18} className="text-rose-600" />
              <p className="font-bold text-xs uppercase text-gray-600">Avg Reading</p>
            </div>
            <p className="text-3xl font-black">{formatTime(class_summary.avg_reading_seconds)}</p>
          </div>
        </div>

        {/* Leaderboard Chart */}
        {students.length > 0 ? (
          <BrutalCard shadow="lg">
            <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
              <Trophy size={20} className="text-amber-500" /> Student Leaderboard
            </h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={leaderboardData} layout="vertical" margin={{ left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 12, fontWeight: 700 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Words Mastered" fill="#6366f1" stroke="#000" strokeWidth={2} radius={[0, 4, 4, 0]} />
                  <Bar dataKey="Avg Accuracy" fill="#f59e0b" stroke="#000" strokeWidth={2} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </BrutalCard>
        ) : (
          <BrutalCard shadow="lg" className="text-center py-10">
            <BarChart3 size={40} className="mx-auto mb-3 text-gray-400" />
            <p className="text-lg font-bold text-gray-500">No student data yet</p>
            <p className="text-sm text-gray-400">Students need to join and complete activities</p>
          </BrutalCard>
        )}

        {/* Student Table */}
        {students.length > 0 && (
          <BrutalCard shadow="lg">
            <h3 className="text-xl font-black uppercase mb-4">Student Details</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b-4 border-black">
                    <th className="py-3 px-4 font-black text-xs uppercase">Student</th>
                    <th className="py-3 px-4 font-black text-xs uppercase">Words Mastered</th>
                    <th className="py-3 px-4 font-black text-xs uppercase">Assessments</th>
                    <th className="py-3 px-4 font-black text-xs uppercase">Avg Accuracy</th>
                    <th className="py-3 px-4 font-black text-xs uppercase">Reading Time</th>
                    <th className="py-3 px-4 font-black text-xs uppercase">Score</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((s, i) => (
                    <tr key={s.id} className={`border-b-2 border-gray-200 ${i === 0 ? 'bg-amber-50' : ''}`} data-testid={`student-row-${s.id}`}>
                      <td className="py-3 px-4 font-bold">{i === 0 && <Trophy size={14} className="inline mr-1 text-amber-500" />}{s.name}</td>
                      <td className="py-3 px-4 font-bold">{s.words_mastered}</td>
                      <td className="py-3 px-4">{s.assessments_completed}</td>
                      <td className="py-3 px-4">{s.avg_accuracy}%</td>
                      <td className="py-3 px-4">{formatTime(s.reading_seconds)}</td>
                      <td className="py-3 px-4 font-bold">{s.score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </BrutalCard>
        )}
      </div>
    );
  }

  if (sessionsLoading) return <div className="text-center py-12 text-2xl font-bold">Loading...</div>;

  return (
    <div className="space-y-6" data-testid="analytics-tab">
      <h2 className="text-3xl font-black uppercase">Class Analytics</h2>
      <p className="text-lg font-medium text-gray-600">Select a session to view class-wide analytics</p>

      {sessions.length === 0 ? (
        <BrutalCard shadow="xl" className="text-center py-12">
          <BarChart3 size={48} className="mx-auto mb-4 text-gray-400" />
          <p className="text-2xl font-bold mb-2">No sessions yet</p>
          <p className="text-lg text-gray-500">Create a classroom session to start tracking analytics</p>
        </BrutalCard>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sessions.map((s) => (
            <BrutalCard
              key={s.id}
              shadow="lg"
              hover
              className="cursor-pointer transition-transform hover:-translate-y-1"
              onClick={() => setSelectedSessionId(s.id)}
              data-testid={`analytics-session-${s.id}`}
            >
              <h3 className="text-xl font-black uppercase mb-2">{s.title}</h3>
              <div className="flex items-center gap-3 mb-3">
                <BrutalBadge variant={s.status === 'active' ? 'emerald' : s.status === 'waiting' ? 'amber' : 'default'} size="sm">{s.status}</BrutalBadge>
                <span className="text-sm font-medium text-gray-500">{s.participating_students?.length || 0} students</span>
              </div>
              <BrutalButton variant="indigo" fullWidth size="sm" className="flex items-center justify-center gap-2" data-testid={`view-analytics-btn-${s.id}`}>
                <BarChart3 size={16} /> View Analytics
              </BrutalButton>
            </BrutalCard>
          ))}
        </div>
      )}
    </div>
  );
};

export default ClassAnalyticsTab;
