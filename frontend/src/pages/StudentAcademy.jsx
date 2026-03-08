import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useQuery } from '@tanstack/react-query';
import { studentAPI, narrativeAPI, classroomAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalProgress, BrutalInput } from '@/components/brutal';
import { BookOpen, Plus, LogOut, TrendingUp, Clock, BookMarked, Home, Users } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import StoryGenerationDialog from '@/components/student/StoryGenerationDialog';
import NarrativeReader from '@/components/student/NarrativeReader';

const StudentAcademy = () => {
  const { student, studentLogout } = useAuth();
  const navigate = useNavigate();
  const [showStoryDialog, setShowStoryDialog] = useState(false);
  const [selectedNarrative, setSelectedNarrative] = useState(null);
  const [sessionCode, setSessionCode] = useState('');
  const [joiningSession, setJoiningSession] = useState(false);
  const [joinedSession, setJoinedSession] = useState(null);

  // Fetch full student data
  const { data: studentData, isLoading: studentLoading } = useQuery({
    queryKey: ['student-detail', student?.id],
    queryFn: async () => {
      const response = await studentAPI.getById(student?.id);
      return response.data;
    },
    enabled: !!student?.id
  });

  // Fetch narratives
  const { data: narratives = [], isLoading: narrativesLoading } = useQuery({
    queryKey: ['student-narratives', student?.id],
    queryFn: async () => {
      const response = await narrativeAPI.getAll(student?.id);
      return response.data;
    },
    enabled: !!student?.id
  });

  const handleLogout = () => {
    studentLogout();
    navigate('/student-login');
  };

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
      toast.error(err.response?.data?.detail || 'Could not join session. Check the code and try again.');
    }
    setJoiningSession(false);
  };

  if (studentLoading) {
    return <div className="min-h-screen flex items-center justify-center text-2xl font-bold">Loading...</div>;
  }

  // If reading a narrative
  if (selectedNarrative) {
    return (
      <NarrativeReader
        narrative={selectedNarrative}
        student={studentData}
        onClose={() => setSelectedNarrative(null)}
      />
    );
  }

  const canGenerateStory = studentData?.assigned_banks && studentData.assigned_banks.length > 0;
  const masteredCount = studentData?.mastered_tokens?.length || 0;
  const biologicalTarget = studentData?.biological_target || 1000;
  const agenticScore = studentData?.agentic_reach_score || 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-yellow-50">
      {/* Header */}
      <header className="bg-white border-b-6 border-black brutal-shadow-md">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="p-3 border-4 border-black bg-amber-100 brutal-shadow-sm hover:brutal-shadow-md transition-all brutal-active"
                title="Home"
              >
                <Home size={24} />
              </button>
              <div>
                <h1 className="text-4xl font-black uppercase">Semantic Vision Academy</h1>
                <p className="text-xl font-bold mt-1">Welcome, {studentData?.full_name}!</p>
              </div>
            </div>
            <BrutalButton
              variant="rose"
              onClick={handleLogout}
              className="flex items-center gap-2"
            >
              <LogOut size={20} />
              Logout
            </BrutalButton>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Dashboard */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Mastered Vocabulary */}
          <BrutalCard variant="indigo" shadow="xl">
            <div className="flex items-center gap-4 mb-4">
              <BookMarked size={48} className="text-indigo-600" />
              <div>
                <p className="text-xs font-bold uppercase text-gray-600">Vocabulary Mastered</p>
                <p className="text-4xl font-black">{masteredCount}</p>
              </div>
            </div>
            <BrutalProgress
              value={masteredCount}
              max={biologicalTarget}
              variant="indigo"
              showLabel
            />
            <p className="mt-2 text-sm font-medium">
              Target: {biologicalTarget} words (age {studentData?.age})
            </p>
          </BrutalCard>

          {/* Agentic Reach Score */}
          <BrutalCard variant="emerald" shadow="xl">
            <div className="flex items-center gap-4">
              <TrendingUp size={48} className="text-emerald-600" />
              <div>
                <p className="text-xs font-bold uppercase text-gray-600">Agentic Reach Score</p>
                <p className="text-4xl font-black">{Math.round(agenticScore)}</p>
                <p className="text-sm font-medium mt-1">
                  {agenticScore < 100 && 'Initiate'}
                  {agenticScore >= 100 && agenticScore < 300 && 'Apprentice'}
                  {agenticScore >= 300 && agenticScore < 600 && 'Adept'}
                  {agenticScore >= 600 && agenticScore < 1000 && 'Expert'}
                  {agenticScore >= 1000 && agenticScore < 1500 && 'Master'}
                  {agenticScore >= 1500 && 'Grandmaster'}
                </p>
              </div>
            </div>
          </BrutalCard>

          {/* Reading Stats */}
          <BrutalCard variant="amber" shadow="xl">
            <div className="flex items-center gap-4">
              <Clock size={48} className="text-amber-600" />
              <div>
                <p className="text-xs font-bold uppercase text-gray-600">Reading Time</p>
                <p className="text-4xl font-black">
                  {Math.floor((studentData?.total_reading_seconds || 0) / 60)}
                </p>
                <p className="text-sm font-medium mt-1">minutes</p>
                <p className="text-xs font-medium">
                  {studentData?.average_wpm || 0} WPM average
                </p>
              </div>
            </div>
          </BrutalCard>
        </div>

        {/* Join Classroom Session */}
        <div className="mb-8">
          <BrutalCard shadow="lg" variant="emerald">
            <div className="flex items-center gap-4 flex-wrap">
              <div className="flex items-center gap-3">
                <Users size={32} className="text-teal-600" />
                <div>
                  <h3 className="text-xl font-black uppercase">Join Classroom Session</h3>
                  <p className="text-sm font-medium text-gray-600">Enter the code from your teacher</p>
                </div>
              </div>
              <form onSubmit={handleJoinSession} className="flex items-center gap-2 ml-auto">
                <input
                  type="text"
                  value={sessionCode}
                  onChange={(e) => setSessionCode(e.target.value)}
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                  className="border-4 border-black px-4 py-2 font-mono font-bold text-lg text-center w-44 brutal-shadow-sm"
                  data-testid="session-code-input"
                />
                <BrutalButton
                  type="submit"
                  variant="dark"
                  disabled={joiningSession || sessionCode.length < 6}
                  data-testid="join-session-btn"
                >
                  {joiningSession ? 'Joining...' : 'Join'}
                </BrutalButton>
              </form>
            </div>
            {joinedSession && (
              <div className="mt-4 pt-4 border-t-4 border-black" data-testid="joined-session-info">
                <p className="font-bold text-lg text-emerald-700">
                  Joined: {joinedSession.title}
                </p>
              </div>
            )}
          </BrutalCard>
        </div>

        {/* Story Generation */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-3xl font-black uppercase">Your Stories</h2>
            <BrutalButton
              variant="indigo"
              size="lg"
              onClick={() => setShowStoryDialog(true)}
              disabled={!canGenerateStory}
              className="flex items-center gap-2"
            >
              <Plus size={24} />
              Create New Story
            </BrutalButton>
          </div>

          {!canGenerateStory && (
            <BrutalCard variant="amber" className="mb-6">
              <p className="font-bold text-lg">
                ⚠️ No word banks assigned! Ask your guardian to assign word banks to your account before generating stories.
              </p>
            </BrutalCard>
          )}

          {/* Narratives Grid */}
          {narratives.length === 0 ? (
            <BrutalCard shadow="xl" className="text-center py-16">
              <BookOpen size={64} className="mx-auto mb-6 text-indigo-600" />
              <p className="text-2xl font-bold mb-4">No stories yet</p>
              <p className="text-lg font-medium mb-6">
                Create your first AI-generated story and start learning!
              </p>
              {canGenerateStory && (
                <BrutalButton
                  variant="indigo"
                  size="lg"
                  onClick={() => setShowStoryDialog(true)}
                  className="flex items-center gap-2 mx-auto"
                >
                  <Plus size={24} />
                  Create Your First Story
                </BrutalButton>
              )}
            </BrutalCard>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {narratives.map((narrative) => {
                const progress = (narrative.chapters_completed?.length || 0) / 5 * 100;
                const isCompleted = narrative.status === 'completed';

                return (
                  <BrutalCard
                    key={narrative.id}
                    shadow="lg"
                    hover
                    className="cursor-pointer"
                    onClick={() => setSelectedNarrative(narrative)}
                  >
                    <div className="mb-4">
                      <h3 className="text-xl font-black uppercase mb-2">{narrative.title}</h3>
                      <p className="text-sm font-medium text-gray-600 line-clamp-2">
                        {narrative.theme}
                      </p>
                    </div>

                    <div className="mb-4">
                      <p className="text-xs font-bold uppercase text-gray-600 mb-1">Progress</p>
                      <BrutalProgress
                        value={narrative.chapters_completed?.length || 0}
                        max={5}
                        variant="indigo"
                        showLabel
                        size="sm"
                      />
                    </div>

                    <div className="flex items-center justify-between mb-4">
                      <BrutalBadge variant={isCompleted ? 'emerald' : 'amber'} size="sm">
                        {isCompleted ? 'Completed' : 'In Progress'}
                      </BrutalBadge>
                      <p className="text-sm font-bold">
                        {narrative.total_word_count} words
                      </p>
                    </div>

                    <BrutalButton
                      variant="indigo"
                      size="sm"
                      fullWidth
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedNarrative(narrative);
                      }}
                    >
                      {isCompleted ? 'Read Again' : 'Continue Reading'}
                    </BrutalButton>
                  </BrutalCard>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Story Generation Dialog */}
      {showStoryDialog && (
        <StoryGenerationDialog
          isOpen={showStoryDialog}
          onClose={() => setShowStoryDialog(false)}
          student={studentData}
        />
      )}
    </div>
  );
};

export default StudentAcademy;
