import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { studentAPI } from '@/lib/api';
import { toast } from 'sonner';
import { Eye, GraduationCap, Key } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const C = {
  bg: '#0A0F1E', surface: '#111827', card: '#1A2236',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8',
};

const StudentLogin = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { studentLogin } = useAuth();
  const [formData, setFormData] = useState({ studentCode: '', pin: '' });
  const [loading, setLoading] = useState(false);
  const [showChangePin, setShowChangePin] = useState(false);
  const [pinChangeData, setPinChangeData] = useState({ current_pin: '', new_pin: '', confirm_pin: '' });
  const [changingPin, setChangingPin] = useState(false);

  const handleChangePin = async (e) => {
    e.preventDefault();
    if (pinChangeData.new_pin !== pinChangeData.confirm_pin) {
      toast.error('New PINs do not match');
      return;
    }
    setChangingPin(true);
    try {
      await studentAPI.changeMyPin({ current_pin: pinChangeData.current_pin, new_pin: pinChangeData.new_pin });
      toast.success('PIN changed! Use your new PIN to login.');
      setShowChangePin(false);
      setPinChangeData({ current_pin: '', new_pin: '', confirm_pin: '' });
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to change PIN');
    }
    setChangingPin(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const result = await studentLogin(formData.studentCode, formData.pin);
    if (result.success) {
      navigate('/academy');
    } else {
      toast.error(result.error || t('auth.loginFailed'));
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
      <nav className="flex items-center justify-between px-6 py-4" style={{ borderBottom: '1px solid rgba(212,168,83,0.12)' }}>
        <button onClick={() => navigate('/')} className="flex items-center gap-3" data-testid="nav-logo">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }}>
            <Eye size={22} className="text-black" />
          </div>
          <span className="text-xl font-bold tracking-tight" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>{t('landing.title')}</span>
        </button>
        <LanguageSwitcher />
      </nav>

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md p-8 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4" style={{ background: `linear-gradient(135deg, ${C.teal}, ${C.gold})` }}>
              <GraduationCap size={32} className="text-black" />
            </div>
            <h2 className="text-2xl font-bold" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }} data-testid="student-login-title">{t('auth.studentLogin')}</h2>
            <p className="mt-2 text-sm" style={{ color: C.muted }}>{t('auth.enterCodePin')}</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-5">
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
                style={{
                  background: 'rgba(212,168,83,0.15)',
                  border: '2px solid rgba(212,168,83,0.4)',
                  color: '#D4A853',
                  fontFamily: "'Sora', monospace",
                  fontSize: '1.5rem',
                  letterSpacing: '0.5em',
                  fontWeight: 700,
                  WebkitTextFillColor: '#D4A853',
                }}
                data-testid="student-pin-input" />
              <p className="text-xs mt-2" style={{ color: 'rgba(148,163,184,0.5)' }}>{t('auth.pinHint')}</p>
            </div>
            <button type="submit" disabled={loading}
              className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all duration-300 hover:scale-[1.02] hover:shadow-lg disabled:opacity-50"
              style={{ background: `linear-gradient(135deg, ${C.teal}, ${C.gold})` }}
              data-testid="student-login-submit">
              {loading ? t('common.loggingIn') : t('auth.enterAcademy')}
            </button>
            <div className="text-center space-y-3 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <button type="button" onClick={() => setShowChangePin(!showChangePin)}
                className="flex items-center gap-1.5 mx-auto text-xs font-semibold hover:underline transition-all"
                style={{ color: C.teal }} data-testid="change-pin-toggle">
                <Key size={12} /> {showChangePin ? 'Back to Login' : 'Change My PIN'}
              </button>
              <p className="text-xs" style={{ color: C.muted }}>{t('auth.askGuardian')}</p>
              <Link to="/login" className="text-sm font-semibold hover:underline" style={{ color: C.gold }}>{t('auth.guardianLoginLink')}</Link>
            </div>
          </form>

          {showChangePin && (
            <form onSubmit={handleChangePin} className="mt-4 p-4 rounded-xl space-y-3" style={{ background: 'rgba(56,189,248,0.06)', border: '1px solid rgba(56,189,248,0.2)' }}>
              <p className="text-sm font-bold" style={{ color: C.teal }}>Change Your PIN</p>
              <input type="password" inputMode="numeric" required placeholder="Current PIN"
                value={pinChangeData.current_pin}
                onChange={(e) => setPinChangeData({ ...pinChangeData, current_pin: e.target.value.replace(/\D/g, '') })}
                className="w-full px-4 py-2.5 rounded-lg text-sm outline-none" style={inputStyle}
                data-testid="change-current-pin" />
              <input type="password" inputMode="numeric" required placeholder="New PIN (4-10 digits)"
                value={pinChangeData.new_pin}
                onChange={(e) => setPinChangeData({ ...pinChangeData, new_pin: e.target.value.replace(/\D/g, '') })}
                className="w-full px-4 py-2.5 rounded-lg text-sm outline-none" style={inputStyle}
                data-testid="change-new-pin" />
              <input type="password" inputMode="numeric" required placeholder="Confirm New PIN"
                value={pinChangeData.confirm_pin}
                onChange={(e) => setPinChangeData({ ...pinChangeData, confirm_pin: e.target.value.replace(/\D/g, '') })}
                className="w-full px-4 py-2.5 rounded-lg text-sm outline-none" style={inputStyle}
                data-testid="change-confirm-pin" />
              <button type="submit" disabled={changingPin}
                className="w-full py-2.5 rounded-lg text-sm font-bold text-black transition-all"
                style={{ background: C.teal }} data-testid="change-pin-submit">
                {changingPin ? 'Changing...' : 'Save New PIN'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentLogin;
