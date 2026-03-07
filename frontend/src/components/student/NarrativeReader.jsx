import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { readLogAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalProgress } from '@/components/brutal';
import { ArrowLeft, ArrowRight, Clock, BookOpen, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import VisionCheckModal from './VisionCheckModal';
import VocabularyAssessment from './VocabularyAssessment';

const NarrativeReader = ({ narrative, student, onClose }) => {
  const queryClient = useQueryClient();
  const [currentChapter, setCurrentChapter] = useState(narrative.current_chapter || 1);
  const [isReading, setIsReading] = useState(false);
  const [sessionStart, setSessionStart] = useState(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [showVisionCheck, setShowVisionCheck] = useState(false);
  const [showAssessment, setShowAssessment] = useState(false);
  const [completedChapters, setCompletedChapters] = useState(narrative.chapters_completed || []);

  const chapter = narrative.chapters[currentChapter - 1];
  const isLastChapter = currentChapter === 5;
  const isChapterCompleted = completedChapters.includes(currentChapter);
  const allChaptersCompleted = completedChapters.length === 5;

  // Timer effect
  useEffect(() => {
    let interval;
    if (isReading && sessionStart) {
      interval = setInterval(() => {
        const elapsed = Math.floor((new Date() - sessionStart) / 1000);
        setElapsedSeconds(elapsed);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isReading, sessionStart]);

  // Create read log mutation
  const createReadLogMutation = useMutation({
    mutationFn: (data) => readLogAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['student-detail']);
      queryClient.invalidateQueries(['read-logs']);
    }
  });

  const handleStartReading = () => {
    setIsReading(true);
    setSessionStart(new Date());
  };

  const handleFinishChapter = () => {
    if (!isReading || !sessionStart) {
      toast.error('Please start reading first');
      return;
    }

    setIsReading(false);
    
    // Create read log
    const sessionEnd = new Date();
    createReadLogMutation.mutate({
      student_id: student.id,
      narrative_id: narrative.id,
      chapter_number: currentChapter,
      session_start: sessionStart.toISOString(),
      session_end: sessionEnd.toISOString(),
      words_read: chapter.word_count
    });

    // Show vision check
    setShowVisionCheck(true);
  };

  const handleVisionCheckComplete = (passed) => {
    setShowVisionCheck(false);
    
    if (passed) {
      // Mark chapter as completed
      const newCompletedChapters = [...new Set([...completedChapters, currentChapter])];
      setCompletedChapters(newCompletedChapters);
      
      // Check if all chapters are now completed
      if (newCompletedChapters.length === 5) {
        toast.success('🎉 Story completed! Time for vocabulary assessment!');
        setTimeout(() => {
          setShowAssessment(true);
        }, 1500);
      } else if (!isLastChapter) {
        toast.success('Great job! Moving to next chapter...');
        setTimeout(() => {
          setCurrentChapter(prev => prev + 1);
          setElapsedSeconds(0);
          setSessionStart(null);
        }, 1000);
      }
    } else {
      toast.error('Try reading the chapter again!');
    }
  };

  const calculateWPM = () => {
    if (elapsedSeconds === 0) return 0;
    return Math.round((chapter.word_count / (elapsedSeconds / 60)));
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Show assessment if all chapters completed
  if (showAssessment) {
    return (
      <VocabularyAssessment
        narrative={narrative}
        student={student}
        onClose={onClose}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white border-b-6 border-black brutal-shadow-md sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <BrutalButton variant="ghost" onClick={onClose} className="flex items-center gap-2">
                <ArrowLeft size={20} />
                Back
              </BrutalButton>
              <div>
                <h1 className="text-2xl font-black uppercase">{narrative.title}</h1>
                <p className="text-sm font-medium text-gray-600">Chapter {currentChapter} of 5</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Timer */}
              <BrutalCard shadow="sm" className="px-4 py-2">
                <div className="flex items-center gap-2">
                  <Clock size={20} className={isReading ? 'text-emerald-600' : 'text-gray-400'} />
                  <span className="font-black text-lg">{formatTime(elapsedSeconds)}</span>
                  {elapsedSeconds > 0 && (
                    <BrutalBadge variant="emerald" size="sm">
                      {calculateWPM()} WPM
                    </BrutalBadge>
                  )}
                </div>
              </BrutalCard>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <BrutalProgress
              value={currentChapter}
              max={5}
              variant="indigo"
              showLabel
            />
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <BrutalCard shadow="xl" className="mb-6">
          {/* Chapter Header */}
          <div className="mb-6 pb-6 border-b-4 border-black">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-3xl font-black uppercase">{chapter.title}</h2>
              {isChapterCompleted && (
                <BrutalBadge variant="emerald" size="lg" className="flex items-center gap-1">
                  <CheckCircle size={18} />
                  Completed
                </BrutalBadge>
              )}
            </div>
            
            <div className="flex items-center gap-4 text-sm font-medium text-gray-600">
              <span>📖 {chapter.word_count} words</span>
              <span>•</span>
              <span>⏱️ ~{Math.ceil(chapter.word_count / 200)} min read</span>
            </div>
          </div>

          {/* Chapter Content */}
          <div className="prose prose-lg max-w-none mb-8">
            <div className="text-lg leading-relaxed whitespace-pre-wrap font-medium">
              {chapter.content}
            </div>
          </div>

          {/* Embedded Vocabulary Preview */}
          {chapter.embedded_tokens && chapter.embedded_tokens.length > 0 && (
            <BrutalCard className="bg-indigo-50 mb-6">
              <p className="font-bold text-sm uppercase mb-3">Vocabulary in this chapter:</p>
              <div className="flex flex-wrap gap-2">
                {chapter.embedded_tokens.map((token, idx) => (
                  <BrutalBadge key={idx} variant={token.tier} size="sm">
                    {token.word}
                  </BrutalBadge>
                ))}
              </div>
            </BrutalCard>
          )}

          {/* Reading Controls */}
          <div className="space-y-4">
            {!isReading && !isChapterCompleted && (
              <BrutalButton
                variant="emerald"
                size="lg"
                fullWidth
                onClick={handleStartReading}
                className="flex items-center justify-center gap-2"
              >
                <BookOpen size={24} />
                Start Reading
              </BrutalButton>
            )}

            {isReading && (
              <div className="space-y-3">
                <BrutalCard variant="emerald" className="bg-emerald-100">
                  <p className="font-bold text-center">
                    📚 Reading in progress... Click "Finish Chapter" when done!
                  </p>
                </BrutalCard>
                
                <BrutalButton
                  variant="indigo"
                  size="lg"
                  fullWidth
                  onClick={handleFinishChapter}
                  className="flex items-center justify-center gap-2"
                >
                  <CheckCircle size={24} />
                  Finish Chapter & Take Quiz
                </BrutalButton>
              </div>
            )}

            {isChapterCompleted && (
              <div className="flex gap-4">
                {currentChapter > 1 && (
                  <BrutalButton
                    variant="ghost"
                    size="lg"
                    onClick={() => setCurrentChapter(prev => prev - 1)}
                    className="flex items-center gap-2"
                  >
                    <ArrowLeft size={20} />
                    Previous
                  </BrutalButton>
                )}
                
                {!isLastChapter && (
                  <BrutalButton
                    variant="indigo"
                    size="lg"
                    fullWidth
                    onClick={() => setCurrentChapter(prev => prev + 1)}
                    className="flex items-center gap-2"
                  >
                    Next Chapter
                    <ArrowRight size={20} />
                  </BrutalButton>
                )}
                
                {isLastChapter && (
                  <BrutalButton
                    variant="emerald"
                    size="lg"
                    fullWidth
                    onClick={onClose}
                    className="flex items-center gap-2"
                  >
                    <CheckCircle size={24} />
                    Complete Story
                  </BrutalButton>
                )}
              </div>
            )}
          </div>
        </BrutalCard>
      </div>

      {/* Vision Check Modal */}
      {showVisionCheck && (
        <VisionCheckModal
          visionCheck={chapter.vision_check}
          chapterNumber={currentChapter}
          onComplete={handleVisionCheckComplete}
        />
      )}
    </div>
  );
};

export default NarrativeReader;
