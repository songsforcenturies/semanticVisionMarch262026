import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton } from '@/components/brutal';
import { LogOut, Users, BarChart3, Home, GraduationCap } from 'lucide-react';
import SessionsTab from '@/components/teacher/SessionsTab';
import ClassAnalyticsTab from '@/components/teacher/ClassAnalyticsTab';

const TeacherPortal = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('sessions');

  const handleLogout = () => {
    logout();
    navigate('/teacher-login');
  };

  const tabs = [
    { id: 'sessions', label: 'Sessions', icon: Users, color: 'emerald' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, color: 'indigo' },
  ];

  return (
    <div className="min-h-screen bg-gray-50" data-testid="teacher-portal">
      <header className="bg-white border-b-6 border-black brutal-shadow-md">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="p-3 border-4 border-black bg-teal-100 brutal-shadow-sm hover:brutal-shadow-md transition-all brutal-active"
                title="Home"
              >
                <Home size={24} />
              </button>
              <div>
                <h1 className="text-4xl font-black uppercase flex items-center gap-2">
                  <GraduationCap size={32} className="text-teal-600" /> Teacher Portal
                </h1>
                <p className="text-lg font-medium mt-1">Welcome, {user?.full_name}!</p>
              </div>
            </div>
            <BrutalButton variant="dark" onClick={handleLogout} className="flex items-center gap-2">
              <LogOut size={20} /> Logout
            </BrutalButton>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="flex gap-4 mb-8 flex-wrap">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <BrutalButton
                key={tab.id}
                variant={isActive ? tab.color : 'default'}
                size="lg"
                onClick={() => setActiveTab(tab.id)}
                className="flex items-center gap-2"
                data-testid={`tab-${tab.id}`}
              >
                <Icon size={24} />
                {tab.label}
              </BrutalButton>
            );
          })}
        </div>

        <div>
          {activeTab === 'sessions' && <SessionsTab />}
          {activeTab === 'analytics' && <ClassAnalyticsTab />}
        </div>
      </div>
    </div>
  );
};

export default TeacherPortal;
