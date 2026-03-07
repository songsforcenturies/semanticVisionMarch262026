import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton, BrutalInput, BrutalCard } from '@/components/brutal';
import { toast } from 'sonner';
import { GraduationCap } from 'lucide-react';
import HomeHeader from '@/components/HomeHeader';

const TeacherLogin = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const result = await login(formData.email, formData.password);
    if (result.success) {
      if (result.user.role !== 'teacher') {
        toast.error('This account is not a teacher account');
        setLoading(false);
        return;
      }
      toast.success('Welcome back, Teacher!');
      navigate('/teacher-portal');
    } else {
      toast.error(result.error || 'Login failed');
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
            <h2 className="text-2xl font-black uppercase text-teal-600">Teacher Login</h2>
            <p className="mt-2 font-medium text-gray-600">Access your classroom portal</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-6">
            <BrutalInput
              label="Email Address"
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="teacher@school.edu"
              data-testid="teacher-email-input"
            />
            <BrutalInput
              label="Password"
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="••••••••"
              data-testid="teacher-password-input"
            />
            <BrutalButton type="submit" variant="emerald" fullWidth disabled={loading} data-testid="teacher-login-submit">
              {loading ? 'Logging in...' : 'Login'}
            </BrutalButton>
            <div className="text-center">
              <p className="font-medium">
                Don't have a teacher account?{' '}
                <Link to="/teacher-register" className="text-teal-600 font-bold hover:underline">Register here</Link>
              </p>
              <p className="mt-4 font-medium">
                <Link to="/login" className="text-indigo-600 font-bold hover:underline">Guardian Login →</Link>
              </p>
            </div>
          </form>
        </BrutalCard>
      </div>
    </div>
  );
};

export default TeacherLogin;
