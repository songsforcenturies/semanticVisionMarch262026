import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton, BrutalInput, BrutalCard } from '@/components/brutal';
import { toast } from 'sonner';
import { GraduationCap } from 'lucide-react';
import HomeHeader from '@/components/HomeHeader';

const TeacherLogin = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { login } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const result = await login(formData.email, formData.password);
    if (result.success) {
      if (result.user.role !== 'teacher') {
        toast.error(t('auth.notTeacherAccount'));
        setLoading(false);
        return;
      }
      toast.success(t('auth.welcomeTeacher'));
      navigate('/teacher-portal');
    } else {
      toast.error(result.error || t('auth.loginFailed'));
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50">
      <HomeHeader showAuth={false} />
      <div className="flex items-center justify-center p-4 py-12">
        <BrutalCard shadow="xl" className="w-full max-w-md bg-teal-50">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-3 mb-4">
              <GraduationCap size={48} className="text-teal-600" />
              <h1 className="text-4xl font-black uppercase">LexiMaster</h1>
            </div>
            <h2 className="text-2xl font-black uppercase text-teal-600" data-testid="teacher-login-title">{t('auth.teacherLogin')}</h2>
            <p className="mt-2 font-medium text-gray-600">{t('auth.accessClassroom')}</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-6">
            <BrutalInput
              label={t('common.email')}
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="teacher@school.edu"
              data-testid="teacher-email-input"
            />
            <BrutalInput
              label={t('common.password')}
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="••••••••"
              data-testid="teacher-password-input"
            />
            <BrutalButton type="submit" variant="emerald" fullWidth disabled={loading} data-testid="teacher-login-submit">
              {loading ? t('common.loggingIn') : t('common.login')}
            </BrutalButton>
            <div className="text-center space-y-2">
              <p className="font-medium">
                {t('auth.noTeacherAccount')}{' '}
                <Link to="/teacher-register" className="text-teal-600 font-bold hover:underline">{t('common.registerHere')}</Link>
              </p>
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

export default TeacherLogin;
