import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { narrativeAPI } from '@/lib/api';
import { BrutalButton, BrutalInput, BrutalCard, BrutalBadge } from '@/components/brutal';
import { X, Sparkles, BookOpen } from 'lucide-react';
import { toast } from 'sonner';

const StoryGenerationDialog = ({ isOpen, onClose, student }) => {
  const queryClient = useQueryClient();
  const [storyPrompt, setStoryPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const generateMutation = useMutation({
    mutationFn: (data) => narrativeAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['student-narratives']);
      toast.success('Story generated successfully! 🎉');
      onClose();
      setStoryPrompt('');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to generate story');
      setIsGenerating(false);
    }
  });

  const handleGenerate = async (e) => {
    e.preventDefault();
    
    if (!storyPrompt.trim()) {
      toast.error('Please enter a story idea');
      return;
    }

    setIsGenerating(true);
    
    generateMutation.mutate({
      student_id: student.id,
      prompt: storyPrompt,
      bank_ids: student.assigned_banks || []
    });
  };

  const suggestedPrompts = [
    "A space adventure to explore distant planets",
    "A detective solving a mysterious case",
    "An underwater journey discovering sea creatures",
    "A time travel adventure to ancient civilizations",
    "A journey through a magical forest"
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70">
      <div className="w-full max-w-2xl bg-white border-4 border-black brutal-shadow-xl flex flex-col" style={{ maxHeight: '90vh' }}>
        {/* Fixed Header */}
        <div className="flex items-start justify-between p-6 pb-4 border-b-4 border-black shrink-0">
          <div className="flex items-center gap-3">
            <Sparkles size={32} className="text-indigo-600" />
            <h2 className="text-2xl font-black uppercase">Generate Your Story</h2>
          </div>
          <button
            onClick={onClose}
            disabled={isGenerating}
            className="p-2 hover:bg-gray-100 border-4 border-black brutal-active"
            data-testid="story-dialog-close"
          >
            <X size={24} />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="overflow-y-auto flex-1 p-6 space-y-4">
          {/* Student Info */}
          <div className="bg-indigo-50 border-4 border-black p-4">
            <p className="font-bold text-sm uppercase mb-1">Story personalized for: <span className="text-lg">{student.full_name}</span></p>
            <div className="flex flex-wrap gap-1 mt-2">
              {student.interests?.map((interest, idx) => (
                <BrutalBadge key={idx} variant="indigo" size="sm">{interest}</BrutalBadge>
              ))}
              {student.virtues?.map((virtue, idx) => (
                <BrutalBadge key={idx} variant="emerald" size="sm">{virtue}</BrutalBadge>
              ))}
            </div>
          </div>

          {/* Word Banks Count */}
          {student.assigned_banks?.length > 0 && (
            <p className="font-bold text-sm text-emerald-700">
              Using vocabulary from {student.assigned_banks.length} word bank(s)
            </p>
          )}

          {/* Story Prompt Input */}
          <div>
            <label className="block mb-2 font-bold uppercase text-sm">What kind of story do you want?</label>
            <textarea
              value={storyPrompt}
              onChange={(e) => setStoryPrompt(e.target.value)}
              placeholder="Describe your story idea..."
              rows={3}
              disabled={isGenerating}
              className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-indigo-500 resize-none"
              required
              data-testid="story-prompt-input"
            />
          </div>

          {/* Suggested Prompts - Compact */}
          <div>
            <p className="font-bold text-xs uppercase mb-2">Quick ideas:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedPrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setStoryPrompt(prompt)}
                  disabled={isGenerating}
                  className="px-3 py-1.5 border-2 border-black bg-white hover:bg-indigo-50 font-medium transition-colors text-xs"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {isGenerating && (
            <div className="bg-yellow-100 border-4 border-black p-4 text-center">
              <p className="font-bold">AI is creating your story... This may take 30-60 seconds!</p>
            </div>
          )}
        </div>

        {/* Fixed Footer Buttons */}
        <div className="p-6 pt-4 border-t-4 border-black shrink-0 flex gap-4">
          <BrutalButton
            type="button"
            variant="indigo"
            size="lg"
            fullWidth
            disabled={isGenerating || !storyPrompt.trim()}
            onClick={handleGenerate}
            className="flex items-center justify-center gap-2"
            data-testid="generate-story-btn"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin">...</div>
                Generating...
              </>
            ) : (
              <>
                <Sparkles size={20} />
                Generate Story
              </>
            )}
          </BrutalButton>
          <BrutalButton
            type="button"
            variant="default"
            size="lg"
            onClick={onClose}
            disabled={isGenerating}
          >
            Cancel
          </BrutalButton>
        </div>
      </div>
    </div>
  );
};

export default StoryGenerationDialog;
