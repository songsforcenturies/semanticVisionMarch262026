import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import { subscriptionAPI, couponAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalInput } from '@/components/brutal';
import { Crown, Users, BookOpen, Check, ArrowRight, Gift, Sparkles, Star } from 'lucide-react';
import { toast } from 'sonner';

const SubscriptionTab = () => {
  const { user } = useAuth();
  const { formatAmount } = useCurrency();
  const queryClient = useQueryClient();
  const [couponCode, setCouponCode] = useState('');

  const { data: subscription } = useQuery({
    queryKey: ['my-subscription', user?.id],
    queryFn: async () => (await subscriptionAPI.get(user.id)).data,
    enabled: !!user?.id,
  });

  const { data: availablePlans = [] } = useQuery({
    queryKey: ['available-plans'],
    queryFn: async () => (await subscriptionAPI.getAvailablePlans()).data,
  });

  const upgradeMutation = useMutation({
    mutationFn: (planId) => subscriptionAPI.upgrade({ plan_id: planId, use_wallet: true }),
    onSuccess: (res) => {
      toast.success(res.data.message);
      queryClient.invalidateQueries(['my-subscription']);
      queryClient.invalidateQueries(['wallet-balance']);
      queryClient.invalidateQueries(['wallet-transactions']);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Upgrade failed'),
  });

  const redeemMutation = useMutation({
    mutationFn: (code) => couponAPI.redeem(code),
    onSuccess: (res) => {
      toast.success(res.data.message);
      setCouponCode('');
      queryClient.invalidateQueries(['my-subscription']);
      queryClient.invalidateQueries(['wallet-balance']);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Redemption failed'),
  });

  const currentPlan = subscription?.plan || 'free';
  const seats = subscription?.student_seats || 0;
  const activeStudents = subscription?.active_students || 0;
  const status = subscription?.status || 'active';

  return (
    <div className="space-y-6" data-testid="subscription-tab">
      {/* Current Plan Card */}
      <BrutalCard shadow="xl" className="bg-gradient-to-r from-indigo-50 to-violet-50">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-bold uppercase text-gray-600 flex items-center gap-2">
              <Crown size={16} /> Current Subscription
            </p>
            <h2 className="text-4xl font-black uppercase mt-2" data-testid="current-plan-name">
              {currentPlan.replace(/_/g, ' ')}
            </h2>
            <div className="flex items-center gap-4 mt-3">
              <BrutalBadge variant={status === 'active' ? 'emerald' : 'rose'}>
                {status}
              </BrutalBadge>
              <span className="text-sm font-bold">
                <Users size={14} className="inline mr-1" />
                {activeStudents} / {seats} students
              </span>
            </div>
            {subscription?.features && (
              <div className="flex flex-wrap gap-2 mt-3">
                {subscription.features.voice_mentor && <BrutalBadge variant="amber">Voice Mentor</BrutalBadge>}
                {subscription.features.contracts && <BrutalBadge variant="amber">Contracts</BrutalBadge>}
                {subscription.features.advanced_analytics && <BrutalBadge variant="amber">Analytics</BrutalBadge>}
                {subscription.features.custom_narratives && <BrutalBadge variant="amber">Custom Stories</BrutalBadge>}
              </div>
            )}
          </div>
          <div className="w-20 h-20 border-4 border-black bg-indigo-200 flex items-center justify-center">
            <Crown size={40} className="text-indigo-700" />
          </div>
        </div>
      </BrutalCard>

      {/* Redeem Coupon / Invitation Code */}
      <BrutalCard shadow="lg">
        <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
          <Gift size={22} /> Redeem Coupon or Invitation Code
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          Enter a coupon code, invitation code, or gift code to unlock features, add student seats, or receive credits.
        </p>
        <div className="flex gap-3">
          <BrutalInput
            placeholder="Enter code..."
            value={couponCode}
            onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
            className="flex-1"
            data-testid="subscription-coupon-input"
          />
          <BrutalButton
            variant="emerald"
            disabled={!couponCode.trim() || redeemMutation.isPending}
            onClick={() => redeemMutation.mutate(couponCode.trim())}
            data-testid="subscription-redeem-btn"
          >
            {redeemMutation.isPending ? 'Redeeming...' : 'Redeem'}
          </BrutalButton>
        </div>
      </BrutalCard>

      {/* Available Plans */}
      {availablePlans.length > 0 && (
        <div>
          <h3 className="text-2xl font-black uppercase mb-4 flex items-center gap-2">
            <Sparkles size={22} /> Available Plans
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {availablePlans.map((plan) => {
              const isCurrent = currentPlan === plan.name.toLowerCase().replace(/ /g, '_');
              return (
                <BrutalCard
                  key={plan.id}
                  shadow="lg"
                  variant={isCurrent ? 'indigo' : 'default'}
                  className="relative"
                  data-testid={`plan-card-${plan.id}`}
                >
                  {isCurrent && (
                    <BrutalBadge variant="indigo" className="absolute -top-3 -right-3">
                      Current Plan
                    </BrutalBadge>
                  )}
                  <div className="mb-4">
                    <h4 className="text-xl font-black uppercase">{plan.name}</h4>
                    {plan.description && <p className="text-sm text-gray-600 mt-1">{plan.description}</p>}
                  </div>

                  <div className="text-3xl font-black text-indigo-600 mb-4">
                    {plan.price_monthly > 0 ? `${formatAmount(plan.price_monthly)}/mo` : 'Free'}
                  </div>

                  <div className="space-y-2 mb-6">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <Check size={16} className="text-emerald-600" />
                      <span>{plan.student_seats} student seats</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <Check size={16} className="text-emerald-600" />
                      <span>{plan.story_limit === -1 ? 'Unlimited' : plan.story_limit} stories</span>
                    </div>
                    {plan.features?.voice_mentor && (
                      <div className="flex items-center gap-2 text-sm font-medium">
                        <Star size={16} className="text-amber-500" />
                        <span>Voice Mentor</span>
                      </div>
                    )}
                    {plan.features?.advanced_analytics && (
                      <div className="flex items-center gap-2 text-sm font-medium">
                        <Star size={16} className="text-amber-500" />
                        <span>Advanced Analytics</span>
                      </div>
                    )}
                    {plan.features?.custom_narratives && (
                      <div className="flex items-center gap-2 text-sm font-medium">
                        <Star size={16} className="text-amber-500" />
                        <span>Custom Narratives</span>
                      </div>
                    )}
                  </div>

                  {!isCurrent ? (
                    <BrutalButton
                      variant="indigo"
                      fullWidth
                      disabled={upgradeMutation.isPending}
                      onClick={() => {
                        if (plan.price_monthly > 0) {
                          if (window.confirm(`Upgrade to ${plan.name} for ${formatAmount(plan.price_monthly)}/mo? This will be deducted from your wallet.`)) {
                            upgradeMutation.mutate(plan.id);
                          }
                        } else {
                          upgradeMutation.mutate(plan.id);
                        }
                      }}
                      className="flex items-center justify-center gap-2"
                      data-testid={`upgrade-btn-${plan.id}`}
                    >
                      {upgradeMutation.isPending ? 'Processing...' : (
                        <>
                          {plan.price_monthly > 0 ? 'Upgrade' : 'Switch'} <ArrowRight size={16} />
                        </>
                      )}
                    </BrutalButton>
                  ) : (
                    <div className="text-center py-3 font-bold text-indigo-700 border-4 border-indigo-300 bg-indigo-50">
                      Active Plan
                    </div>
                  )}
                </BrutalCard>
              );
            })}
          </div>
        </div>
      )}

      {availablePlans.length === 0 && (
        <BrutalCard shadow="lg" className="text-center py-8">
          <BookOpen size={48} className="mx-auto mb-4 text-gray-400" />
          <p className="font-bold text-gray-500">No subscription plans are available yet.</p>
          <p className="text-sm text-gray-400 mt-1">Contact your administrator to set up plans.</p>
        </BrutalCard>
      )}
    </div>
  );
};

export default SubscriptionTab;
