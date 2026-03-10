import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import AppShell from '@/components/AppShell';
import { Users, ShoppingBag, TrendingUp, Wallet, Share2, Crown, Shield, Gift, HelpCircle, RotateCcw, Mic, Headphones } from 'lucide-react';
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
import OnboardingWizard from '@/components/OnboardingWizard';
import { guardianOnboardingSteps } from '@/components/onboardingSteps';
import FAQSection from '@/components/FAQSection';
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
    { id: 'subscription', label: 'Subscription', icon: Crown },
    { id: 'marketplace', label: t('guardian.marketplace'), icon: ShoppingBag },
    { id: 'wallet', label: t('guardian.wallet'), icon: Wallet },
    { id: 'referral', label: t('guardian.inviteEarn'), icon: Share2 },
    { id: 'offers', label: 'Offers', icon: Gift },
    { id: 'affiliate', label: 'Affiliate', icon: Share2 },
    { id: 'audio-memories', label: 'Audio Memories', icon: Mic },
    { id: 'audio-books', label: 'Audio Books', icon: Headphones },
    { id: 'progress', label: t('guardian.progress'), icon: TrendingUp },
    { id: 'faq', label: 'FAQ', icon: HelpCircle },
  ];

  const rightContent = (
    <div className="flex items-center gap-2">
      {user?.role === 'admin' && (
        <button onClick={() => navigate('/admin')}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all hover:scale-105"
          style={{ color: '#D4A853', border: '1px solid rgba(212,168,83,0.3)', background: 'rgba(212,168,83,0.08)' }}
          data-testid="admin-link">
          <Shield size={16} /> Admin
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
      <div className="container mx-auto px-4 py-6">
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
          {activeTab === 'students' && <StudentsTab />}
          {activeTab === 'subscription' && <SubscriptionTab />}
          {activeTab === 'marketplace' && <MarketplaceTab />}
          {activeTab === 'wallet' && <WalletTab />}
          {activeTab === 'referral' && <ReferralTab />}
          {activeTab === 'offers' && <OffersTab />}
          {activeTab === 'affiliate' && <AffiliateTab />}
          {activeTab === 'audio-memories' && <AudioMemoryTab />}
          {activeTab === 'audio-books' && <AudioBookCollection embedded />}
          {activeTab === 'progress' && <ProgressTab />}
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

export default GuardianPortal;
