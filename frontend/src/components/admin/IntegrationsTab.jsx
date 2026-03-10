import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalInput } from '@/components/brutal';
import { CreditCard, Key, Mail, Eye, EyeOff, CheckCircle, XCircle, Shield } from 'lucide-react';
import { toast } from 'sonner';

const IntegrationsTab = () => {
  const queryClient = useQueryClient();
  const [showKeys, setShowKeys] = useState({});
  const [form, setForm] = useState({
    stripe_api_key: '',
    paypal_client_id: '',
    paypal_secret: '',
    resend_api_key: '',
    daily_api_key: '',
    sender_email: 'Semantic Vision <hello@semanticvision.ai>',
    paypal_mode: 'sandbox',
    stripe_enabled: true,
    paypal_enabled: false,
    resend_enabled: true,
    daily_enabled: false,
  });

  const { data: integrations, isLoading } = useQuery({
    queryKey: ['admin-integrations'],
    queryFn: async () => (await adminAPI.getIntegrations()).data,
  });

  useEffect(() => {
    if (integrations) {
      setForm({
        stripe_api_key: integrations.stripe.api_key_masked || '',
        paypal_client_id: integrations.paypal.client_id_masked || '',
        paypal_secret: integrations.paypal.secret_masked || '',
        resend_api_key: integrations.resend.api_key_masked || '',
        daily_api_key: integrations.daily?.api_key_masked || '',
        sender_email: integrations.resend.sender_email || 'Semantic Vision <hello@semanticvision.ai>',
        paypal_mode: integrations.paypal.mode || 'sandbox',
        stripe_enabled: integrations.stripe.enabled,
        paypal_enabled: integrations.paypal.enabled,
        resend_enabled: integrations.resend.enabled,
        daily_enabled: integrations.daily?.enabled || false,
      });
    }
  }, [integrations]);

  const saveMutation = useMutation({
    mutationFn: (data) => adminAPI.updateIntegrations(data),
    onSuccess: () => {
      toast.success('Integration settings saved!');
      queryClient.invalidateQueries(['admin-integrations']);
      queryClient.invalidateQueries(['paypal-config']);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Save failed'),
  });

  const toggleShowKey = (field) => setShowKeys((prev) => ({ ...prev, [field]: !prev[field] }));

  const handleKeyChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const StatusDot = ({ active }) => (
    <span className={`inline-flex items-center gap-1 text-xs font-bold uppercase ${active ? 'text-emerald-400' : 'text-gray-500'}`}>
      {active ? <CheckCircle size={14} /> : <XCircle size={14} />}
      {active ? 'Configured' : 'Not Set'}
    </span>
  );

  if (isLoading) return <div className="text-center py-8 font-bold">Loading integrations...</div>;

  return (
    <div className="space-y-6" data-testid="integrations-tab">
      <BrutalCard shadow="xl" className="bg-gradient-to-r from-slate-800 to-slate-900 text-white border-indigo-500">
        <div className="flex items-center gap-3 mb-2">
          <Shield size={24} className="text-indigo-400" />
          <h3 className="text-xl font-black uppercase">Integration Settings</h3>
        </div>
        <p className="text-sm text-slate-400">Manage your payment providers and email service API keys. Keys are encrypted and masked for security.</p>
      </BrutalCard>

      {/* Stripe */}
      <BrutalCard shadow="lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-100 border-2 border-black flex items-center justify-center">
              <CreditCard size={20} className="text-indigo-600" />
            </div>
            <div>
              <h4 className="font-black text-lg uppercase">Stripe</h4>
              <p className="text-xs text-gray-500">Card payments, Google Pay, Apple Pay</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <StatusDot active={integrations?.stripe?.has_key} />
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.stripe_enabled}
                onChange={(e) => handleKeyChange('stripe_enabled', e.target.checked)}
                className="w-5 h-5"
                data-testid="stripe-enabled-toggle"
              />
              <span className="text-sm font-bold">Enabled</span>
            </label>
          </div>
        </div>
        <div className="relative">
          <label className="block font-bold text-sm uppercase mb-2">API Secret Key</label>
          <div className="flex gap-2">
            <input
              type={showKeys.stripe ? 'text' : 'password'}
              value={form.stripe_api_key}
              onChange={(e) => handleKeyChange('stripe_api_key', e.target.value)}
              onFocus={() => { if (form.stripe_api_key.startsWith('*')) handleKeyChange('stripe_api_key', ''); }}
              placeholder="sk_live_... or sk_test_..."
              className="flex-1 border-4 border-black px-4 py-3 font-mono text-sm"
              data-testid="stripe-api-key-input"
            />
            <button
              onClick={() => toggleShowKey('stripe')}
              className="border-4 border-black px-3 bg-gray-100 hover:bg-gray-200"
              data-testid="stripe-key-toggle-visibility"
            >
              {showKeys.stripe ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">Get your key from <a href="https://dashboard.stripe.com/apikeys" target="_blank" rel="noreferrer" className="text-indigo-600 underline">Stripe Dashboard</a></p>
        </div>
      </BrutalCard>

      {/* PayPal */}
      <BrutalCard shadow="lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 border-2 border-black flex items-center justify-center">
              <svg className="w-5 h-5 text-yellow-700" viewBox="0 0 24 24" fill="currentColor"><path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944.901C5.026.382 5.474 0 5.998 0h7.46c2.57 0 4.578.543 5.69 1.81 1.01 1.15 1.304 2.42 1.012 4.287-.023.143-.047.288-.077.437-.983 5.05-4.349 6.797-8.647 6.797H9.603c-.534 0-.988.393-1.07.927l-.92 5.82-.262 1.656a.546.546 0 0 1-.54.462l.265-1.86z"/></svg>
            </div>
            <div>
              <h4 className="font-black text-lg uppercase">PayPal</h4>
              <p className="text-xs text-gray-500">PayPal checkout, Venmo, PayPal Credit</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <StatusDot active={integrations?.paypal?.has_keys} />
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.paypal_enabled}
                onChange={(e) => handleKeyChange('paypal_enabled', e.target.checked)}
                className="w-5 h-5"
                data-testid="paypal-enabled-toggle"
              />
              <span className="text-sm font-bold">Enabled</span>
            </label>
          </div>
        </div>
        <div className="space-y-3">
          <div>
            <label className="block font-bold text-sm uppercase mb-2">Client ID</label>
            <div className="flex gap-2">
              <input
                type={showKeys.paypal_id ? 'text' : 'password'}
                value={form.paypal_client_id}
                onChange={(e) => handleKeyChange('paypal_client_id', e.target.value)}
                onFocus={() => { if (form.paypal_client_id.startsWith('*')) handleKeyChange('paypal_client_id', ''); }}
                placeholder="AV3nT..."
                className="flex-1 border-4 border-black px-4 py-3 font-mono text-sm"
                data-testid="paypal-client-id-input"
              />
              <button onClick={() => toggleShowKey('paypal_id')} className="border-4 border-black px-3 bg-gray-100 hover:bg-gray-200">
                {showKeys.paypal_id ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>
          <div>
            <label className="block font-bold text-sm uppercase mb-2">Secret</label>
            <div className="flex gap-2">
              <input
                type={showKeys.paypal_secret ? 'text' : 'password'}
                value={form.paypal_secret}
                onChange={(e) => handleKeyChange('paypal_secret', e.target.value)}
                onFocus={() => { if (form.paypal_secret.startsWith('*')) handleKeyChange('paypal_secret', ''); }}
                placeholder="EJk2..."
                className="flex-1 border-4 border-black px-4 py-3 font-mono text-sm"
                data-testid="paypal-secret-input"
              />
              <button onClick={() => toggleShowKey('paypal_secret')} className="border-4 border-black px-3 bg-gray-100 hover:bg-gray-200">
                {showKeys.paypal_secret ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>
          <div>
            <label className="block font-bold text-sm uppercase mb-2">Mode</label>
            <div className="flex gap-3">
              <button
                onClick={() => handleKeyChange('paypal_mode', 'sandbox')}
                className={`flex-1 p-3 border-4 border-black font-bold text-center ${form.paypal_mode === 'sandbox' ? 'bg-yellow-100' : 'bg-white'}`}
                data-testid="paypal-mode-sandbox"
              >
                Sandbox (Testing)
              </button>
              <button
                onClick={() => handleKeyChange('paypal_mode', 'live')}
                className={`flex-1 p-3 border-4 border-black font-bold text-center ${form.paypal_mode === 'live' ? 'bg-green-100' : 'bg-white'}`}
                data-testid="paypal-mode-live"
              >
                Live (Production)
              </button>
            </div>
          </div>
          <p className="text-xs text-gray-500">Get your keys from <a href="https://developer.paypal.com/dashboard/applications" target="_blank" rel="noreferrer" className="text-indigo-600 underline">PayPal Developer Dashboard</a></p>
        </div>
      </BrutalCard>

      {/* Resend / Email */}
      <BrutalCard shadow="lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-100 border-2 border-black flex items-center justify-center">
              <Mail size={20} className="text-emerald-600" />
            </div>
            <div>
              <h4 className="font-black text-lg uppercase">Resend (Email)</h4>
              <p className="text-xs text-gray-500">Transactional emails, verification, notifications</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <StatusDot active={integrations?.resend?.has_key} />
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.resend_enabled}
                onChange={(e) => handleKeyChange('resend_enabled', e.target.checked)}
                className="w-5 h-5"
                data-testid="resend-enabled-toggle"
              />
              <span className="text-sm font-bold">Enabled</span>
            </label>
          </div>
        </div>
        <div className="space-y-3">
          <div>
            <label className="block font-bold text-sm uppercase mb-2">API Key</label>
            <div className="flex gap-2">
              <input
                type={showKeys.resend ? 'text' : 'password'}
                value={form.resend_api_key}
                onChange={(e) => handleKeyChange('resend_api_key', e.target.value)}
                onFocus={() => { if (form.resend_api_key.startsWith('*')) handleKeyChange('resend_api_key', ''); }}
                placeholder="re_..."
                className="flex-1 border-4 border-black px-4 py-3 font-mono text-sm"
                data-testid="resend-api-key-input"
              />
              <button onClick={() => toggleShowKey('resend')} className="border-4 border-black px-3 bg-gray-100 hover:bg-gray-200">
                {showKeys.resend ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">Get your key from <a href="https://resend.com/api-keys" target="_blank" rel="noreferrer" className="text-indigo-600 underline">Resend Dashboard</a></p>
          </div>
          <div>
            <label className="block font-bold text-sm uppercase mb-2">Sender Email</label>
            <input
              type="text"
              value={form.sender_email}
              onChange={(e) => handleKeyChange('sender_email', e.target.value)}
              placeholder="Semantic Vision <hello@semanticvision.ai>"
              className="w-full border-4 border-black px-4 py-3 font-mono text-sm"
              data-testid="sender-email-input"
            />
            <p className="text-xs text-gray-500 mt-1">Format: Name &lt;email@domain.com&gt;. Domain must be verified in Resend.</p>
          </div>
        </div>
      </BrutalCard>

      {/* Daily.co (Screen Share) */}
      <BrutalCard shadow="lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 border-2 border-black flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" /></svg>
            </div>
            <div>
              <h4 className="font-black text-lg uppercase">Daily.co (Screen Share)</h4>
              <p className="text-xs text-gray-500">Video calls and screen sharing for support</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <StatusDot active={integrations?.daily?.has_key} />
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={form.daily_enabled}
                onChange={(e) => handleKeyChange('daily_enabled', e.target.checked)}
                className="w-5 h-5" data-testid="daily-enabled-toggle" />
              <span className="text-sm font-bold">Enabled</span>
            </label>
          </div>
        </div>
        <div>
          <label className="block font-bold text-sm uppercase mb-2">API Key</label>
          <div className="flex gap-2">
            <input type={showKeys.daily ? 'text' : 'password'} value={form.daily_api_key}
              onChange={(e) => handleKeyChange('daily_api_key', e.target.value)}
              onFocus={() => { if (form.daily_api_key.startsWith('*')) handleKeyChange('daily_api_key', ''); }}
              placeholder="your_daily_api_key..."
              className="flex-1 border-4 border-black px-4 py-3 font-mono text-sm" data-testid="daily-api-key-input" />
            <button onClick={() => toggleShowKey('daily')} className="border-4 border-black px-3 bg-gray-100 hover:bg-gray-200">
              {showKeys.daily ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">Get your key from <a href="https://dashboard.daily.co/developers" target="_blank" rel="noreferrer" className="text-indigo-600 underline">Daily.co Dashboard</a> (free: 10,000 min/month)</p>
        </div>
      </BrutalCard>

      {/* Save Button */}
      <BrutalButton
        variant="indigo"
        fullWidth
        size="lg"
        onClick={() => saveMutation.mutate(form)}
        disabled={saveMutation.isPending}
        data-testid="save-integrations-btn"
        className="flex items-center justify-center gap-2"
      >
        <Key size={20} />
        {saveMutation.isPending ? 'Saving...' : 'Save Integration Settings'}
      </BrutalButton>
    </div>
  );
};

export default IntegrationsTab;
