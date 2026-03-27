import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { studentAPI, subscriptionAPI, adPreferencesAPI, narrativeAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalProgress } from '@/components/brutal';
import { Plus, Edit, Trash2, Copy, Check, BookOpen, RefreshCw, Type, SpellCheck, Megaphone, User, Camera, Sparkles, X } from 'lucide-react';
import { toast } from 'sonner';
import StudentFormDialog from './StudentFormDialog';
import DeleteConfirmDialog from './DeleteConfirmDialog';
import ParentalControlsPanel from './ParentalControlsPanel';

const StudentsTab = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  const [deletingStudent, setDeletingStudent] = useState(null);
  const [copiedPin, setCopiedPin] = useState(null);
  const [assigningBanksStudent, setAssigningBanksStudent] = useState(null);
  const [resettingPin, setResettingPin] = useState(null);
  const [changingPin, setChangingPin] = useState(null);
  const [pinForm, setPinForm] = useState({ current_pin: '', new_pin: '', confirm_pin: '' });
  const [storyDialogOpen, setStoryDialogOpen] = useState(false);
  const [selectedStudentIds, setSelectedStudentIds] = useState([]);
  const [storyPrompt, setStoryPrompt] = useState('');
  const [storyGenerating, setStoryGenerating] = useState(false);
  const [storyProgress, setStoryProgress] = useState('');

  // Fetch students
  const { data: students = [], isLoading: studentsLoading } = useQuery({
    queryKey: ['students', user?.id],
    queryFn: async () => {
      const response = await studentAPI.getAll(user?.id);
      return response.data;
    },
    enabled: !!user?.id
  });

  // Fetch subscription
  const { data: subscription } = useQuery({
    queryKey: ['subscription', user?.id],
    queryFn: async () => {
      const response = await subscriptionAPI.get(user?.id);
      return response.data;
    },
    enabled: !!user?.id
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (studentId) => studentAPI.delete(studentId),
    onSuccess: () => {
      queryClient.invalidateQueries(['students']);
      queryClient.invalidateQueries(['subscription']);
      toast.success('Student deleted successfully');
      setDeletingStudent(null);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to delete student');
    }
  });

  // Reset PIN mutation
  const resetPinMutation = useMutation({
    mutationFn: (studentId) => studentAPI.resetPin(studentId),
    onSuccess: (response, studentId) => {
      queryClient.invalidateQueries(['students']);
      const newPin = response.data.new_pin;
      toast.success(`PIN reset! New PIN: ${newPin}`);
      setResettingPin(null);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to reset PIN');
      setResettingPin(null);
    }
  });

  // Spellcheck toggle mutation
  const changePinMutation = useMutation({
    mutationFn: ({ studentId, data }) => studentAPI.changePin(studentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['students']);
      toast.success('PIN changed successfully!');
      setChangingPin(null);
      setPinForm({ current_pin: '', new_pin: '', confirm_pin: '' });
    },
    onError: (error) => toast.error(error.response?.data?.detail || 'Failed to change PIN'),
  });

  const handleChangePin = (studentId) => {
    if (pinForm.new_pin !== pinForm.confirm_pin) {
      toast.error('New PINs do not match');
      return;
    }
    changePinMutation.mutate({ studentId, data: { current_pin: pinForm.current_pin, new_pin: pinForm.new_pin } });
  };

  // Spellcheck toggle mutation (original)
  const spellcheckMutation = useMutation({
    mutationFn: (studentId) => studentAPI.toggleSpellcheck(studentId),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['students'] });
      toast.success(`Spellcheck ${response.data.spellcheck_disabled ? 'disabled' : 'enabled'}`);
    },
  });

  // Spelling mode toggle mutation
  const spellingModeMutation = useMutation({
    mutationFn: (studentId) => studentAPI.toggleSpellingMode(studentId),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['students'] });
      toast.success(`Spelling mode: ${response.data.spelling_mode}`);
    },
  });

  // Ad preferences toggle
  const adPrefMutation = useMutation({
    mutationFn: ({ studentId, prefs }) => adPreferencesAPI.update(studentId, prefs),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] });
      toast.success('Brand story preferences updated');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  const handleEdit = (student) => {
    setEditingStudent(student);
    setIsFormOpen(true);
  };

  const handleAssignBanks = (student) => {
    setEditingStudent(student);
    setAssigningBanksStudent(student);
    setIsFormOpen(true);
  };

  const handleDelete = (student) => {
    setDeletingStudent(student);
  };

  const handleCopyPin = (pin, studentName) => {
    navigator.clipboard.writeText(pin);
    setCopiedPin(pin);
    toast.success(`PIN copied for ${studentName}`);
    setTimeout(() => setCopiedPin(null), 2000);
  };

  const handleAddStudent = () => {
    setEditingStudent(null);
    setIsFormOpen(true);
  };

  const quickIdeas = [
    'An adventure in space',
    'A mystery at the beach',
    'A trip to the rainforest',
    'A day as a superhero',
    'A magical cooking contest',
    'An underwater treasure hunt',
  ];

  const handleOpenStoryDialog = (preselectedStudentId = null) => {
    if (preselectedStudentId) {
      setSelectedStudentIds([preselectedStudentId]);
    } else {
      setSelectedStudentIds([]);
    }
    setStoryPrompt('');
    setStoryProgress('');
    setStoryDialogOpen(true);
  };

  const handleToggleStudent = (studentId) => {
    setSelectedStudentIds((prev) =>
      prev.includes(studentId) ? prev.filter((id) => id !== studentId) : [...prev, studentId]
    );
  };

  const handleSelectAll = () => {
    if (selectedStudentIds.length === students.length) {
      setSelectedStudentIds([]);
    } else {
      setSelectedStudentIds(students.map((s) => s.id));
    }
  };

  const handleGenerateStories = async () => {
    if (selectedStudentIds.length === 0) {
      toast.error('Please select at least one student');
      return;
    }
    if (!storyPrompt.trim()) {
      toast.error('Please enter a story prompt');
      return;
    }
    setStoryGenerating(true);
    try {
      // Show progress for each student
      for (let i = 0; i < selectedStudentIds.length; i++) {
        const s = students.find((st) => st.id === selectedStudentIds[i]);
        setStoryProgress(`Generating for ${s?.full_name || 'student'}... (${i + 1}/${selectedStudentIds.length})`);
      }
      const response = await narrativeAPI.createBatch({
        student_ids: selectedStudentIds,
        prompt: storyPrompt.trim(),
        bank_ids: [],
      });
      const data = response.data;
      if (data.generated > 0) {
        toast.success(`Stories generated for ${data.generated} student${data.generated > 1 ? 's' : ''}!`);
      }
      if (data.failed > 0) {
        const failedNames = data.results.filter((r) => r.status === 'failed').map((r) => r.student_name).join(', ');
        toast.error(`Failed for: ${failedNames}`);
      }
      setStoryDialogOpen(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Story generation failed');
    } finally {
      setStoryGenerating(false);
      setStoryProgress('');
    }
  };

  const canAddMore = subscription && subscription.active_students < subscription.student_seats;

  if (studentsLoading) {
    return <div className="text-center py-12 text-2xl font-bold">Loading students...</div>;
  }

  return (
    <div className="space-y-8">
      {/* Subscription Info */}
      {subscription && (
        <BrutalCard variant="indigo" shadow="xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-3xl font-black uppercase mb-2">Subscription</h2>
              <p className="text-xl font-bold capitalize">{subscription.plan} Plan</p>
            </div>
            <BrutalBadge variant="indigo" size="lg">
              {subscription.status}
            </BrutalBadge>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <p className="font-bold uppercase text-sm mb-2">Student Seats</p>
              <BrutalProgress
                value={subscription.active_students}
                max={subscription.student_seats}
                variant="indigo"
                showLabel
                size="lg"
              />
            </div>
            <div>
              <p className="font-bold uppercase text-sm mb-2">Word Banks Purchased</p>
              <div className="text-4xl font-black">{subscription.bank_access?.length || 0}</div>
            </div>
          </div>
        </BrutalCard>
      )}

      {/* Add Student Button */}
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-black uppercase">Your Students</h2>
        <div className="flex items-center gap-3">
          {students.length > 0 && (
            <BrutalButton
              variant="indigo"
              size="lg"
              onClick={() => handleOpenStoryDialog()}
              className="flex items-center gap-2"
            >
              <Sparkles size={24} />
              Generate Story for Students
            </BrutalButton>
          )}
          <BrutalButton
            variant="emerald"
            size="lg"
            onClick={handleAddStudent}
            disabled={!canAddMore}
            className="flex items-center gap-2"
          >
            <Plus size={24} />
            Add Student
          </BrutalButton>
        </div>
      </div>

      {!canAddMore && subscription && (
        <BrutalCard variant="amber">
          <p className="font-bold text-lg">
            ⚠️ You've reached your student seat limit ({subscription.student_seats}). 
            Upgrade your plan to add more students.
          </p>
        </BrutalCard>
      )}

      {/* Students Grid */}
      {students.length === 0 ? (
        <BrutalCard shadow="xl" className="text-center py-12">
          <p className="text-2xl font-bold mb-4">No students yet</p>
          <p className="text-lg font-medium mb-6">Add your first student to get started!</p>
          <BrutalButton
            variant="indigo"
            size="lg"
            onClick={handleAddStudent}
            disabled={!canAddMore}
            className="flex items-center gap-2 mx-auto"
          >
            <Plus size={24} />
            Add Your First Student
          </BrutalButton>
        </BrutalCard>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {students.map((student) => (
            <BrutalCard
              key={student.id}
              shadow="lg"
              hover
              className="relative"
            >
              {/* Student Info */}
              <div className="mb-4">
                <div className="flex items-center gap-4 mb-3">
                  <div className="w-16 h-16 rounded-full overflow-hidden flex-shrink-0 flex items-center justify-center border-4 border-indigo-200" style={{ background: '#e8e5ff' }}>
                    {student.photo_url ? (
                      <img src={student.photo_url} alt={student.full_name} className="w-full h-full object-cover" />
                    ) : (
                      <User size={28} className="text-indigo-400" />
                    )}
                  </div>
                  <div>
                    <h3 className="text-2xl font-black uppercase">{student.full_name}</h3>
                    {!student.photo_url && (
                      <label className="inline-flex items-center gap-1 text-[10px] font-bold text-purple-600 cursor-pointer hover:text-purple-800">
                        <Camera size={10} /> Add photo
                        <input type="file" accept="image/*" className="hidden" onChange={async (e) => {
                          const file = e.target.files?.[0];
                          if (!file) return;
                          try {
                            await studentAPI.uploadPhoto(student.id, file);
                            queryClient.invalidateQueries(['students']);
                            toast.success('Photo uploaded!');
                          } catch (err) { toast.error('Upload failed'); }
                          e.target.value = '';
                        }} />
                      </label>
                    )}
                  </div>
                </div>
                
                {/* Student Code & PIN Display */}
                <div className="space-y-2 mb-3">
                  <div>
                    <p className="font-bold text-xs uppercase text-gray-600">Student Code</p>
                    <div className="flex items-center gap-2">
                      <div className="bg-indigo-100 border-4 border-black px-4 py-2 font-mono text-lg font-black tracking-wider" style={{ color: '#1e1b4b' }}>
                        {student.student_code}
                      </div>
                      <BrutalButton
                        variant="indigo"
                        size="sm"
                        onClick={() => handleCopyPin(student.student_code, student.full_name)}
                        className="flex items-center gap-1"
                      >
                        {copiedPin === student.student_code ? (
                          <Check size={16} />
                        ) : (
                          <Copy size={16} />
                        )}
                      </BrutalButton>
                    </div>
                  </div>
                  
                  <div>
                    <p className="font-bold text-xs uppercase text-gray-600" data-testid="pin-label">PIN</p>
                    <div className="flex items-center gap-2">
                      <div className="bg-yellow-100 border-4 border-black px-4 py-2 font-mono text-lg font-black tracking-wider" style={{ color: '#78350f' }}>
                        {student.access_pin}
                      </div>
                      <BrutalButton
                        variant="amber"
                        size="sm"
                        onClick={() => handleCopyPin(student.access_pin, student.full_name)}
                        className="flex items-center gap-1"
                      >
                        {copiedPin === student.access_pin ? (
                          <Check size={16} />
                        ) : (
                          <Copy size={16} />
                        )}
                      </BrutalButton>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-1">
                    <BrutalButton variant="amber" size="sm"
                      onClick={() => { setChangingPin(changingPin === student.id ? null : student.id); setPinForm({ current_pin: '', new_pin: '', confirm_pin: '' }); }}
                      className="text-xs" data-testid={`change-pin-btn-${student.id}`}>
                      {changingPin === student.id ? 'Cancel' : 'Change PIN'}
                    </BrutalButton>
                  </div>
                  {changingPin === student.id && (
                    <div className="mt-2 p-3 bg-yellow-50 border-4 border-black space-y-2" data-testid={`change-pin-form-${student.id}`}>
                      <input type="password" placeholder="Current PIN" value={pinForm.current_pin}
                        onChange={(e) => setPinForm({ ...pinForm, current_pin: e.target.value })}
                        className="w-full border-2 border-black px-3 py-2 font-mono text-sm" />
                      <input type="password" placeholder="New PIN (4-10 digits)" value={pinForm.new_pin}
                        onChange={(e) => setPinForm({ ...pinForm, new_pin: e.target.value })}
                        className="w-full border-2 border-black px-3 py-2 font-mono text-sm" />
                      <input type="password" placeholder="Confirm New PIN" value={pinForm.confirm_pin}
                        onChange={(e) => setPinForm({ ...pinForm, confirm_pin: e.target.value })}
                        className="w-full border-2 border-black px-3 py-2 font-mono text-sm" />
                      <BrutalButton variant="indigo" size="sm" fullWidth
                        onClick={() => handleChangePin(student.id)}
                        disabled={changePinMutation.isPending}
                        data-testid={`submit-change-pin-${student.id}`}>
                        {changePinMutation.isPending ? 'Changing...' : 'Save New PIN'}
                      </BrutalButton>
                    </div>
                  )}
                </div>

              {/* Details */}
              <div className="space-y-2">
                  {student.age && (
                    <p className="font-medium">
                      <span className="font-bold">Age:</span> {student.age} years
                    </p>
                  )}
                  {student.grade_level && (
                    <p className="font-medium">
                      <span className="font-bold">Grade:</span> {student.grade_level}
                    </p>
                  )}
                  {student.interests && student.interests.length > 0 && (
                    <div>
                      <p className="font-bold mb-1">Interests:</p>
                      <div className="flex flex-wrap gap-1">
                        {student.interests.map((interest, idx) => (
                          <BrutalBadge key={idx} variant="indigo" size="sm">
                            {interest}
                          </BrutalBadge>
                        ))}
                      </div>
                    </div>
                  )}
                  {student.virtues && student.virtues.length > 0 && (
                    <div>
                      <p className="font-bold mb-1">Learning:</p>
                      <div className="flex flex-wrap gap-1">
                        {student.virtues.map((virtue, idx) => (
                          <BrutalBadge key={idx} variant="emerald" size="sm">
                            ✨ {virtue}
                          </BrutalBadge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Stats */}
              <div className="border-t-4 border-black pt-4 mb-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs font-bold uppercase text-gray-600">Mastered</p>
                    <p className="text-2xl font-black">{student.mastered_tokens?.length || 0}</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold uppercase text-gray-600">Word Banks</p>
                    <p className="text-2xl font-black">{student.assigned_banks?.length || 0}</p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-2">
                <div className="flex gap-2">
                  <BrutalButton
                    variant="indigo"
                    size="sm"
                    fullWidth
                    onClick={() => handleEdit(student)}
                    className="flex items-center justify-center gap-1"
                  >
                    <Edit size={16} />
                    Edit
                  </BrutalButton>
                  <BrutalButton
                    variant="rose"
                    size="sm"
                    fullWidth
                    onClick={() => handleDelete(student)}
                    className="flex items-center justify-center gap-1"
                  >
                    <Trash2 size={16} />
                    Delete
                  </BrutalButton>
                </div>
                
                <BrutalButton
                  variant="emerald"
                  size="sm"
                  fullWidth
                  onClick={() => handleAssignBanks(student)}
                  className="flex items-center justify-center gap-1"
                >
                  <BookOpen size={16} />
                  Assign Word Banks
                </BrutalButton>

                <BrutalButton
                  variant="emerald"
                  size="sm"
                  fullWidth
                  onClick={() => handleOpenStoryDialog(student.id)}
                  className="flex items-center justify-center gap-1"
                  style={{ background: '#14b8a6', borderColor: '#0d9488' }}
                >
                  <Sparkles size={16} />
                  Generate Story
                </BrutalButton>

                <BrutalButton
                  variant="amber"
                  size="sm"
                  fullWidth
                  onClick={() => {
                    setResettingPin(student.id);
                    resetPinMutation.mutate(student.id);
                  }}
                  disabled={resettingPin === student.id}
                  className="flex items-center justify-center gap-1"
                  data-testid={`reset-pin-btn-${student.id}`}
                >
                  <RefreshCw size={16} className={resettingPin === student.id ? 'animate-spin' : ''} />
                  {resettingPin === student.id ? 'Resetting...' : 'Reset PIN'}
                </BrutalButton>

                {/* Spelling Controls */}
                <div className="flex gap-2">
                  <BrutalButton
                    variant={student.spellcheck_disabled ? 'rose' : 'emerald'}
                    size="sm"
                    fullWidth
                    onClick={() => spellcheckMutation.mutate(student.id)}
                    className="flex items-center justify-center gap-1 text-xs"
                    data-testid={`spellcheck-toggle-${student.id}`}
                  >
                    <SpellCheck size={14} />
                    {student.spellcheck_disabled ? 'Spellcheck OFF' : 'Spellcheck ON'}
                  </BrutalButton>
                  <BrutalButton
                    variant={student.spelling_mode === 'exact' ? 'rose' : 'emerald'}
                    size="sm"
                    fullWidth
                    onClick={() => spellingModeMutation.mutate(student.id)}
                    className="flex items-center justify-center gap-1 text-xs"
                    data-testid={`spelling-mode-${student.id}`}
                  >
                    <Type size={14} />
                    {student.spelling_mode === 'exact' ? 'Phonetic OFF' : 'Phonetic ON'}
                  </BrutalButton>
                  <BrutalButton
                    variant={student.ad_preferences?.allow_brand_stories ? 'emerald' : 'rose'}
                    size="sm"
                    fullWidth
                    onClick={() => {
                      const current = student.ad_preferences || { allow_brand_stories: false, preferred_categories: [], blocked_categories: [] };
                      adPrefMutation.mutate({
                        studentId: student.id,
                        prefs: { ...current, allow_brand_stories: !current.allow_brand_stories },
                      });
                    }}
                    className="flex items-center justify-center gap-1 text-xs"
                    data-testid={`brand-toggle-${student.id}`}
                  >
                    <Megaphone size={14} />
                    {student.ad_preferences?.allow_brand_stories ? 'Brand Stories ON' : 'Brand Stories OFF'}
                  </BrutalButton>
                </div>

                {/* Parental Controls */}
                <ParentalControlsPanel studentId={student.id} studentName={student.full_name} />
              </div>
            </BrutalCard>
          ))}
        </div>
      )}

      {/* Story Generation Dialog */}
      {storyDialogOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white border-4 border-black p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto shadow-[8px_8px_0_0_rgba(0,0,0,1)]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-2xl font-black uppercase">Generate Story</h3>
              <button onClick={() => setStoryDialogOpen(false)} className="p-1 hover:bg-gray-100 border-2 border-black">
                <X size={20} />
              </button>
            </div>

            {/* Student Selection */}
            <div className="mb-4">
              <p className="font-bold uppercase text-sm mb-2">Select Students</p>
              <label className="flex items-center gap-2 mb-2 cursor-pointer font-bold text-sm">
                <input
                  type="checkbox"
                  checked={selectedStudentIds.length === students.length}
                  onChange={handleSelectAll}
                  className="w-5 h-5 accent-indigo-600"
                />
                Select All
              </label>
              <div className="space-y-1 max-h-40 overflow-y-auto border-2 border-black p-2">
                {students.map((s) => (
                  <label key={s.id} className="flex items-center gap-2 cursor-pointer p-1 hover:bg-indigo-50">
                    <input
                      type="checkbox"
                      checked={selectedStudentIds.includes(s.id)}
                      onChange={() => handleToggleStudent(s.id)}
                      className="w-5 h-5 accent-indigo-600"
                    />
                    <span className="font-bold">{s.full_name}</span>
                    {s.grade_level && <span className="text-xs text-gray-500">(Grade {s.grade_level})</span>}
                  </label>
                ))}
              </div>
            </div>

            {/* Story Prompt */}
            <div className="mb-4">
              <p className="font-bold uppercase text-sm mb-2">Story Prompt</p>
              <textarea
                value={storyPrompt}
                onChange={(e) => setStoryPrompt(e.target.value)}
                placeholder="Describe the story theme or idea..."
                className="w-full border-4 border-black p-3 font-medium text-sm min-h-[80px] resize-y"
              />
            </div>

            {/* Quick Ideas */}
            <div className="mb-4">
              <p className="font-bold uppercase text-xs mb-2 text-gray-600">Quick Ideas</p>
              <div className="flex flex-wrap gap-2">
                {quickIdeas.map((idea) => (
                  <button
                    key={idea}
                    onClick={() => setStoryPrompt(idea)}
                    className="text-xs font-bold px-3 py-1 border-2 border-black bg-indigo-50 hover:bg-indigo-100 transition-colors"
                  >
                    {idea}
                  </button>
                ))}
              </div>
            </div>

            {/* Progress */}
            {storyGenerating && storyProgress && (
              <div className="mb-4 p-3 bg-indigo-50 border-2 border-indigo-300 font-bold text-sm text-indigo-800">
                {storyProgress}
              </div>
            )}

            {/* Generate Button */}
            <BrutalButton
              variant="indigo"
              size="lg"
              fullWidth
              onClick={handleGenerateStories}
              disabled={storyGenerating || selectedStudentIds.length === 0 || !storyPrompt.trim()}
              className="flex items-center justify-center gap-2"
            >
              <Sparkles size={20} className={storyGenerating ? 'animate-spin' : ''} />
              {storyGenerating
                ? storyProgress || 'Generating...'
                : `Generate Story for ${selectedStudentIds.length} Student${selectedStudentIds.length !== 1 ? 's' : ''}`}
            </BrutalButton>
          </div>
        </div>
      )}

      {/* Student Form Dialog */}
      <StudentFormDialog
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingStudent(null);
          setAssigningBanksStudent(null);
        }}
        student={editingStudent}
        guardianId={user?.id}
        focusOnBanks={!!assigningBanksStudent}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        isOpen={!!deletingStudent}
        onClose={() => setDeletingStudent(null)}
        onConfirm={() => deleteMutation.mutate(deletingStudent.id)}
        title="Delete Student"
        message={`Are you sure you want to delete ${deletingStudent?.full_name}? This action cannot be undone.`}
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
};

export default StudentsTab;
