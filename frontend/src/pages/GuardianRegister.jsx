import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { Eye, Heart, Megaphone, BookOpen, Gift } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const C = {
  bg: '#0A0F1E', surface: '#111827', card: '#1A2236',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8', white: '#FFFFFF',
};

const ROLES = [
  { id: 'parent', label: 'Parents', icon: Heart, color: '#D4A853', bg: 'rgba(212,168,83,0.10)', apiRole: 'guardian' },
  { id: 'teacher', label: 'Teachers', icon: BookOpen, color: '#A78BFA', bg: 'rgba(167,139,250,0.10)', apiRole: 'teacher' },
  { id: 'brand', label: 'Brands', icon: Megaphone, color: '#F472B6', bg: 'rgba(244,114,182,0.10)', apiRole: 'brand_partner' },
];

const inputStyle = {
  background: 'rgba(255,255,255,0.06)',
  border: '1px solid rgba(255,255,255,0.1)',
  color: C.cream,
};

const GuardianRegister = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const { register } = useAuth();

  const roleParam = searchParams.get('role');
  const initialRole = roleParam === 'brand_partner' ? 'brand' : roleParam === 'teacher' ? 'teacher' : 'parent';

  const [activeRole, setActiveRole] = useState(initialRole);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    referralCode: searchParams.get('ref') || '',
  });
  const [loading, setLoading] = useState(false);

  const activeConfig = ROLES.find(r => r.id === activeRole);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      toast.error(t('auth.passwordMismatch'));
      return;
    }
    if (formData.password.length < 6) {
      toast.error(t('auth.passwordTooShort'));
      return;
    }
    setLoading(true);
    const result = await register(
      formData.fullName, formData.email, formData.password,
      activeRole === 'parent' ? (formData.referralCode || undefined) : undefined,
      activeConfig.apiRole
    );
    if (result.success) {
      if (activeRole === 'brand') {
        toast.success(t('auth.brandPartnerCreated'));
        navigate('/brand-portal');
      } else if (activeRole === 'teacher') {
        toast.success(t('auth.teacherAccountCreated'));
        navigate('/teacher-portal');
      } else {
        toast.success(formData.referralCode ? t('auth.referralApplied') : t('auth.accountCreated'));
        navigate('/portal');
      }
    } else {
      toast.error(result.error || t('auth.registrationFailed'));
    }
    setLoading(false);
  };

  const titles = {
    parent: { heading: t('auth.createAccount'), sub: t('auth.startVocabJourney') },
    teacher: { heading: t('auth.teacherRegistration'), sub: t('auth.createClassroomAccount') },
    brand: { heading: t('auth.brandPartnerReg'), sub: t('auth.brandPartnerDesc') },
  };

  const placeholders = {
    parent: { name: 'John Doe', email: 'parent@example.com' },
    teacher: { name: 'Ms. Johnson', email: 'teacher@school.edu' },
    brand: { name: 'Company Name', email: 'brand@company.com' },
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: C.bg, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4" style={{ borderBottom: '1px solid rgba(212,168,83,0.12)' }}>
        <button onClick={() => navigate('/')} className="flex items-center gap-3 group" data-testid="nav-logo">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }}>
            <Eye size={22} className="text-black" />
          </div>
          <span className="text-xl font-bold tracking-tight" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>
            {t('landing.title')}
          </span>
        </button>
        <LanguageSwitcher />
      </nav>

      {/* Form */}
      <div className="flex-1 flex items-center justify-center p-4 py-8">
        <div className="w-full max-w-md p-8 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>

          {/* Role Selector at TOP */}
          <div className="mb-6">
            <p className="text-xs font-semibold uppercase tracking-wide text-center mb-3" style={{ color: C.muted }}>
              I am a...
            </p>
            <div className="grid grid-cols-3 gap-2" data-testid="register-role-selector">
              {ROLES.map((role) => {
                const Icon = role.icon;
                const isActive = activeRole === role.id;
                return (
                  <button
                    key={role.id}
                    type="button"
                    onClick={() => setActiveRole(role.id)}
                    className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-all hover:scale-105"
                    style={{
                      background: isActive ? `${role.color}20` : 'rgba(255,255,255,0.03)',
                      border: isActive ? `2px solid ${role.color}` : '1px solid rgba(255,255,255,0.08)',
                      transform: isActive ? 'scale(1.05)' : 'scale(1)',
                    }}
                    data-testid={`register-role-${role.id}`}
                  >
                    <Icon size={20} style={{ color: isActive ? role.color : C.muted }} />
                    <span className="text-xs font-semibold" style={{ color: isActive ? role.color : C.muted }}>
                      {role.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Dynamic Header */}
          <div className="text-center mb-6">
            <div
              className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-3 transition-all"
              style={{ background: `${activeConfig.color}20` }}
            >
              <activeConfig.icon size={28} style={{ color: activeConfig.color }} />
            </div>
            <h2 className="text-xl font-bold" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }} data-testid="register-title">
              {titles[activeRole].heading}
            </h2>
            <p className="mt-1 text-sm" style={{ color: C.muted }}>{titles[activeRole].sub}</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.fullName')}</label>
              <input type="text" required value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                placeholder={placeholders[activeRole].name}
                className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2"
                style={inputStyle} data-testid="register-name" />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.email')}</label>
              <input type="email" required value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder={placeholders[activeRole].email}
                className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2"
                style={inputStyle} data-testid="register-email" />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.password')}</label>
              <input type="password" required value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Min 6 characters"
                className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2"
                style={inputStyle} data-testid="register-password" />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.confirmPassword')}</label>
              <input type="password" required value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                placeholder="Confirm password"
                className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2"
                style={inputStyle} data-testid="register-confirm-password" />
            </div>

            {/* Referral code — only for parents */}
            {activeRole === 'parent' && (
              <div className="p-4 rounded-xl" style={{
                background: formData.referralCode ? 'rgba(16,185,129,0.08)' : 'transparent',
                border: formData.referralCode ? '1px solid rgba(16,185,129,0.3)' : 'none',
              }}>
                <label className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>
                  <Gift size={14} style={{ color: C.teal }} /> {t('auth.referralCode')} ({t('common.optional')})
                </label>
                <input type="text" value={formData.referralCode}
                  onChange={(e) => setFormData({ ...formData, referralCode: e.target.value.toUpperCase() })}
                  placeholder="REF-XXXXXX"
                  className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2"
                  style={inputStyle} data-testid="referral-code-input" />
                {formData.referralCode && (
                  <p className="text-xs font-semibold mt-2" style={{ color: '#10B981' }}>{t('auth.referralBonus')}</p>
                )}
              </div>
            )}

            <button type="submit" disabled={loading}
              className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all duration-300 hover:scale-[1.02] hover:shadow-lg disabled:opacity-50 mt-2"
              style={{ background: `linear-gradient(135deg, ${activeConfig.color}, ${C.goldLight})` }}
              data-testid="register-submit">
              {loading ? t('common.creatingAccount') : t('common.register')}
            </button>

            <div className="text-center pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <p className="text-sm" style={{ color: C.muted }}>
                {t('common.hasAccount')}{' '}
                <Link
                  to={activeRole === 'brand' ? '/login?type=brand' : activeRole === 'teacher' ? '/login?type=teacher' : '/login'}
                  className="font-semibold hover:underline"
                  style={{ color: C.gold }}
                  data-testid="login-link"
                >
                  {t('common.loginHere')}
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default GuardianRegister;
