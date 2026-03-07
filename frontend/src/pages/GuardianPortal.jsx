import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton } from '@/components/brutal';
import { LogOut, Users, ShoppingBag, TrendingUp, Home, Wallet, Share2 } from 'lucide-react';
import StudentsTab from '@/components/guardian/StudentsTab';
import MarketplaceTab from '@/components/guardian/MarketplaceTab';
import ProgressTab from '@/components/guardian/ProgressTab';
import WalletTab from '@/components/guardian/WalletTab';
import ReferralTab from '@/components/guardian/ReferralTab';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const GuardianPortal = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('students');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const tabs = [
    { id: 'students', label: t('guardian.students'), icon: Users, color: 'indigo' },
    { id: 'marketplace', label: t('guardian.marketplace'), icon: ShoppingBag, color: 'emerald' },
    { id: 'wallet', label: t('guardian.wallet'), icon: Wallet, color: 'amber' },
    { id: 'referral', label: t('guardian.inviteEarn'), icon: Share2, color: 'rose' },
    { id: 'progress', label: t('guardian.progress'), icon: TrendingUp, color: 'rose' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b-6 border-black brutal-shadow-md">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/')} className="p-3 border-4 border-black bg-indigo-100 brutal-shadow-sm hover:brutal-shadow-md transition-all brutal-active" title={t('common.home')}>
                <Home size={24} />
              </button>
              <div>
                <h1 className="text-4xl font-black uppercase" data-testid="portal-title">{t('guardian.portalTitle')}</h1>
                <p className="text-lg font-medium mt-1" data-testid="welcome-user">{t('guardian.welcomeUser', { name: user?.full_name })}</p>
              </div>
            </div>
            <div className="flex gap-2 items-center">
              <LanguageSwitcher />
              <BrutalButton variant="default" size="sm" onClick={() => navigate('/admin')} data-testid="admin-link">{t('common.admin')}</BrutalButton>
              <BrutalButton variant="dark" onClick={handleLogout} className="flex items-center gap-2">
                <LogOut size={20} />
                {t('common.logout')}
              </BrutalButton>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="flex gap-4 mb-8 flex-wrap">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <BrutalButton key={tab.id} variant={isActive ? tab.color : 'default'} size="lg" onClick={() => setActiveTab(tab.id)} className="flex items-center gap-2" data-testid={`tab-${tab.id}`}>
                <Icon size={24} />
                {tab.label}
              </BrutalButton>
            );
          })}
        </div>

        <div>
          {activeTab === 'students' && <StudentsTab />}
          {activeTab === 'marketplace' && <MarketplaceTab />}
          {activeTab === 'wallet' && <WalletTab />}
          {activeTab === 'referral' && <ReferralTab />}
          {activeTab === 'progress' && <ProgressTab />}
        </div>
      </div>
    </div>
  );
};

export default GuardianPortal;
