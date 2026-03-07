import React, { useState } from 'react';
import { useNavigate, Routes, Route } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton, BrutalCard } from '@/components/brutal';
import { LogOut, Users, ShoppingBag, TrendingUp, Home } from 'lucide-react';
import StudentsTab from '@/components/guardian/StudentsTab';
import MarketplaceTab from '@/components/guardian/MarketplaceTab';
import ProgressTab from '@/components/guardian/ProgressTab';

const GuardianPortal = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('students');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const tabs = [
    { id: 'students', label: 'Students', icon: Users, color: 'indigo' },
    { id: 'marketplace', label: 'Marketplace', icon: ShoppingBag, color: 'emerald' },
    { id: 'progress', label: 'Progress', icon: TrendingUp, color: 'amber' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b-6 border-black brutal-shadow-md">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="p-3 border-4 border-black bg-indigo-100 brutal-shadow-sm hover:brutal-shadow-md transition-all brutal-active"
                title="Home"
              >
                <Home size={24} />
              </button>
              <div>
                <h1 className="text-4xl font-black uppercase">LexiMaster Portal</h1>
                <p className="text-lg font-medium mt-1">Welcome, {user?.full_name}!</p>
              </div>
            </div>
            <div className="flex gap-2">
              <BrutalButton
                variant="default"
                size="sm"
                onClick={() => navigate('/admin')}
                className="flex items-center gap-1"
                data-testid="admin-link"
              >
                Admin
              </BrutalButton>
              <BrutalButton
                variant="dark"
                onClick={handleLogout}
                className="flex items-center gap-2"
              >
                <LogOut size={20} />
                Logout
              </BrutalButton>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
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
              >
                <Icon size={24} />
                {tab.label}
              </BrutalButton>
            );
          })}
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'students' && <StudentsTab />}
          {activeTab === 'marketplace' && <MarketplaceTab />}
          {activeTab === 'progress' && <ProgressTab />}
        </div>
      </div>
    </div>
  );
};

export default GuardianPortal;
