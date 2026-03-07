import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton, BrutalInput, BrutalCard } from '@/components/brutal';
import { toast } from 'sonner';
import { BookOpen, Gift } from 'lucide-react';
import HomeHeader from '@/components/HomeHeader';

const GuardianRegister = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { register } = useAuth();
  const roleParam = searchParams.get('role');
  const isBrandPartner = roleParam === 'brand_partner';
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    referralCode: searchParams.get('ref') || '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    const result = await register(
      formData.fullName, formData.email, formData.password,
      formData.referralCode || undefined,
      isBrandPartner ? 'brand_partner' : 'guardian'
    );

    if (result.success) {
      if (isBrandPartner) {
        toast.success('Brand partner account created! Pending admin approval.');
        navigate('/brand-portal');
      } else {
        toast.success(formData.referralCode
          ? 'Account created! Referral bonus applied!'
          : 'Account created successfully!');
        navigate('/portal');
      }
    } else {
      toast.error(result.error || 'Registration failed');
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
          <h2 className="text-2xl font-black uppercase">
            {isBrandPartner ? 'Brand Partner Registration' : 'Create Account'}
          </h2>
          <p className="mt-2 font-medium text-gray-600">
            {isBrandPartner ? 'Partner with LexiMaster to reach young learners' : 'Start your vocabulary journey'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <BrutalInput
            label="Full Name"
            type="text"
            required
            value={formData.fullName}
            onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
            placeholder="John Doe"
          />

          <BrutalInput
            label="Email Address"
            type="email"
            required
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="guardian@example.com"
          />

          <BrutalInput
            label="Password"
            type="password"
            required
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            placeholder="••••••••"
          />

          <BrutalInput
            label="Confirm Password"
            type="password"
            required
            value={formData.confirmPassword}
            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
            placeholder="********"
          />

          {/* Referral Code */}
          <div className={formData.referralCode ? 'border-4 border-emerald-300 p-3 bg-emerald-50' : ''}>
            <BrutalInput
              label={
                <span className="flex items-center gap-1">
                  <Gift size={14} /> Referral Code (optional)
                </span>
              }
              type="text"
              value={formData.referralCode}
              onChange={(e) => setFormData({ ...formData, referralCode: e.target.value.toUpperCase() })}
              placeholder="REF-XXXXXX"
              data-testid="referral-code-input"
            />
            {formData.referralCode && (
              <p className="text-sm font-bold text-emerald-600 mt-1">
                You and your referrer will both receive a wallet bonus!
              </p>
            )}
          </div>

          <BrutalButton
            type="submit"
            variant="indigo"
            fullWidth
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Register'}
          </BrutalButton>

          <div className="text-center">
            <p className="font-medium">
              Already have an account?{' '}
              <Link to="/login" className="text-indigo-600 font-bold hover:underline">
                Login here
              </Link>
            </p>
          </div>
        </form>
      </BrutalCard>
    </div>
    </div>
  );
};

export default GuardianRegister;
