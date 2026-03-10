import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { spellingContestsAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalInput, BrutalBadge } from '@/components/brutal';
import { Award, Trash2, PlusCircle, Users, Clock, ToggleLeft } from 'lucide-react';
import { toast } from 'sonner';

const AdminSpellingContestsTab = () => {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    title: '', description: '', words: '', time_limit: '120',
    start_date: '', end_date: '',
  });
  const [showLeaderboard, setShowLeaderboard] = useState(null);

  const { data: contests = [] } = useQuery({
    queryKey: ['admin-spelling-contests'],
    queryFn: async () => (await spellingContestsAPI.adminList()).data,
  });

  const { data: leaderboard = [] } = useQuery({
    queryKey: ['spelling-leaderboard', showLeaderboard],
    queryFn: async () => (await spellingContestsAPI.leaderboard(showLeaderboard)).data,
    enabled: !!showLeaderboard,
  });

  const createMutation = useMutation({
    mutationFn: (data) => spellingContestsAPI.adminCreate(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-spelling-contests']);
      toast.success('Spelling contest created!');
      setForm({ title: '', description: '', words: '', time_limit: '120', start_date: '', end_date: '' });
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to create'),
  });

  const toggleMutation = useMutation({
    mutationFn: (id) => spellingContestsAPI.adminToggle(id),
    onSuccess: () => queryClient.invalidateQueries(['admin-spelling-contests']),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => spellingContestsAPI.adminDelete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-spelling-contests']);
      toast.success('Contest deleted');
    },
  });

  const handleCreate = (e) => {
    e.preventDefault();
    const wordList = form.words.split(',').map(w => w.trim()).filter(Boolean);
    if (wordList.length === 0) { toast.error('Add at least one word'); return; }
    createMutation.mutate({
      title: form.title,
      description: form.description,
      word_list: wordList,
      time_limit_seconds: parseInt(form.time_limit) || 120,
      start_date: new Date(form.start_date).toISOString(),
      end_date: new Date(form.end_date).toISOString(),
    });
  };

  return (
    <div className="space-y-6" data-testid="spelling-contests-tab">
      <BrutalCard shadow="xl">
        <h3 className="text-2xl font-black uppercase mb-4 flex items-center gap-2">
          <Award size={24} className="text-purple-500" /> Create Spelling Contest
        </h3>
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <BrutalInput label="Contest Title *" required value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="e.g. March Spelling Bee" data-testid="spell-title" />
            <BrutalInput label="Time Limit (seconds)" type="number" value={form.time_limit}
              onChange={(e) => setForm({ ...form, time_limit: e.target.value })}
              placeholder="120" data-testid="spell-time" />
          </div>
          <BrutalInput label="Description" value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="A fun spelling challenge for all students!" data-testid="spell-desc" />
          <div>
            <label className="block font-bold text-sm uppercase mb-2">Words (comma-separated) *</label>
            <textarea value={form.words}
              onChange={(e) => setForm({ ...form, words: e.target.value })}
              placeholder="beautiful, knowledge, science, adventure, rhythm..."
              rows={3}
              className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-purple-500 resize-none"
              style={{ color: '#111827' }}
              data-testid="spell-words" />
            <p className="text-xs text-gray-500 mt-1">
              {form.words.split(',').filter(w => w.trim()).length} words added
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <BrutalInput label="Start Date *" type="datetime-local" required value={form.start_date}
              onChange={(e) => setForm({ ...form, start_date: e.target.value })} data-testid="spell-start" />
            <BrutalInput label="End Date *" type="datetime-local" required value={form.end_date}
              onChange={(e) => setForm({ ...form, end_date: e.target.value })} data-testid="spell-end" />
          </div>
          <BrutalButton type="submit" variant="indigo" size="lg" fullWidth
            disabled={createMutation.isPending} data-testid="spell-create-btn">
            {createMutation.isPending ? 'Creating...' : 'Launch Spelling Contest'}
          </BrutalButton>
        </form>
      </BrutalCard>

      <h3 className="text-2xl font-black uppercase">All Spelling Contests ({contests.length})</h3>
      {contests.length === 0 ? (
        <BrutalCard shadow="md" className="text-center py-8">
          <Award size={48} className="mx-auto text-gray-300 mb-3" />
          <p className="text-lg font-bold text-gray-500">No spelling contests yet</p>
        </BrutalCard>
      ) : (
        <div className="space-y-4">
          {contests.map((c) => {
            const isExpired = new Date(c.end_date) < new Date();
            return (
              <BrutalCard key={c.id} shadow="lg" data-testid={`spell-contest-${c.id}`}>
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h4 className="text-xl font-black uppercase">{c.title}</h4>
                      {c.is_active && !isExpired ? (
                        <BrutalBadge variant="emerald" size="sm">LIVE</BrutalBadge>
                      ) : isExpired ? (
                        <BrutalBadge variant="default" size="sm">ENDED</BrutalBadge>
                      ) : (
                        <BrutalBadge variant="rose" size="sm">PAUSED</BrutalBadge>
                      )}
                    </div>
                    {c.description && <p className="text-sm text-gray-600 mb-2">{c.description}</p>}
                    <div className="flex items-center gap-4 text-sm flex-wrap">
                      <span className="font-bold text-purple-700">{c.word_list?.length || 0} words</span>
                      <span className="text-gray-500 flex items-center gap-1"><Clock size={14} /> {c.time_limit_seconds}s limit</span>
                      <span className="text-gray-500 flex items-center gap-1"><Users size={14} /> {c.participants?.length || 0} participants</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      {new Date(c.start_date).toLocaleDateString()} - {new Date(c.end_date).toLocaleDateString()}
                    </p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {c.word_list?.slice(0, 8).map((w, i) => (
                        <span key={i} className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-100 text-purple-700">{w}</span>
                      ))}
                      {(c.word_list?.length || 0) > 8 && (
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-gray-100 text-gray-500">+{c.word_list.length - 8} more</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <BrutalButton variant="indigo" size="sm"
                      onClick={() => setShowLeaderboard(showLeaderboard === c.id ? null : c.id)}
                      data-testid={`spell-leaderboard-${c.id}`}>
                      Leaderboard
                    </BrutalButton>
                    <BrutalButton variant={c.is_active ? 'rose' : 'emerald'} size="sm"
                      onClick={() => toggleMutation.mutate(c.id)}>
                      {c.is_active ? 'Pause' : 'Activate'}
                    </BrutalButton>
                    <BrutalButton variant="dark" size="sm"
                      onClick={() => { if (window.confirm(`Delete "${c.title}"?`)) deleteMutation.mutate(c.id); }}>
                      <Trash2 size={14} />
                    </BrutalButton>
                  </div>
                </div>
                {/* Leaderboard */}
                {showLeaderboard === c.id && (
                  <div className="mt-4 pt-4 border-t-4 border-black">
                    <h5 className="font-black uppercase mb-3">Leaderboard</h5>
                    {leaderboard.length === 0 ? (
                      <p className="text-sm text-gray-500">No submissions yet</p>
                    ) : (
                      <div className="space-y-2">
                        {leaderboard.map((s, i) => (
                          <div key={s.id} className="flex items-center gap-3 p-2 rounded-lg bg-gray-50">
                            <span className="font-black text-lg w-8 text-center" style={{ color: i === 0 ? '#D4A853' : i === 1 ? '#94A3B8' : i === 2 ? '#CD7F32' : '#6B7280' }}>
                              #{s.rank}
                            </span>
                            <div className="flex-1">
                              <p className="font-bold text-sm">{s.student_name}</p>
                              <p className="text-xs text-gray-500">{s.correct_count}/{s.total_words} correct in {s.time_taken_seconds}s</p>
                            </div>
                            <span className="text-xl font-black" style={{ color: s.score >= 80 ? '#10b981' : s.score >= 50 ? '#f59e0b' : '#ef4444' }}>
                              {s.score}%
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </BrutalCard>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AdminSpellingContestsTab;
