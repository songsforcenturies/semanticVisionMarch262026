import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalButton, BrutalInput, BrutalCard } from '@/components/brutal';
import { toast } from 'sonner';
import { BookOpen } from 'lucide-react';
import HomeHeader from '@/components/HomeHeader';

const StudentLogin = () => {
  const navigate = useNavigate();
  const { studentLogin } = useAuth();
  const [studentCode, setStudentCode] = useState('');
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!studentCode.trim()) {
      toast.error('Please enter your Student Code');
      return;
    }

    if (pin.length !== 9) {
      toast.error('PIN must be 9 digits');
      return;
    }

    setLoading(true);

    const result = await studentLogin(studentCode.toUpperCase().trim(), pin);

    if (result.success) {
      toast.success(`Welcome back, ${result.student.full_name}!`);
      navigate('/academy');
    } else {
      toast.error(result.error || 'Invalid credentials');
      setPin('');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-yellow-50">
      <HomeHeader showAuth={false} />
      
      <div className="flex items-center justify-center p-4 py-12">
        <BrutalCard shadow="xl" className="w-full max-w-md bg-amber-50">

        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <BookOpen size={48} className="text-amber-600" />
            <h1 className="text-4xl font-black uppercase">LexiMaster</h1>
          </div>
          <h2 className="text-2xl font-black uppercase text-amber-600">Student Login</h2>
          <p className="mt-2 font-medium text-gray-600">
            Enter your Student Code and PIN
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <BrutalInput
            label="Student Code"
            type="text"
            required
            value={studentCode}
            onChange={(e) => setStudentCode(e.target.value.toUpperCase())}
            placeholder="STU-ABC123"
            className="uppercase"
            autoFocus
          />
          
          <BrutalInput
            variant="pin"
            label="9-Digit PIN"
            type="text"
            required
            maxLength={9}
            value={pin}
            onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))}
            placeholder="•••••••••"
          />

          <BrutalButton
            type="submit"
            variant="amber"
            fullWidth
            size="lg"
            disabled={loading || !studentCode || pin.length !== 9}
          >
            {loading ? 'Logging in...' : 'Enter Academy'}
          </BrutalButton>

          <div className="text-center">
            <p className="font-medium text-sm text-gray-600">
              Ask your guardian for your Student Code and PIN
            </p>
          </div>
        </form>
      </BrutalCard>
    </div>
    </div>
  );
};

export default StudentLogin;
