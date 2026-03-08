import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { authAPI } from '@/lib/api';
import { Eye, Mail, KeyRound, ChevronLeft, Check, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const C = {
  bg: '#0A0F1E', card: '#1A2236',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8',
};

const inputStyle = {
  background: 'rgba(255,255,255,0.06)',
  border: '1px solid rgba(255,255,255,0.1)',
  color: C.cream,
};

const ForgotPassword = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendCode = async (e) => {
    e.preventDefault();
    if (!email.trim()) return;
    setLoading(true);
    try {
      await authAPI.forgotPassword(email);
      toast.success('If an account exists, a reset code has been sent to your email.');
      setStep(2);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Something went wrong');
    }
    setLoading(false);
  };

  const handleVerifyAndReset = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) { toast.error('Passwords do not match'); return; }
    if (newPassword.length < 6) { toast.error('Password must be at least 6 characters'); return; }
    setLoading(true);
    try {
      await authAPI.resetPassword({ email, code, new_password: newPassword });
      toast.success('Password reset successfully!');
      setStep(3);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid or expired code');
    }
    setLoading(false);
  };

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

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md p-8 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }} data-testid="forgot-password-card">
          {step === 1 && (
            <>
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4" style={{ background: 'rgba(212,168,83,0.12)' }}>
                  <Mail size={28} style={{ color: C.gold }} />
                </div>
                <h2 className="text-2xl font-bold" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>Forgot Password</h2>
                <p className="text-sm mt-2" style={{ color: C.muted }}>Enter your email and we'll send you a 6-digit reset code.</p>
              </div>
              <form onSubmit={handleSendCode} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>Email Address</label>
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com" className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none focus:ring-2"
                    style={inputStyle} data-testid="forgot-email-input" />
                </div>
                <button type="submit" disabled={!email.trim() || loading}
                  className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all hover:scale-[1.02] disabled:opacity-50"
                  style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }} data-testid="send-code-btn">
                  {loading ? 'Sending...' : 'Send Reset Code'}
                </button>
              </form>
            </>
          )}

          {step === 2 && (
            <>
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4" style={{ background: 'rgba(56,189,248,0.12)' }}>
                  <KeyRound size={28} style={{ color: C.teal }} />
                </div>
                <h2 className="text-2xl font-bold" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>Enter Reset Code</h2>
                <p className="text-sm mt-2" style={{ color: C.muted }}>Check your email for a 6-digit code sent to <strong style={{ color: C.cream }}>{email}</strong></p>
              </div>
              <form onSubmit={handleVerifyAndReset} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>6-Digit Code</label>
                  <input type="text" maxLength={6} value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                    className="w-full px-4 py-4 rounded-xl text-center text-3xl font-bold tracking-[12px] outline-none focus:ring-2"
                    style={inputStyle} placeholder="000000" data-testid="reset-code-input" />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>New Password</label>
                  <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Min 6 characters" className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none focus:ring-2"
                    style={inputStyle} data-testid="new-password-input" />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>Confirm Password</label>
                  <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm new password" className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none focus:ring-2"
                    style={inputStyle} data-testid="confirm-password-input" />
                </div>
                <button type="submit" disabled={code.length !== 6 || !newPassword || !confirmPassword || loading}
                  className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all hover:scale-[1.02] disabled:opacity-50"
                  style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }} data-testid="reset-password-btn">
                  {loading ? 'Resetting...' : 'Reset Password'}
                </button>
                <button type="button" onClick={() => { setStep(1); setCode(''); }}
                  className="w-full text-center text-sm font-semibold hover:underline" style={{ color: C.muted }} data-testid="resend-code-btn">
                  Didn't receive it? Send again
                </button>
              </form>
            </>
          )}

          {step === 3 && (
            <div className="text-center" data-testid="reset-success">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4" style={{ background: 'rgba(16,185,129,0.12)' }}>
                <Check size={32} style={{ color: '#10B981' }} />
              </div>
              <h2 className="text-2xl font-bold mb-2" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>Password Reset!</h2>
              <p className="text-sm mb-6" style={{ color: C.muted }}>Your password has been updated. You can now log in.</p>
              <button onClick={() => navigate('/login')}
                className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all hover:scale-[1.02]"
                style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }} data-testid="go-to-login-btn">
                Go to Login
              </button>
            </div>
          )}

          {step !== 3 && (
            <Link to="/login" className="flex items-center justify-center gap-1 mt-6 text-sm font-semibold hover:underline" style={{ color: C.muted }} data-testid="back-to-login">
              <ChevronLeft size={16} /> Back to Login
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
