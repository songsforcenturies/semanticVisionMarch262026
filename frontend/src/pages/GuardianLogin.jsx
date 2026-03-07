import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton, BrutalInput, BrutalCard } from '@/components/brutal';
import { toast } from 'sonner';
import { BookOpen } from 'lucide-react';
import HomeHeader from '@/components/HomeHeader';

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
      if (result.user.role === 'brand_partner') {
        navigate('/brand-portal');
      } else {
        navigate('/guardian');
      }
    } else {
      toast.error(result.error || t('auth.loginFailed'));
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50">
      <HomeHeader showAuth={false} />
      <div className="flex items-center justify-center p-4 py-12">
        <BrutalCard shadow="xl" className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-3 mb-4">
              <BookOpen size={48} className="text-indigo-600" />
              <h1 className="text-4xl font-black uppercase">LexiMaster</h1>
            </div>
            <h2 className="text-2xl font-black uppercase text-indigo-600" data-testid="login-title">{t('auth.guardianLogin')}</h2>
            <p className="mt-2 font-medium text-gray-600">{t('auth.accessPortal')}</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-6">
            <BrutalInput
              label={t('common.email')}
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="guardian@example.com"
              data-testid="login-email"
            />
            <BrutalInput
              label={t('common.password')}
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="••••••••"
              data-testid="login-password"
            />
            <BrutalButton type="submit" variant="indigo" fullWidth disabled={loading} data-testid="login-submit">
              {loading ? t('common.loggingIn') : t('common.login')}
            </BrutalButton>
            <div className="text-center space-y-2">
              <p className="font-medium">
                {t('common.noAccount')}{' '}
                <Link to="/register" className="text-indigo-600 font-bold hover:underline">{t('common.registerHere')}</Link>
              </p>
              <p className="font-medium">
                <Link to="/student-login" className="text-amber-600 font-bold hover:underline">{t('auth.studentPinLogin')}</Link>
              </p>
            </div>
          </form>
        </BrutalCard>
      </div>
    </div>
  );
};

export default GuardianLogin;
