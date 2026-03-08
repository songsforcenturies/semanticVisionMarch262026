import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { Eye, Gift, Megaphone, GraduationCap, Heart } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const C = {
  bg: '#0A0F1E', surface: '#111827', card: '#1A2236',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8', white: '#FFFFFF',
};

const GuardianRegister = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const { register } = useAuth();
  const roleParam = searchParams.get('role');
  const isBrandPartner = roleParam === 'brand_partner';
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    referralCode: searchParams.get('ref') || '',
  });
  const [loading, setLoading] = useState(false);

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
      formData.referralCode || undefined,
      isBrandPartner ? 'brand_partner' : 'guardian'
    );
    if (result.success) {
      if (isBrandPartner) {
        toast.success(t('auth.brandPartnerCreated'));
        navigate('/brand-portal');
      } else {
        toast.success(formData.referralCode ? t('auth.referralApplied') : t('auth.accountCreated'));
        navigate('/portal');
      }
    } else {
      toast.error(result.error || t('auth.registrationFailed'));
    }
    setLoading(false);
  };

  const inputStyle = {
    background: 'rgba(255,255,255,0.06)',
    border: '1px solid rgba(255,255,255,0.1)',
    color: C.cream,
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
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4" style={{ background: isBrandPartner ? `linear-gradient(135deg, #F472B6, ${C.gold})` : `linear-gradient(135deg, ${C.gold}, ${C.teal})` }}>
              {isBrandPartner ? <Megaphone size={32} className="text-black" /> : <Eye size={32} className="text-black" />}
            </div>
            <h2 className="text-2xl font-bold" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }} data-testid="register-title">
              {isBrandPartner ? t('auth.brandPartnerReg') : t('auth.createAccount')}
            </h2>
            <p className="mt-2 text-sm" style={{ color: C.muted }}>
              {isBrandPartner ? t('auth.brandPartnerDesc') : t('auth.startVocabJourney')}
            </p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.fullName')}</label>
              <input type="text" required value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                placeholder={isBrandPartner ? "Company Name" : "John Doe"}
                className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2"
                style={inputStyle} data-testid="register-name" />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.email')}</label>
              <input type="email" required value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="you@example.com"
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
            {!isBrandPartner && (
              <div className="p-4 rounded-xl" style={{ background: formData.referralCode ? 'rgba(16,185,129,0.08)' : 'transparent', border: formData.referralCode ? '1px solid rgba(16,185,129,0.3)' : 'none' }}>
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
              style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}
              data-testid="register-submit">
              {loading ? t('common.creatingAccount') : t('common.register')}
            </button>
            <div className="text-center pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <p className="text-sm" style={{ color: C.muted }}>
                {t('common.hasAccount')}{' '}
                <Link to="/login" className="font-semibold hover:underline" style={{ color: C.gold }}>{t('common.loginHere')}</Link>
              </p>
            </div>
            {/* Access Your Portal */}
            <div className="pt-4 mt-2" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <p className="text-xs font-semibold uppercase tracking-wide text-center mb-3" style={{ color: C.muted }}>Access Your Portal</p>
              <div className="grid grid-cols-3 gap-2">
                <button type="button" onClick={() => navigate('/login')} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-all hover:scale-105" style={{ background: 'rgba(212,168,83,0.08)', border: '1px solid rgba(212,168,83,0.2)' }}>
                  <Heart size={18} style={{ color: '#D4A853' }} />
                  <span className="text-xs font-semibold" style={{ color: '#F8F5EE' }}>Parents</span>
                </button>
                <button type="button" onClick={() => navigate('/register?role=brand_partner')} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-all hover:scale-105" style={{ background: 'rgba(244,114,182,0.08)', border: '1px solid rgba(244,114,182,0.2)' }}>
                  <Megaphone size={18} style={{ color: '#F472B6' }} />
                  <span className="text-xs font-semibold" style={{ color: '#F8F5EE' }}>Brands</span>
                </button>
                <button type="button" onClick={() => navigate('/student-login')} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-all hover:scale-105" style={{ background: 'rgba(56,189,248,0.08)', border: '1px solid rgba(56,189,248,0.2)' }}>
                  <GraduationCap size={18} style={{ color: '#38BDF8' }} />
                  <span className="text-xs font-semibold" style={{ color: '#F8F5EE' }}>Students</span>
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default GuardianRegister;
