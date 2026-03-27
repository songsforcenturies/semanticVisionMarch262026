import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import AppShell from '@/components/AppShell';
import { Users, BarChart3, HelpCircle } from 'lucide-react';
import SessionsTab from '@/components/teacher/SessionsTab';
import ClassAnalyticsTab from '@/components/teacher/ClassAnalyticsTab';
import FAQSection from '@/components/FAQSection';
import { teacherFAQ } from '@/components/faqContent';

const TeacherPortal = () => {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('sessions');

  const handleLogout = () => { logout(); navigate('/login?type=teacher'); };

  const tabs = [
    { id: 'sessions', label: t('teacher.sessions'), icon: Users },
    { id: 'analytics', label: t('teacher.analytics'), icon: BarChart3 },
    { id: 'faq', label: t('teacher.faq'), icon: HelpCircle },
  ];

  return (
    <AppShell
      title={t('teacher.portal')}
      subtitle={`${t('common.welcome')}, ${user?.full_name}!`}
      onLogout={handleLogout}
    >
      <div className="container mx-auto px-4 py-6" data-testid="teacher-portal">
        <div className="flex gap-2 mb-6 flex-wrap">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`sv-tab flex items-center gap-2 px-5 py-2.5 text-sm font-semibold transition-all ${isActive ? 'sv-tab-active' : ''}`}
                data-testid={`tab-${tab.id}`}>
                <Icon size={18} /> {tab.label}
              </button>
            );
          })}
        </div>
        <div>
          {activeTab === 'sessions' && <SessionsTab />}
          {activeTab === 'analytics' && <ClassAnalyticsTab />}
          {activeTab === 'faq' && <FAQSection items={teacherFAQ} title={t('teacher.teacherFaq')} />}
        </div>
      </div>
    </AppShell>
  );
};

export default TeacherPortal;
