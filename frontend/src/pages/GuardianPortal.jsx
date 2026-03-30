import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import AppShell from '@/components/AppShell';
import { Users, ShoppingBag, TrendingUp, Wallet, Share2, Crown, Shield, Gift, HelpCircle, RotateCcw, Mic, Headphones, CreditCard, Music, Sparkles, Save, Plus, Trash2 } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studentAPI } from '@/lib/api';
import api from '@/lib/api';
import { toast } from 'sonner';
import StudentsTab from '@/components/guardian/StudentsTab';
import MarketplaceTab from '@/components/guardian/MarketplaceTab';
import ProgressTab from '@/components/guardian/ProgressTab';
import WalletTab from '@/components/guardian/WalletTab';
import ReferralTab from '@/components/guardian/ReferralTab';
import SubscriptionTab from '@/components/guardian/SubscriptionTab';
import OffersTab from '@/components/guardian/OffersTab';
import AffiliateTab from '@/components/guardian/AffiliateTab';
import AudioMemoryTab from '@/components/guardian/AudioMemoryTab';
import AudioBookCollection from '@/components/AudioBookCollection';
import UserIDCards from '@/components/guardian/UserIDCards';
import OnboardingWizard from '@/components/OnboardingWizard';
import { guardianOnboardingSteps } from '@/components/onboardingSteps';
import FAQSection from '@/components/FAQSection';
import ParentMediaTab from '@/components/guardian/ParentMediaTab';
import { parentFAQ } from '@/components/faqContent';

