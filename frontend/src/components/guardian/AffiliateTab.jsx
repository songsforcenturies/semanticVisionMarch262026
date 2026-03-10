import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import { affiliateAPI } from '@/lib/api';
import { BrutalCard, BrutalBadge } from '@/components/brutal';
import { Share2, Copy, Check, Users, DollarSign, Clock, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

const AffiliateTab = () => {
  const { user } = useAuth();
  const { formatAmount } = useCurrency();
  const [copied, setCopied] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['affiliate-my-stats'],
    queryFn: async () => (await affiliateAPI.getMyStats()).data,
  });

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  if (isLoading) {
    return (
      <div className="text-center py-16" data-testid="affiliate-tab-loading">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto mb-3" />
        <p className="font-bold text-gray-500">Loading affiliate data...</p>
      </div>
    );
  }

  if (!data?.is_affiliate) {
    return (
      <BrutalCard shadow="xl" className="text-center py-12" data-testid="affiliate-tab-not-affiliate">
        <Share2 size={48} className="mx-auto text-gray-300 mb-4" />
        <h3 className="text-xl font-black mb-2">Not an Affiliate Yet</h3>
        <p className="text-gray-500 font-medium mb-4">
          Join our affiliate program to earn money by referring families to Semantic Vision.
        </p>
        <a
          href="/affiliate"
          className="inline-flex items-center gap-2 px-6 py-3 bg-black text-white font-bold rounded-lg border-2 border-black hover:bg-gray-800 transition-all"
          data-testid="join-affiliate-btn"
        >
          <Share2 size={18} /> Join Affiliate Program
        </a>
      </BrutalCard>
    );
  }

  const aff = data.affiliate;
  const referrals = data.referrals || [];
  const shareUrl = `${window.location.origin}/register?ref=${aff.affiliate_code}`;

  return (
    <div className="space-y-6" data-testid="affiliate-tab">
      {/* Status Banner */}
      <BrutalCard shadow="xl" className={aff.confirmed ? 'bg-gradient-to-r from-emerald-50 to-teal-50' : 'bg-gradient-to-r from-amber-50 to-yellow-50'}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Share2 size={24} className={aff.confirmed ? 'text-emerald-600' : 'text-amber-600'} />
              <h2 className="text-2xl font-black uppercase">Affiliate Dashboard</h2>
            </div>
            <p className="text-gray-600 font-medium">
              {aff.confirmed
                ? 'Your affiliate account is active. Share your link to earn!'
                : 'Your affiliate application is pending approval.'}
            </p>
          </div>
          <BrutalBadge variant={aff.confirmed ? 'emerald' : 'amber'} size="lg" data-testid="affiliate-status-badge">
            {aff.confirmed ? 'Active' : 'Pending'}
          </BrutalBadge>
        </div>
      </BrutalCard>

      {/* Affiliate Code & Link */}
      {aff.confirmed && (
        <BrutalCard shadow="xl">
          <div className="text-center mb-4">
            <p className="text-xs font-bold uppercase text-gray-500 mb-2">Your Affiliate Code</p>
            <p className="text-3xl font-black tracking-widest font-mono" data-testid="affiliate-code-display">{aff.affiliate_code}</p>
          </div>
          <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 mb-4">
            <p className="text-xs font-bold uppercase text-gray-500 mb-1">Referral Link</p>
            <p className="text-sm break-all text-indigo-600 font-medium" data-testid="affiliate-link-display">{shareUrl}</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => handleCopy(aff.affiliate_code)}
              className="flex-1 flex items-center justify-center gap-2 py-3 bg-black text-white font-bold rounded-lg border-2 border-black hover:bg-gray-800 transition-all"
              data-testid="copy-affiliate-code-btn"
            >
              {copied ? <Check size={18} /> : <Copy size={18} />}
              {copied ? 'Copied!' : 'Copy Code'}
            </button>
            <button
              onClick={() => handleCopy(shareUrl)}
              className="flex-1 flex items-center justify-center gap-2 py-3 bg-indigo-600 text-white font-bold rounded-lg border-2 border-indigo-700 hover:bg-indigo-700 transition-all"
              data-testid="copy-affiliate-link-btn"
            >
              <Share2 size={18} /> Copy Link
            </button>
          </div>
        </BrutalCard>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <BrutalCard shadow="lg" className="text-center">
          <Users size={24} className="mx-auto text-indigo-600 mb-2" />
          <p className="text-3xl font-black" data-testid="affiliate-total-referrals">{aff.total_referrals || 0}</p>
          <p className="text-xs font-bold uppercase text-gray-500">Referrals</p>
        </BrutalCard>
        <BrutalCard shadow="lg" className="text-center">
          <DollarSign size={24} className="mx-auto text-emerald-600 mb-2" />
          <p className="text-3xl font-black" data-testid="affiliate-total-earned">{formatAmount(aff.total_earned || 0)}</p>
          <p className="text-xs font-bold uppercase text-gray-500">Total Earned</p>
        </BrutalCard>
        <BrutalCard shadow="lg" className="text-center">
          <Clock size={24} className="mx-auto text-amber-600 mb-2" />
          <p className="text-3xl font-black" data-testid="affiliate-pending-balance">{formatAmount(aff.pending_balance || 0)}</p>
          <p className="text-xs font-bold uppercase text-gray-500">Pending</p>
        </BrutalCard>
        <BrutalCard shadow="lg" className="text-center">
          <TrendingUp size={24} className="mx-auto text-violet-600 mb-2" />
          <p className="text-3xl font-black" data-testid="affiliate-paid-out">{formatAmount(aff.total_paid || 0)}</p>
          <p className="text-xs font-bold uppercase text-gray-500">Paid Out</p>
        </BrutalCard>
      </div>

      {/* Reward Info */}
      <BrutalCard shadow="lg" className="bg-indigo-50">
        <div className="flex items-center gap-3">
          <DollarSign size={28} className="text-indigo-600" />
          <div>
            <p className="font-black text-lg">Your Reward Rate</p>
            <p className="text-gray-600 font-medium text-sm">
              You earn <span className="font-black text-indigo-600">{formatAmount(aff.flat_fee_amount || 5)}</span> for every new family that signs up with your referral link.
            </p>
          </div>
        </div>
      </BrutalCard>

      {/* Referral History */}
      <BrutalCard shadow="lg" data-testid="affiliate-referral-history">
        <h3 className="text-xl font-black uppercase mb-4">Referral History</h3>
        {referrals.length === 0 ? (
          <div className="text-center py-10">
            <Users size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="font-bold text-gray-500">No referrals yet. Share your link to start earning!</p>
          </div>
        ) : (
          <div className="space-y-2">
            {referrals.map((ref, i) => (
              <div key={ref.id || i} className="flex items-center justify-between p-3 border-2 border-gray-200 rounded-lg" data-testid={`affiliate-referral-${i}`}>
                <div>
                  <p className="font-bold">{ref.referred_name || 'New User'}</p>
                  <p className="text-xs text-gray-500">{new Date(ref.created_date).toLocaleDateString()}</p>
                </div>
                <BrutalBadge variant="emerald" size="sm">+{formatAmount(ref.reward_amount || aff.flat_fee_amount || 5)}</BrutalBadge>
              </div>
            ))}
          </div>
        )}
      </BrutalCard>
    </div>
  );
};

export default AffiliateTab;
