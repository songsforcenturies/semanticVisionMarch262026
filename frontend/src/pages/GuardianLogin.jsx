import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton, BrutalInput } from '@/components/brutal';
import { toast } from 'sonner';
import { Eye, ArrowRight, GraduationCap, Megaphone, Heart } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const C = {
  bg: '#0A0F1E', surface: '#111827', card: '#1A2236',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8', white: '#FFFFFF',
};

const GuardianLogin = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { login } = useAuth();
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const result = await login(formData.email, formData.password);
    if (result.success) {
      toast.success(t('auth.welcomeBack'));
      const role = result.user.role;
      if (role === 'admin') {
        navigate('/admin');
      } else if (role === 'teacher') {
        navigate('/teacher-portal');
      } else if (role === 'brand_partner') {
        navigate('/brand-portal');
      } else {
        navigate('/portal');
      }
    } else {
      toast.error(result.error || t('auth.loginFailed'));
    }
    setLoading(false);
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
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md p-8 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }}>
              <Eye size={32} className="text-black" />
            </div>
            <h2 className="text-2xl font-bold" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }} data-testid="login-title">{t('auth.guardianLogin')}</h2>
            <p className="mt-2 text-sm" style={{ color: C.muted }}>{t('auth.accessPortal')}</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.email')}</label>
              <input type="email" required value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="parent@example.com"
                className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2"
                style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: C.cream, '--tw-ring-color': C.gold }}
                data-testid="login-email"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.password')}</label>
              <input type="password" required value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Enter your password"
                className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2"
                style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: C.cream, '--tw-ring-color': C.gold }}
                data-testid="login-password"
              />
            </div>
            <button type="submit" disabled={loading}
              className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all duration-300 hover:scale-[1.02] hover:shadow-lg disabled:opacity-50"
              style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}
              data-testid="login-submit">
              {loading ? t('common.loggingIn') : t('common.login')}
            </button>
            <div className="text-center">
              <Link to="/forgot-password" className="text-sm font-semibold hover:underline" style={{ color: C.teal }} data-testid="forgot-password-link">
                Forgot Password?
              </Link>
            </div>
            <div className="text-center space-y-3 pt-2" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <p className="text-sm" style={{ color: C.muted }}>
                {t('common.noAccount')}{' '}
                <Link to="/register" className="font-semibold hover:underline" style={{ color: C.gold }}>{t('common.registerHere')}</Link>
              </p>
            </div>
            {/* Access Your Portal */}
            <div className="pt-4 mt-2" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <p className="text-xs font-semibold uppercase tracking-wide text-center mb-3" style={{ color: C.muted }}>Access Your Portal</p>
              <div className="grid grid-cols-3 gap-2">
                <button type="button" onClick={() => navigate('/login')} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-all hover:scale-105" style={{ background: 'rgba(212,168,83,0.08)', border: '1px solid rgba(212,168,83,0.2)' }}>
                  <Heart size={18} style={{ color: C.gold }} />
                  <span className="text-xs font-semibold" style={{ color: C.cream }}>Parents</span>
                </button>
                <button type="button" onClick={() => navigate('/register?role=brand_partner')} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-all hover:scale-105" style={{ background: 'rgba(244,114,182,0.08)', border: '1px solid rgba(244,114,182,0.2)' }}>
                  <Megaphone size={18} style={{ color: '#F472B6' }} />
                  <span className="text-xs font-semibold" style={{ color: C.cream }}>Brands</span>
                </button>
                <button type="button" onClick={() => navigate('/student-login')} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-all hover:scale-105" style={{ background: 'rgba(56,189,248,0.08)', border: '1px solid rgba(56,189,248,0.2)' }}>
                  <GraduationCap size={18} style={{ color: C.teal }} />
                  <span className="text-xs font-semibold" style={{ color: C.cream }}>Students</span>
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default GuardianLogin;
