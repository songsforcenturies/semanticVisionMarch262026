import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { Eye, BookOpen } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const C = {
  bg: '#0A0F1E', card: '#1A2236',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8',
};

const TeacherRegister = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { register } = useAuth();
  const [formData, setFormData] = useState({ fullName: '', email: '', password: '', confirmPassword: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) { toast.error(t('auth.passwordMismatch')); return; }
    if (formData.password.length < 6) { toast.error(t('auth.passwordTooShort')); return; }
    setLoading(true);
    const result = await register(formData.fullName, formData.email, formData.password, undefined, 'teacher');
    if (result.success) {
      toast.success(t('auth.teacherAccountCreated'));
      navigate('/teacher-portal');
    } else {
      toast.error(result.error || t('auth.registrationFailed'));
    }
    setLoading(false);
  };

  const inputStyle = { background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: C.cream };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: C.bg, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      <nav className="flex items-center justify-between px-6 py-4" style={{ borderBottom: '1px solid rgba(212,168,83,0.12)' }}>
        <button onClick={() => navigate('/')} className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }}>
            <Eye size={22} className="text-black" />
          </div>
          <span className="text-xl font-bold tracking-tight" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>{t('landing.title')}</span>
        </button>
        <LanguageSwitcher />
      </nav>

      <div className="flex-1 flex items-center justify-center p-4 py-8">
        <div className="w-full max-w-md p-8 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4" style={{ background: 'rgba(167,139,250,0.15)' }}>
              <BookOpen size={32} style={{ color: '#A78BFA' }} />
            </div>
            <h2 className="text-2xl font-bold" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>{t('auth.teacherRegistration')}</h2>
            <p className="mt-2 text-sm" style={{ color: C.muted }}>{t('auth.createClassroomAccount')}</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.fullName')}</label>
              <input type="text" required value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                placeholder="Ms. Johnson" className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none focus:ring-2"
                style={inputStyle} data-testid="teacher-name-input" />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.email')}</label>
              <input type="email" required value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="teacher@school.edu" className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none focus:ring-2"
                style={inputStyle} data-testid="teacher-email-input" />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.password')}</label>
              <input type="password" required value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Min 6 characters" className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none focus:ring-2"
                style={inputStyle} data-testid="teacher-password-input" />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>{t('common.confirmPassword')}</label>
              <input type="password" required value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                placeholder="Confirm password" className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none focus:ring-2"
                style={inputStyle} data-testid="teacher-confirm-password-input" />
            </div>
            <button type="submit" disabled={loading}
              className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all hover:scale-[1.02] disabled:opacity-50 mt-2"
              style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }} data-testid="teacher-register-submit">
              {loading ? t('common.creatingAccount') : t('auth.createTeacherAccount')}
            </button>
            <div className="text-center pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <p className="text-sm" style={{ color: C.muted }}>
                {t('common.hasAccount')}{' '}
                <Link to="/teacher-login" className="font-semibold hover:underline" style={{ color: '#A78BFA' }}>{t('common.loginHere')}</Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TeacherRegister;
