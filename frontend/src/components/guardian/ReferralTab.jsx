import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import { referralAPI } from '@/lib/api';
import apiClient from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge } from '@/components/brutal';
import { Share2, Copy, Check, Users, DollarSign, Gift } from 'lucide-react';
import { toast } from 'sonner';

const ReferralTab = () => {
  const { user } = useAuth();
  const { formatAmount } = useCurrency();
  const [copied, setCopied] = useState(false);

  const { data: codeData } = useQuery({
    queryKey: ['my-referral-code'],
    queryFn: async () => (await referralAPI.getMyCode()).data,
  });

  const { data: referralData } = useQuery({
    queryKey: ['my-referrals'],
    queryFn: async () => (await referralAPI.getMyReferrals()).data,
  });

  const { data: rewardData } = useQuery({
    queryKey: ['referral-reward-amount'],
    queryFn: async () => (await apiClient.get('/referrals/reward-amount')).data,
  });

  const referrals = referralData?.referrals || referralData || [];
  const totalEarned = referralData?.total_earned ?? referrals.reduce((sum, r) => sum + (r.reward_amount || 0), 0);
  const rewardAmount = rewardData?.referral_reward_amount ?? 5.0;

  const code = codeData?.referral_code || user?.referral_code || '';
  const shareUrl = `${window.location.origin}/register?ref=${code}`;

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6" data-testid="referral-tab">
      {/* Share Card */}
      <BrutalCard shadow="xl" className="bg-gradient-to-r from-violet-50 to-indigo-50">
        <div className="text-center mb-6">
          <Share2 size={48} className="mx-auto text-indigo-600 mb-3" />
          <h2 className="text-3xl font-black uppercase">Invite & Earn</h2>
          <p className="text-lg font-medium mt-2 text-gray-600">
            Share your code. You and your friend both get <span className="font-black text-indigo-600">{formatAmount(rewardAmount)}</span> wallet credit!
          </p>
        </div>

        <div className="bg-white border-4 border-black p-4 text-center mb-4">
          <p className="text-xs font-bold uppercase text-gray-500 mb-2">Your Referral Code</p>
          <p className="text-4xl font-black tracking-widest font-mono" data-testid="referral-code">{code}</p>
        </div>

        <div className="flex gap-3">
          <BrutalButton variant="indigo" fullWidth size="lg"
            onClick={() => handleCopy(code)}
            className="flex items-center justify-center gap-2"
            data-testid="copy-code-btn">
            {copied ? <Check size={20} /> : <Copy size={20} />}
            {copied ? 'Copied!' : 'Copy Code'}
          </BrutalButton>
          <BrutalButton variant="emerald" fullWidth size="lg"
            onClick={() => handleCopy(shareUrl)}
            className="flex items-center justify-center gap-2"
            data-testid="copy-link-btn">
            <Share2 size={20} />
            Copy Link
          </BrutalButton>
        </div>
      </BrutalCard>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <BrutalCard shadow="lg" className="text-center">
          <Users size={24} className="mx-auto text-indigo-600 mb-2" />
          <p className="text-3xl font-black" data-testid="referral-count">{referrals.length}</p>
          <p className="text-xs font-bold uppercase text-gray-500">Referred</p>
        </BrutalCard>
        <BrutalCard shadow="lg" className="text-center">
          <DollarSign size={24} className="mx-auto text-emerald-600 mb-2" />
          <p className="text-3xl font-black" data-testid="total-earned">{formatAmount(totalEarned)}</p>
          <p className="text-xs font-bold uppercase text-gray-500">Total Earned</p>
        </BrutalCard>
        <BrutalCard shadow="lg" className="text-center">
          <Gift size={24} className="mx-auto text-amber-600 mb-2" />
          <p className="text-3xl font-black" data-testid="friends-saved">{formatAmount(totalEarned)}</p>
          <p className="text-xs font-bold uppercase text-gray-500">Friends Saved</p>
        </BrutalCard>
      </div>

      {/* Referral History */}
      <BrutalCard shadow="lg">
        <h3 className="text-xl font-black uppercase mb-4">Referral History</h3>
        {referrals.length === 0 ? (
          <p className="text-center py-8 text-gray-500 font-bold">
            No referrals yet. Share your code to start earning!
          </p>
        ) : (
          <div className="space-y-2">
            {referrals.map((ref, i) => (
              <div key={ref.id || i} className="flex items-center justify-between p-3 border-2 border-black" data-testid={`referral-${i}`}>
                <div>
                  <p className="font-bold">{ref.referred_name || 'User'}</p>
                  <p className="text-xs text-gray-500">{new Date(ref.created_date).toLocaleDateString()}</p>
                </div>
                <BrutalBadge variant="emerald" size="sm">+{formatAmount(ref.reward_amount || rewardAmount)}</BrutalBadge>
              </div>
            ))}
          </div>
        )}
      </BrutalCard>
    </div>
  );
};

export default ReferralTab;
