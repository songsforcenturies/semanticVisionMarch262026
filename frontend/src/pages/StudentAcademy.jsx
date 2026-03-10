import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useQuery } from '@tanstack/react-query';
import { studentAPI, narrativeAPI, classroomAPI } from '@/lib/api';
import { BookOpen, Plus, TrendingUp, Clock, BookMarked, Users, ArrowRight, HelpCircle, RotateCcw, WifiOff, Award } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import AppShell from '@/components/AppShell';
import StoryGenerationDialog from '@/components/student/StoryGenerationDialog';
import NarrativeReader from '@/components/student/NarrativeReader';
import OnboardingWizard from '@/components/OnboardingWizard';
import { studentOnboardingSteps } from '@/components/onboardingSteps';
import FAQSection from '@/components/FAQSection';
import { studentFAQ } from '@/components/faqContent';
import OfflineLibrary from '@/components/OfflineLibrary';
import SpellingBee from '@/components/student/SpellingBee';
import TaskReminders from '@/components/student/TaskReminders';

const C = {
  bg: '#0A0F1E', card: '#1A2236', surface: '#111827',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8',
};

const StatCard = ({ icon: Icon, label, value, sub, accent }) => (
  <div className="p-4 sm:p-5 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
    <div className="flex items-center gap-3 sm:gap-4">
      <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `${accent}18` }}>
        <Icon size={20} style={{ color: accent }} />
      </div>
      <div className="min-w-0">
        <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: C.muted }}>{label}</p>
        <p className="text-2xl sm:text-3xl font-bold mt-0.5" style={{ color: C.cream }}>{value}</p>
        {sub && <p className="text-xs mt-1 truncate" style={{ color: C.muted }}>{sub}</p>}
      </div>
    </div>
  </div>
);

