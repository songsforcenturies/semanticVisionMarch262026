import React, { useState, useEffect, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { readLogAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalProgress } from '@/components/brutal';
import { ArrowLeft, ArrowRight, Clock, BookOpen, CheckCircle, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import WrittenAnswerModal from './WrittenAnswerModal';
import VocabularyAssessment from './VocabularyAssessment';
import WordDefinitionModal from './WordDefinitionModal';

const NarrativeReader = ({ narrative, student, onClose }) => {
  const queryClient = useQueryClient();
  const [currentChapter, setCurrentChapter] = useState(narrative.current_chapter || 1);
  const [sessionStart] = useState(new Date()); // Auto-start, no control
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [showWrittenCheck, setShowWrittenCheck] = useState(false);
  const [showAssessment, setShowAssessment] = useState(false);
  const [completedChapters, setCompletedChapters] = useState(narrative.chapters_completed || []);
  const [selectedWord, setSelectedWord] = useState(null);
  const [wordContext, setWordContext] = useState('');

  const chapter = narrative.chapters[currentChapter - 1];
  const isLastChapter = currentChapter === 5;
  const isChapterCompleted = completedChapters.includes(currentChapter);
  const allChaptersCompleted = completedChapters.length === 5;

  // Auto-start timer — runs continuously, student CANNOT stop it
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedSeconds(Math.floor((new Date() - sessionStart) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [sessionStart]);

  // Create read log mutation
  const createReadLogMutation = useMutation({
    mutationFn: (data) => readLogAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['student-detail']);
      queryClient.invalidateQueries(['read-logs']);
    }
  });

  const handleFinishChapter = () => {
    // Log reading time
    createReadLogMutation.mutate({
      student_id: student.id,
      narrative_id: narrative.id,
      chapter_number: currentChapter,
      session_start: sessionStart.toISOString(),
      session_end: new Date().toISOString(),
      words_read: chapter.word_count
    });
    // Show written comprehension check — result will be sent separately
    setShowWrittenCheck(true);
  };

  const handleWrittenCheckComplete = (passed) => {
    setShowWrittenCheck(false);
    // Send vision check result to backend
    readLogAPI.create({
      student_id: student.id,
      narrative_id: narrative.id,
      chapter_number: currentChapter,
      session_start: sessionStart.toISOString(),
      session_end: new Date().toISOString(),
      words_read: 0,
      vision_check_passed: passed,
    }).catch(() => {});

    if (passed) {
      const newCompletedChapters = [...new Set([...completedChapters, currentChapter])];
      setCompletedChapters(newCompletedChapters);
      if (newCompletedChapters.length === 5) {
        toast.success('Story completed! Time for vocabulary assessment!');
        setTimeout(() => setShowAssessment(true), 1500);
      } else if (!isLastChapter) {
        toast.success('Great job! Moving to next chapter...');
        setTimeout(() => setCurrentChapter(prev => prev + 1), 1000);
      }
    } else {
      toast.error('Try reading the chapter again more carefully!');
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

  if (showAssessment) {
    return <VocabularyAssessment narrative={narrative} student={student} onClose={onClose} />;
  }

  // Determine if spellcheck should be disabled
  const disableSpellcheck = student.spellcheck_disabled || false;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white border-b-6 border-black brutal-shadow-md sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <BrutalButton variant="ghost" onClick={onClose} className="flex items-center gap-2" data-testid="reader-back-btn">
                <ArrowLeft size={20} /> Back
              </BrutalButton>
              <div>
                <h1 className="text-2xl font-black uppercase" data-testid="story-title">{narrative.title}</h1>
                <p className="text-sm font-medium text-gray-600">Chapter {currentChapter} of 5</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {/* Always-running timer */}
              <BrutalCard shadow="sm" className="px-4 py-2" data-testid="reading-timer">
                <div className="flex items-center gap-2">
                  <Clock size={20} className="text-emerald-600 animate-pulse" />
                  <span className="font-black text-lg font-mono">{formatTime(elapsedSeconds)}</span>
                  {elapsedSeconds > 0 && (
                    <BrutalBadge variant="emerald" size="sm">{calculateWPM()} WPM</BrutalBadge>
                  )}
                </div>
              </BrutalCard>
              {disableSpellcheck && (
                <BrutalBadge variant="amber" size="sm" data-testid="spellcheck-off-badge">
                  <AlertTriangle size={12} className="inline mr-1" /> Spellcheck OFF
                </BrutalBadge>
              )}
            </div>
          </div>
          <div className="mt-4">
            <BrutalProgress value={currentChapter} max={5} variant="indigo" showLabel />
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <BrutalCard shadow="xl" className="mb-6">
          <div className="mb-6 pb-6 border-b-4 border-black">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-3xl font-black uppercase">{chapter.title}</h2>
              {isChapterCompleted && (
                <BrutalBadge variant="emerald" size="lg" className="flex items-center gap-1">
                  <CheckCircle size={18} /> Completed
                </BrutalBadge>
              )}
            </div>
            <div className="flex items-center gap-4 text-sm font-medium text-gray-600">
              <span>{chapter.word_count} words</span>
              <span>~{Math.ceil(chapter.word_count / 200)} min read</span>
            </div>
          </div>

          {/* Chapter Content — Click any word to define */}
          <div className="prose prose-lg max-w-none mb-8">
            <div className="text-lg leading-relaxed font-medium">
              {chapter.content.split(/(\s+)/).map((segment, idx) => {
                const cleanWord = segment.replace(/[^a-zA-Z'-]/g, '');
                if (!cleanWord || cleanWord.length < 2) {
                  return <span key={idx}>{segment}</span>;
                }
                return (
                  <span
                    key={idx}
                    className="cursor-pointer hover:bg-indigo-100 hover:border-b-2 hover:border-indigo-400 transition-colors rounded px-[1px]"
                    onClick={() => {
                      setSelectedWord(cleanWord);
                      // Get surrounding context
                      const words = chapter.content.split(/\s+/);
                      const wIdx = words.findIndex(w => w.includes(cleanWord));
                      const start = Math.max(0, wIdx - 5);
                      const end = Math.min(words.length, wIdx + 6);
                      setWordContext(words.slice(start, end).join(' '));
                    }}
                    data-testid={`word-${idx}`}
                  >
                    {segment}
                  </span>
                );
              })}
            </div>
            <p className="text-xs text-gray-400 mt-2 italic">Tap any word to see its definition</p>
          </div>

          {/* Embedded Vocabulary */}
          {chapter.embedded_tokens && chapter.embedded_tokens.length > 0 && (
            <BrutalCard className="bg-indigo-50 mb-6">
              <p className="font-bold text-sm uppercase mb-3">Vocabulary in this chapter:</p>
              <div className="flex flex-wrap gap-2">
                {chapter.embedded_tokens.map((token, idx) => (
                  <BrutalBadge key={idx} variant={token.tier} size="sm">{token.word}</BrutalBadge>
                ))}
              </div>
            </BrutalCard>
          )}

          {/* Reading Controls */}
          <div className="space-y-4">
            {!isChapterCompleted && (
              <BrutalButton variant="indigo" size="lg" fullWidth onClick={handleFinishChapter}
                className="flex items-center justify-center gap-2" data-testid="finish-chapter-btn">
                <CheckCircle size={24} /> Finish Chapter & Answer Question
              </BrutalButton>
            )}

            {isChapterCompleted && (
              <div className="flex gap-4">
                {currentChapter > 1 && (
                  <BrutalButton variant="ghost" size="lg" onClick={() => setCurrentChapter(prev => prev - 1)} className="flex items-center gap-2">
                    <ArrowLeft size={20} /> Previous
                  </BrutalButton>
                )}
                {!isLastChapter && (
                  <BrutalButton variant="indigo" size="lg" fullWidth onClick={() => setCurrentChapter(prev => prev + 1)} className="flex items-center gap-2">
                    Next Chapter <ArrowRight size={20} />
                  </BrutalButton>
                )}
                {isLastChapter && (
                  <BrutalButton variant="emerald" size="lg" fullWidth onClick={onClose} className="flex items-center gap-2">
                    <CheckCircle size={24} /> Complete Story
                  </BrutalButton>
                )}
              </div>
            )}
          </div>
        </BrutalCard>
      </div>

      {/* Written Answer Modal (replaces multiple choice) */}
      {showWrittenCheck && (
        <WrittenAnswerModal
          question={chapter.vision_check?.question || `What was the main idea of ${chapter.title}?`}
          chapterNumber={currentChapter}
          chapterContent={chapter.content}
          student={student}
          onComplete={handleWrittenCheckComplete}
        />
      )}

      {/* Word Definition Modal */}
      {selectedWord && (
        <WordDefinitionModal
          word={selectedWord}
          context={wordContext}
          onClose={() => { setSelectedWord(null); setWordContext(''); }}
        />
      )}
    </div>
  );
};

export default NarrativeReader;
