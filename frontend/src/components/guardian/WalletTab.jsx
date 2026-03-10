import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import { walletAPI, couponAPI, paypalAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalInput } from '@/components/brutal';
import { Wallet, Plus, ArrowUpRight, ArrowDownLeft, Gift, Clock, DollarSign, CreditCard } from 'lucide-react';
import { PayPalScriptProvider, PayPalButtons } from '@paypal/react-paypal-js';
import { toast } from 'sonner';

const PACKAGE_LABELS = {
  small: '$5',
  medium: '$10',
  large: '$25',
  xl: '$50',
  xxl: '$100',
};

const WalletTab = () => {
  const { user } = useAuth();
  const { formatAmount } = useCurrency();
  const queryClient = useQueryClient();
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [couponCode, setCouponCode] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('stripe');

  // Check for payment return
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get('session_id');
    const paymentStatus = params.get('payment');

    if (sessionId && paymentStatus === 'success') {
      pollPaymentStatus(sessionId);
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
    } else if (paymentStatus === 'cancelled') {
      toast.error('Payment was cancelled');
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    if (attempts >= 5) {
      toast.info('Payment is still processing. Please check back shortly.');
      return;
    }
    try {
      const res = await walletAPI.getPaymentStatus(sessionId);
      if (res.data.payment_status === 'paid') {
        toast.success(`${formatAmount(res.data.amount)} added to your wallet!`);
        queryClient.invalidateQueries(['wallet-balance']);
        queryClient.invalidateQueries(['wallet-transactions']);
        return;
      }
      if (res.data.status === 'expired') {
        toast.error('Payment session expired.');
        return;
      }
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), 2000);
    } catch {
      toast.error('Error checking payment status');
    }
  };

  const { data: balanceData } = useQuery({
    queryKey: ['wallet-balance'],
    queryFn: async () => (await walletAPI.getBalance()).data,
  });

  const { data: transactions = [] } = useQuery({
    queryKey: ['wallet-transactions'],
    queryFn: async () => (await walletAPI.getTransactions()).data,
  });

  const { data: packages = [] } = useQuery({
    queryKey: ['wallet-packages'],
    queryFn: async () => (await walletAPI.getPackages()).data,
  });

  const { data: paypalConfig } = useQuery({
    queryKey: ['paypal-config'],
    queryFn: async () => (await paypalAPI.getConfig()).data,
  });

  const topupMutation = useMutation({
    mutationFn: (packageId) =>
      walletAPI.topup({ package_id: packageId, origin_url: window.location.origin }),
    onSuccess: (res) => {
      if (res.data.url) {
        window.location.href = res.data.url;
      }
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Top-up failed'),
  });

  const redeemMutation = useMutation({
    mutationFn: (code) => couponAPI.redeem(code),
    onSuccess: (res) => {
      toast.success(res.data.message);
      setCouponCode('');
      queryClient.invalidateQueries(['wallet-balance']);
      queryClient.invalidateQueries(['wallet-transactions']);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Redemption failed'),
  });

  const balance = balanceData?.balance ?? 0;

  return (
    <div className="space-y-6" data-testid="wallet-tab">
      {/* Balance Card */}
      <BrutalCard shadow="xl" className="bg-gradient-to-r from-indigo-50 to-violet-50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-bold uppercase text-gray-600 flex items-center gap-2">
              <Wallet size={16} /> Account Balance
            </p>
            <p className="text-5xl font-black mt-2" data-testid="wallet-balance">
              {formatAmount(balance)}
            </p>
          </div>
          <div className="w-20 h-20 border-4 border-black bg-indigo-200 flex items-center justify-center">
            <DollarSign size={40} className="text-indigo-700" />
          </div>
        </div>
      </BrutalCard>

      {/* Top-Up Section */}
      <BrutalCard shadow="lg">
        <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
          <CreditCard size={22} /> Add Funds
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mb-4">
          {packages.map((pkg) => (
            <button
              key={pkg.id}
              onClick={() => setSelectedPackage(pkg.id)}
              className={`p-4 border-4 border-black font-black text-xl text-center transition-all ${
                selectedPackage === pkg.id
                  ? 'bg-indigo-200 translate-x-[2px] translate-y-[2px] shadow-none'
                  : 'bg-white brutal-shadow-sm hover:brutal-shadow-md'
              }`}
              data-testid={`package-${pkg.id}`}
            >
              {formatAmount(pkg.amount)}
            </button>
          ))}
        </div>

        {/* Payment Method Toggle */}
        <div className="flex gap-2 mb-4" data-testid="payment-method-toggle">
          <button
            onClick={() => setPaymentMethod('stripe')}
            className={`flex-1 p-3 border-4 border-black font-bold text-sm transition-all ${
              paymentMethod === 'stripe'
                ? 'bg-indigo-200 translate-x-[1px] translate-y-[1px] shadow-none'
                : 'bg-white brutal-shadow-sm'
            }`}
            data-testid="payment-method-stripe"
          >
            <CreditCard size={16} className="inline mr-2" />
            Card / Stripe
          </button>
          {paypalConfig?.enabled && (
            <button
              onClick={() => setPaymentMethod('paypal')}
              className={`flex-1 p-3 border-4 border-black font-bold text-sm transition-all ${
                paymentMethod === 'paypal'
                  ? 'bg-yellow-200 translate-x-[1px] translate-y-[1px] shadow-none'
                  : 'bg-white brutal-shadow-sm'
              }`}
              data-testid="payment-method-paypal"
            >
              <svg className="inline mr-2 w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944.901C5.026.382 5.474 0 5.998 0h7.46c2.57 0 4.578.543 5.69 1.81 1.01 1.15 1.304 2.42 1.012 4.287-.023.143-.047.288-.077.437-.983 5.05-4.349 6.797-8.647 6.797H9.603c-.534 0-.988.393-1.07.927l-.92 5.82-.262 1.656a.546.546 0 0 1-.54.462l.265-1.86z"/></svg>
              PayPal
            </button>
          )}
        </div>

        {/* Stripe Button */}
        {paymentMethod === 'stripe' && (
          <>
            <BrutalButton
              variant="indigo"
              fullWidth
              size="lg"
              disabled={!selectedPackage || topupMutation.isPending}
              onClick={() => selectedPackage && topupMutation.mutate(selectedPackage)}
              data-testid="topup-btn"
              className="flex items-center justify-center gap-2"
            >
              <Plus size={20} />
              {topupMutation.isPending
                ? 'Redirecting to checkout...'
                : selectedPackage
                ? `Pay ${PACKAGE_LABELS[selectedPackage] || ''} with Card`
                : 'Select an amount'}
            </BrutalButton>
            <p className="text-xs text-gray-500 font-medium mt-2 text-center">
              Powered by Stripe. Secure card payments, Google Pay, Apple Pay.
            </p>
          </>
        )}

        {/* PayPal Button */}
        {paymentMethod === 'paypal' && paypalConfig?.enabled && selectedPackage && (
          <PayPalScriptProvider options={{ clientId: paypalConfig.client_id, currency: 'USD' }}>
            <div data-testid="paypal-button-container" className="mt-2">
              <PayPalButtons
                style={{ layout: 'vertical', shape: 'rect', label: 'pay', height: 48 }}
                createOrder={async () => {
                  try {
                    const res = await paypalAPI.createOrder({
                      package_id: selectedPackage,
                      origin_url: window.location.origin,
                    });
                    return res.data.order_id;
                  } catch (err) {
                    toast.error(err.response?.data?.detail || 'Failed to create PayPal order');
                    throw err;
                  }
                }}
                onApprove={async (data) => {
                  try {
                    const res = await paypalAPI.captureOrder(data.orderID);
                    if (res.data.status === 'completed' || res.data.status === 'already_credited') {
                      toast.success(`$${res.data.amount} added to your wallet via PayPal!`);
                      queryClient.invalidateQueries(['wallet-balance']);
                      queryClient.invalidateQueries(['wallet-transactions']);
                    } else {
                      toast.error('Payment not completed. Please try again.');
                    }
                  } catch (err) {
                    toast.error(err.response?.data?.detail || 'Failed to capture payment');
                  }
                }}
                onCancel={() => toast.info('PayPal payment cancelled')}
                onError={(err) => {
                  console.error('PayPal error:', err);
                  toast.error('PayPal encountered an error');
                }}
              />
            </div>
          </PayPalScriptProvider>
        )}
        {paymentMethod === 'paypal' && !selectedPackage && (
          <p className="text-center text-gray-500 font-bold py-4">Select an amount above to pay with PayPal</p>
        )}
      </BrutalCard>

      {/* Coupon Redemption */}
      <BrutalCard shadow="lg">
        <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
          <Gift size={22} /> Redeem Coupon
        </h3>
        <div className="flex gap-3">
          <BrutalInput
            placeholder="Enter coupon code..."
            value={couponCode}
            onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
            className="flex-1"
            data-testid="coupon-input"
          />
          <BrutalButton
            variant="emerald"
            disabled={!couponCode.trim() || redeemMutation.isPending}
            onClick={() => redeemMutation.mutate(couponCode.trim())}
            data-testid="redeem-btn"
          >
            {redeemMutation.isPending ? 'Redeeming...' : 'Redeem'}
          </BrutalButton>
        </div>
      </BrutalCard>

      {/* Transaction History */}
      <BrutalCard shadow="lg">
        <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
          <Clock size={22} /> Transaction History
        </h3>
        {transactions.length === 0 ? (
          <p className="text-center py-8 text-gray-500 font-bold">No transactions yet</p>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {transactions.map((txn, i) => (
              <div
                key={txn.id || i}
                className="flex items-center justify-between p-3 border-2 border-black"
                data-testid={`transaction-${i}`}
              >
                <div className="flex items-center gap-3">
                  {txn.type === 'credit' || txn.type === 'coupon' ? (
                    <div className="w-8 h-8 bg-emerald-100 border-2 border-black flex items-center justify-center">
                      <ArrowDownLeft size={16} className="text-emerald-700" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 bg-rose-100 border-2 border-black flex items-center justify-center">
                      <ArrowUpRight size={16} className="text-rose-700" />
                    </div>
                  )}
                  <div>
                    <p className="font-bold text-sm">{txn.description}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(txn.created_date).toLocaleDateString()} {new Date(txn.created_date).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-black text-lg ${txn.type === 'debit' ? 'text-rose-600' : 'text-emerald-600'}`}>
                    {txn.type === 'debit' ? '-' : '+'}{formatAmount(txn.amount)}
                  </p>
                  <p className="text-xs text-gray-500">Bal: {formatAmount(txn.balance_after)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </BrutalCard>
    </div>
  );
};

export default WalletTab;
