import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { Eye, Heart, Megaphone, GraduationCap, BookOpen, ArrowRight } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const C = {
  bg: '#0A0F1E', surface: '#111827', card: '#1A2236',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8', white: '#FFFFFF',
};

const ROLES = [
  { id: 'parent', label: 'Parents', icon: Heart, color: '#D4A853', bg: 'rgba(212,168,83,0.10)' },
  { id: 'student', label: 'Students', icon: GraduationCap, color: '#38BDF8', bg: 'rgba(56,189,248,0.10)' },
  { id: 'teacher', label: 'Teachers', icon: BookOpen, color: '#A78BFA', bg: 'rgba(167,139,250,0.10)' },
  { id: 'brand', label: 'Brands', icon: Megaphone, color: '#F472B6', bg: 'rgba(244,114,182,0.10)' },
];

const inputStyle = {
  background: 'rgba(255,255,255,0.06)',
  border: '1px solid rgba(255,255,255,0.1)',
  color: C.cream,
};

const GuardianLogin = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { login, studentLogin } = useAuth();
  const [searchParams] = useSearchParams();
  const initialType = searchParams.get('type') || 'parent';
  const [activeRole, setActiveRole] = useState(ROLES.find(r => r.id === initialType) ? initialType : 'parent');
  const [formData, setFormData] = useState({ email: '', password: '', studentCode: '', pin: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (activeRole === 'student') {
      const result = await studentLogin(formData.studentCode, formData.pin);
      if (result.success) {
        navigate('/academy');
      } else {
        toast.error(result.error || t('auth.loginFailed'));
      }
    } else {
      const result = await login(formData.email, formData.password);
      if (result.success) {
        toast.success(t('auth.welcomeBack'));
        const role = result.user.role;
        if (role === 'admin') navigate('/admin');
        else if (role === 'teacher') navigate('/teacher-portal');
        else if (role === 'brand_partner') navigate('/brand-portal');
        else navigate('/portal');
      } else {
        toast.error(result.error || t('auth.loginFailed'));
      }
    }
    setLoading(false);
  };

  const activeConfig = ROLES.find(r => r.id === activeRole);
  const isStudent = activeRole === 'student';

  const titles = {
    parent: { heading: t('auth.guardianLogin'), sub: t('auth.accessPortal') },
    student: { heading: t('auth.studentLogin'), sub: t('auth.enterCodePin') },
    teacher: { heading: t('auth.teacherLogin'), sub: t('auth.accessClassroom') },
    brand: { heading: 'Brand Partner Login', sub: 'Access your brand dashboard' },
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

          {/* Role Selector at TOP */}
          <div className="mb-6">
            <p className="text-xs font-semibold uppercase tracking-wide text-center mb-3" style={{ color: C.muted }}>
              Choose Your Portal
            </p>
            <div className="grid grid-cols-4 gap-2" data-testid="login-role-selector">
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
                    data-testid={`login-role-${role.id}`}
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
            <h2 className="text-xl font-bold" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }} data-testid="login-title">
              {titles[activeRole].heading}
            </h2>
            <p className="mt-1 text-sm" style={{ color: C.muted }}>{titles[activeRole].sub}</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {isStudent ? (
              <>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('auth.studentCode')}</label>
                  <input type="text" required value={formData.studentCode}
                    onChange={(e) => setFormData({ ...formData, studentCode: e.target.value.toUpperCase() })}
                    placeholder="STU-XXXXX"
                    className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2 uppercase tracking-wider"
                    style={inputStyle} data-testid="student-code-input" />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('auth.pin')}</label>
                  <input type="text" inputMode="numeric" pattern="[0-9]*" required value={formData.pin}
                    onChange={(e) => setFormData({ ...formData, pin: e.target.value.replace(/\D/g, '') })}
                    placeholder="Enter your PIN"
                    className="w-full px-4 py-3 rounded-xl outline-none transition-all focus:ring-2 text-center"
                    style={{ ...inputStyle, fontFamily: "'Sora', monospace", fontSize: '1.5rem', letterSpacing: '0.5em', fontWeight: 700 }}
                    data-testid="student-pin-input" />
                  <p className="text-xs mt-2" style={{ color: C.muted }}>{t('auth.pinHint')}</p>
                </div>
              </>
            ) : (
              <>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.email')}</label>
                  <input type="email" required value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder={activeRole === 'teacher' ? 'teacher@school.edu' : activeRole === 'brand' ? 'brand@company.com' : 'parent@example.com'}
                    className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2"
                    style={inputStyle} data-testid="login-email" />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.password')}</label>
                  <input type="password" required value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="Enter your password"
                    className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none transition-all focus:ring-2"
                    style={inputStyle} data-testid="login-password" />
                </div>
              </>
            )}

            <button type="submit" disabled={loading}
              className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all duration-300 hover:scale-[1.02] hover:shadow-lg disabled:opacity-50"
              style={{ background: `linear-gradient(135deg, ${activeConfig.color}, ${C.goldLight})` }}
              data-testid="login-submit">
              {loading ? t('common.loggingIn') : isStudent ? t('auth.enterAcademy') : t('common.login')}
            </button>

            {/* Footer links */}
            <div className="space-y-3 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              {!isStudent && (
                <div className="text-center">
                  <Link to="/forgot-password" className="text-sm font-semibold hover:underline" style={{ color: C.teal }} data-testid="forgot-password-link">
                    Forgot Password?
                  </Link>
                </div>
              )}
              {isStudent ? (
                <p className="text-xs text-center" style={{ color: C.muted }}>{t('auth.askGuardian')}</p>
              ) : (
                <p className="text-sm text-center" style={{ color: C.muted }}>
                  Don't have an account?{' '}
                  <Link
                    to={activeRole === 'brand' ? '/register?role=brand_partner' : activeRole === 'teacher' ? '/register?role=teacher' : '/register'}
                    className="font-semibold hover:underline"
                    style={{ color: C.gold }}
                    data-testid="register-link"
                  >
                    {t('common.registerHere')}
                  </Link>
                </p>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default GuardianLogin;
