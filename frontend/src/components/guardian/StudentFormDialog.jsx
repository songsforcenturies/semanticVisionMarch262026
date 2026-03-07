import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { studentAPI, subscriptionAPI, wordBankAPI } from '@/lib/api';
import { BrutalButton, BrutalInput, BrutalCard, BrutalBadge } from '@/components/brutal';
import { Dialog } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { X, Check } from 'lucide-react';

const GRADE_LEVELS = [
  { value: 'pre-k', label: 'Pre-K' },
  { value: 'k', label: 'Kindergarten' },
  { value: '1-12', label: 'Grades 1-12' },
  { value: 'college', label: 'College' },
  { value: 'adult', label: 'Adult' }
];

const StudentFormDialog = ({ isOpen, onClose, student, guardianId, focusOnBanks = false }) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    full_name: '',
    age: '',
    grade_level: '',
    interests: '',
    virtues: '',
    assigned_banks: []
  });

  // Fetch subscription to get available word banks
  const { data: subscription } = useQuery({
    queryKey: ['subscription', guardianId],
    queryFn: async () => {
      const response = await subscriptionAPI.get(guardianId);
      return response.data;
    },
    enabled: !!guardianId && isOpen
  });

  // Fetch word bank details for owned banks
  const { data: availableBanks = [] } = useQuery({
    queryKey: ['available-banks'],
    queryFn: async () => {
      const response = await wordBankAPI.getAll({});
      return response.data;
    },
    enabled: isOpen
  });

  useEffect(() => {
    if (student) {
      setFormData({
        full_name: student.full_name || '',
        age: student.age?.toString() || '',
        grade_level: student.grade_level || '',
        interests: student.interests?.join(', ') || '',
        virtues: student.virtues?.join(', ') || '',
        assigned_banks: student.assigned_banks || []
      });
    } else {
      setFormData({
        full_name: '',
        age: '',
        grade_level: '',
        interests: '',
        virtues: '',
        assigned_banks: []
      });
    }
  }, [student, isOpen]);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data) => studentAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['students']);
      queryClient.invalidateQueries(['subscription']);
      toast.success('Student created successfully!');
      onClose();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create student');
    }
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => studentAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['students']);
      toast.success('Student updated successfully!');
      onClose();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update student');
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    // Process interests
    const interestsArray = formData.interests
      .split(',')
      .map(i => i.trim())
      .filter(i => i.length > 0);

    // Process virtues
    const virtuesArray = formData.virtues
      .split(',')
      .map(v => v.trim())
      .filter(v => v.length > 0);

    const submitData = {
      full_name: formData.full_name,
      age: formData.age ? parseInt(formData.age) : null,
      grade_level: formData.grade_level || null,
      interests: interestsArray,
      virtues: virtuesArray,
      guardian_id: guardianId
    };

    if (student) {
      // Update existing student
      const { guardian_id, ...updateData } = submitData;
      updateMutation.mutate({ id: student.id, data: updateData });
    } else {
      // Create new student
      createMutation.mutate(submitData);
    }
  };

  // Assign banks mutation (separate from create/update)
  const assignBanksMutation = useMutation({
    mutationFn: ({ studentId, bankIds }) => wordBankAPI.assignToStudent(studentId, bankIds),
    onSuccess: () => {
      queryClient.invalidateQueries(['students']);
      toast.success('Word banks assigned successfully!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to assign word banks');
    }
  });

  const handleBankToggle = (bankId) => {
    setFormData(prev => {
      const current = prev.assigned_banks || [];
      const newBanks = current.includes(bankId)
        ? current.filter(id => id !== bankId)
        : [...current, bankId];
      return { ...prev, assigned_banks: newBanks };
    });
  };

  const handleSaveBanks = () => {
    if (student) {
      assignBanksMutation.mutate({
        studentId: student.id,
        bankIds: formData.assigned_banks
      });
    }
  };

  const ownedBankIds = subscription?.bank_access || [];
  const ownedBanks = availableBanks.filter(bank => 
    ownedBankIds.includes(bank.id) || bank.visibility === 'global'
  );

  const isLoading = createMutation.isPending || updateMutation.isPending || assignBanksMutation.isPending;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <BrutalCard shadow="xl" className="w-full max-w-2xl bg-white max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-black uppercase">
            {student ? 'Edit Student' : 'Add New Student'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 border-4 border-black brutal-active"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <BrutalInput
            label="Full Name *"
            type="text"
            required
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            placeholder="John Doe"
          />

          <div className="grid md:grid-cols-2 gap-6">
            <BrutalInput
              label="Age"
              type="number"
              min="3"
              max="100"
              value={formData.age}
              onChange={(e) => setFormData({ ...formData, age: e.target.value })}
              placeholder="10"
            />

            <div>
              <label className="block mb-2 font-bold uppercase text-sm">
                Grade Level
              </label>
              <select
                value={formData.grade_level}
                onChange={(e) => setFormData({ ...formData, grade_level: e.target.value })}
                className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-indigo-500 bg-white"
              >
                <option value="">Select grade...</option>
                {GRADE_LEVELS.map((grade) => (
                  <option key={grade.value} value={grade.value}>
                    {grade.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block mb-2 font-bold uppercase text-sm">
              Interests (comma-separated)
            </label>
            <textarea
              value={formData.interests}
              onChange={(e) => setFormData({ ...formData, interests: e.target.value })}
              placeholder="space, dinosaurs, robots, science"
              rows={3}
              className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-indigo-500 resize-none"
            />
            <p className="mt-1 text-sm font-medium text-gray-600">
              These will be used to personalize AI-generated stories
            </p>
          </div>

          <div>
            <label className="block mb-2 font-bold uppercase text-sm">
              ✨ Virtues & Life Lessons (comma-separated)
            </label>
            <textarea
              value={formData.virtues}
              onChange={(e) => setFormData({ ...formData, virtues: e.target.value })}
              placeholder="patience, kindness, honesty, courage, responsibility"
              rows={3}
              className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-emerald-500 resize-none"
            />
            <p className="mt-1 text-sm font-medium text-emerald-700">
              💡 Stories will teach these character traits and life lessons to your child
            </p>
            <p className="mt-1 text-xs font-medium text-gray-600">
              Examples: Patience, Kindness, Honesty, Courage, Responsibility, Perseverance, Gratitude, Justice, Compassion, Respect, Empathy, Self-discipline
            </p>
          </div>

          {student && (
            <BrutalCard variant="amber" className="bg-yellow-100">
              <p className="font-bold text-sm uppercase mb-3">Student Login Credentials</p>
              <div className="space-y-3">
                <div>
                  <p className="text-xs font-bold uppercase text-gray-600 mb-1">Student Code</p>
                  <p className="text-xl font-black font-mono tracking-wider">{student.student_code}</p>
                </div>
                <div>
                  <p className="text-xs font-bold uppercase text-gray-600 mb-1">9-Digit PIN</p>
                  <p className="text-xl font-black font-mono tracking-wider">{student.access_pin}</p>
                </div>
              </div>
              <p className="text-sm font-medium mt-3 text-amber-800">
                ⚠️ Both codes are required to login and cannot be changed
              </p>
            </BrutalCard>
          )}

          {/* Word Bank Assignment */}
          {student && ownedBanks.length > 0 && (
            <div className={focusOnBanks ? 'border-4 border-emerald-500 p-4 bg-emerald-50' : ''}>
              <label className="block mb-3 font-bold uppercase text-sm">
                {focusOnBanks && '✨ '}Assign Word Banks ({formData.assigned_banks.length} selected)
              </label>
              {focusOnBanks && (
                <p className="mb-3 text-sm font-medium text-emerald-700">
                  Select which word banks this student can use to generate stories:
                </p>
              )}
              <div className="space-y-2 max-h-48 overflow-y-auto border-4 border-black p-4 bg-gray-50">
                {ownedBanks.map((bank) => {
                  const isSelected = formData.assigned_banks.includes(bank.id);
                  return (
                    <label
                      key={bank.id}
                      className={`flex items-center gap-3 p-3 border-4 border-black cursor-pointer transition-colors ${
                        isSelected ? 'bg-emerald-200' : 'bg-white hover:bg-gray-100'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleBankToggle(bank.id)}
                        className="w-6 h-6 border-4 border-black"
                      />
                      <div className="flex-1">
                        <p className="font-black text-sm">{bank.name}</p>
                        <p className="text-xs font-medium text-gray-600">
                          {bank.total_tokens} words • {bank.specialty || bank.category}
                        </p>
                      </div>
                      {isSelected && (
                        <Check size={20} className="text-emerald-600" />
                      )}
                    </label>
                  );
                })}
              </div>
              {student && (
                <BrutalButton
                  type="button"
                  variant="emerald"
                  size="md"
                  fullWidth
                  onClick={handleSaveBanks}
                  disabled={assignBanksMutation.isPending}
                  className="mt-3"
                >
                  {assignBanksMutation.isPending ? 'Saving...' : '💾 Save Bank Assignments'}
                </BrutalButton>
              )}
            </div>
          )}

          {ownedBanks.length === 0 && student && (
            <BrutalCard className="bg-amber-50 border-amber-500">
              <p className="font-medium text-sm">
                💡 No word banks available. Visit the Marketplace tab to add word banks to your library!
              </p>
            </BrutalCard>
          )}

          <div className="flex gap-4">
            <BrutalButton
              type="submit"
              variant="emerald"
              fullWidth
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : student ? 'Update Student' : 'Create Student'}
            </BrutalButton>
            <BrutalButton
              type="button"
              variant="ghost"
              fullWidth
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </BrutalButton>
          </div>
        </form>
      </BrutalCard>
    </div>
  );
};

export default StudentFormDialog;
