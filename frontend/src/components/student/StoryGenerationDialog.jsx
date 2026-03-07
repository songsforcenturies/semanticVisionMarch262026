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
      <BrutalCard shadow="xl" className="w-full max-w-2xl bg-white">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-3">
            <Sparkles size={32} className="text-indigo-600" />
            <h2 className="text-3xl font-black uppercase">Generate Your Story</h2>
          </div>
          <button
            onClick={onClose}
            disabled={isGenerating}
            className="p-2 hover:bg-gray-100 border-4 border-black brutal-active"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleGenerate} className="space-y-6">
          {/* Student Info */}
          <BrutalCard variant="indigo" className="bg-indigo-50">
            <p className="font-bold text-sm uppercase mb-2">Story will be personalized for:</p>
            <p className="text-xl font-black mb-2">{student.full_name}</p>
            {student.interests && student.interests.length > 0 && (
              <div className="mb-2">
                <p className="font-bold text-xs uppercase mb-1">Your Interests:</p>
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
                <p className="font-bold text-xs uppercase mb-1">✨ Life Lessons You'll Learn:</p>
                <div className="flex flex-wrap gap-1">
                  {student.virtues.map((virtue, idx) => (
                    <BrutalBadge key={idx} variant="emerald" size="sm">
                      {virtue}
                    </BrutalBadge>
                  ))}
                </div>
              </div>
            )}
          </BrutalCard>

          {/* Word Banks */}
          {student.assigned_banks && student.assigned_banks.length > 0 && (
            <BrutalCard className="bg-emerald-50 border-emerald-500">
              <p className="font-bold text-sm uppercase mb-2">
                Using vocabulary from {student.assigned_banks.length} word bank(s)
              </p>
              <p className="text-xs font-medium text-gray-600">
                Your story will include words to help you learn!
              </p>
            </BrutalCard>
          )}

          {/* Story Prompt Input */}
          <div>
            <label className="block mb-3 font-bold uppercase text-sm">
              What kind of story do you want? ✨
            </label>
            <textarea
              value={storyPrompt}
              onChange={(e) => setStoryPrompt(e.target.value)}
              placeholder="Describe your story idea... (e.g., 'A space adventure where I discover a new planet')"
              rows={4}
              disabled={isGenerating}
              className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-indigo-500 resize-none"
              required
            />
          </div>

          {/* Suggested Prompts */}
          <div>
            <p className="font-bold text-sm uppercase mb-2">Need ideas? Try these:</p>
            <div className="grid grid-cols-1 gap-2">
              {suggestedPrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setStoryPrompt(prompt)}
                  disabled={isGenerating}
                  className="text-left p-3 border-4 border-black bg-white hover:bg-indigo-50 font-medium transition-colors brutal-active text-sm"
                >
                  💡 {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Info Box */}
          <BrutalCard className="bg-amber-50 border-amber-500">
            <p className="font-bold text-sm mb-2">📚 Your story will have:</p>
            <ul className="space-y-1 text-sm font-medium">
              <li>✅ 5 exciting chapters</li>
              <li>✅ Vocabulary words to learn</li>
              <li>✅ Questions to test your understanding</li>
              {student.virtues && student.virtues.length > 0 && (
                <li>✨ Life lessons about {student.virtues.slice(0, 2).join(' and ')}</li>
              )}
              <li>✅ A personalized adventure just for you!</li>
            </ul>
          </BrutalCard>

          {/* Generate Button */}
          <div className="flex gap-4">
            <BrutalButton
              type="submit"
              variant="indigo"
              size="lg"
              fullWidth
              disabled={isGenerating}
              className="flex items-center justify-center gap-2"
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin">⏳</div>
                  Generating Your Story...
                </>
              ) : (
                <>
                  <Sparkles size={24} />
                  Generate Story
                </>
              )}
            </BrutalButton>
            
            <BrutalButton
              type="button"
              variant="ghost"
              size="lg"
              onClick={onClose}
              disabled={isGenerating}
            >
              Cancel
            </BrutalButton>
          </div>

          {isGenerating && (
            <BrutalCard variant="amber" className="bg-yellow-100">
              <p className="font-bold text-center">
                ⚡ AI is creating your personalized story... This may take 30-60 seconds!
              </p>
            </BrutalCard>
          )}
        </form>
      </BrutalCard>
    </div>
  );
};

export default StoryGenerationDialog;
