import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton, BrutalInput, BrutalCard } from '@/components/brutal';
import { toast } from 'sonner';
import { Zap } from 'lucide-react';
import HomeHeader from '@/components/HomeHeader';

const StudentLogin = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { studentLogin } = useAuth();
  const [formData, setFormData] = useState({ studentCode: '', pin: '' });
  const [loading, setLoading] = useState(false);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-50">
      <HomeHeader showAuth={false} />
      <div className="flex items-center justify-center p-4 py-12">
        <BrutalCard shadow="xl" className="w-full max-w-md bg-amber-50">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-3 mb-4">
              <Zap size={48} className="text-amber-600" />
              <h1 className="text-4xl font-black uppercase">Semantic Vision</h1>
            </div>
            <h2 className="text-2xl font-black uppercase text-amber-600" data-testid="student-login-title">{t('auth.studentLogin')}</h2>
            <p className="mt-2 font-medium text-gray-600">{t('auth.enterCodePin')}</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-6">
            <BrutalInput
              label={t('auth.studentCode')}
              type="text"
              required
              value={formData.studentCode}
              onChange={(e) => setFormData({ ...formData, studentCode: e.target.value.toUpperCase() })}
              placeholder="ABC-1234"
              data-testid="student-code-input"
            />
            <div>
              <BrutalInput
                label={t('auth.pin')}
                type="password"
                required
                value={formData.pin}
                onChange={(e) => setFormData({ ...formData, pin: e.target.value })}
                placeholder="••••••"
                data-testid="student-pin-input"
              />
              <p className="text-sm text-gray-500 mt-1 font-medium">{t('auth.pinHint')}</p>
            </div>
            <BrutalButton type="submit" variant="amber" fullWidth disabled={loading} data-testid="student-login-submit">
              {loading ? t('common.loggingIn') : t('auth.enterAcademy')}
            </BrutalButton>
            <div className="text-center space-y-2">
              <p className="text-sm font-bold text-gray-500">{t('auth.askGuardian')}</p>
              <p className="font-medium">
                <Link to="/login" className="text-indigo-600 font-bold hover:underline">{t('auth.guardianLoginLink')}</Link>
              </p>
            </div>
          </form>
        </BrutalCard>
      </div>
    </div>
  );
};

export default StudentLogin;
