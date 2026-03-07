import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { brandPortalAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalInput } from '@/components/brutal';
import {
  Home, LogOut, BarChart3, Megaphone, DollarSign, PlusCircle, Trash2,
  Play, Pause, CreditCard, Clock, TrendingUp, Eye, Zap,
} from 'lucide-react';
import { toast } from 'sonner';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const AD_CATEGORIES = [
  'technology', 'education', 'food', 'sports', 'arts', 'health',
  'games', 'books', 'science', 'music', 'nature', 'travel',
];

const BrandPortal = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [campaignForm, setCampaignForm] = useState({
    name: '', description: '', products_text: '',
    target_categories: [], budget: '', cost_per_impression: '0.05',
  });
  const [topupAmount, setTopupAmount] = useState('');

  // Check payment return
  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get('session_id');
    const payment = params.get('payment');
    if (sessionId && payment === 'success') {
      pollTopup(sessionId);
      window.history.replaceState({}, '', '/brand-portal');
    } else if (payment === 'cancelled') {
      toast.error(t('brand.paymentCancelled'));
      window.history.replaceState({}, '', '/brand-portal');
    }
  }, []);

  const pollTopup = async (sessionId, attempts = 0) => {
    if (attempts >= 5) { toast.info(t('brand.paymentProcessing')); return; }
    try {
      const res = await brandPortalAPI.getTopupStatus(sessionId);
      if (res.data.status === 'paid') {
        toast.success(`$${res.data.amount.toFixed(2)} added to campaign budget!`);
        queryClient.invalidateQueries(['brand-dashboard']);
        return;
      }
      setTimeout(() => pollTopup(sessionId, attempts + 1), 2000);
    } catch { toast.error('Error checking payment'); }
  };

  const { data: dashboard } = useQuery({
    queryKey: ['brand-dashboard'],
    queryFn: async () => (await brandPortalAPI.getDashboard()).data,
  });

  const createCampaignMut = useMutation({
    mutationFn: (data) => brandPortalAPI.createCampaign(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['brand-dashboard']);
      toast.success('Campaign created!');
      setCampaignForm({ name: '', description: '', products_text: '', target_categories: [], budget: '', cost_per_impression: '0.05' });
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  const updateCampaignMut = useMutation({
    mutationFn: ({ id, data }) => brandPortalAPI.updateCampaign(id, data),
    onSuccess: () => { queryClient.invalidateQueries(['brand-dashboard']); toast.success('Campaign updated'); },
  });

  const deleteCampaignMut = useMutation({
    mutationFn: (id) => brandPortalAPI.deleteCampaign(id),
    onSuccess: () => { queryClient.invalidateQueries(['brand-dashboard']); toast.success('Campaign deleted'); },
  });

  const topupMut = useMutation({
    mutationFn: (amount) => brandPortalAPI.topup({ amount: parseFloat(amount), origin_url: window.location.origin }),
    onSuccess: (res) => { if (res.data.url) window.location.href = res.data.url; },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  const brand = dashboard?.brand;
  const stats = dashboard?.stats || {};
  const campaigns = dashboard?.campaigns || [];

  const notApproved = user?.role === 'brand_partner' && !user?.brand_approved;

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'campaigns', label: 'Campaigns', icon: Megaphone },
    { id: 'budget', label: 'Budget', icon: DollarSign },
    { id: 'impressions', label: 'Impressions', icon: Eye },
  ];

  return (
    <div className="min-h-screen bg-gray-50" data-testid="brand-portal">
      <header className="bg-white border-b-6 border-black brutal-shadow-md">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/')} className="p-3 border-4 border-black bg-amber-100 brutal-shadow-sm hover:brutal-shadow-md brutal-active">
                <Home size={24} />
              </button>
              <div>
                <h1 className="text-4xl font-black uppercase flex items-center gap-2">
                  <Megaphone size={32} className="text-amber-600" /> Brand Portal
                </h1>
                <p className="text-lg font-medium mt-1">
                  {brand?.name || user?.full_name}
                  {notApproved && <BrutalBadge variant="amber" size="sm" className="ml-2">PENDING APPROVAL</BrutalBadge>}
                </p>
              </div>
            </div>
            <BrutalButton variant="dark" onClick={() => { logout(); navigate('/login'); }} className="flex items-center gap-2">
              <LogOut size={20} /> Logout
            </BrutalButton>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {notApproved && (
          <BrutalCard shadow="lg" className="bg-amber-50 border-amber-400 mb-6">
            <p className="font-bold text-lg">Your brand partner account is pending admin approval.</p>
            <p className="text-sm text-gray-600 mt-1">Once approved, you'll be able to create campaigns, manage budgets, and view impression analytics.</p>
          </BrutalCard>
        )}

        <div className="flex gap-3 mb-8 flex-wrap">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <BrutalButton key={tab.id} variant={activeTab === tab.id ? 'amber' : 'default'} size="md"
                onClick={() => setActiveTab(tab.id)} className="flex items-center gap-2" data-testid={`tab-${tab.id}`}>
                <Icon size={18} /> {tab.label}
              </BrutalButton>
            );
          })}
        </div>

        {/* ======= DASHBOARD ======= */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6" data-testid="brand-dashboard-tab">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard icon={Eye} label="Impressions" value={stats.total_impressions || 0} color="indigo" />
              <StatCard icon={DollarSign} label="Spent" value={`$${(stats.total_spent || 0).toFixed(2)}`} color="rose" />
              <StatCard icon={DollarSign} label="Budget Left" value={`$${(stats.budget_remaining || 0).toFixed(2)}`} color="emerald" />
              <StatCard icon={Megaphone} label="Active Campaigns" value={stats.active_campaigns || 0} color="amber" />
            </div>
            {brand && (
              <BrutalCard shadow="lg">
                <h3 className="text-xl font-black uppercase mb-3">Brand Info</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-bold text-gray-500">Name</p>
                    <p className="text-lg font-black">{brand.name}</p>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-500">Website</p>
                    <p className="text-lg font-medium">{brand.website || '—'}</p>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-500">Products</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {brand.products?.map((p, i) => <BrutalBadge key={i} variant="indigo" size="sm">{p.name}</BrutalBadge>)}
                      {(!brand.products || brand.products.length === 0) && <span className="text-gray-400">None</span>}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-500">Categories</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {brand.target_categories?.map((c, i) => <BrutalBadge key={i} variant="emerald" size="sm">{c}</BrutalBadge>)}
                    </div>
                  </div>
                </div>
              </BrutalCard>
            )}
            {dashboard?.sponsorships?.length > 0 && (
              <BrutalCard shadow="lg">
                <h3 className="text-xl font-black uppercase mb-3">Classroom Sponsorships</h3>
                <div className="space-y-2">
                  {dashboard.sponsorships.map((sp, i) => (
                    <div key={sp.id || i} className="flex items-center justify-between p-3 border-2 border-black">
                      <div>
                        <p className="font-bold">{sp.badge_text}</p>
                        <p className="text-sm text-gray-600">{sp.school_name} | ${sp.amount_paid}</p>
                      </div>
                      <BrutalBadge variant={sp.is_active ? 'emerald' : 'rose'} size="sm">{sp.is_active ? 'Active' : 'Inactive'}</BrutalBadge>
                    </div>
                  ))}
                </div>
              </BrutalCard>
            )}
          </div>
        )}

        {/* ======= CAMPAIGNS ======= */}
        {activeTab === 'campaigns' && (
          <div className="space-y-6" data-testid="campaigns-tab">
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2"><PlusCircle size={22} /> New Campaign</h3>
              <form onSubmit={(e) => {
                e.preventDefault();
                const products = campaignForm.products_text ? campaignForm.products_text.split(',').map(p => ({ name: p.trim(), category: '' })) : [];
                createCampaignMut.mutate({
                  name: campaignForm.name, description: campaignForm.description,
                  products, target_categories: campaignForm.target_categories,
                  budget: parseFloat(campaignForm.budget) || 0,
                  cost_per_impression: parseFloat(campaignForm.cost_per_impression) || 0.05,
                });
              }} className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <BrutalInput label="Campaign Name" value={campaignForm.name} onChange={(e) => setCampaignForm({ ...campaignForm, name: e.target.value })} placeholder="Summer Reading Push" data-testid="campaign-name" />
                  <BrutalInput label="Products (comma-separated)" value={campaignForm.products_text} onChange={(e) => setCampaignForm({ ...campaignForm, products_text: e.target.value })} placeholder="Smart Tablet, Study App" data-testid="campaign-products" />
                </div>
                <BrutalInput label="Description" value={campaignForm.description} onChange={(e) => setCampaignForm({ ...campaignForm, description: e.target.value })} placeholder="Campaign details..." />
                <div>
                  <label className="block font-bold text-sm uppercase mb-2">Target Categories</label>
                  <div className="flex flex-wrap gap-2">
                    {AD_CATEGORIES.map((cat) => (
                      <button key={cat} type="button" onClick={() => {
                        const cats = campaignForm.target_categories.includes(cat)
                          ? campaignForm.target_categories.filter(c => c !== cat)
                          : [...campaignForm.target_categories, cat];
                        setCampaignForm({ ...campaignForm, target_categories: cats });
                      }}
                        className={`px-3 py-1 border-2 border-black font-bold text-sm ${campaignForm.target_categories.includes(cat) ? 'bg-amber-200' : 'bg-white'}`}
                        data-testid={`cat-${cat}`}
                      >{cat}</button>
                    ))}
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <BrutalInput label="Budget ($)" type="number" step="0.01" value={campaignForm.budget} onChange={(e) => setCampaignForm({ ...campaignForm, budget: e.target.value })} placeholder="100.00" data-testid="campaign-budget" />
                  <BrutalInput label="Cost Per Impression ($)" type="number" step="0.01" value={campaignForm.cost_per_impression} onChange={(e) => setCampaignForm({ ...campaignForm, cost_per_impression: e.target.value })} />
                </div>
                <BrutalButton type="submit" variant="amber" fullWidth disabled={!campaignForm.name || createCampaignMut.isPending || notApproved} data-testid="create-campaign-btn">
                  {createCampaignMut.isPending ? 'Creating...' : 'Launch Campaign'}
                </BrutalButton>
              </form>
            </BrutalCard>

            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4">My Campaigns ({campaigns.length})</h3>
              {campaigns.length === 0 ? <p className="text-center py-6 text-gray-500 font-bold">No campaigns yet</p> : (
                <div className="space-y-3">
                  {campaigns.map((c) => (
                    <div key={c.id} className={`border-4 border-black p-4 ${c.status === 'active' ? 'bg-white' : 'bg-gray-50'}`} data-testid={`campaign-${c.id}`}>
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-black text-lg">{c.name}</h4>
                            <BrutalBadge variant={c.status === 'active' ? 'emerald' : c.status === 'paused' ? 'amber' : 'rose'} size="sm">{c.status.toUpperCase()}</BrutalBadge>
                          </div>
                          {c.description && <p className="text-sm text-gray-600">{c.description}</p>}
                          {c.products?.length > 0 && <p className="text-xs text-gray-500 mt-1">Products: {c.products.map(p => p.name).join(', ')}</p>}
                        </div>
                        <div className="flex gap-2">
                          <BrutalButton variant={c.status === 'active' ? 'amber' : 'emerald'} size="sm"
                            onClick={() => updateCampaignMut.mutate({ id: c.id, data: { status: c.status === 'active' ? 'paused' : 'active' } })}>
                            {c.status === 'active' ? <Pause size={14} /> : <Play size={14} />}
                          </BrutalButton>
                          <BrutalButton variant="rose" size="sm" onClick={() => deleteCampaignMut.mutate(c.id)}><Trash2 size={14} /></BrutalButton>
                        </div>
                      </div>
                      <div className="flex gap-6 mt-3 pt-3 border-t-2 border-gray-200 text-sm">
                        <span>Budget: <strong>${c.budget?.toFixed(2)}</strong></span>
                        <span>Spent: <strong>${c.budget_spent?.toFixed(2)}</strong></span>
                        <span>Impressions: <strong>{c.total_impressions || 0}</strong></span>
                        <span>CPI: <strong>${c.cost_per_impression?.toFixed(2)}</strong></span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </BrutalCard>
          </div>
        )}

        {/* ======= BUDGET ======= */}
        {activeTab === 'budget' && (
          <div className="space-y-6" data-testid="budget-tab">
            <div className="grid grid-cols-3 gap-4">
              <StatCard icon={DollarSign} label="Total Budget" value={`$${(stats.budget_total || 0).toFixed(2)}`} color="indigo" />
              <StatCard icon={DollarSign} label="Spent" value={`$${(stats.total_spent || 0).toFixed(2)}`} color="rose" />
              <StatCard icon={DollarSign} label="Remaining" value={`$${(stats.budget_remaining || 0).toFixed(2)}`} color="emerald" />
            </div>
            <BrutalCard shadow="xl">
              <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2"><CreditCard size={22} /> Add Campaign Budget</h3>
              <div className="grid grid-cols-4 gap-3 mb-4">
                {[25, 50, 100, 250].map((amt) => (
                  <button key={amt} onClick={() => setTopupAmount(String(amt))}
                    className={`p-4 border-4 border-black font-black text-xl text-center ${parseFloat(topupAmount) === amt ? 'bg-amber-200 translate-x-[2px] translate-y-[2px] shadow-none' : 'bg-white brutal-shadow-sm'}`}
                    data-testid={`topup-${amt}`}>${amt}</button>
                ))}
              </div>
              <div className="flex gap-3">
                <input type="number" min="5" step="0.01" value={topupAmount} onChange={(e) => setTopupAmount(e.target.value)}
                  className="flex-1 border-4 border-black px-4 py-3 font-bold text-xl" placeholder="Custom amount..." data-testid="topup-amount" />
                <BrutalButton variant="amber" size="lg" onClick={() => topupMut.mutate(topupAmount)}
                  disabled={!topupAmount || parseFloat(topupAmount) < 5 || topupMut.isPending} data-testid="topup-btn">
                  {topupMut.isPending ? 'Redirecting...' : 'Fund Campaign'}
                </BrutalButton>
              </div>
              <p className="text-xs text-gray-500 mt-2 text-center">Secure payment via Stripe. Min $5.</p>
            </BrutalCard>
          </div>
        )}

        {/* ======= IMPRESSIONS ======= */}
        {activeTab === 'impressions' && (
          <div className="space-y-6" data-testid="impressions-tab">
            <div className="grid grid-cols-3 gap-4">
              <StatCard icon={Eye} label="Total Impressions" value={stats.total_impressions || 0} color="indigo" />
              <StatCard icon={DollarSign} label="Total Cost" value={`$${(stats.total_spent || 0).toFixed(2)}`} color="rose" />
              <StatCard icon={TrendingUp} label="Avg CPI" value={`$${stats.total_impressions ? ((stats.total_spent || 0) / stats.total_impressions).toFixed(3) : '0.000'}`} color="emerald" />
            </div>
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4">Recent Impressions</h3>
              {(dashboard?.recent_impressions?.length || 0) === 0 ? (
                <p className="text-center py-8 text-gray-500 font-bold">No impressions yet. Create campaigns and wait for stories to be generated!</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left"><thead><tr className="border-b-4 border-black">
                    <th className="py-3 px-3 font-black text-xs uppercase">Date</th>
                    <th className="py-3 px-3 font-black text-xs uppercase">Products</th>
                    <th className="py-3 px-3 font-black text-xs uppercase">Cost</th>
                  </tr></thead><tbody>
                    {dashboard.recent_impressions.map((imp, i) => (
                      <tr key={imp.id || i} className="border-b-2 border-gray-200">
                        <td className="py-2 px-3 text-sm">{new Date(imp.created_date).toLocaleDateString()}</td>
                        <td className="py-2 px-3 text-sm">{imp.products_featured?.join(', ') || '—'}</td>
                        <td className="py-2 px-3 text-sm font-bold">${imp.cost?.toFixed(3)}</td>
                      </tr>
                    ))}
                  </tbody></table>
                </div>
              )}
            </BrutalCard>
          </div>
        )}
      </div>
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value, color = 'indigo' }) => {
  const bgMap = { indigo: 'bg-indigo-50', emerald: 'bg-emerald-50', amber: 'bg-amber-50', rose: 'bg-rose-50' };
  const textMap = { indigo: 'text-indigo-600', emerald: 'text-emerald-600', amber: 'text-amber-600', rose: 'text-rose-600' };
  return (
    <div className={`${bgMap[color]} border-4 border-black p-5 brutal-shadow-sm`}>
      <div className="flex items-center gap-2 mb-2"><Icon size={18} className={textMap[color]} /><p className="font-bold text-xs uppercase text-gray-600">{label}</p></div>
      <p className="text-3xl font-black">{value}</p>
    </div>
  );
};

export default BrandPortal;
