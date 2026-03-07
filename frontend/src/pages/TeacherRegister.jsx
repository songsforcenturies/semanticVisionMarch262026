import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton, BrutalInput, BrutalCard } from '@/components/brutal';
import { toast } from 'sonner';
import { GraduationCap } from 'lucide-react';
import HomeHeader from '@/components/HomeHeader';

const TeacherRegister = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { register } = useAuth();
  const [formData, setFormData] = useState({ fullName: '', email: '', password: '', confirmPassword: '' });
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
    const result = await register(formData.fullName, formData.email, formData.password, 'teacher');
    if (result.success) {
      toast.success(t('auth.teacherAccountCreated'));
      navigate('/teacher-portal');
    } else {
      toast.error(result.error || t('auth.registrationFailed'));
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
            <h2 className="text-2xl font-black uppercase text-teal-600">{t('auth.teacherRegistration')}</h2>
            <p className="mt-2 font-medium text-gray-600">{t('auth.createClassroomAccount')}</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-6">
            <BrutalInput
              label={t('common.fullName')}
              type="text"
              required
              value={formData.fullName}
              onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
              placeholder="Ms. Johnson"
              data-testid="teacher-name-input"
            />
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
            <BrutalInput
              label={t('common.confirmPassword')}
              type="password"
              required
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              placeholder="••••••••"
              data-testid="teacher-confirm-password-input"
            />
            <BrutalButton type="submit" variant="emerald" fullWidth disabled={loading} data-testid="teacher-register-submit">
              {loading ? t('common.creatingAccount') : t('auth.createTeacherAccount')}
            </BrutalButton>
            <div className="text-center">
              <p className="font-medium">
                {t('common.hasAccount')}{' '}
                <Link to="/teacher-login" className="text-teal-600 font-bold hover:underline">{t('common.loginHere')}</Link>
              </p>
            </div>
          </form>
        </BrutalCard>
      </div>
    </div>
  );
};

export default TeacherRegister;
