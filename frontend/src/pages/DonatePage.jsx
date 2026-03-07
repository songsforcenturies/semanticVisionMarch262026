import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { donationAPI } from '@/lib/api';
import { useNavigate } from 'react-router-dom';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalInput } from '@/components/brutal';
import { Heart, BookOpen, Users, DollarSign, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

const PRESET_AMOUNTS = [5, 10, 20, 50, 100];

const DonatePage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [amount, setAmount] = useState('');
  const [message, setMessage] = useState('');

  // Check for return from Stripe
  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const status = params.get('status');
    const sessionId = params.get('session_id');
    if (status === 'success' && sessionId) {
      toast.success('Thank you for your generous donation!');
      window.history.replaceState({}, '', '/donate');
    } else if (status === 'cancelled') {
      toast.error('Donation was cancelled');
      window.history.replaceState({}, '', '/donate');
    }
  }, []);

  const { data: stats } = useQuery({
    queryKey: ['donation-stats'],
    queryFn: async () => (await donationAPI.getStats()).data,
  });

  const donateMutation = useMutation({
    mutationFn: (data) => donationAPI.create(data),
    onSuccess: (res) => {
      if (res.data.url) {
        window.location.href = res.data.url;
      }
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Donation failed'),
  });

  const handleDonate = () => {
    const amt = parseFloat(amount);
    if (!amt || amt < 1) { toast.error('Minimum donation is $1'); return; }
    donateMutation.mutate({ amount: amt, message, origin_url: window.location.origin });
  };

  const costPerStory = 0.20;
  const storiesFromAmount = amount ? Math.floor(parseFloat(amount) / costPerStory) : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 to-amber-50">
      <header className="bg-white border-b-6 border-black brutal-shadow-md">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/')} className="p-3 border-4 border-black bg-rose-100 brutal-shadow-sm hover:brutal-shadow-md brutal-active">
              <ArrowLeft size={24} />
            </button>
            <div>
              <h1 className="text-4xl font-black uppercase flex items-center gap-3">
                <Heart size={32} className="text-rose-500" /> Sponsor a Reader
              </h1>
              <p className="text-lg font-medium mt-1">Help children learn through the gift of stories</p>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Impact Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <BrutalCard shadow="lg" className="text-center bg-rose-50">
            <DollarSign size={28} className="mx-auto text-rose-600 mb-2" />
            <p className="text-3xl font-black">${stats?.total_donated?.toFixed(2) || '0.00'}</p>
            <p className="text-xs font-bold uppercase text-gray-500">Total Donated</p>
          </BrutalCard>
          <BrutalCard shadow="lg" className="text-center bg-amber-50">
            <BookOpen size={28} className="mx-auto text-amber-600 mb-2" />
            <p className="text-3xl font-black">{stats?.total_stories_funded || 0}</p>
            <p className="text-xs font-bold uppercase text-gray-500">Stories Funded</p>
          </BrutalCard>
          <BrutalCard shadow="lg" className="text-center bg-emerald-50">
            <Users size={28} className="mx-auto text-emerald-600 mb-2" />
            <p className="text-3xl font-black">{stats?.total_donors || 0}</p>
            <p className="text-xs font-bold uppercase text-gray-500">Generous Donors</p>
          </BrutalCard>
        </div>

        {/* Donation Form */}
        <BrutalCard shadow="xl" className="mb-8">
          <h2 className="text-2xl font-black uppercase mb-6 text-center">Make a Donation</h2>

          <div className="grid grid-cols-5 gap-3 mb-4">
            {PRESET_AMOUNTS.map((preset) => (
              <button
                key={preset}
                onClick={() => setAmount(String(preset))}
                className={`p-4 border-4 border-black font-black text-xl text-center transition-all ${
                  parseFloat(amount) === preset
                    ? 'bg-rose-200 translate-x-[2px] translate-y-[2px] shadow-none'
                    : 'bg-white brutal-shadow-sm hover:brutal-shadow-md'
                }`}
                data-testid={`donate-${preset}`}
              >
                ${preset}
              </button>
            ))}
          </div>

          <div className="mb-4">
            <label className="block font-bold text-sm uppercase mb-2">Custom Amount ($)</label>
            <input
              type="number"
              min="1"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full border-4 border-black px-4 py-3 font-bold text-2xl"
              placeholder="Enter amount..."
              data-testid="donate-amount"
            />
          </div>

          {amount && parseFloat(amount) >= 1 && (
            <BrutalCard className="bg-amber-50 border-amber-400 mb-4">
              <p className="font-bold text-center text-lg">
                Your ${parseFloat(amount).toFixed(2)} donation could fund approximately{' '}
                <span className="text-2xl font-black text-rose-600">{storiesFromAmount}</span>{' '}
                stories for children!
              </p>
            </BrutalCard>
          )}

          <div className="mb-4">
            <label className="block font-bold text-sm uppercase mb-2">Message (optional)</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Leave a message of encouragement..."
              rows={2}
              className="w-full border-4 border-black px-4 py-3 font-medium resize-none"
              data-testid="donate-message"
            />
          </div>

          {user ? (
            <BrutalButton
              variant="rose"
              fullWidth
              size="lg"
              onClick={handleDonate}
              disabled={!amount || parseFloat(amount) < 1 || donateMutation.isPending}
              data-testid="donate-btn"
              className="flex items-center justify-center gap-2"
            >
              <Heart size={24} />
              {donateMutation.isPending ? 'Redirecting...' : `Donate $${parseFloat(amount || 0).toFixed(2)}`}
            </BrutalButton>
          ) : (
            <BrutalButton variant="indigo" fullWidth size="lg" onClick={() => navigate('/login')} data-testid="login-to-donate-btn">
              Login to Donate
            </BrutalButton>
          )}
          <p className="text-xs text-gray-500 text-center mt-2">Secure payment powered by Stripe</p>
        </BrutalCard>

        {/* Recent Donors */}
        {stats?.recent?.length > 0 && (
          <BrutalCard shadow="lg">
            <h3 className="text-xl font-black uppercase mb-4">Recent Supporters</h3>
            <div className="space-y-2">
              {stats.recent.map((d, i) => (
                <div key={i} className="flex items-center justify-between p-3 border-2 border-black">
                  <div>
                    <p className="font-bold">{d.donor_name}</p>
                    {d.message && <p className="text-sm text-gray-600 italic">"{d.message}"</p>}
                    <p className="text-xs text-gray-400">{new Date(d.created_date).toLocaleDateString()}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-black text-lg text-rose-600">${d.amount.toFixed(2)}</p>
                    <p className="text-xs text-gray-500">{d.stories_funded} stories</p>
                  </div>
                </div>
              ))}
            </div>
          </BrutalCard>
        )}
      </div>
    </div>
  );
};

export default DonatePage;