const GuardianPortal = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('students');
  const [wizardKey, setWizardKey] = useState(0);

  const handleLogout = () => { logout(); navigate('/login'); };

  const resetOnboarding = () => {
    localStorage.removeItem(`sv_onboarding_guardian_${user?.id || user?.email}`);
    setWizardKey((k) => k + 1);
  };

  const tabs = [
    { id: 'students', label: t('guardian.students'), icon: Users },
    { id: 'marketplace', label: 'Word Bank', icon: ShoppingBag },
    { id: 'audio-memories', label: 'Audio Memories', icon: Mic },
    { id: 'audio-books', label: 'Audio Books', icon: Headphones },
    { id: 'media', label: 'Music & Media', icon: Music },
    { id: 'progress', label: t('guardian.progress'), icon: TrendingUp },
    { id: 'id-cards', label: 'ID Cards', icon: CreditCard },
    { id: 'referral', label: t('guardian.inviteEarn'), icon: Share2 },
    { id: 'subscription', label: 'Subscription', icon: Crown },
    { id: 'wallet', label: t('guardian.wallet'), icon: Wallet },
    { id: 'offers', label: 'Offers', icon: Gift },
    { id: 'affiliate', label: 'Affiliate', icon: Share2 },
    { id: 'life-lessons', label: 'Life Lessons', icon: Sparkles },
    { id: 'faq', label: 'FAQ', icon: HelpCircle },
  ];

  const rightContent = (
    <div className="flex items-center gap-2 flex-wrap">
      {(user?.role === 'admin' || user?.is_delegated_admin) && (
        <button onClick={() => navigate('/admin')}
          className="flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all hover:scale-105"
          style={{ color: '#D4A853', border: '1px solid rgba(212,168,83,0.3)', background: 'rgba(212,168,83,0.08)' }}
          data-testid="admin-link">
          <Shield size={14} /> Admin
        </button>
      )}
      <button onClick={resetOnboarding}
        className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all hover:scale-105"
        style={{ color: '#94A3B8', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.04)' }}
        data-testid="reset-onboarding-btn">
        <RotateCcw size={14} /> Tutorial
      </button>
    </div>
  );

  return (
    <AppShell
      title={t('guardian.portalTitle')}
      subtitle={t('guardian.welcomeUser', { name: user?.full_name })}
      onLogout={handleLogout}
      rightContent={rightContent}
    >
      <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-6">
        {/* Horizontally scrollable tabs */}
        {/* Impersonation Banner */}
        {(() => {
          const savedUser = JSON.parse(localStorage.getItem('user') || '{}');
          if (savedUser?._impersonated) {
            return (
              <div className="mb-4 p-3 border-4 border-amber-500 bg-amber-50 flex items-center justify-between" data-testid="impersonation-banner">
                <p className="font-bold text-sm text-amber-800">
                  Viewing as: <span className="text-amber-900">{savedUser.full_name || savedUser.email}</span> (Admin Preview)
                </p>
                <button onClick={() => {
                  const origToken = localStorage.getItem('admin_original_token');
                  const origUser = localStorage.getItem('admin_original_user');
                  if (origToken && origUser) {
                    localStorage.setItem('token', origToken);
                    localStorage.setItem('user', origUser);
                    localStorage.removeItem('admin_original_token');
                    localStorage.removeItem('admin_original_user');
                    window.location.href = '/admin';
                  }
                }}
                  className="px-4 py-1.5 bg-amber-600 text-white font-bold text-sm border-2 border-black hover:bg-amber-700 transition-all"
                  data-testid="exit-impersonation-btn">
                  Exit to Admin
                </button>
              </div>
            );
          }
          return null;
        })()}

        <div className="mb-4 sm:mb-6 -mx-3 sm:mx-0 px-3 sm:px-0 overflow-x-auto scrollbar-hide">
          <div className="flex gap-1.5 sm:gap-2 pb-2 sm:flex-wrap min-w-max sm:min-w-0">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`sv-tab flex items-center gap-1.5 sm:gap-2 px-3 sm:px-5 py-2 sm:py-2.5 text-xs sm:text-sm font-semibold transition-all whitespace-nowrap flex-shrink-0 sm:flex-shrink ${isActive ? 'sv-tab-active' : ''}`}
                  data-testid={`tab-${tab.id}`}>
                  <Icon size={16} /> {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        <div>
          {activeTab === 'students' && <StudentsTab />}
          {activeTab === 'subscription' && <SubscriptionTab />}
          {activeTab === 'marketplace' && <MarketplaceTab />}
          {activeTab === 'wallet' && <WalletTab />}
          {activeTab === 'referral' && <ReferralTab />}
          {activeTab === 'offers' && <OffersTab />}
          {activeTab === 'affiliate' && <AffiliateTab />}
          {activeTab === 'audio-memories' && <AudioMemoryTab />}
          {activeTab === 'audio-books' && <AudioBookCollection embedded />}
          {activeTab === 'media' && <ParentMediaTab />}
          {activeTab === 'id-cards' && <UserIDCards />}
          {activeTab === 'progress' && <ProgressTab />}
          {activeTab === 'life-lessons' && <LifeLessonsTab />}
          {activeTab === 'faq' && <FAQSection items={parentFAQ} title="Parent & Guardian FAQ" />}
        </div>
      </div>

      <OnboardingWizard
        key={wizardKey}
        steps={guardianOnboardingSteps}
        portalType="guardian"
        userId={user?.id || user?.email}
      />
    </AppShell>
  );
};

/* ============================== Life Lessons Tab ============================== */

const RELATIONSHIP_OPTIONS = [
  { value: 'brother_sister', label: 'Brother/Sister' },
  { value: 'best_friend', label: 'Best Friend' },
  { value: 'classmate', label: 'Classmate' },
  { value: 'bully', label: 'Bully' },
  { value: 'teacher', label: 'Teacher' },
  { value: 'coach', label: 'Coach' },
  { value: 'neighbor', label: 'Neighbor' },
  { value: 'cousin', label: 'Cousin' },
  { value: 'online_friend', label: 'Online Friend' },
  { value: 'other', label: 'Other' },
];

const DELIVERY_METHODS = [
  { value: 'mentor_character', label: 'Through a wise mentor character' },
  { value: 'friend_advice', label: "Through a friend's advice" },
  { value: 'story_moral', label: "Through the story's events" },
  { value: 'inner_voice', label: 'As an inner realization' },
];

