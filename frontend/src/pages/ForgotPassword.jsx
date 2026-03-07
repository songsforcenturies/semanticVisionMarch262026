import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { authAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalInput } from '@/components/brutal';
import { Mail, KeyRound, ChevronLeft, Check, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const ForgotPassword = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // 1=email, 2=code, 3=new password
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
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (newPassword.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }
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
    <div className="min-h-screen bg-amber-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <BrutalCard shadow="xl" className="p-8" data-testid="forgot-password-card">
          {/* Step 1: Enter Email */}
          {step === 1 && (
            <>
              <div className="text-center mb-6">
                <Mail size={40} className="mx-auto text-amber-600 mb-3" />
                <h2 className="text-2xl font-black uppercase">Forgot Password</h2>
                <p className="text-sm text-gray-500 mt-1">Enter your email and we'll send you a 6-digit reset code.</p>
              </div>
              <form onSubmit={handleSendCode} className="space-y-4">
                <BrutalInput label="Email Address" type="email" value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com" data-testid="forgot-email-input" />
                <BrutalButton type="submit" variant="amber" fullWidth disabled={!email.trim() || loading}
                  data-testid="send-code-btn">
                  {loading ? <><Loader2 size={18} className="animate-spin mr-2" /> Sending...</> : 'Send Reset Code'}
                </BrutalButton>
              </form>
            </>
          )}

          {/* Step 2: Enter Code + New Password */}
          {step === 2 && (
            <>
              <div className="text-center mb-6">
                <KeyRound size={40} className="mx-auto text-amber-600 mb-3" />
                <h2 className="text-2xl font-black uppercase">Enter Reset Code</h2>
                <p className="text-sm text-gray-500 mt-1">Check your email for a 6-digit code sent to <strong>{email}</strong></p>
              </div>
              <form onSubmit={handleVerifyAndReset} className="space-y-4">
                <div>
                  <label className="block font-bold text-sm uppercase mb-2">6-Digit Code</label>
                  <input type="text" maxLength={6} value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                    className="w-full border-4 border-black px-4 py-4 text-center text-3xl font-black tracking-[12px] focus:outline-none focus:ring-2 focus:ring-amber-400"
                    placeholder="000000" data-testid="reset-code-input" />
                </div>
                <BrutalInput label="New Password" type="password" value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Min 6 characters" data-testid="new-password-input" />
                <BrutalInput label="Confirm Password" type="password" value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm new password" data-testid="confirm-password-input" />
                <BrutalButton type="submit" variant="amber" fullWidth
                  disabled={code.length !== 6 || !newPassword || !confirmPassword || loading}
                  data-testid="reset-password-btn">
                  {loading ? <><Loader2 size={18} className="animate-spin mr-2" /> Resetting...</> : 'Reset Password'}
                </BrutalButton>
                <button type="button" onClick={() => { setStep(1); setCode(''); }}
                  className="w-full text-center text-sm font-bold text-gray-500 hover:text-gray-800 mt-2"
                  data-testid="resend-code-btn">
                  Didn't receive it? Send again
                </button>
              </form>
            </>
          )}

          {/* Step 3: Success */}
          {step === 3 && (
            <div className="text-center" data-testid="reset-success">
              <div className="w-16 h-16 bg-emerald-100 border-4 border-black mx-auto flex items-center justify-center mb-4">
                <Check size={32} className="text-emerald-600" />
              </div>
              <h2 className="text-2xl font-black uppercase mb-2">Password Reset!</h2>
              <p className="text-sm text-gray-500 mb-6">Your password has been updated. You can now log in.</p>
              <BrutalButton variant="amber" fullWidth onClick={() => navigate('/login')} data-testid="go-to-login-btn">
                Go to Login
              </BrutalButton>
            </div>
          )}

          {/* Back to login link */}
          {step !== 3 && (
            <Link to="/login" className="flex items-center justify-center gap-1 mt-6 text-sm font-bold text-gray-500 hover:text-gray-800"
              data-testid="back-to-login">
              <ChevronLeft size={16} /> Back to Login
            </Link>
          )}
        </BrutalCard>
      </div>
    </div>
  );
};

export default ForgotPassword;
