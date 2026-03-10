import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { studentAPI, subscriptionAPI, adPreferencesAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalProgress } from '@/components/brutal';
import { Plus, Edit, Trash2, Copy, Check, BookOpen, RefreshCw, Type, SpellCheck, Megaphone } from 'lucide-react';
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
                <h3 className="text-2xl font-black uppercase mb-2">{student.full_name}</h3>
                
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
