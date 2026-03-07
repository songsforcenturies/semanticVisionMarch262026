import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { studentAPI } from '@/lib/api';
import { BrutalButton, BrutalInput, BrutalCard } from '@/components/brutal';
import { Dialog } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { X } from 'lucide-react';

const GRADE_LEVELS = [
  { value: 'pre-k', label: 'Pre-K' },
  { value: 'k', label: 'Kindergarten' },
  { value: '1-12', label: 'Grades 1-12' },
  { value: 'college', label: 'College' },
  { value: 'adult', label: 'Adult' }
];

const StudentFormDialog = ({ isOpen, onClose, student, guardianId }) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    full_name: '',
    age: '',
    grade_level: '',
    interests: ''
  });

  useEffect(() => {
    if (student) {
      setFormData({
        full_name: student.full_name || '',
        age: student.age?.toString() || '',
        grade_level: student.grade_level || '',
        interests: student.interests?.join(', ') || ''
      });
    } else {
      setFormData({
        full_name: '',
        age: '',
        grade_level: '',
        interests: ''
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

    const submitData = {
      full_name: formData.full_name,
      age: formData.age ? parseInt(formData.age) : null,
      grade_level: formData.grade_level || null,
      interests: interestsArray,
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

  const isLoading = createMutation.isPending || updateMutation.isPending;

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

          {student && (
            <BrutalCard variant="amber" className="bg-yellow-100">
              <p className="font-bold text-sm uppercase mb-1">Current PIN</p>
              <p className="text-2xl font-black font-mono tracking-wider">{student.access_pin}</p>
              <p className="text-sm font-medium mt-2">PIN cannot be changed</p>
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
