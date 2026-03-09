import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import AppShell from '@/components/AppShell';
import { Users, ShoppingBag, TrendingUp, Wallet, Share2, Crown, Shield, Gift } from 'lucide-react';
import StudentsTab from '@/components/guardian/StudentsTab';
import MarketplaceTab from '@/components/guardian/MarketplaceTab';
import ProgressTab from '@/components/guardian/ProgressTab';
import WalletTab from '@/components/guardian/WalletTab';
import ReferralTab from '@/components/guardian/ReferralTab';
import SubscriptionTab from '@/components/guardian/SubscriptionTab';
import OffersTab from '@/components/guardian/OffersTab';

const GuardianPortal = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('students');

  const handleLogout = () => { logout(); navigate('/login'); };

  const tabs = [
    { id: 'students', label: t('guardian.students'), icon: Users },
    { id: 'subscription', label: 'Subscription', icon: Crown },
    { id: 'marketplace', label: t('guardian.marketplace'), icon: ShoppingBag },
    { id: 'wallet', label: t('guardian.wallet'), icon: Wallet },
    { id: 'referral', label: t('guardian.inviteEarn'), icon: Share2 },
    { id: 'offers', label: 'Offers', icon: Gift },
    { id: 'progress', label: t('guardian.progress'), icon: TrendingUp },
  ];

  const adminBtn = user?.role === 'admin' ? (
    <button onClick={() => navigate('/admin')}
      className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all hover:scale-105"
      style={{ color: '#D4A853', border: '1px solid rgba(212,168,83,0.3)', background: 'rgba(212,168,83,0.08)' }}
      data-testid="admin-link">
      <Shield size={16} /> Admin
    </button>
  ) : null;

  return (
    <AppShell
      title={t('guardian.portalTitle')}
      subtitle={t('guardian.welcomeUser', { name: user?.full_name })}
      onLogout={handleLogout}
      rightContent={adminBtn}
    >
      <div className="container mx-auto px-4 py-6">
        {/* Tab Bar */}
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

        {/* Tab Content */}
        <div>
          {activeTab === 'students' && <StudentsTab />}
          {activeTab === 'subscription' && <SubscriptionTab />}
          {activeTab === 'marketplace' && <MarketplaceTab />}
          {activeTab === 'wallet' && <WalletTab />}
          {activeTab === 'referral' && <ReferralTab />}
          {activeTab === 'offers' && <OffersTab />}
          {activeTab === 'progress' && <ProgressTab />}
        </div>
      </div>
    </AppShell>
  );
};

export default GuardianPortal;