const StudentAcademy = () => {
  const { student, studentLogout } = useAuth();
  const navigate = useNavigate();
  const [showStoryDialog, setShowStoryDialog] = useState(false);
  const [selectedNarrative, setSelectedNarrative] = useState(null);
  const [sessionCode, setSessionCode] = useState('');
  const [joiningSession, setJoiningSession] = useState(false);
  const [joinedSession, setJoinedSession] = useState(null);
  const [wizardKey, setWizardKey] = useState(0);
  const [showFAQ, setShowFAQ] = useState(false);
  const [showOffline, setShowOffline] = useState(false);
  const [showSpelling, setShowSpelling] = useState(false);

  const resetOnboarding = () => {
    localStorage.removeItem(`sv_onboarding_student_${student?.id || student?.student_code}`);
    setWizardKey((k) => k + 1);
  };

  const { data: studentData, isLoading: studentLoading } = useQuery({
    queryKey: ['student-detail', student?.id],
    queryFn: async () => (await studentAPI.getById(student?.id)).data,
    enabled: !!student?.id,
  });

  const { data: narratives = [] } = useQuery({
    queryKey: ['student-narratives', student?.id],
    queryFn: async () => (await narrativeAPI.getAll(student?.id)).data,
    enabled: !!student?.id,
  });

  const handleLogout = () => { studentLogout(); navigate('/student-login'); };

  const handleJoinSession = async (e) => {
    e.preventDefault();
    if (!sessionCode.trim() || !student?.id) return;
    setJoiningSession(true);
    try {
      const res = await classroomAPI.join(sessionCode.trim(), student.id);
      setJoinedSession(res.data);
      toast.success(`Joined session: ${res.data.title}`);
      setSessionCode('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not join session.');
    }
    setJoiningSession(false);
  };

  if (studentLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: C.bg }}>
        <div className="text-xl font-bold" style={{ color: C.cream }}>Loading...</div>
      </div>
    );
  }

  if (selectedNarrative) {
    return <NarrativeReader narrative={selectedNarrative} student={studentData} onClose={() => setSelectedNarrative(null)} />;
  }

  const canGenerateStory = studentData?.assigned_banks?.length > 0;
  const masteredCount = studentData?.mastered_tokens?.length || 0;
  const biologicalTarget = studentData?.biological_target || 1000;
  const agenticScore = studentData?.agentic_reach_score || 0;

  return (
    <AppShell title="Semantic Vision Academy" subtitle={`Welcome, ${studentData?.full_name}!`} onLogout={handleLogout}
      isStudent={true} studentId={student?.id}
      rightContent={
        <div className="flex items-center gap-2 flex-wrap">
          <button onClick={() => { setShowSpelling(!showSpelling); setShowOffline(false); setShowFAQ(false); }}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all hover:scale-105"
            style={{ color: showSpelling ? '#D4A853' : '#94A3B8', border: '1px solid rgba(255,255,255,0.1)', background: showSpelling ? 'rgba(212,168,83,0.1)' : 'rgba(255,255,255,0.04)' }}
            data-testid="student-spelling-btn">
            <Award size={14} /> Spelling Bee
          </button>
          <button onClick={() => { setShowOffline(!showOffline); setShowSpelling(false); setShowFAQ(false); }}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all hover:scale-105"
            style={{ color: showOffline ? '#D4A853' : '#94A3B8', border: '1px solid rgba(255,255,255,0.1)', background: showOffline ? 'rgba(212,168,83,0.1)' : 'rgba(255,255,255,0.04)' }}
            data-testid="student-offline-btn">
            <WifiOff size={14} /> Offline
          </button>
          <button onClick={() => { setShowFAQ(!showFAQ); setShowOffline(false); setShowSpelling(false); }}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all hover:scale-105"
            style={{ color: showFAQ ? '#D4A853' : '#94A3B8', border: '1px solid rgba(255,255,255,0.1)', background: showFAQ ? 'rgba(212,168,83,0.1)' : 'rgba(255,255,255,0.04)' }}
            data-testid="student-faq-btn">
            <HelpCircle size={14} /> FAQ
          </button>
          <button onClick={resetOnboarding}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all hover:scale-105"
            style={{ color: '#94A3B8', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.04)' }}
            data-testid="reset-onboarding-btn">
            <RotateCcw size={14} /> Tutorial
          </button>
        </div>
      }
    >
      <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-6">
        {/* FAQ Section */}
        {showFAQ && (
          <div className="mb-6">
            <FAQSection items={studentFAQ} title="Student FAQ" />
          </div>
        )}

        {/* Offline Library Section */}
        {showOffline && (
          <div className="mb-6">
            <h2 className="text-lg sm:text-xl font-bold mb-3" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>Offline Library</h2>
            <OfflineLibrary studentId={student?.id} onReadStory={(story) => setSelectedNarrative(story)} />
          </div>
        )}

        {/* Spelling Bee Section */}
        {showSpelling && (
          <div className="mb-6">
            <h2 className="text-lg sm:text-xl font-bold mb-3" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>Spelling Bee Contests</h2>
            <SpellingBee studentId={student?.id} studentName={studentData?.full_name} />
          </div>
        )}

        {/* Task Reminders - always visible */}
        <TaskReminders
          studentId={student?.id}
          onOpenStory={(narrativeId) => {
            const n = narratives.find(n => n.id === narrativeId);
            if (n) setSelectedNarrative(n);
          }}
          onOpenSpelling={() => { setShowSpelling(true); setShowOffline(false); setShowFAQ(false); }}
        />

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6">
          <StatCard icon={BookMarked} label="Vocabulary Mastered" value={masteredCount} sub={`Target: ${biologicalTarget} words`} accent="#818CF8" />
          <StatCard icon={TrendingUp} label="Agentic Reach Score" value={Math.round(agenticScore)} sub={agenticScore >= 600 ? 'Expert' : agenticScore >= 300 ? 'Adept' : agenticScore >= 100 ? 'Apprentice' : 'Initiate'} accent="#34D399" />
          <StatCard icon={Clock} label="Reading Time" value={`${Math.floor((studentData?.total_reading_seconds || 0) / 60)}m`} sub={`${studentData?.average_wpm || 0} WPM average`} accent="#FBBF24" />
        </div>

        {/* Join Classroom */}
        <div className="p-4 sm:p-5 rounded-2xl mb-4 sm:mb-6" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
          <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(56,189,248,0.12)' }}>
                <Users size={20} style={{ color: C.teal }} />
              </div>
              <div>
                <h3 className="text-sm sm:text-base font-bold" style={{ color: C.cream }}>Join Classroom</h3>
                <p className="text-xs" style={{ color: C.muted }}>Enter teacher's code</p>
              </div>
            </div>
            <form onSubmit={handleJoinSession} className="flex items-center gap-2 sm:ml-auto">
              <input type="text" value={sessionCode} onChange={(e) => setSessionCode(e.target.value)}
                placeholder="6-digit code" maxLength={6}
                className="px-3 sm:px-4 py-2 rounded-xl font-mono font-bold text-center w-28 sm:w-36 text-sm outline-none"
                style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: C.cream }}
                data-testid="session-code-input" />
              <button type="submit" disabled={joiningSession || sessionCode.length < 6}
                className="px-4 sm:px-5 py-2 rounded-xl text-sm font-bold text-black disabled:opacity-50"
                style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}
                data-testid="join-session-btn">
                {joiningSession ? '...' : 'Join'}
              </button>
            </form>
          </div>
          {joinedSession && (
            <div className="mt-3 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }} data-testid="joined-session-info">
              <p className="text-sm font-bold" style={{ color: '#34D399' }}>Joined: {joinedSession.title}</p>
            </div>
          )}
        </div>

        {/* Stories */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4 gap-2">
            <h2 className="text-xl sm:text-2xl font-bold" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>Your Stories</h2>
            <button onClick={() => setShowStoryDialog(true)} disabled={!canGenerateStory}
              className="flex items-center gap-1.5 sm:gap-2 px-3 sm:px-5 py-2 sm:py-2.5 rounded-xl text-xs sm:text-sm font-bold text-black transition-all hover:scale-105 disabled:opacity-50 flex-shrink-0"
              style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}>
              <Plus size={16} /> <span className="hidden sm:inline">Create New Story</span><span className="sm:hidden">New</span>
            </button>
          </div>

          {!canGenerateStory && (
            <div className="p-3 sm:p-4 rounded-xl mb-4" style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)' }}>
              <p className="text-xs sm:text-sm font-semibold" style={{ color: '#FBBF24' }}>
                No word banks assigned! Ask your guardian to assign word banks.
              </p>
            </div>
          )}

          {narratives.length === 0 ? (
            <div className="text-center py-12 sm:py-16 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
              <BookOpen size={40} className="mx-auto mb-4" style={{ color: C.gold }} />
              <p className="text-lg sm:text-xl font-bold mb-2" style={{ color: C.cream }}>No stories yet</p>
              <p className="text-xs sm:text-sm mb-6" style={{ color: C.muted }}>Create your first AI-generated story and start learning!</p>
              {canGenerateStory && (
                <button onClick={() => setShowStoryDialog(true)}
                  className="flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-black mx-auto hover:scale-105 transition-all"
                  style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}>
                  <Plus size={18} /> Create Your First Story
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
              {narratives.map((narrative) => {
                const chaptersCompleted = narrative.chapters_completed?.length || 0;
                const isCompleted = narrative.status === 'completed';
                return (
                  <div key={narrative.id}
                    className="p-4 sm:p-5 rounded-2xl cursor-pointer transition-all hover:scale-[1.02]"
                    style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}
                    onClick={() => setSelectedNarrative(narrative)}>
                    <h3 className="text-sm sm:text-base font-bold mb-1" style={{ color: C.cream }}>{narrative.title}</h3>
                    <p className="text-xs mb-3 sm:mb-4 line-clamp-2" style={{ color: C.muted }}>{narrative.theme}</p>
                    <div className="mb-3">
                      <div className="flex justify-between text-xs mb-1" style={{ color: C.muted }}>
                        <span>Progress</span>
                        <span>{chaptersCompleted}/5</span>
                      </div>
                      <div className="w-full h-2 rounded-full" style={{ background: 'rgba(255,255,255,0.08)' }}>
                        <div className="h-2 rounded-full transition-all" style={{ width: `${(chaptersCompleted / 5) * 100}%`, background: isCompleted ? '#34D399' : `linear-gradient(90deg, ${C.gold}, ${C.teal})` }} />
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold px-2 sm:px-3 py-1 rounded-full"
                        style={{ background: isCompleted ? 'rgba(52,211,153,0.15)' : 'rgba(245,158,11,0.15)', color: isCompleted ? '#34D399' : '#FBBF24' }}>
                        {isCompleted ? 'Completed' : 'In Progress'}
                      </span>
                      <span className="text-xs" style={{ color: C.muted }}>{narrative.total_word_count} words</span>
                    </div>
                    <button onClick={(e) => { e.stopPropagation(); setSelectedNarrative(narrative); }}
                      className="w-full mt-3 sm:mt-4 py-2 rounded-xl text-sm font-bold text-black transition-all hover:scale-[1.02]"
                      style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}>
                      {isCompleted ? 'Read Again' : 'Continue Reading'} <ArrowRight size={14} className="inline ml-1" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {showStoryDialog && (
        <StoryGenerationDialog isOpen={showStoryDialog} onClose={() => setShowStoryDialog(false)} student={studentData} />
      )}

      <OnboardingWizard
        key={wizardKey}
        steps={studentOnboardingSteps}
        portalType="student"
        userId={student?.id || student?.student_code}
      />
    </AppShell>
  );
};

export default StudentAcademy;
