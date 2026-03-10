import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import { Eye, Share2, DollarSign, Users, TrendingUp, Check, ArrowRight } from 'lucide-react';
import { affiliateAPI } from '@/lib/api';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const C = {
  bg: '#0A0F1E', card: '#1A2236', gold: '#D4A853',
  goldLight: '#F5D799', teal: '#38BDF8', cream: '#F8F5EE',
  muted: '#94A3B8', border: 'rgba(255,255,255,0.08)',
};

const benefits = [
  { icon: DollarSign, title: 'Earn Per Referral', desc: 'Get paid for every new family that signs up with your link' },
  { icon: Users, title: 'Help Families Learn', desc: 'Connect families with AI-powered personalized reading stories' },
  { icon: TrendingUp, title: 'Track Your Impact', desc: 'See your referral count, earnings, and payout status in real time' },
];

const AffiliateSignup = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [form, setForm] = useState({ full_name: '', email: '' });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.full_name.trim() || !form.email.trim()) {
      toast.error('Please fill in all fields');
      return;
    }
    setLoading(true);
    try {
      const res = await affiliateAPI.signup(form);
      setResult(res.data);
      toast.success('Affiliate registration successful!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: C.bg, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4" style={{ borderBottom: `1px solid rgba(212,168,83,0.12)` }}>
        <button onClick={() => navigate('/')} className="flex items-center gap-3" data-testid="nav-logo">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }}>
            <Eye size={22} className="text-black" />
          </div>
          <span className="text-xl font-bold tracking-tight" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>
            {t('landing.title')}
          </span>
        </button>
        <div className="flex items-center gap-3">
          <LanguageSwitcher />
          <button onClick={() => navigate('/login')} className="px-4 py-2 rounded-lg text-sm font-semibold" style={{ color: C.gold, border: `1px solid rgba(212,168,83,0.3)` }} data-testid="login-btn">
            Login
          </button>
        </div>
      </nav>

      <div className="flex-1 flex items-center justify-center p-4 py-8">
        <div className="w-full max-w-xl">

          {!result ? (
            <>
              {/* Hero */}
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4" style={{ background: `${C.gold}20` }}>
                  <Share2 size={32} style={{ color: C.gold }} />
                </div>
                <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }} data-testid="affiliate-heading">
                  Become an Affiliate
                </h1>
                <p className="text-base" style={{ color: C.muted }}>
                  Earn money by sharing Semantic Vision with families. Get your unique referral link and start earning today.
                </p>
              </div>

              {/* Benefits */}
              <div className="grid gap-3 mb-8">
                {benefits.map((b, i) => (
                  <div key={i} className="flex items-start gap-4 p-4 rounded-xl" style={{ background: C.card, border: `1px solid ${C.border}` }}>
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${C.gold}18` }}>
                      <b.icon size={20} style={{ color: C.gold }} />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold" style={{ color: C.cream }}>{b.title}</h3>
                      <p className="text-xs mt-0.5" style={{ color: C.muted }}>{b.desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Form */}
              <div className="p-6 rounded-2xl" style={{ background: C.card, border: `1px solid ${C.border}` }}>
                <h2 className="text-lg font-bold mb-4" style={{ color: C.cream }}>Sign Up as an Affiliate</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>Full Name</label>
                    <input type="text" required value={form.full_name}
                      onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                      placeholder="Your full name"
                      className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none"
                      style={{ background: 'rgba(255,255,255,0.06)', border: `1px solid rgba(255,255,255,0.1)`, color: C.cream }}
                      data-testid="affiliate-name" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>Email Address</label>
                    <input type="email" required value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                      placeholder="you@example.com"
                      className="w-full px-4 py-3 rounded-xl text-sm font-medium outline-none"
                      style={{ background: 'rgba(255,255,255,0.06)', border: `1px solid rgba(255,255,255,0.1)`, color: C.cream }}
                      data-testid="affiliate-email" />
                  </div>
                  <button type="submit" disabled={loading}
                    className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all hover:scale-[1.02] disabled:opacity-50"
                    style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}
                    data-testid="affiliate-submit">
                    {loading ? 'Registering...' : 'Join Affiliate Program'}
                  </button>
                </form>
              </div>
            </>
          ) : (
            /* Success State */
            <div className="p-8 rounded-2xl text-center" style={{ background: C.card, border: `1px solid ${C.border}` }} data-testid="affiliate-success">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4" style={{ background: 'rgba(16,185,129,0.15)' }}>
                <Check size={32} style={{ color: '#10B981' }} />
              </div>
              <h2 className="text-2xl font-bold mb-2" style={{ color: C.cream }}>
                {result.confirmed ? "You're In!" : "Registration Received!"}
              </h2>
              <p className="text-sm mb-6" style={{ color: C.muted }}>
                {result.confirmed
                  ? "Your affiliate account is active. Share your code to start earning!"
                  : "Your registration is pending admin approval. We'll email you once approved."}
              </p>

              {/* Affiliate Code */}
              <div className="p-5 rounded-xl mb-4" style={{ background: '#0F172A', border: `1px solid ${C.gold}30` }}>
                <p className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: C.gold }}>Your Affiliate Code</p>
                <p className="text-3xl font-bold tracking-wider" style={{ fontFamily: 'monospace', color: C.cream }} data-testid="affiliate-code">
                  {result.affiliate_code}
                </p>
              </div>

              {/* Referral Link */}
              <div className="p-5 rounded-xl mb-6" style={{ background: '#0F172A', border: `1px solid ${C.border}` }}>
                <p className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: C.gold }}>Your Referral Link</p>
                <p className="text-sm break-all" style={{ color: C.teal }} data-testid="affiliate-link">
                  {window.location.origin}/register?ref={result.affiliate_code}
                </p>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(`${window.location.origin}/register?ref=${result.affiliate_code}`);
                    toast.success('Link copied!');
                  }}
                  className="mt-3 px-4 py-2 rounded-lg text-xs font-bold"
                  style={{ background: `${C.teal}20`, color: C.teal, border: `1px solid ${C.teal}30` }}
                  data-testid="copy-link-btn"
                >
                  Copy Referral Link
                </button>
              </div>

              <p className="text-xs mb-4" style={{ color: C.muted }}>
                Check your email for a confirmation with your full affiliate details.
              </p>

              <div className="flex gap-3 justify-center">
                <button onClick={() => navigate('/')} className="px-5 py-2.5 rounded-lg text-sm font-semibold"
                  style={{ color: C.muted, border: `1px solid ${C.border}` }}>
                  Back to Home
                </button>
                <button onClick={() => navigate('/login')} className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold text-black"
                  style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}>
                  Login <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AffiliateSignup;
