import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { spellingContestsAPI } from '@/lib/api';
import { Award, Clock, CheckCircle, XCircle, Trophy, Play, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';

const C = {
  card: '#1A2236', cream: '#F8F5EE', muted: '#94A3B8', gold: '#D4A853', teal: '#38BDF8',
};

const SpellingBee = ({ studentId, studentName }) => {
  const [activeContest, setActiveContest] = useState(null);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [timeLeft, setTimeLeft] = useState(0);
  const [started, setStarted] = useState(false);
  const [result, setResult] = useState(null);
  const [showLeaderboard, setShowLeaderboard] = useState(null);
  const timerRef = useRef(null);
  const inputRef = useRef(null);

  const { data: contests = [] } = useQuery({
    queryKey: ['active-spelling-contests'],
    queryFn: async () => (await spellingContestsAPI.listActive()).data,
  });

  const { data: leaderboard = [] } = useQuery({
    queryKey: ['spell-leaderboard', showLeaderboard],
    queryFn: async () => (await spellingContestsAPI.leaderboard(showLeaderboard)).data,
    enabled: !!showLeaderboard,
  });

  const submitMutation = useMutation({
    mutationFn: (data) => spellingContestsAPI.submit(data),
    onSuccess: (res) => {
      setResult(res.data);
      toast.success(`Score: ${res.data.score}%`);
    },
    onError: () => toast.error('Failed to submit'),
  });

  useEffect(() => {
    if (started && timeLeft > 0) {
      timerRef.current = setInterval(() => setTimeLeft(t => t - 1), 1000);
      return () => clearInterval(timerRef.current);
    }
    if (started && timeLeft <= 0 && !result) {
      handleFinish();
    }
  }, [started, timeLeft]);

  const startContest = (contest) => {
    setActiveContest(contest);
    setCurrentWordIndex(0);
    setAnswers({});
    setCurrentAnswer('');
    setTimeLeft(contest.time_limit_seconds);
    setStarted(true);
    setResult(null);
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const handleNextWord = useCallback(() => {
    if (!activeContest) return;
    const word = activeContest.word_list[currentWordIndex];
    const newAnswers = { ...answers, [word]: currentAnswer };
    setAnswers(newAnswers);
    setCurrentAnswer('');

    if (currentWordIndex < activeContest.word_list.length - 1) {
      setCurrentWordIndex(i => i + 1);
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      handleFinish(newAnswers);
    }
  }, [activeContest, currentWordIndex, currentAnswer, answers]);

  const handleFinish = useCallback((finalAnswers) => {
    if (timerRef.current) clearInterval(timerRef.current);
    setStarted(false);
    const ans = finalAnswers || answers;
    const elapsed = activeContest.time_limit_seconds - timeLeft;
    submitMutation.mutate({
      contest_id: activeContest.id,
      student_id: studentId,
      student_name: studentName,
      answers: ans,
      time_taken_seconds: elapsed,
    });
  }, [activeContest, answers, timeLeft, studentId, studentName]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleNextWord();
    }
  };

  const fmt = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;

  if (result) {
    return (
      <div className="space-y-4" data-testid="spelling-result">
        <div className="p-6 rounded-2xl text-center" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
          <Trophy size={48} className="mx-auto mb-3" style={{ color: result.score >= 80 ? '#34D399' : result.score >= 50 ? '#FBBF24' : '#EF4444' }} />
          <h2 className="text-3xl font-bold mb-1" style={{ color: C.cream }}>{result.score}%</h2>
          <p className="text-sm" style={{ color: C.muted }}>{result.correct_count}/{result.total_words} correct in {result.time_taken_seconds}s</p>
        </div>
        <div className="space-y-2">
          {result.results?.map((r, i) => (
            <div key={i} className="flex items-center gap-3 p-3 rounded-xl"
              style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }}>
              {r.correct ? <CheckCircle size={18} style={{ color: '#34D399' }} /> : <XCircle size={18} style={{ color: '#EF4444' }} />}
              <span className="text-sm font-bold" style={{ color: C.cream }}>{r.word}</span>
              {!r.correct && <span className="text-xs" style={{ color: '#EF4444' }}>You wrote: {r.answer || '(skipped)'}</span>}
            </div>
          ))}
        </div>
        <button onClick={() => { setActiveContest(null); setResult(null); }}
          className="w-full py-3 rounded-xl text-sm font-bold" style={{ background: 'rgba(255,255,255,0.06)', color: C.cream, border: '1px solid rgba(255,255,255,0.1)' }}
          data-testid="spelling-back-btn">
          Back to Contests
        </button>
      </div>
    );
  }

  if (activeContest && started) {
    const word = activeContest.word_list[currentWordIndex];
    const progress = ((currentWordIndex) / activeContest.word_list.length) * 100;

    return (
      <div className="space-y-4" data-testid="spelling-active">
        <div className="flex items-center justify-between">
          <p className="text-sm font-bold" style={{ color: C.cream }}>Word {currentWordIndex + 1}/{activeContest.word_list.length}</p>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg" style={{ background: timeLeft < 30 ? 'rgba(239,68,68,0.15)' : 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)' }}>
            <Clock size={14} style={{ color: timeLeft < 30 ? '#EF4444' : C.muted }} />
            <span className="font-mono font-bold text-sm" style={{ color: timeLeft < 30 ? '#EF4444' : C.cream }}>{fmt(timeLeft)}</span>
          </div>
        </div>
        <div className="w-full h-1.5 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
          <div className="h-full rounded-full transition-all" style={{ width: `${progress}%`, background: `linear-gradient(90deg, ${C.gold}, ${C.teal})` }} />
        </div>
        <div className="p-6 rounded-2xl text-center" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.1)' }}>
          <p className="text-xs font-bold uppercase mb-3" style={{ color: C.muted }}>Spell this word:</p>
          <p className="text-2xl font-bold mb-6" style={{ color: C.gold }}>
            {"_ ".repeat(word.length).trim()}
          </p>
          <p className="text-xs mb-4" style={{ color: C.muted }}>
            Hint: {word.length} letters, starts with "{word[0].toUpperCase()}"
          </p>
          <input
            ref={inputRef}
            type="text"
            value={currentAnswer}
            onChange={(e) => setCurrentAnswer(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your spelling..."
            className="w-full px-4 py-3 rounded-xl text-center text-lg font-bold outline-none"
            style={{ background: 'rgba(255,255,255,0.06)', color: C.cream, border: '2px solid rgba(212,168,83,0.3)', letterSpacing: '0.15em' }}
            autoFocus
            autoComplete="off"
            spellCheck={false}
            data-testid="spelling-input"
          />
        </div>
        <button onClick={handleNextWord}
          className="w-full py-3 rounded-xl text-sm font-bold text-black"
          style={{ background: `linear-gradient(135deg, ${C.gold}, #F5D799)` }}
          data-testid="spelling-next-btn">
          {currentWordIndex < activeContest.word_list.length - 1 ? 'Next Word' : 'Finish'} <ArrowRight size={14} className="inline ml-1" />
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="spelling-contests-list">
      {contests.length === 0 ? (
        <div className="text-center py-12 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }}>
          <Award size={40} className="mx-auto mb-3" style={{ color: C.muted }} />
          <h3 className="text-lg font-bold mb-1" style={{ color: C.cream }}>No Active Spelling Contests</h3>
          <p className="text-sm" style={{ color: C.muted }}>Check back soon for new challenges!</p>
        </div>
      ) : (
        contests.map(c => (
          <div key={c.id} className="p-4 rounded-xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}
            data-testid={`contest-${c.id}`}>
            <div className="flex items-center justify-between gap-3">
              <div className="flex-1 min-w-0">
                <h3 className="text-base font-bold" style={{ color: C.cream }}>{c.title}</h3>
                {c.description && <p className="text-xs mt-0.5" style={{ color: C.muted }}>{c.description}</p>}
                <div className="flex items-center gap-3 mt-2 text-xs" style={{ color: C.muted }}>
                  <span>{c.word_list?.length || 0} words</span>
                  <span>{c.time_limit_seconds}s limit</span>
                  <span>{c.participant_count || 0} participants</span>
                </div>
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <button onClick={() => setShowLeaderboard(showLeaderboard === c.id ? null : c.id)}
                  className="p-2 rounded-lg text-xs font-bold"
                  style={{ color: C.muted, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)' }}
                  data-testid={`leaderboard-btn-${c.id}`}>
                  <Trophy size={16} />
                </button>
                <button onClick={() => startContest(c)}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold text-black"
                  style={{ background: `linear-gradient(135deg, ${C.gold}, #F5D799)` }}
                  data-testid={`start-contest-${c.id}`}>
                  <Play size={14} /> Start
                </button>
              </div>
            </div>
            {showLeaderboard === c.id && (
              <div className="mt-3 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                <p className="text-xs font-bold uppercase mb-2" style={{ color: C.gold }}>Leaderboard</p>
                {leaderboard.length === 0 ? (
                  <p className="text-xs" style={{ color: C.muted }}>No submissions yet. Be the first!</p>
                ) : (
                  <div className="space-y-1.5">
                    {leaderboard.slice(0, 10).map((s) => (
                      <div key={s.id} className="flex items-center gap-2 p-2 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                        <span className="text-sm font-bold w-6 text-center" style={{ color: s.rank <= 3 ? C.gold : C.muted }}>#{s.rank}</span>
                        <span className="text-sm font-semibold flex-1" style={{ color: C.cream }}>{s.student_name}</span>
                        <span className="text-sm font-bold" style={{ color: s.score >= 80 ? '#34D399' : s.score >= 50 ? '#FBBF24' : '#EF4444' }}>{s.score}%</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default SpellingBee;