const LifeLessonsTab = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [characters, setCharacters] = React.useState([]);
  const [lessons, setLessons] = React.useState([]);
  const [showCharForm, setShowCharForm] = React.useState(false);
  const [showLessonForm, setShowLessonForm] = React.useState(false);
  const [editingCharIdx, setEditingCharIdx] = React.useState(null);
  const [editingLessonIdx, setEditingLessonIdx] = React.useState(null);
  const [saving, setSaving] = React.useState(false);

  // New character form state
  const emptyChar = { id: '', name: '', relationship: 'classmate', relationship_type: 'neutral', description: '', influence_level: 'medium', applies_to: [] };
  const emptyLesson = { id: '', topic: '', character_name: '', problem: '', parent_solution: '', delivery_method: 'story_moral', active: true, applies_to: [] };
  const [charForm, setCharForm] = React.useState({ ...emptyChar });
  const [lessonForm, setLessonForm] = React.useState({ ...emptyLesson });

  // Fetch students
  const { data: students = [], isLoading } = useQuery({
    queryKey: ['students', user?.id],
    queryFn: async () => {
      const response = await studentAPI.getAll(user?.id);
      return response.data;
    },
    enabled: !!user?.id,
  });

  // Load characters & lessons from all students on mount
  React.useEffect(() => {
    if (students.length === 0) return;
    const charMap = {};
    const lessonMap = {};
    students.forEach((s) => {
      (s.life_characters || []).forEach((c) => {
        const key = c.id || c.name;
        if (!charMap[key]) {
          charMap[key] = { ...c, applies_to: [s._id || s.id] };
        } else {
          charMap[key].applies_to = [...new Set([...charMap[key].applies_to, s._id || s.id])];
        }
      });
      (s.life_lessons || []).forEach((l) => {
        const key = l.id || l.topic;
        if (!lessonMap[key]) {
          lessonMap[key] = { ...l, applies_to: [s._id || s.id] };
        } else {
          lessonMap[key].applies_to = [...new Set([...lessonMap[key].applies_to, s._id || s.id])];
        }
      });
    });
    setCharacters(Object.values(charMap));
    setLessons(Object.values(lessonMap));
  }, [students]);

  const studentIds = students.map((s) => s._id || s.id);

  const toggleStudentForChar = (charIdx, studentId) => {
    const updated = [...characters];
    const arr = updated[charIdx].applies_to || [];
    updated[charIdx].applies_to = arr.includes(studentId) ? arr.filter((id) => id !== studentId) : [...arr, studentId];
    setCharacters(updated);
  };

  const toggleStudentForLesson = (lessonIdx, studentId) => {
    const updated = [...lessons];
    const arr = updated[lessonIdx].applies_to || [];
    updated[lessonIdx].applies_to = arr.includes(studentId) ? arr.filter((id) => id !== studentId) : [...arr, studentId];
    setLessons(updated);
  };

  const selectAllStudentsForChar = (charIdx) => {
    const updated = [...characters];
    const allSelected = studentIds.every((id) => (updated[charIdx].applies_to || []).includes(id));
    updated[charIdx].applies_to = allSelected ? [] : [...studentIds];
    setCharacters(updated);
  };

  const selectAllStudentsForLesson = (lessonIdx) => {
    const updated = [...lessons];
    const allSelected = studentIds.every((id) => (updated[lessonIdx].applies_to || []).includes(id));
    updated[lessonIdx].applies_to = allSelected ? [] : [...studentIds];
    setLessons(updated);
  };

  const addCharacter = () => {
    if (!charForm.name.trim()) { toast.error('Character name is required'); return; }
    const newChar = { ...charForm, id: Date.now().toString() };
    setCharacters([...characters, newChar]);
    setCharForm({ ...emptyChar });
    setShowCharForm(false);
  };

  const updateCharacter = () => {
    if (editingCharIdx === null) return;
    const updated = [...characters];
    updated[editingCharIdx] = { ...charForm, applies_to: updated[editingCharIdx].applies_to };
    setCharacters(updated);
    setEditingCharIdx(null);
    setCharForm({ ...emptyChar });
    setShowCharForm(false);
  };

  const deleteCharacter = (idx) => {
    setCharacters(characters.filter((_, i) => i !== idx));
  };

  const addLesson = () => {
    if (!lessonForm.topic.trim()) { toast.error('Lesson topic is required'); return; }
    const newLesson = { ...lessonForm, id: Date.now().toString() };
    setLessons([...lessons, newLesson]);
    setLessonForm({ ...emptyLesson });
    setShowLessonForm(false);
  };

  const updateLesson = () => {
    if (editingLessonIdx === null) return;
    const updated = [...lessons];
    updated[editingLessonIdx] = { ...lessonForm, applies_to: updated[editingLessonIdx].applies_to };
    setLessons(updated);
    setEditingLessonIdx(null);
    setLessonForm({ ...emptyLesson });
    setShowLessonForm(false);
  };

  const deleteLesson = (idx) => {
    setLessons(lessons.filter((_, i) => i !== idx));
  };

  const toggleLessonActive = (idx) => {
    const updated = [...lessons];
    updated[idx].active = !updated[idx].active;
    setLessons(updated);
  };

  const handleSaveAll = async () => {
    setSaving(true);
    try {
      let saved = 0;
      for (const s of students) {
        const sid = s._id || s.id;
        const studentChars = characters.filter((c) => (c.applies_to || []).includes(sid)).map(({ applies_to, ...rest }) => rest);
        const studentLessons = lessons.filter((l) => (l.applies_to || []).includes(sid)).map(({ applies_to, ...rest }) => rest);
        // Always send update — include a dummy field so it's never empty
        await api.patch(`/students/${sid}`, {
          life_characters: studentChars,
          life_lessons: studentLessons,
          full_name: s.full_name,
        });
        saved++;
      }
      queryClient.invalidateQueries({ queryKey: ['students'] });
      toast.success(`Life characters & lessons saved for ${saved} students`);
    } catch (err) {
      toast.error('Failed to save: ' + (err?.response?.data?.detail || err.message));
    }
    setSaving(false);
  };

  const relLabel = (val) => RELATIONSHIP_OPTIONS.find((r) => r.value === val)?.label || val;
  const typeBadge = (t) => {
    if (t === 'positive') return { bg: '#d1fae5', color: '#065f46', label: 'Positive' };
    if (t === 'negative') return { bg: '#fee2e2', color: '#991b1b', label: 'Challenge' };
    return { bg: '#e5e7eb', color: '#374151', label: 'Neutral' };
  };

  if (isLoading) return <div className="text-center py-8 text-gray-400">Loading students...</div>;
  if (students.length === 0) return <div className="text-center py-8 text-gray-400">No students found. Add students first.</div>;

  return (
    <div className="space-y-6">
      {/* ---- Characters Section ---- */}
      <div className="rounded-xl p-5" style={{ background: '#fff', border: '1px solid rgba(0,0,0,0.08)' }}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Sparkles size={20} style={{ color: '#6366f1' }} /> Life Characters
          </h3>
          <button
            onClick={() => { setCharForm({ ...emptyChar }); setEditingCharIdx(null); setShowCharForm(!showCharForm); }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-indigo-100 text-indigo-700 hover:bg-indigo-200 transition-all">
            <Plus size={14} /> Add Character
          </button>
        </div>
        <p className="text-xs mb-4" style={{ color: '#8c8780' }}>
          Add real people in your children's lives. Check which students each character applies to.
        </p>

        {/* Character Form */}
        {showCharForm && (
          <div className="p-4 rounded-lg mb-4" style={{ background: '#f5f3ee', border: '1px solid #e8e5de' }}>
            <p className="text-xs font-bold uppercase mb-3" style={{ color: '#6366f1' }}>
              {editingCharIdx !== null ? 'Edit Character' : 'New Character'}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <input value={charForm.name} onChange={(e) => setCharForm({ ...charForm, name: e.target.value })}
                placeholder="Name" className="px-3 py-2 rounded-lg text-sm border border-gray-300 font-bold bg-white" style={{ color: '#111827' }} />
              <select value={charForm.relationship} onChange={(e) => setCharForm({ ...charForm, relationship: e.target.value })}
                className="px-3 py-2 rounded-lg text-sm border border-gray-300 bg-white" style={{ color: '#111827' }}>
                {RELATIONSHIP_OPTIONS.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
              </select>
            </div>
            <div className="flex gap-2 mb-3">
              {['positive', 'neutral', 'negative'].map((t) => (
                <button key={t} onClick={() => setCharForm({ ...charForm, relationship_type: t })}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${charForm.relationship_type === t
                    ? (t === 'positive' ? 'bg-emerald-500 text-white' : t === 'negative' ? 'bg-red-500 text-white' : 'bg-gray-500 text-white')
                    : 'bg-gray-100 text-gray-500'}`}>
                  {t === 'positive' ? 'Positive' : t === 'negative' ? 'Challenge' : 'Neutral'}
                </button>
              ))}
              <select value={charForm.influence_level} onChange={(e) => setCharForm({ ...charForm, influence_level: e.target.value })}
                className="px-3 py-1.5 rounded-lg text-xs border border-gray-300 ml-auto bg-white" style={{ color: '#111827' }}>
                <option value="low">Low influence</option>
                <option value="medium">Medium influence</option>
                <option value="high">High influence</option>
              </select>
            </div>
            <textarea value={charForm.description} onChange={(e) => setCharForm({ ...charForm, description: e.target.value })}
              placeholder="Brief description (e.g., 'A boy in class who teases him about reading')"
              className="w-full px-3 py-2 rounded-lg text-sm border border-gray-300 resize-none bg-white mb-3" style={{ color: '#111827' }} rows={2} />
            <div className="flex gap-2">
              <button onClick={editingCharIdx !== null ? updateCharacter : addCharacter}
                className="px-4 py-2 rounded-lg text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-700 transition-all flex items-center gap-1.5">
                <Save size={14} /> {editingCharIdx !== null ? 'Update' : 'Add'}
              </button>
              <button onClick={() => { setShowCharForm(false); setEditingCharIdx(null); }}
                className="px-4 py-2 rounded-lg text-xs font-bold bg-gray-200 text-gray-700 hover:bg-gray-300 transition-all">
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Characters Table */}
        {characters.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: '2px solid rgba(0,0,0,0.1)' }}>
                  <th className="text-left py-2 px-2 text-xs font-bold text-gray-500 uppercase">Name</th>
                  <th className="text-left py-2 px-2 text-xs font-bold text-gray-500 uppercase">Relationship</th>
                  <th className="text-left py-2 px-2 text-xs font-bold text-gray-500 uppercase">Type</th>
                  <th className="text-left py-2 px-2 text-xs font-bold text-gray-500 uppercase">Influence</th>
                  {students.map((s) => (
                    <th key={s._id || s.id} className="text-center py-2 px-2 text-xs font-bold text-gray-500 uppercase">{s.full_name || s.name}</th>
                  ))}
                  <th className="text-center py-2 px-2 text-xs font-bold text-gray-500 uppercase">All</th>
                  <th className="text-right py-2 px-2 text-xs font-bold text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                {characters.map((char, idx) => {
                  const badge = typeBadge(char.relationship_type);
                  return (
                    <tr key={char.id || idx} style={{ borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
                      <td className="py-2.5 px-2 font-bold text-gray-900">{char.name}</td>
                      <td className="py-2.5 px-2 text-gray-600">{relLabel(char.relationship)}</td>
                      <td className="py-2.5 px-2">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold" style={{ background: badge.bg, color: badge.color }}>{badge.label}</span>
                      </td>
                      <td className="py-2.5 px-2 text-gray-600 capitalize">{char.influence_level}</td>
                      {students.map((s) => {
                        const sid = s._id || s.id;
                        return (
                          <td key={sid} className="py-2.5 px-2 text-center">
                            <input type="checkbox" checked={(char.applies_to || []).includes(sid)}
                              onChange={() => toggleStudentForChar(idx, sid)}
                              className="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                          </td>
                        );
                      })}
                      <td className="py-2.5 px-2 text-center">
                        <input type="checkbox"
                          checked={studentIds.every((id) => (char.applies_to || []).includes(id))}
                          onChange={() => selectAllStudentsForChar(idx)}
                          className="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                      </td>
                      <td className="py-2.5 px-2 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button onClick={() => { setCharForm({ ...char }); setEditingCharIdx(idx); setShowCharForm(true); }}
                            className="text-xs font-bold text-indigo-600 hover:text-indigo-800 px-2 py-1">Edit</button>
                          <button onClick={() => deleteCharacter(idx)}
                            className="text-xs font-bold text-red-500 hover:text-red-700 px-1 py-1"><Trash2 size={14} /></button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs italic text-center py-4" style={{ color: '#b0aba4' }}>No characters added yet. Click "Add Character" to get started.</p>
        )}
      </div>

      {/* ---- Lessons Section ---- */}
      <div className="rounded-xl p-5" style={{ background: '#fff', border: '1px solid rgba(212,168,83,0.25)' }}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Sparkles size={20} style={{ color: '#D4A853' }} /> Life Lessons
          </h3>
          <button
            onClick={() => { setLessonForm({ ...emptyLesson }); setEditingLessonIdx(null); setShowLessonForm(!showLessonForm); }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-100 text-amber-700 hover:bg-amber-200 transition-all">
            <Plus size={14} /> Add Lesson
          </button>
        </div>
        <p className="text-xs mb-4" style={{ color: '#8c8780' }}>
          Add life lessons you want woven into stories. The AI will deliver your wisdom through trusted story characters so your child absorbs the lesson naturally.
        </p>

        {/* Lesson Form */}
        {showLessonForm && (
          <div className="p-4 rounded-lg mb-4" style={{ background: 'rgba(212,168,83,0.06)', border: '1px solid rgba(212,168,83,0.2)' }}>
            <p className="text-xs font-bold uppercase mb-3" style={{ color: '#D4A853' }}>
              {editingLessonIdx !== null ? 'Edit Lesson' : 'New Lesson'}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <input value={lessonForm.topic} onChange={(e) => setLessonForm({ ...lessonForm, topic: e.target.value })}
                placeholder="Topic (e.g., Dealing with bullies)" className="px-3 py-2 rounded-lg text-sm border border-gray-300 font-bold bg-white" style={{ color: '#111827' }} />
              <select value={lessonForm.character_name} onChange={(e) => setLessonForm({ ...lessonForm, character_name: e.target.value })}
                className="px-3 py-2 rounded-lg text-sm border border-gray-300 bg-white" style={{ color: '#111827' }}>
                <option value="">Related to...</option>
                {characters.map((c) => <option key={c.id} value={c.name}>{c.name}</option>)}
                <option value="general">General life lesson</option>
              </select>
            </div>
            <textarea value={lessonForm.problem} onChange={(e) => setLessonForm({ ...lessonForm, problem: e.target.value })}
              placeholder="The problem (e.g., Marcus teases SJ about reading and calls him a nerd)"
              className="w-full px-3 py-2 rounded-lg text-sm border border-gray-300 resize-none bg-white mb-3" style={{ color: '#111827' }} rows={2} />
            <textarea value={lessonForm.parent_solution} onChange={(e) => setLessonForm({ ...lessonForm, parent_solution: e.target.value })}
              placeholder="Your solution -- what you want your child to learn (e.g., Stand tall, look them in the eye...)"
              className="w-full px-3 py-2 rounded-lg text-sm border border-gray-300 resize-none bg-white mb-3" style={{ color: '#111827' }} rows={3}
              style={{ background: 'rgba(212,168,83,0.08)' }} />
            <div className="flex gap-3 mb-3">
              <select value={lessonForm.delivery_method} onChange={(e) => setLessonForm({ ...lessonForm, delivery_method: e.target.value })}
                className="flex-1 px-3 py-2 rounded-lg text-sm border border-gray-300 bg-white" style={{ color: '#111827' }}>
                {DELIVERY_METHODS.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
              </select>
            </div>
            <div className="flex gap-2">
              <button onClick={editingLessonIdx !== null ? updateLesson : addLesson}
                className="px-4 py-2 rounded-lg text-xs font-bold text-white hover:opacity-90 transition-all flex items-center gap-1.5"
                style={{ background: '#D4A853' }}>
                <Save size={14} /> {editingLessonIdx !== null ? 'Update' : 'Add'}
              </button>
              <button onClick={() => { setShowLessonForm(false); setEditingLessonIdx(null); }}
                className="px-4 py-2 rounded-lg text-xs font-bold bg-gray-200 text-gray-700 hover:bg-gray-300 transition-all">
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Lessons Table */}
        {lessons.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: '2px solid rgba(212,168,83,0.3)' }}>
                  <th className="text-left py-2 px-2 text-xs font-bold text-gray-500 uppercase">Topic</th>
                  <th className="text-left py-2 px-2 text-xs font-bold text-gray-500 uppercase">Character</th>
                  <th className="text-left py-2 px-2 text-xs font-bold text-gray-500 uppercase">Problem</th>
                  <th className="text-left py-2 px-2 text-xs font-bold text-gray-500 uppercase">Method</th>
                  {students.map((s) => (
                    <th key={s._id || s.id} className="text-center py-2 px-2 text-xs font-bold text-gray-500 uppercase">{s.full_name || s.name}</th>
                  ))}
                  <th className="text-center py-2 px-2 text-xs font-bold text-gray-500 uppercase">All</th>
                  <th className="text-center py-2 px-2 text-xs font-bold text-gray-500 uppercase">Active</th>
                  <th className="text-right py-2 px-2 text-xs font-bold text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                {lessons.map((lesson, idx) => (
                  <tr key={lesson.id || idx} style={{ borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
                    <td className="py-2.5 px-2 font-bold text-gray-900">{lesson.topic}</td>
                    <td className="py-2.5 px-2 text-gray-600">{lesson.character_name || '--'}</td>
                    <td className="py-2.5 px-2 text-gray-600 max-w-[150px] truncate">{lesson.problem || '--'}</td>
                    <td className="py-2.5 px-2 text-gray-600 text-xs">
                      {DELIVERY_METHODS.find((m) => m.value === lesson.delivery_method)?.label || lesson.delivery_method}
                    </td>
                    {students.map((s) => {
                      const sid = s._id || s.id;
                      return (
                        <td key={sid} className="py-2.5 px-2 text-center">
                          <input type="checkbox" checked={(lesson.applies_to || []).includes(sid)}
                            onChange={() => toggleStudentForLesson(idx, sid)}
                            className="w-4 h-4 rounded border-gray-300 text-amber-600 focus:ring-amber-500" />
                        </td>
                      );
                    })}
                    <td className="py-2.5 px-2 text-center">
                      <input type="checkbox"
                        checked={studentIds.every((id) => (lesson.applies_to || []).includes(id))}
                        onChange={() => selectAllStudentsForLesson(idx)}
                        className="w-4 h-4 rounded border-gray-300 text-amber-600 focus:ring-amber-500" />
                    </td>
                    <td className="py-2.5 px-2 text-center">
                      <button onClick={() => toggleLessonActive(idx)}
                        className={`px-2 py-1 rounded text-[10px] font-bold ${lesson.active ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-200 text-gray-500'}`}>
                        {lesson.active ? 'Active' : 'Inactive'}
                      </button>
                    </td>
                    <td className="py-2.5 px-2 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => { setLessonForm({ ...lesson }); setEditingLessonIdx(idx); setShowLessonForm(true); }}
                          className="text-xs font-bold text-amber-600 hover:text-amber-800 px-2 py-1">Edit</button>
                        <button onClick={() => deleteLesson(idx)}
                          className="text-xs font-bold text-red-500 hover:text-red-700 px-1 py-1"><Trash2 size={14} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs italic text-center py-4" style={{ color: '#b0aba4' }}>No lessons added yet. Click "Add Lesson" to get started.</p>
        )}
      </div>

      {/* Save All Button */}
      <div className="flex justify-end">
        <button onClick={handleSaveAll} disabled={saving}
          className="flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold text-white transition-all hover:opacity-90 disabled:opacity-50"
          style={{ background: 'linear-gradient(135deg, #6366f1, #D4A853)' }}>
          <Save size={16} />
          {saving ? 'Saving...' : 'Save All Characters & Lessons'}
        </button>
      </div>
    </div>
  );
};

export default GuardianPortal;
