import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { readLogAPI } from '@/lib/api';
import { ArrowLeft, ArrowRight, Clock, BookOpen, CheckCircle, AlertTriangle, Eye, Mic } from 'lucide-react';
import { toast } from 'sonner';
import WrittenAnswerModal from './WrittenAnswerModal';
import VocabularyAssessment from './VocabularyAssessment';
import WordDefinitionModal from './WordDefinitionModal';
import ReadAloudRecorder from '@/components/ReadAloudRecorder';

const C = {
  bg: '#0A0F1E', surface: '#111827', card: '#1A2236',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8', reading: '#E8E0D0',
};

const NarrativeReader = ({ narrative, student, onClose }) => {
  const queryClient = useQueryClient();
  const [currentChapter, setCurrentChapter] = useState(narrative.current_chapter || 1);
  const [sessionStart] = useState(new Date());
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [showWrittenCheck, setShowWrittenCheck] = useState(false);
  const [showAssessment, setShowAssessment] = useState(false);
  const [completedChapters, setCompletedChapters] = useState(narrative.chapters_completed || []);
  const [selectedWord, setSelectedWord] = useState(null);
  const [wordContext, setWordContext] = useState('');
  const [showRecorder, setShowRecorder] = useState(false);

  const chapter = narrative.chapters[currentChapter - 1];
  const isLastChapter = currentChapter === 5;
  const isChapterCompleted = completedChapters.includes(currentChapter);
  const allChaptersCompleted = completedChapters.length === 5;

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedSeconds(Math.floor((new Date() - sessionStart) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [sessionStart]);

  const createReadLogMutation = useMutation({
    mutationFn: (data) => readLogAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['student-detail']);
      queryClient.invalidateQueries(['read-logs']);
    },
  });

  const handleFinishChapter = () => {
    createReadLogMutation.mutate({
      student_id: student.id, narrative_id: narrative.id,
      chapter_number: currentChapter, session_start: sessionStart.toISOString(),
      session_end: new Date().toISOString(), words_read: chapter.word_count,
    });
    setShowWrittenCheck(true);
  };

  const handleWrittenCheckComplete = (passed) => {
    setShowWrittenCheck(false);
    readLogAPI.create({
      student_id: student.id, narrative_id: narrative.id,
      chapter_number: currentChapter, session_start: sessionStart.toISOString(),
      session_end: new Date().toISOString(), words_read: 0, vision_check_passed: passed,
    }).catch(() => {});

    if (passed) {
      const newCompleted = [...new Set([...completedChapters, currentChapter])];
      setCompletedChapters(newCompleted);
      if (newCompleted.length === 5) {
        toast.success('Story completed! Time for vocabulary assessment!');
        setTimeout(() => setShowAssessment(true), 1500);
      } else if (!isLastChapter) {
        toast.success('Great job! Moving to next chapter...');
        setTimeout(() => setCurrentChapter((prev) => prev + 1), 1000);
      }
    } else {
      toast.error('Try reading the chapter again more carefully!');
    }
  };

  const calculateWPM = () => (elapsedSeconds === 0 ? 0 : Math.round(chapter.word_count / (elapsedSeconds / 60)));
  const formatTime = (s) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  if (showAssessment) {
    return <VocabularyAssessment narrative={narrative} student={student} onClose={onClose} />;
  }

  return (
    <div className="min-h-screen sv-dark" style={{ background: C.bg, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Sticky Header */}
      <header className="sticky top-0 z-50" style={{ background: C.surface, borderBottom: '1px solid rgba(212,168,83,0.15)' }}>
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button onClick={onClose} className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold transition-all hover:scale-105"
                style={{ color: C.muted, border: '1px solid rgba(255,255,255,0.1)' }} data-testid="reader-back-btn">
                <ArrowLeft size={16} /> Back
              </button>
              <div className="flex items-center gap-2" style={{ borderLeft: '1px solid rgba(255,255,255,0.1)', paddingLeft: '12px' }}>
                <Eye size={18} style={{ color: C.gold }} />
                <div>
                  <h1 className="text-sm font-bold" style={{ color: C.cream }} data-testid="story-title">{narrative.title}</h1>
                  <p className="text-xs" style={{ color: C.muted }}>Chapter {currentChapter} of 5</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }} data-testid="reading-timer">
                <Clock size={14} style={{ color: '#34D399' }} className="animate-pulse" />
                <span className="font-mono font-bold text-sm" style={{ color: C.cream }}>{formatTime(elapsedSeconds)}</span>
                {elapsedSeconds > 0 && (
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: 'rgba(52,211,153,0.12)', color: '#34D399' }}>
                    {calculateWPM()} WPM
                  </span>
                )}
              </div>
              {student.spellcheck_disabled && (
                <span className="text-xs font-semibold px-2 py-1 rounded-full" style={{ background: 'rgba(245,158,11,0.12)', color: '#FBBF24' }} data-testid="spellcheck-off-badge">
                  <AlertTriangle size={10} className="inline mr-1" /> Spellcheck OFF
                </span>
              )}
            </div>
          </div>
          {/* Progress bar */}
          <div className="mt-3 w-full h-1.5 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
            <div className="h-1.5 rounded-full transition-all duration-500" style={{ width: `${(currentChapter / 5) * 100}%`, background: `linear-gradient(90deg, ${C.gold}, ${C.teal})` }} />
          </div>
        </div>
      </header>

      {/* Reading Content */}
      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <div className="p-8 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }}>
          {/* Chapter Title */}
          <div className="mb-8 pb-6" style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-2xl font-bold" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>{chapter.title}</h2>
              {isChapterCompleted && (
                <span className="flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full" style={{ background: 'rgba(52,211,153,0.12)', color: '#34D399' }}>
                  <CheckCircle size={14} /> Completed
                </span>
              )}
            </div>
            <div className="flex items-center gap-4 text-xs" style={{ color: C.muted }}>
              <span>{chapter.word_count} words</span>
              <span>~{Math.ceil(chapter.word_count / 200)} min read</span>
            </div>
          </div>

          {/* Story Text — warm reading color */}
          <div className="mb-8">
            <div className="text-lg leading-[1.9] font-medium" style={{ color: C.reading }}>
              {chapter.content.split(/(\s+)/).map((segment, idx) => {
                const cleanWord = segment.replace(/[^a-zA-Z'-]/g, '');
                if (!cleanWord || cleanWord.length < 2) return <span key={idx}>{segment}</span>;
                return (
                  <span key={idx}
                    className="cursor-pointer transition-colors rounded px-[1px]"
                    style={{ borderBottom: '1px solid transparent' }}
                    onMouseEnter={(e) => { e.target.style.borderBottomColor = C.gold; e.target.style.color = C.gold; }}
                    onMouseLeave={(e) => { e.target.style.borderBottomColor = 'transparent'; e.target.style.color = C.reading; }}
                    onClick={() => {
                      setSelectedWord(cleanWord);
                      const words = chapter.content.split(/\s+/);
                      const wIdx = words.findIndex((w) => w.includes(cleanWord));
                      const start = Math.max(0, wIdx - 5);
                      const end = Math.min(words.length, wIdx + 6);
                      setWordContext(words.slice(start, end).join(' '));
                    }}
                    data-testid={`word-${idx}`}>
                    {segment}
                  </span>
                );
              })}
            </div>
            <p className="text-xs mt-4 italic" style={{ color: C.muted }}>Tap any word to see its definition</p>
          </div>

          {/* Vocabulary Tokens */}
          {chapter.embedded_tokens?.length > 0 && (
            <div className="p-4 rounded-xl mb-6" style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)' }}>
              <p className="text-xs font-bold uppercase mb-2" style={{ color: '#818CF8' }}>Vocabulary in this chapter</p>
              <div className="flex flex-wrap gap-2">
                {chapter.embedded_tokens.map((token, idx) => (
                  <span key={idx} className="text-xs font-semibold px-3 py-1 rounded-full"
                    style={{ background: token.tier === 'stretch' ? 'rgba(244,63,94,0.12)' : token.tier === 'target' ? 'rgba(245,158,11,0.12)' : 'rgba(52,211,153,0.12)', color: token.tier === 'stretch' ? '#FB7185' : token.tier === 'target' ? '#FBBF24' : '#34D399' }}>
                    {token.word}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Read Aloud Section */}
          <div className="mb-4">
            {!showRecorder ? (
              <button onClick={() => setShowRecorder(true)}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold transition-all hover:scale-[1.01]"
                style={{ background: 'rgba(239,68,68,0.1)', color: '#EF4444', border: '1px solid rgba(239,68,68,0.2)' }}
                data-testid="read-aloud-btn">
                <Mic size={16} /> Read This Chapter Aloud
              </button>
            ) : (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-bold uppercase" style={{ color: C.gold }}>Read Aloud Recording</p>
                  <button onClick={() => setShowRecorder(false)} className="text-xs font-bold" style={{ color: C.muted }}>Close</button>
                </div>
                <ReadAloudRecorder
                  studentId={student.id}
                  narrativeId={narrative.id}
                  chapterNumber={currentChapter}
                  onRecordingComplete={(result) => toast.success(`Diction score: ${result.diction_scores?.overall}%`)}
                />
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="space-y-3">
            {!isChapterCompleted && (
              <button onClick={handleFinishChapter}
                className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all hover:scale-[1.01]"
                style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }} data-testid="finish-chapter-btn">
                <CheckCircle size={18} className="inline mr-2" /> Finish Chapter & Answer Question
              </button>
            )}
            {isChapterCompleted && (
              <div className="flex gap-3">
                {currentChapter > 1 && (
                  <button onClick={() => setCurrentChapter((p) => p - 1)}
                    className="flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold transition-all"
                    style={{ color: C.muted, border: '1px solid rgba(255,255,255,0.1)' }}>
                    <ArrowLeft size={16} /> Previous
                  </button>
                )}
                {!isLastChapter ? (
                  <button onClick={() => setCurrentChapter((p) => p + 1)}
                    className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-base font-bold text-black transition-all hover:scale-[1.01]"
                    style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}>
                    Next Chapter <ArrowRight size={16} />
                  </button>
                ) : (
                  <button onClick={onClose}
                    className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-base font-bold text-black transition-all hover:scale-[1.01]"
                    style={{ background: `linear-gradient(135deg, #34D399, #6EE7B7)` }}>
                    <CheckCircle size={18} /> Complete Story
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {showWrittenCheck && (
        <WrittenAnswerModal question={chapter.vision_check?.question || `What was the main idea of ${chapter.title}?`}
          chapterNumber={currentChapter} chapterContent={chapter.content} student={student}
          onComplete={handleWrittenCheckComplete} />
      )}
      {selectedWord && (
        <WordDefinitionModal word={selectedWord} context={wordContext}
          onClose={() => { setSelectedWord(null); setWordContext(''); }} />
      )}
    </div>
  );
};

export default NarrativeReader;
