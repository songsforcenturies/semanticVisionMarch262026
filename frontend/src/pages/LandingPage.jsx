import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BrutalButton, BrutalCard } from '@/components/brutal';
import { BookOpen, Users, TrendingUp, Sparkles, GraduationCap, Heart, Megaphone } from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <div className="mb-8 flex justify-center">
            <div className="brutal-shadow-xl border-6 border-black bg-white p-6 inline-block">
              <BookOpen size={80} className="text-indigo-600" />
            </div>
          </div>

          <h1 className="text-7xl font-black uppercase mb-6 tracking-tight">
            LexiMaster
          </h1>

          <p className="text-2xl font-bold mb-12 text-gray-700">
            AI-Powered Vocabulary Learning Through Personalized Stories
          </p>

          <div className="flex gap-4 justify-center flex-wrap mb-16">
            <BrutalButton
              variant="indigo"
              size="xl"
              onClick={() => navigate('/register')}
            >
              Get Started Free
            </BrutalButton>
            <BrutalButton
              variant="default"
              size="xl"
              onClick={() => navigate('/login')}
            >
              Guardian Login
            </BrutalButton>
            <BrutalButton
              variant="amber"
              size="xl"
              onClick={() => navigate('/student-login')}
            >
              Student Login
            </BrutalButton>
            <BrutalButton
              variant="emerald"
              size="xl"
              onClick={() => navigate('/teacher-login')}
              data-testid="teacher-login-link"
            >
              Teacher Login
            </BrutalButton>
            <BrutalButton
              variant="rose"
              size="xl"
              onClick={() => navigate('/donate')}
              data-testid="donate-link"
              className="flex items-center gap-2"
            >
              <Heart size={20} />
              Sponsor a Reader
            </BrutalButton>
            <BrutalButton
              variant="amber"
              size="xl"
              onClick={() => navigate('/register?role=brand_partner')}
              data-testid="brand-partner-link"
              className="flex items-center gap-2"
            >
              <Megaphone size={20} />
              Brand Partners
            </BrutalButton>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mt-20">
          <BrutalCard variant="indigo" shadow="xl" hover>
            <Sparkles size={48} className="mb-4 text-indigo-600" />
            <h3 className="text-2xl font-black uppercase mb-4">AI Stories</h3>
            <p className="text-lg font-medium">
              Generate personalized 5-chapter narratives based on student interests with embedded vocabulary
            </p>
          </BrutalCard>

          <BrutalCard variant="emerald" shadow="xl" hover>
            <TrendingUp size={48} className="mb-4 text-emerald-600" />
            <h3 className="text-2xl font-black uppercase mb-4">Track Progress</h3>
            <p className="text-lg font-medium">
              Monitor mastered vocabulary, reading speed, and Agentic Reach Score in real-time
            </p>
          </BrutalCard>

          <BrutalCard variant="amber" shadow="xl" hover>
            <Users size={48} className="mb-4 text-amber-600" />
            <h3 className="text-2xl font-black uppercase mb-4">Word Banks</h3>
            <p className="text-lg font-medium">
              Access specialized vocabulary banks for Aviation, Medicine, Law, and more
            </p>
          </BrutalCard>
        </div>

        {/* Vocabulary Tiers */}
        <div className="mt-20 text-center">
          <h2 className="text-4xl font-black uppercase mb-8">
            60/30/10 Learning System
          </h2>
          <div className="flex gap-6 justify-center flex-wrap">
            <BrutalCard variant="default" className="bg-blue-100">
              <div className="text-6xl font-black mb-2">60%</div>
              <div className="text-xl font-black uppercase">Baseline</div>
              <p className="mt-2 font-medium">Foundation vocabulary</p>
            </BrutalCard>
            <BrutalCard variant="default" className="bg-purple-100">
              <div className="text-6xl font-black mb-2">30%</div>
              <div className="text-xl font-black uppercase">Target</div>
              <p className="mt-2 font-medium">Growth vocabulary</p>
            </BrutalCard>
            <BrutalCard variant="default" className="bg-orange-100">
              <div className="text-6xl font-black mb-2">10%</div>
              <div className="text-xl font-black uppercase">Stretch</div>
              <p className="mt-2 font-medium">Challenge vocabulary</p>
            </BrutalCard>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t-6 border-black bg-black text-white py-8 mt-20">
        <div className="container mx-auto px-4 text-center">
          <p className="font-bold text-lg">
            © 2026 LexiMaster - Building Vocabulary, One Story at a Time
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
