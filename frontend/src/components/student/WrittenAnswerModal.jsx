import React, { useState } from 'react';
import { BrutalButton, BrutalCard, BrutalBadge } from '@/components/brutal';
import { CheckCircle, XCircle, Send, Loader } from 'lucide-react';
import apiClient from '@/lib/api';

const WrittenAnswerModal = ({ question, chapterNumber, chapterContent, student, onComplete }) => {
  const [answer, setAnswer] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [result, setResult] = useState(null);

  const disableSpellcheck = student?.spellcheck_disabled || false;

  const handleSubmit = async () => {
    if (!answer.trim()) return;
    setIsEvaluating(true);
    try {
      const res = await apiClient.post('/assessments/evaluate-written', {
        student_id: student.id,
        chapter_number: chapterNumber,
        question,
        student_answer: answer,
        chapter_summary: chapterContent?.slice(0, 500) || '',
        spelling_mode: student.spelling_mode || 'phonetic',
      });
      setResult(res.data);
    } catch (err) {
      setResult({ passed: true, feedback: 'Great effort! Keep reading!', spelling_errors: [] });
    }
    setIsEvaluating(false);
  };

  const handleContinue = () => {
    onComplete(result?.passed ?? false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 overflow-y-auto">
      <BrutalCard shadow="xl" className="w-full max-w-2xl bg-white my-auto">
        {!result ? (
          <>
            <div className="mb-4 sm:mb-6">
              <div className="flex items-center gap-3 mb-3 sm:mb-4">
                <div className="bg-indigo-500 text-white font-black text-xl sm:text-2xl w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center border-4 border-black flex-shrink-0">?</div>
                <h2 className="text-lg sm:text-2xl font-black uppercase">Comprehension Check</h2>
              </div>
              <p className="text-base sm:text-lg font-bold mb-2">Chapter {chapterNumber}</p>
              <p className="text-base sm:text-xl font-medium" data-testid="written-question">{question}</p>
            </div>

            <div className="mb-4 sm:mb-6">
              <label className="block mb-2 sm:mb-3 font-bold uppercase text-sm">Write your answer:</label>
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer here... Use complete sentences."
                rows={4}
                spellCheck={!disableSpellcheck}
                autoComplete={disableSpellcheck ? "off" : "on"}
                className="w-full px-3 sm:px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-indigo-500 resize-none text-sm sm:text-base"
                data-testid="written-answer-input"
              />
              {disableSpellcheck && (
                <p className="text-xs font-bold text-amber-600 mt-1">Spellcheck is disabled — your spelling will be tracked</p>
              )}
            </div>

            <BrutalButton variant="indigo" size="lg" fullWidth onClick={handleSubmit}
              disabled={isEvaluating || !answer.trim()} className="flex items-center justify-center gap-2"
              data-testid="submit-written-answer">
              {isEvaluating ? (
                <><Loader size={20} className="animate-spin" /> Evaluating...</>
              ) : (
                <><Send size={20} /> Submit Answer</>
              )}
            </BrutalButton>
          </>
        ) : (
          <>
            <div className="text-center mb-4 sm:mb-6">
              <div className="flex justify-center mb-4">
                {result.passed ? (
                  <div className="bg-emerald-100 p-4 sm:p-6 border-6 border-black brutal-shadow-lg">
                    <CheckCircle size={60} className="text-emerald-600 sm:hidden" />
                    <CheckCircle size={80} className="text-emerald-600 hidden sm:block" />
                  </div>
                ) : (
                  <div className="bg-rose-100 p-4 sm:p-6 border-6 border-black brutal-shadow-lg">
                    <XCircle size={60} className="text-rose-600 sm:hidden" />
                    <XCircle size={80} className="text-rose-600 hidden sm:block" />
                  </div>
                )}
              </div>
              <h2 className="text-2xl sm:text-4xl font-black uppercase mb-4" data-testid="written-result">
                {result.passed ? 'Correct!' : 'Not Quite'}
              </h2>
              <BrutalCard variant={result.passed ? 'emerald' : 'rose'} className="mb-4">
                <p className="text-base sm:text-lg font-bold">{result.feedback}</p>
              </BrutalCard>

              {result.spelling_errors && result.spelling_errors.length > 0 && (
                <BrutalCard className="bg-amber-50 border-amber-500 mb-4 text-left">
                  <p className="font-bold text-sm uppercase mb-2">Spelling Notes:</p>
                  <div className="flex flex-wrap gap-2">
                    {result.spelling_errors.map((err, i) => (
                      <BrutalBadge key={i} variant="amber" size="sm">
                        {err.written} → {err.correct}
                      </BrutalBadge>
                    ))}
                  </div>
                </BrutalCard>
              )}
            </div>

            <BrutalButton variant={result.passed ? 'emerald' : 'amber'} size="lg" fullWidth onClick={handleContinue}
              data-testid="continue-after-answer">
              {result.passed ? 'Continue to Next Chapter' : 'Read Chapter Again'}
            </BrutalButton>
          </>
        )}
      </BrutalCard>
    </div>
  );
};

export default WrittenAnswerModal;
