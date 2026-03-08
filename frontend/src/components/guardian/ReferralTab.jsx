import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import { referralAPI } from '@/lib/api';
import apiClient from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge } from '@/components/brutal';
import { Share2, Copy, Check, Users, DollarSign, Gift, Trophy, Medal, Crown, Flame, Timer } from 'lucide-react';
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

  const { data: activeContest } = useQuery({
    queryKey: ['active-contest'],
    queryFn: async () => (await referralAPI.getActiveContest()).data,
  });

  const contestId = activeContest?.id;
  const { data: leaderboardData } = useQuery({
    queryKey: ['referral-leaderboard', contestId],
    queryFn: async () => (await referralAPI.getLeaderboard(contestId)).data,
  });

  const referrals = referralData?.referrals || [];
  const totalEarned = referralData?.total_earned ?? 0;
  const rewardAmount = rewardData?.referral_reward_amount ?? 5.0;
  const leaderboard = leaderboardData?.leaderboard || [];

  const code = codeData?.referral_code || user?.referral_code || '';
  const shareUrl = `${window.location.origin}/register?ref=${code}`;

  const myRank = leaderboard.find(e => e.user_id === user?.id)?.rank;

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const getTimeLeft = (endDate) => {
    if (!endDate) return null;
    const diff = new Date(endDate) - new Date();
    if (diff <= 0) return 'Ended';
    const days = Math.floor(diff / 86400000);
    const hours = Math.floor((diff % 86400000) / 3600000);
    if (days > 0) return `${days}d ${hours}h left`;
    const mins = Math.floor((diff % 3600000) / 60000);
    return `${hours}h ${mins}m left`;
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return <Crown size={22} className="text-yellow-500" />;
    if (rank === 2) return <Medal size={22} className="text-gray-400" />;
    if (rank === 3) return <Medal size={22} className="text-amber-600" />;
    return <span className="font-black text-lg w-[22px] text-center">{rank}</span>;
  };

  const getRankBg = (rank) => {
    if (rank === 1) return 'bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-400';
    if (rank === 2) return 'bg-gradient-to-r from-gray-50 to-slate-50 border-gray-300';
    if (rank === 3) return 'bg-gradient-to-r from-orange-50 to-amber-50 border-orange-300';
    return 'bg-white border-gray-200';
  };

  return (
    <div className="space-y-6" data-testid="referral-tab">
      {/* Active Contest Banner */}
      {activeContest?.id && (
        <BrutalCard shadow="xl" className="bg-gradient-to-r from-violet-600 to-indigo-700 text-white border-violet-800" data-testid="contest-banner">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Trophy size={28} className="text-yellow-300" />
                <h2 className="text-2xl font-black uppercase">{activeContest.title}</h2>
              </div>
              <p className="text-violet-100 font-medium mb-4">{activeContest.description}</p>
              <div className="bg-white/15 backdrop-blur-sm rounded-lg p-4 inline-block">
                <p className="text-xs font-bold uppercase text-violet-200 mb-1">Grand Prize</p>
                <p className="text-2xl font-black text-yellow-300" data-testid="contest-prize">{activeContest.prize_description}</p>
                {activeContest.prize_value && (
                  <p className="text-sm text-violet-200 mt-1">Value: {formatAmount(activeContest.prize_value)}</p>
                )}
              </div>
              {activeContest.runner_up_prizes?.length > 0 && (
                <div className="flex gap-3 mt-3">
                  {activeContest.runner_up_prizes.map((p, i) => (
                    <div key={i} className="bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
                      <p className="text-xs font-bold text-violet-200">{p.place === 2 ? '2nd' : p.place === 3 ? '3rd' : `${p.place}th`} Place</p>
                      <p className="font-black text-sm">{p.prize}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 bg-white/15 backdrop-blur-sm rounded-lg px-3 py-2">
                <Timer size={16} className="text-yellow-300" />
                <span className="font-black text-sm">{getTimeLeft(activeContest.end_date)}</span>
              </div>
              {myRank && (
                <div className="mt-3 bg-yellow-400 text-black rounded-lg px-3 py-2">
                  <p className="text-xs font-bold">Your Rank</p>
                  <p className="text-2xl font-black">#{myRank}</p>
                </div>
              )}
            </div>
          </div>
        </BrutalCard>
      )}

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
            <Share2 size={20} /> Copy Link
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

      {/* Leaderboard */}
      <BrutalCard shadow="xl" data-testid="leaderboard-card">
        <div className="flex items-center gap-3 mb-5">
          <Flame size={28} className="text-orange-500" />
          <h3 className="text-2xl font-black uppercase">
            {activeContest?.id ? 'Contest Leaderboard' : 'Top Referrers'}
          </h3>
        </div>

        {leaderboard.length === 0 ? (
          <div className="text-center py-10">
            <Trophy size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="font-bold text-gray-500">No referrals yet. Be the first to claim the top spot!</p>
          </div>
        ) : (
          <div className="space-y-2">
            {leaderboard.map((entry) => {
              const isMe = entry.user_id === user?.id;
              return (
                <div
                  key={entry.user_id}
                  className={`flex items-center gap-4 p-3 border-2 rounded-lg transition-all ${getRankBg(entry.rank)} ${isMe ? 'ring-4 ring-indigo-400 ring-offset-1' : ''}`}
                  data-testid={`leaderboard-rank-${entry.rank}`}
                >
                  <div className="flex items-center justify-center w-10">
                    {getRankIcon(entry.rank)}
                  </div>
                  <div className="flex-1">
                    <p className="font-black text-lg">
                      {entry.display_name}
                      {isMe && <BrutalBadge variant="indigo" size="sm" className="ml-2">YOU</BrutalBadge>}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-black text-xl">{entry.referral_count}</p>
                    <p className="text-xs font-bold text-gray-500">referrals</p>
                  </div>
                  <div className="text-right min-w-[80px]">
                    <BrutalBadge variant="emerald" size="sm">{formatAmount(entry.total_earned)}</BrutalBadge>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </BrutalCard>

      {/* Referral History */}
      <BrutalCard shadow="lg">
        <h3 className="text-xl font-black uppercase mb-4">Your Referral History</h3>
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
