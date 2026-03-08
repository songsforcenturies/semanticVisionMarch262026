import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { donationAPI } from '@/lib/api';
import { useNavigate } from 'react-router-dom';
import { Heart, BookOpen, Users, DollarSign } from 'lucide-react';
import { toast } from 'sonner';
import AppShell from '@/components/AppShell';

const C = {
  bg: '#0A0F1E', card: '#1A2236',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8',
};

const PRESET_AMOUNTS = [5, 10, 20, 50, 100];

const DonatePage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [amount, setAmount] = useState('');
  const [message, setMessage] = useState('');

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const status = params.get('status');
    const sessionId = params.get('session_id');
    if (status === 'success' && sessionId) {
      toast.success(t('donate.donationSuccess'));
      window.history.replaceState({}, '', '/donate');
    } else if (status === 'cancelled') {
      toast.error(t('donate.donationCancelled'));
      window.history.replaceState({}, '', '/donate');
    }
  }, []);

  const { data: stats } = useQuery({
    queryKey: ['donation-stats'],
    queryFn: async () => (await donationAPI.getStats()).data,
  });

  const donateMutation = useMutation({
    mutationFn: (data) => donationAPI.create(data),
    onSuccess: (res) => { if (res.data.url) window.location.href = res.data.url; },
    onError: (err) => toast.error(err.response?.data?.detail || t('donate.donationFailed')),
  });

  const handleDonate = () => {
    const amt = parseFloat(amount);
    if (!amt || amt < 1) { toast.error(t('donate.minDonation')); return; }
    donateMutation.mutate({ amount: amt, message, origin_url: window.location.origin });
  };

  const storiesFromAmount = amount ? Math.floor(parseFloat(amount) / 0.20) : 0;

  return (
    <AppShell title="Sponsor a Reader" subtitle="Help children learn through the gift of stories">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Impact Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[
            { icon: DollarSign, label: 'Total Donated', value: `$${stats?.total_donated?.toFixed(2) || '0.00'}`, color: '#FB7185' },
            { icon: BookOpen, label: 'Stories Funded', value: stats?.total_stories_funded || 0, color: '#FBBF24' },
            { icon: Users, label: 'Generous Donors', value: stats?.total_donors || 0, color: '#34D399' },
          ].map((s, i) => (
            <div key={i} className="p-5 rounded-2xl text-center" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
              <s.icon size={24} className="mx-auto mb-2" style={{ color: s.color }} />
              <p className="text-2xl font-bold" style={{ color: C.cream }}>{s.value}</p>
              <p className="text-xs font-semibold uppercase" style={{ color: C.muted }}>{s.label}</p>
            </div>
          ))}
        </div>

        {/* Donation Form */}
        <div className="p-8 rounded-2xl mb-8" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
          <h2 className="text-xl font-bold text-center mb-6" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>Make a Donation</h2>
          <div className="grid grid-cols-5 gap-2 mb-4">
            {PRESET_AMOUNTS.map((preset) => (
              <button key={preset} onClick={() => setAmount(String(preset))}
                className="p-3 rounded-xl font-bold text-lg text-center transition-all hover:scale-105"
                style={{
                  background: parseFloat(amount) === preset ? `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` : 'rgba(255,255,255,0.04)',
                  color: parseFloat(amount) === preset ? '#000' : C.cream,
                  border: `1px solid ${parseFloat(amount) === preset ? C.gold : 'rgba(255,255,255,0.1)'}`,
                }}
                data-testid={`donate-${preset}`}>
                ${preset}
              </button>
            ))}
          </div>
          <div className="mb-4">
            <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>Custom Amount ($)</label>
            <input type="number" min="1" step="0.01" value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="Enter amount..."
              className="w-full px-4 py-3 rounded-xl text-xl font-bold outline-none"
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: C.cream }}
              data-testid="donate-amount" />
          </div>
          {amount && parseFloat(amount) >= 1 && (
            <div className="p-4 rounded-xl mb-4" style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)' }}>
              <p className="text-sm font-bold text-center" style={{ color: C.cream }}>
                Your ${parseFloat(amount).toFixed(2)} donation could fund approximately{' '}
                <span className="text-xl font-black" style={{ color: '#FB7185' }}>{storiesFromAmount}</span> stories for children!
              </p>
            </div>
          )}
          <div className="mb-4">
            <label className="block text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: C.muted }}>Message (optional)</label>
            <textarea value={message} onChange={(e) => setMessage(e.target.value)}
              placeholder="Leave a message of encouragement..." rows={2}
              className="w-full px-4 py-3 rounded-xl text-sm outline-none resize-none"
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: C.cream }}
              data-testid="donate-message" />
          </div>
          {user ? (
            <button onClick={handleDonate} disabled={!amount || parseFloat(amount) < 1 || donateMutation.isPending}
              className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all hover:scale-[1.02] disabled:opacity-50 flex items-center justify-center gap-2"
              style={{ background: `linear-gradient(135deg, #FB7185, #F472B6)` }}
              data-testid="donate-btn">
              <Heart size={18} /> {donateMutation.isPending ? 'Redirecting...' : `Donate $${parseFloat(amount || 0).toFixed(2)}`}
            </button>
          ) : (
            <button onClick={() => navigate('/login')}
              className="w-full py-3.5 rounded-xl text-base font-bold text-black transition-all hover:scale-[1.02]"
              style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}
              data-testid="login-to-donate-btn">
              Login to Donate
            </button>
          )}
          <p className="text-xs text-center mt-3" style={{ color: C.muted }}>Secure payment powered by Stripe</p>
        </div>

        {/* Recent Donors */}
        {stats?.recent?.length > 0 && (
          <div className="p-6 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
            <h3 className="text-lg font-bold mb-4" style={{ color: C.cream }}>Recent Supporters</h3>
            <div className="space-y-2">
              {stats.recent.map((d, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div>
                    <p className="text-sm font-bold" style={{ color: C.cream }}>{d.donor_name}</p>
                    {d.message && <p className="text-xs italic" style={{ color: C.muted }}>"{d.message}"</p>}
                    <p className="text-xs" style={{ color: C.muted }}>{new Date(d.created_date).toLocaleDateString()}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold" style={{ color: '#FB7185' }}>${d.amount.toFixed(2)}</p>
                    <p className="text-xs" style={{ color: C.muted }}>{d.stories_funded} stories</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
};

export default DonatePage;
