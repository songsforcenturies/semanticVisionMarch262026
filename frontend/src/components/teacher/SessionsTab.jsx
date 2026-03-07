import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { classroomAPI, wordBankAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalBadge } from '@/components/brutal';
import { BrutalInput } from '@/components/brutal';
import { Plus, Play, Square, Copy, Check, Users, Clock, Hash } from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

const statusColors = { waiting: 'amber', active: 'emerald', completed: 'default' };

const SessionsTab = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
  const [copiedCode, setCopiedCode] = useState(null);
  const [formData, setFormData] = useState({ title: '', description: '', bank_ids: [] });

  const { data: sessions = [], isLoading } = useQuery({
    queryKey: ['classroom-sessions'],
    queryFn: async () => (await classroomAPI.getAll()).data,
  });

  const { data: wordBanks = [] } = useQuery({
    queryKey: ['word-banks-all'],
    queryFn: async () => (await wordBankAPI.getAll()).data,
  });

  const createMutation = useMutation({
    mutationFn: (data) => classroomAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['classroom-sessions']);
      setShowCreate(false);
      setFormData({ title: '', description: '', bank_ids: [] });
      toast.success('Session created!');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to create session'),
  });

  const startMutation = useMutation({
    mutationFn: (id) => classroomAPI.start(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['classroom-sessions']);
      toast.success('Session started!');
    },
  });

  const endMutation = useMutation({
    mutationFn: (id) => classroomAPI.end(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['classroom-sessions']);
      toast.success('Session ended');
    },
  });

  const handleCopyCode = (code) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    toast.success('Session code copied!');
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const handleCreate = (e) => {
    e.preventDefault();
    if (!formData.title.trim()) { toast.error('Title is required'); return; }
    createMutation.mutate(formData);
  };

  const toggleBank = (bankId) => {
    setFormData(prev => ({
      ...prev,
      bank_ids: prev.bank_ids.includes(bankId)
        ? prev.bank_ids.filter(id => id !== bankId)
        : [...prev.bank_ids, bankId]
    }));
  };

  if (isLoading) return <div className="text-center py-12 text-2xl font-bold">Loading sessions...</div>;

  // Session detail view
  if (selectedSession) {
    const s = selectedSession;
    return (
      <div className="space-y-6" data-testid="session-detail">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <BrutalButton variant="default" size="sm" onClick={() => setSelectedSession(null)} data-testid="session-back-btn">
              Back
            </BrutalButton>
            <h2 className="text-3xl font-black uppercase">{s.title}</h2>
            <BrutalBadge variant={statusColors[s.status]} size="lg">{s.status}</BrutalBadge>
          </div>
          <div className="flex gap-2">
            {s.status === 'waiting' && (
              <BrutalButton variant="emerald" size="sm" onClick={() => { startMutation.mutate(s.id); setSelectedSession({ ...s, status: 'active' }); }} data-testid="start-session-btn">
                <Play size={16} className="mr-1" /> Start Session
              </BrutalButton>
            )}
            {s.status === 'active' && (
              <BrutalButton variant="rose" size="sm" onClick={() => { endMutation.mutate(s.id); setSelectedSession({ ...s, status: 'completed' }); }} data-testid="end-session-btn">
                <Square size={16} className="mr-1" /> End Session
              </BrutalButton>
            )}
          </div>
        </div>

        {/* Session Code */}
        <BrutalCard variant="emerald" shadow="xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-bold text-xs uppercase text-gray-600">Session Join Code</p>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-5xl font-black font-mono tracking-widest">{s.session_code}</span>
                <BrutalButton variant="dark" size="sm" onClick={() => handleCopyCode(s.session_code)}>
                  {copiedCode === s.session_code ? <Check size={18} /> : <Copy size={18} />}
                </BrutalButton>
              </div>
              <p className="text-sm font-medium text-gray-600 mt-1">Share this code with students to join</p>
            </div>
            <div className="text-right">
              <p className="font-bold text-xs uppercase text-gray-600">Students Joined</p>
              <p className="text-4xl font-black">{s.participating_students?.length || 0}</p>
            </div>
          </div>
        </BrutalCard>

        {/* Roster */}
        <BrutalCard shadow="lg">
          <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
            <Users size={20} /> Class Roster
          </h3>
          {s.participating_students?.length > 0 ? (
            <div className="space-y-2">
              {s.participating_students.map((p, i) => (
                <div key={i} className="flex items-center justify-between border-4 border-black p-3 bg-white" data-testid={`roster-student-${i}`}>
                  <span className="font-bold text-lg">{p.student_name}</span>
                  <span className="text-sm text-gray-500 font-medium">Joined {new Date(p.joined_at).toLocaleTimeString()}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 border-4 border-dashed border-gray-300 bg-gray-50">
              <Users size={36} className="mx-auto mb-2 text-gray-400" />
              <p className="font-bold text-gray-500">No students have joined yet</p>
              <p className="text-sm text-gray-400">Share the session code above</p>
            </div>
          )}
        </BrutalCard>

        {s.description && (
          <BrutalCard shadow="lg">
            <h3 className="text-xl font-black uppercase mb-2">Description</h3>
            <p className="font-medium text-gray-700">{s.description}</p>
          </BrutalCard>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="sessions-tab">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-black uppercase">Classroom Sessions</h2>
        <BrutalButton variant="emerald" size="lg" onClick={() => setShowCreate(true)} className="flex items-center gap-2" data-testid="create-session-btn">
          <Plus size={24} /> New Session
        </BrutalButton>
      </div>

      {sessions.length === 0 ? (
        <BrutalCard shadow="xl" className="text-center py-12">
          <Users size={48} className="mx-auto mb-4 text-gray-400" />
          <p className="text-2xl font-bold mb-2">No sessions yet</p>
          <p className="text-lg text-gray-500">Create your first classroom session to get started</p>
        </BrutalCard>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sessions.map((s) => (
            <BrutalCard
              key={s.id}
              shadow="lg"
              hover
              className="cursor-pointer transition-transform hover:-translate-y-1"
              onClick={() => setSelectedSession(s)}
              data-testid={`session-card-${s.id}`}
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xl font-black uppercase">{s.title}</h3>
                <BrutalBadge variant={statusColors[s.status]} size="sm">{s.status}</BrutalBadge>
              </div>
              <div className="grid grid-cols-2 gap-3 border-t-4 border-black pt-3">
                <div className="flex items-center gap-2">
                  <Hash size={14} className="text-gray-500" />
                  <span className="font-mono font-bold">{s.session_code}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users size={14} className="text-gray-500" />
                  <span className="font-bold">{s.participating_students?.length || 0} students</span>
                </div>
                <div className="flex items-center gap-2 col-span-2">
                  <Clock size={14} className="text-gray-500" />
                  <span className="text-sm font-medium text-gray-500">{new Date(s.created_date).toLocaleDateString()}</span>
                </div>
              </div>
            </BrutalCard>
          ))}
        </div>
      )}

      {/* Create Session Dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-lg border-4 border-black">
          <DialogHeader>
            <DialogTitle className="text-2xl font-black uppercase">New Classroom Session</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreate} className="space-y-4">
            <BrutalInput
              label="Session Title"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., Week 3 Vocabulary Review"
              data-testid="session-title-input"
            />
            <BrutalInput
              label="Description (optional)"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of the session"
              data-testid="session-description-input"
            />
            {wordBanks.length > 0 && (
              <div>
                <p className="font-bold text-sm uppercase mb-2">Assign Word Banks (optional)</p>
                <div className="max-h-40 overflow-y-auto space-y-1 border-2 border-black p-2">
                  {wordBanks.map((wb) => (
                    <label key={wb.id} className="flex items-center gap-2 cursor-pointer p-1 hover:bg-gray-50">
                      <input
                        type="checkbox"
                        checked={formData.bank_ids.includes(wb.id)}
                        onChange={() => toggleBank(wb.id)}
                        className="w-4 h-4"
                      />
                      <span className="font-medium">{wb.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
            <div className="flex gap-2 pt-2">
              <BrutalButton type="submit" variant="emerald" fullWidth disabled={createMutation.isPending} data-testid="create-session-submit">
                {createMutation.isPending ? 'Creating...' : 'Create Session'}
              </BrutalButton>
              <BrutalButton type="button" variant="default" fullWidth onClick={() => setShowCreate(false)}>
                Cancel
              </BrutalButton>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SessionsTab;
