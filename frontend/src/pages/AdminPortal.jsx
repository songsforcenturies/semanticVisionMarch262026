import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { adminAPI } from '@/lib/api';
import apiClient from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalBadge, BrutalInput } from '@/components/brutal';
import {
  Home, LogOut, DollarSign, Cpu, Users, BarChart3, Settings, Shield,
  Ticket, Crown, PlusCircle, Trash2, UserCheck, BookOpen, Clock, Zap, Sliders, ToggleLeft,
  Megaphone, Building2, Edit,
} from 'lucide-react';
import { toast } from 'sonner';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts';

const COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899'];

const AdminPortal = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('stats');

  // === Data Queries ===
  const { data: costs } = useQuery({
    queryKey: ['admin-costs'],
    queryFn: async () => (await adminAPI.getCosts()).data,
  });
  const { data: modelConfig } = useQuery({
    queryKey: ['admin-models'],
    queryFn: async () => (await adminAPI.getModels()).data,
  });
  const { data: adminSettings } = useQuery({
    queryKey: ['admin-settings'],
    queryFn: async () => (await adminAPI.getSettings()).data,
  });
  const { data: stats } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => (await adminAPI.getStats()).data,
  });
  const { data: allUsers = [] } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => (await adminAPI.getUsers()).data,
    enabled: activeTab === 'users',
  });
  const { data: coupons = [] } = useQuery({
    queryKey: ['admin-coupons'],
    queryFn: async () => (await adminAPI.getCoupons()).data,
    enabled: activeTab === 'coupons',
  });
  const { data: plans = [] } = useQuery({
    queryKey: ['admin-plans'],
    queryFn: async () => (await adminAPI.getPlans()).data,
    enabled: activeTab === 'plans',
  });
  const { data: billingConfig } = useQuery({
    queryKey: ['admin-billing'],
    queryFn: async () => (await adminAPI.getBillingConfig()).data,
    enabled: activeTab === 'billing',
  });
  const { data: featureFlags } = useQuery({
    queryKey: ['admin-features'],
    queryFn: async () => (await adminAPI.getFeatureFlags()).data,
    enabled: activeTab === 'features',
  });
  const { data: brands = [] } = useQuery({
    queryKey: ['admin-brands'],
    queryFn: async () => (await adminAPI.getBrands()).data,
    enabled: activeTab === 'brands' || activeTab === 'users',
  });
  const { data: brandAnalytics } = useQuery({
    queryKey: ['admin-brand-analytics'],
    queryFn: async () => (await adminAPI.getBrandAnalytics()).data,
    enabled: activeTab === 'brands',
  });
  const { data: sponsorships = [] } = useQuery({
    queryKey: ['admin-sponsorships'],
    queryFn: async () => (await adminAPI.getClassroomSponsorships()).data,
    enabled: activeTab === 'brands',
  });

  // === Form States ===
  const [llmForm, setLlmForm] = useState({ provider: 'emergent', model: 'gpt-5.2', openrouter_key: '' });
  const [settingsForm, setSettingsForm] = useState({
    global_spellcheck_disabled: false, global_spelling_mode: 'phonetic',
    free_account_story_limit: 5, free_account_assessment_limit: 10,
  });
  const [couponForm, setCouponForm] = useState({
    code: '', coupon_type: 'wallet_credit', value: '', max_uses: '1', description: '',
  });
  const [delegateEmail, setDelegateEmail] = useState('');
  const [createUserForm, setCreateUserForm] = useState({ email: '', full_name: '', role: 'guardian' });
  const [createdUser, setCreatedUser] = useState(null); // {email, temp_password}
  const [editingUser, setEditingUser] = useState(null);
  const [editForm, setEditForm] = useState({ email: '', full_name: '' });
  const [resetResult, setResetResult] = useState(null); // {email, temp_password}
  const [planForm, setPlanForm] = useState({
    name: '', description: '', price_monthly: '', student_seats: '10', story_limit: '-1',
  });
  const [billingForm, setBillingForm] = useState({
    pricing_model: 'per_seat', per_seat_price: 4.99, roi_markup_percent: 300,
    flat_fee_per_story: 0.50, avg_cost_per_story: 0.20, free_tier_stories: 5,
    remove_limits_on_paid: true, referral_reward_amount: 5.0, donation_cost_per_story: 0.20,
  });
  const [flagsForm, setFlagsForm] = useState({
    belief_system_enabled: true, cultural_context_enabled: true, multi_language_enabled: true,
    donations_enabled: true, referrals_enabled: true, word_definitions_enabled: true, accessibility_mode: true,
    brand_sponsorship_enabled: true, classroom_sponsorship_enabled: true,
  });
  const [brandForm, setBrandForm] = useState({
    name: '', description: '', website: '', logo_url: '',
    target_categories: '', budget_total: '', cost_per_impression: '0.05',
    products_text: '',
  });
  const [sponsorForm, setSponsorForm] = useState({
    brand_id: '', school_name: '', stories_limit: '-1', amount_paid: '',
  });

  // === Mutations ===
  const updateModelMutation = useMutation({
    mutationFn: (data) => adminAPI.updateModels(data),
    onSuccess: () => { queryClient.invalidateQueries(['admin-models']); toast.success('LLM configuration updated!'); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const updateSettingsMutation = useMutation({
    mutationFn: (data) => adminAPI.updateSettings(data),
    onSuccess: () => { queryClient.invalidateQueries(['admin-settings']); toast.success('Settings updated!'); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const createCouponMutation = useMutation({
    mutationFn: (data) => adminAPI.createCoupon(data),
    onSuccess: () => { queryClient.invalidateQueries(['admin-coupons']); toast.success('Coupon created!'); setCouponForm({ code: '', coupon_type: 'wallet_credit', value: '', max_uses: '1', description: '' }); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const deleteCouponMutation = useMutation({
    mutationFn: (id) => adminAPI.deleteCoupon(id),
    onSuccess: () => { queryClient.invalidateQueries(['admin-coupons']); toast.success('Coupon deleted'); },
  });
  const delegateMutation = useMutation({
    mutationFn: (data) => adminAPI.delegateAdmin(data),
    onSuccess: (res) => { queryClient.invalidateQueries(['admin-users']); toast.success(res.data.message); setDelegateEmail(''); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const approveBrandMut = useMutation({
    mutationFn: (userId) => apiClient.post(`/admin/approve-brand-partner/${userId}`),
    onSuccess: () => { queryClient.invalidateQueries(['admin-users']); toast.success('Brand partner approved!'); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const rejectBrandMut = useMutation({
    mutationFn: (userId) => apiClient.post(`/admin/reject-brand-partner/${userId}`),
    onSuccess: () => { queryClient.invalidateQueries(['admin-users']); toast.success('Brand partner suspended'); },
  });
  const linkBrandMut = useMutation({
    mutationFn: ({ userId, brandId }) => apiClient.post(`/admin/link-brand/${userId}/${brandId}`),
    onSuccess: () => { queryClient.invalidateQueries(['admin-users']); toast.success('Brand linked!'); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const createUserMut = useMutation({
    mutationFn: (data) => adminAPI.createUser(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries(['admin-users']);
      setCreatedUser({ email: res.data.email, temp_password: res.data.temp_password, role: res.data.role });
      setCreateUserForm({ email: '', full_name: '', role: 'guardian' });
      toast.success('User created!');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to create user'),
  });
  const updateUserMut = useMutation({
    mutationFn: ({ id, data }) => adminAPI.updateUser(id, data),
    onSuccess: () => { queryClient.invalidateQueries(['admin-users']); toast.success('User updated'); setEditingUser(null); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const resetPasswordMut = useMutation({
    mutationFn: (id) => adminAPI.resetPassword(id),
    onSuccess: (res) => {
      setResetResult({ email: res.data.email, temp_password: res.data.temp_password });
      toast.success('Password reset!');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const deactivateUserMut = useMutation({
    mutationFn: (id) => adminAPI.deactivateUser(id),
    onSuccess: (res) => { queryClient.invalidateQueries(['admin-users']); toast.success(res.data.message); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const deleteUserMut = useMutation({
    mutationFn: (id) => adminAPI.deleteUser(id),
    onSuccess: () => { queryClient.invalidateQueries(['admin-users']); toast.success('User deleted'); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const createPlanMutation = useMutation({
    mutationFn: (data) => adminAPI.createPlan(data),
    onSuccess: () => { queryClient.invalidateQueries(['admin-plans']); toast.success('Plan created!'); setPlanForm({ name: '', description: '', price_monthly: '', student_seats: '10', story_limit: '-1' }); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const deletePlanMutation = useMutation({
    mutationFn: (id) => adminAPI.deletePlan(id),
    onSuccess: () => { queryClient.invalidateQueries(['admin-plans']); toast.success('Plan deleted'); },
  });
  const updateBillingMutation = useMutation({
    mutationFn: (data) => adminAPI.updateBillingConfig(data),
    onSuccess: () => { queryClient.invalidateQueries(['admin-billing']); toast.success('Billing config updated!'); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const updateFlagsMutation = useMutation({
    mutationFn: (data) => adminAPI.updateFeatureFlags(data),
    onSuccess: () => { queryClient.invalidateQueries(['admin-features']); toast.success('Feature flags updated!'); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const createBrandMutation = useMutation({
    mutationFn: (data) => adminAPI.createBrand(data),
    onSuccess: () => { queryClient.invalidateQueries(['admin-brands']); queryClient.invalidateQueries(['admin-brand-analytics']); toast.success('Brand created!'); setBrandForm({ name: '', description: '', website: '', logo_url: '', target_categories: '', budget_total: '', cost_per_impression: '0.05', products_text: '' }); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const deleteBrandMutation = useMutation({
    mutationFn: (id) => adminAPI.deleteBrand(id),
    onSuccess: () => { queryClient.invalidateQueries(['admin-brands']); queryClient.invalidateQueries(['admin-brand-analytics']); toast.success('Brand deleted'); },
  });
  const toggleBrandMutation = useMutation({
    mutationFn: ({ id, is_active }) => adminAPI.updateBrand(id, { is_active }),
    onSuccess: () => { queryClient.invalidateQueries(['admin-brands']); toast.success('Brand updated'); },
  });
  const createSponsorshipMutation = useMutation({
    mutationFn: (data) => adminAPI.createClassroomSponsorship(data),
    onSuccess: () => { queryClient.invalidateQueries(['admin-sponsorships']); toast.success('Sponsorship created!'); setSponsorForm({ brand_id: '', school_name: '', stories_limit: '-1', amount_paid: '' }); },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });
  const deleteSponsorshipMutation = useMutation({
    mutationFn: (id) => adminAPI.deleteClassroomSponsorship(id),
    onSuccess: () => { queryClient.invalidateQueries(['admin-sponsorships']); toast.success('Sponsorship removed'); },
  });

  // === Sync forms with data ===
  React.useEffect(() => {
    if (modelConfig) setLlmForm({ provider: modelConfig.provider || 'emergent', model: modelConfig.model || 'gpt-5.2', openrouter_key: modelConfig.openrouter_key || '' });
  }, [modelConfig]);
  React.useEffect(() => {
    if (adminSettings) setSettingsForm({
      global_spellcheck_disabled: adminSettings.global_spellcheck_disabled ?? false,
      global_spelling_mode: adminSettings.global_spelling_mode ?? 'phonetic',
      free_account_story_limit: adminSettings.free_account_story_limit ?? 5,
      free_account_assessment_limit: adminSettings.free_account_assessment_limit ?? 10,
    });
  }, [adminSettings]);
  React.useEffect(() => {
    if (billingConfig) setBillingForm(prev => ({ ...prev, ...billingConfig }));
  }, [billingConfig]);
  React.useEffect(() => {
    if (featureFlags) setFlagsForm(prev => ({ ...prev, ...featureFlags }));
  }, [featureFlags]);

  const handleLogout = () => { logout(); navigate('/login'); };

  const tabs = [
    { id: 'stats', label: 'Statistics', icon: BarChart3 },
    { id: 'costs', label: 'AI Costs', icon: DollarSign },
    { id: 'brands', label: 'Brands', icon: Megaphone },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'coupons', label: 'Coupons', icon: Ticket },
    { id: 'plans', label: 'Plans', icon: Crown },
    { id: 'billing', label: 'Billing/ROI', icon: Sliders },
    { id: 'features', label: 'Features', icon: ToggleLeft },
    { id: 'config', label: 'LLM Config', icon: Settings },
    { id: 'settings', label: 'App Settings', icon: Shield },
  ];

  return (
    <div className="min-h-screen bg-gray-50" data-testid="admin-portal">
      <header className="bg-white border-b-6 border-black brutal-shadow-md">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/')} className="p-3 border-4 border-black bg-rose-100 brutal-shadow-sm hover:brutal-shadow-md brutal-active">
                <Home size={24} />
              </button>
              <div>
                <h1 className="text-4xl font-black uppercase flex items-center gap-2">
                  <Cpu size={32} className="text-rose-600" /> Admin Dashboard
                </h1>
                <p className="text-lg font-medium mt-1">{user?.full_name} — Master Admin</p>
              </div>
            </div>
            <BrutalButton variant="dark" onClick={handleLogout} className="flex items-center gap-2">
              <LogOut size={20} /> Logout
            </BrutalButton>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="flex gap-3 mb-8 flex-wrap">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <BrutalButton key={tab.id} variant={activeTab === tab.id ? 'rose' : 'default'} size="md"
                onClick={() => setActiveTab(tab.id)} className="flex items-center gap-2" data-testid={`tab-${tab.id}`}>
                <Icon size={18} /> {tab.label}
              </BrutalButton>
            );
          })}
        </div>

        {/* =================== STATISTICS TAB =================== */}
        {activeTab === 'stats' && stats && (
          <div className="space-y-6" data-testid="stats-tab">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard icon={Users} label="Parents" value={stats.users.guardians} color="indigo" />
              <StatCard icon={UserCheck} label="Teachers" value={stats.users.teachers} color="emerald" />
              <StatCard icon={BookOpen} label="Students" value={stats.users.students} color="amber" />
              <StatCard icon={Zap} label="Recent Signups" value={stats.users.recent_signups} color="rose" />
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard icon={BookOpen} label="Word Banks" value={stats.content.word_banks} color="indigo" />
              <StatCard icon={BookOpen} label="Stories" value={stats.content.narratives} color="emerald" />
              <StatCard icon={BookOpen} label="Assessments" value={stats.content.assessments_completed} sub={`/ ${stats.content.assessments_total}`} color="amber" />
              <StatCard icon={Clock} label="Reading Hours" value={stats.reading.total_reading_hours} color="rose" />
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard icon={DollarSign} label="Revenue" value={`$${stats.revenue.total_revenue.toFixed(2)}`} color="emerald" />
              <StatCard icon={DollarSign} label="Payments" value={stats.revenue.total_payments} color="indigo" />
              <StatCard icon={Ticket} label="Coupons Used" value={stats.coupons.total_redemptions} sub={`/ ${stats.coupons.total_coupons} created`} color="amber" />
              <StatCard icon={Cpu} label="AI Cost" value={`$${stats.ai.total_cost.toFixed(4)}`} sub={`${stats.ai.total_calls} calls`} color="rose" />
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <StatCard icon={Users} label="Classrooms" value={stats.classrooms.total_sessions} sub={`${stats.classrooms.active_sessions} active`} color="indigo" />
              <StatCard icon={BookOpen} label="Words Read" value={stats.reading.total_words_read.toLocaleString()} color="emerald" />
            </div>
          </div>
        )}

        {/* =================== AI COSTS TAB =================== */}
        {activeTab === 'costs' && (
          <div className="space-y-6" data-testid="costs-tab">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-rose-50 border-4 border-black p-5 brutal-shadow-sm" data-testid="stat-total-cost">
                <div className="flex items-center gap-2 mb-2"><DollarSign size={18} className="text-rose-600" /><p className="font-bold text-xs uppercase text-gray-600">Total Cost</p></div>
                <p className="text-3xl font-black">${costs?.total_cost?.toFixed(4) || '0.0000'}</p>
              </div>
              <div className="bg-indigo-50 border-4 border-black p-5 brutal-shadow-sm" data-testid="stat-total-stories">
                <div className="flex items-center gap-2 mb-2"><BarChart3 size={18} className="text-indigo-600" /><p className="font-bold text-xs uppercase text-gray-600">Total Stories</p></div>
                <p className="text-3xl font-black">{costs?.total_stories || 0}</p>
              </div>
              <div className="bg-amber-50 border-4 border-black p-5 brutal-shadow-sm">
                <div className="flex items-center gap-2 mb-2"><Users size={18} className="text-amber-600" /><p className="font-bold text-xs uppercase text-gray-600">Users</p></div>
                <p className="text-3xl font-black">{costs?.per_user?.length || 0}</p>
              </div>
              <div className="bg-emerald-50 border-4 border-black p-5 brutal-shadow-sm">
                <div className="flex items-center gap-2 mb-2"><Cpu size={18} className="text-emerald-600" /><p className="font-bold text-xs uppercase text-gray-600">Avg/Story</p></div>
                <p className="text-3xl font-black">${costs?.total_stories ? (costs.total_cost / costs.total_stories).toFixed(4) : '0.0000'}</p>
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <BrutalCard shadow="lg">
                <h3 className="text-xl font-black uppercase mb-4">Cost by User</h3>
                {costs?.per_user?.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={costs.per_user.slice(0, 10)}>
                        <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="user_name" tick={{ fontSize: 11, fontWeight: 700 }} angle={-20} textAnchor="end" height={60} />
                        <YAxis tick={{ fontSize: 12 }} tickFormatter={v => `$${v.toFixed(3)}`} /><Tooltip formatter={v => `$${Number(v).toFixed(4)}`} />
                        <Bar dataKey="total_cost" fill="#6366f1" stroke="#000" strokeWidth={2} radius={[4, 4, 0, 0]} name="Cost" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : <p className="text-center py-8 text-gray-500 font-bold">No cost data yet</p>}
              </BrutalCard>
              <BrutalCard shadow="lg">
                <h3 className="text-xl font-black uppercase mb-4">Cost by Model</h3>
                {costs?.per_model?.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart><Pie data={costs.per_model} cx="50%" cy="50%" outerRadius={80} dataKey="total_cost" label={({ model, total_cost }) => `${model}: $${total_cost.toFixed(4)}`}>
                        {costs.per_model.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="#000" strokeWidth={2} />)}
                      </Pie><Tooltip formatter={v => `$${Number(v).toFixed(4)}`} /></PieChart>
                    </ResponsiveContainer>
                  </div>
                ) : <p className="text-center py-8 text-gray-500 font-bold">No model data yet</p>}
              </BrutalCard>
            </div>
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4">Recent Logs</h3>
              {costs?.recent_logs?.length > 0 ? (
                <div className="overflow-x-auto"><table className="w-full text-left"><thead><tr className="border-b-4 border-black">
                  <th className="py-3 px-3 font-black text-xs uppercase">Date</th><th className="py-3 px-3 font-black text-xs uppercase">Student</th>
                  <th className="py-3 px-3 font-black text-xs uppercase">Model</th><th className="py-3 px-3 font-black text-xs uppercase">Tokens</th>
                  <th className="py-3 px-3 font-black text-xs uppercase">Cost</th><th className="py-3 px-3 font-black text-xs uppercase">Status</th>
                </tr></thead><tbody>
                  {costs.recent_logs.map((log, i) => (
                    <tr key={log.id || i} className="border-b-2 border-gray-200">
                      <td className="py-2 px-3 text-sm">{new Date(log.created_date).toLocaleDateString()}</td>
                      <td className="py-2 px-3 font-bold text-sm">{log.student_name}</td>
                      <td className="py-2 px-3 text-sm font-mono">{log.model}</td>
                      <td className="py-2 px-3 text-sm">{log.total_tokens}</td>
                      <td className="py-2 px-3 text-sm font-bold">${log.estimated_cost?.toFixed(4)}</td>
                      <td className="py-2 px-3"><BrutalBadge variant={log.success ? 'emerald' : 'rose'} size="sm">{log.success ? 'OK' : 'FAIL'}</BrutalBadge></td>
                    </tr>
                  ))}
                </tbody></table></div>
              ) : <p className="text-center py-8 text-gray-500 font-bold">No logs yet</p>}
            </BrutalCard>
          </div>
        )}


        {/* =================== BRANDS TAB =================== */}
        {activeTab === 'brands' && (
          <div className="space-y-6" data-testid="brands-tab">
            {/* Brand Analytics Summary */}
            {brandAnalytics && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard icon={DollarSign} label="Brand Revenue" value={`$${brandAnalytics.total_brand_revenue.toFixed(2)}`} color="emerald" />
                <StatCard icon={Megaphone} label="Impressions" value={brandAnalytics.total_impressions} color="indigo" />
                <StatCard icon={Megaphone} label="Active Brands" value={`${brandAnalytics.active_brands}/${brandAnalytics.total_brands}`} color="amber" />
                <StatCard icon={Building2} label="Classroom Sponsors" value={brandAnalytics.active_classroom_sponsorships} sub={`$${brandAnalytics.total_sponsorship_amount.toFixed(0)}`} color="rose" />
              </div>
            )}

            {/* Create Brand */}
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2"><PlusCircle size={22} /> Add Brand Sponsor</h3>
              <form onSubmit={(e) => {
                e.preventDefault();
                const products = brandForm.products_text ? brandForm.products_text.split(',').map(p => ({ name: p.trim(), category: '' })) : [];
                const categories = brandForm.target_categories ? brandForm.target_categories.split(',').map(c => c.trim()) : [];
                createBrandMutation.mutate({
                  name: brandForm.name, description: brandForm.description,
                  website: brandForm.website, logo_url: brandForm.logo_url,
                  products, target_categories: categories,
                  budget_total: parseFloat(brandForm.budget_total) || 0,
                  cost_per_impression: parseFloat(brandForm.cost_per_impression) || 0.05,
                });
              }} className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <BrutalInput label="Brand Name" value={brandForm.name} onChange={(e) => setBrandForm({ ...brandForm, name: e.target.value })} placeholder="e.g. LearnTech Pro" data-testid="brand-name" />
                  <BrutalInput label="Website" value={brandForm.website} onChange={(e) => setBrandForm({ ...brandForm, website: e.target.value })} placeholder="https://..." />
                </div>
                <BrutalInput label="Description" value={brandForm.description} onChange={(e) => setBrandForm({ ...brandForm, description: e.target.value })} placeholder="What does this brand do?" />
                <div className="grid md:grid-cols-2 gap-4">
                  <BrutalInput label="Products (comma-separated)" value={brandForm.products_text} onChange={(e) => setBrandForm({ ...brandForm, products_text: e.target.value })} placeholder="Learning Tablet, Study App, Smart Pen" data-testid="brand-products" />
                  <BrutalInput label="Categories (comma-separated)" value={brandForm.target_categories} onChange={(e) => setBrandForm({ ...brandForm, target_categories: e.target.value })} placeholder="technology, education, sports" />
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <BrutalInput label="Budget ($)" type="number" step="0.01" value={brandForm.budget_total} onChange={(e) => setBrandForm({ ...brandForm, budget_total: e.target.value })} placeholder="1000.00" data-testid="brand-budget" />
                  <BrutalInput label="Cost Per Impression ($)" type="number" step="0.01" value={brandForm.cost_per_impression} onChange={(e) => setBrandForm({ ...brandForm, cost_per_impression: e.target.value })} placeholder="0.05" />
                </div>
                <BrutalButton type="submit" variant="indigo" fullWidth disabled={!brandForm.name || createBrandMutation.isPending} data-testid="create-brand-btn">
                  {createBrandMutation.isPending ? 'Creating...' : 'Add Brand'}
                </BrutalButton>
              </form>
            </BrutalCard>

            {/* Active Brands */}
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4">Brands ({brands.length})</h3>
              {brands.length === 0 ? <p className="text-center py-6 text-gray-500 font-bold">No brands yet</p> : (
                <div className="space-y-3">
                  {brands.map((b) => {
                    const analytics = brandAnalytics?.brands?.find(ab => ab.id === b.id);
                    return (
                      <div key={b.id} className={`border-4 border-black p-4 ${b.is_active ? 'bg-white' : 'bg-gray-100'}`} data-testid={`brand-${b.id}`}>
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-black text-lg">{b.name}</h4>
                              <BrutalBadge variant={b.is_active ? 'emerald' : 'rose'} size="sm">{b.is_active ? 'ACTIVE' : 'PAUSED'}</BrutalBadge>
                            </div>
                            {b.description && <p className="text-sm text-gray-600">{b.description}</p>}
                            {b.products?.length > 0 && <p className="text-xs text-gray-500 mt-1">Products: {b.products.map(p => p.name).join(', ')}</p>}
                            {b.target_categories?.length > 0 && <p className="text-xs text-gray-400">Categories: {b.target_categories.join(', ')}</p>}
                          </div>
                          <div className="flex gap-2">
                            <BrutalButton variant={b.is_active ? 'amber' : 'emerald'} size="sm" onClick={() => toggleBrandMutation.mutate({ id: b.id, is_active: !b.is_active })}>
                              {b.is_active ? 'Pause' : 'Activate'}
                            </BrutalButton>
                            <BrutalButton variant="rose" size="sm" onClick={() => deleteBrandMutation.mutate(b.id)}><Trash2 size={14} /></BrutalButton>
                          </div>
                        </div>
                        {analytics && (
                          <div className="flex gap-6 mt-3 pt-3 border-t-2 border-gray-200 text-sm">
                            <span><strong>{analytics.impressions}</strong> impressions</span>
                            <span><strong>${analytics.budget_spent?.toFixed(2)}</strong> spent</span>
                            <span><strong>${analytics.budget_remaining?.toFixed(2)}</strong> remaining</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </BrutalCard>

            {/* Classroom Sponsorships */}
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2"><Building2 size={22} /> Classroom Sponsorships</h3>
              <form onSubmit={(e) => {
                e.preventDefault();
                createSponsorshipMutation.mutate({
                  brand_id: sponsorForm.brand_id, school_name: sponsorForm.school_name,
                  stories_limit: parseInt(sponsorForm.stories_limit), amount_paid: parseFloat(sponsorForm.amount_paid) || 0,
                });
              }} className="space-y-4 mb-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block font-bold text-sm uppercase mb-2">Brand Sponsor</label>
                    <select value={sponsorForm.brand_id} onChange={(e) => setSponsorForm({ ...sponsorForm, brand_id: e.target.value })} className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="sponsor-brand">
                      <option value="">Select brand...</option>
                      {brands.filter(b => b.is_active).map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                    </select>
                  </div>
                  <BrutalInput label="School / Classroom Name" value={sponsorForm.school_name} onChange={(e) => setSponsorForm({ ...sponsorForm, school_name: e.target.value })} placeholder="Lincoln Elementary" data-testid="sponsor-school" />
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <BrutalInput label="Stories Limit (-1=unlimited)" type="number" value={sponsorForm.stories_limit} onChange={(e) => setSponsorForm({ ...sponsorForm, stories_limit: e.target.value })} />
                  <BrutalInput label="Amount Paid ($)" type="number" step="0.01" value={sponsorForm.amount_paid} onChange={(e) => setSponsorForm({ ...sponsorForm, amount_paid: e.target.value })} placeholder="500.00" />
                </div>
                <BrutalButton type="submit" variant="emerald" fullWidth disabled={!sponsorForm.brand_id || !sponsorForm.school_name || createSponsorshipMutation.isPending} data-testid="create-sponsorship-btn">
                  {createSponsorshipMutation.isPending ? 'Creating...' : 'Create Sponsorship'}
                </BrutalButton>
              </form>
              {sponsorships.length > 0 && (
                <div className="space-y-2 mt-4">
                  {sponsorships.map((sp) => (
                    <div key={sp.id} className="flex items-center justify-between p-3 border-2 border-black" data-testid={`sponsorship-${sp.id}`}>
                      <div>
                        <p className="font-bold">{sp.badge_text || sp.brand_name}</p>
                        <p className="text-sm text-gray-600">{sp.school_name} | {sp.stories_limit === -1 ? 'Unlimited' : sp.stories_limit} stories | ${sp.amount_paid}</p>
                      </div>
                      <BrutalButton variant="rose" size="sm" onClick={() => deleteSponsorshipMutation.mutate(sp.id)}><Trash2 size={14} /></BrutalButton>
                    </div>
                  ))}
                </div>
              )}
            </BrutalCard>
          </div>
        )}

        {/* =================== USERS TAB =================== */}
        {activeTab === 'users' && (
          <div className="space-y-6" data-testid="users-tab">
            {/* Create New User */}
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2"><PlusCircle size={22} /> Create New User</h3>
              <form onSubmit={(e) => { e.preventDefault(); createUserMut.mutate(createUserForm); }} className="space-y-4">
                <div className="grid md:grid-cols-3 gap-4">
                  <BrutalInput label="Full Name" value={createUserForm.full_name}
                    onChange={(e) => setCreateUserForm({ ...createUserForm, full_name: e.target.value })}
                    placeholder="John Smith" data-testid="create-user-name" />
                  <BrutalInput label="Email" type="email" value={createUserForm.email}
                    onChange={(e) => setCreateUserForm({ ...createUserForm, email: e.target.value })}
                    placeholder="user@example.com" data-testid="create-user-email" />
                  <div>
                    <label className="block font-bold text-sm uppercase mb-2">Role</label>
                    <select value={createUserForm.role} onChange={(e) => setCreateUserForm({ ...createUserForm, role: e.target.value })}
                      className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="create-user-role">
                      <option value="guardian">Parent / School</option>
                      <option value="teacher">Teacher</option>
                      <option value="brand_partner">Brand Partner</option>
                    </select>
                  </div>
                </div>
                <BrutalButton type="submit" variant="indigo" disabled={!createUserForm.email || !createUserForm.full_name || createUserMut.isPending}
                  data-testid="create-user-btn">
                  {createUserMut.isPending ? 'Creating...' : 'Create User'}
                </BrutalButton>
              </form>
              {createdUser && (
                <div className="mt-4 p-4 bg-emerald-50 border-4 border-emerald-400" data-testid="created-user-result">
                  <p className="font-black text-lg mb-1">User Created Successfully!</p>
                  <p className="text-sm"><strong>Email:</strong> {createdUser.email}</p>
                  <p className="text-sm"><strong>Temporary Password:</strong> <code className="bg-white px-2 py-1 border-2 border-black font-bold text-lg">{createdUser.temp_password}</code></p>
                  <p className="text-sm"><strong>Role:</strong> {createdUser.role === 'guardian' ? 'Parent / School' : createdUser.role === 'teacher' ? 'Teacher' : 'Brand Partner'}</p>
                  <p className="text-xs text-gray-500 mt-2">Share the temporary password with the user. They should change it on first login.</p>
                  <BrutalButton variant="default" size="sm" onClick={() => setCreatedUser(null)} className="mt-2">Dismiss</BrutalButton>
                </div>
              )}
            </BrutalCard>

            {/* Reset Password Result */}
            {resetResult && (
              <BrutalCard shadow="lg" className="bg-amber-50 border-amber-400">
                <div className="flex items-center justify-between" data-testid="reset-password-result">
                  <div>
                    <p className="font-black text-lg">Password Reset for {resetResult.email}</p>
                    <p className="text-sm mt-1">New Temporary Password: <code className="bg-white px-2 py-1 border-2 border-black font-bold text-lg">{resetResult.temp_password}</code></p>
                  </div>
                  <BrutalButton variant="default" size="sm" onClick={() => setResetResult(null)}>Dismiss</BrutalButton>
                </div>
              </BrutalCard>
            )}

            {/* Edit User Dialog */}
            {editingUser && (
              <BrutalCard shadow="lg" className="bg-indigo-50 border-indigo-400">
                <h4 className="font-black text-lg mb-3 flex items-center gap-2"><Edit size={18} /> Edit User: {editingUser.full_name}</h4>
                <form onSubmit={(e) => { e.preventDefault(); updateUserMut.mutate({ id: editingUser.id, data: editForm }); }}
                  className="space-y-3" data-testid="edit-user-form">
                  <div className="grid md:grid-cols-2 gap-4">
                    <BrutalInput label="Full Name" value={editForm.full_name}
                      onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                      data-testid="edit-user-name" />
                    <BrutalInput label="Email" type="email" value={editForm.email}
                      onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                      data-testid="edit-user-email" />
                  </div>
                  <div className="flex gap-3">
                    <BrutalButton type="submit" variant="indigo" disabled={updateUserMut.isPending} data-testid="save-edit-btn">
                      {updateUserMut.isPending ? 'Saving...' : 'Save Changes'}
                    </BrutalButton>
                    <BrutalButton type="button" variant="default" onClick={() => setEditingUser(null)}>Cancel</BrutalButton>
                  </div>
                </form>
              </BrutalCard>
            )}

            {/* Delegate Admin */}
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4">Delegate Admin Privileges</h3>
              <div className="flex gap-3">
                <BrutalInput placeholder="User email..." value={delegateEmail} onChange={(e) => setDelegateEmail(e.target.value)} className="flex-1" data-testid="delegate-email" />
                <BrutalButton variant="indigo" onClick={() => delegateMutation.mutate({ email: delegateEmail, is_delegated: true })} disabled={!delegateEmail.trim()} data-testid="delegate-btn">Grant</BrutalButton>
                <BrutalButton variant="rose" onClick={() => delegateMutation.mutate({ email: delegateEmail, is_delegated: false })} disabled={!delegateEmail.trim()} data-testid="revoke-btn">Revoke</BrutalButton>
              </div>
              <p className="text-xs text-gray-500 mt-2">Delegated admins can create/edit word banks and manage subscriptions.</p>
            </BrutalCard>

            {/* All Users Table */}
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4">All Users ({allUsers.length})</h3>
              <div className="overflow-x-auto"><table className="w-full text-left"><thead><tr className="border-b-4 border-black">
                <th className="py-3 px-3 font-black text-xs uppercase">Name</th><th className="py-3 px-3 font-black text-xs uppercase">Email</th>
                <th className="py-3 px-3 font-black text-xs uppercase">Role</th><th className="py-3 px-3 font-black text-xs uppercase">Balance</th>
                <th className="py-3 px-3 font-black text-xs uppercase">Status</th><th className="py-3 px-3 font-black text-xs uppercase">Actions</th>
              </tr></thead><tbody>
                {allUsers.map((u) => {
                  const roleLabel = u.role === 'guardian' ? 'Parent/School' : u.role === 'teacher' ? 'Teacher' : u.role === 'brand_partner' ? 'Brand' : u.role === 'admin' ? 'Admin' : u.role;
                  const isInactive = u.is_active === false;
                  return (
                    <tr key={u.id} className={`border-b-2 border-gray-200 ${isInactive ? 'opacity-50 bg-gray-50' : ''}`} data-testid={`user-row-${u.id}`}>
                      <td className="py-2 px-3 font-bold text-sm">{u.full_name}</td>
                      <td className="py-2 px-3 text-sm">{u.email}</td>
                      <td className="py-2 px-3"><BrutalBadge variant={u.role === 'admin' ? 'rose' : u.role === 'brand_partner' ? 'amber' : u.role === 'teacher' ? 'indigo' : 'emerald'} size="sm">{roleLabel}</BrutalBadge></td>
                      <td className="py-2 px-3 text-sm font-bold">${(u.wallet_balance || 0).toFixed(2)}</td>
                      <td className="py-2 px-3">
                        <div className="flex flex-wrap gap-1">
                          {isInactive && <BrutalBadge variant="rose" size="sm">INACTIVE</BrutalBadge>}
                          {u.is_delegated_admin && <BrutalBadge variant="amber" size="sm">DELEGATE</BrutalBadge>}
                          {u.role === 'brand_partner' && (u.brand_approved ? <BrutalBadge variant="emerald" size="sm">APPROVED</BrutalBadge> : <BrutalBadge variant="rose" size="sm">PENDING</BrutalBadge>)}
                        </div>
                      </td>
                      <td className="py-2 px-3">
                        <div className="flex flex-wrap gap-1">
                          {u.role !== 'admin' && (
                            <>
                              <BrutalButton variant="default" size="sm" onClick={() => { setEditingUser(u); setEditForm({ email: u.email, full_name: u.full_name }); }} data-testid={`edit-${u.id}`}>
                                <Edit size={13} />
                              </BrutalButton>
                              <BrutalButton variant="amber" size="sm" onClick={() => resetPasswordMut.mutate(u.id)} disabled={resetPasswordMut.isPending} data-testid={`reset-pwd-${u.id}`}>
                                Reset Pwd
                              </BrutalButton>
                              <BrutalButton variant={isInactive ? 'emerald' : 'rose'} size="sm" onClick={() => deactivateUserMut.mutate(u.id)} data-testid={`toggle-active-${u.id}`}>
                                {isInactive ? 'Activate' : 'Deactivate'}
                              </BrutalButton>
                              <BrutalButton variant="rose" size="sm" onClick={() => { if (window.confirm(`Delete user ${u.full_name}? This is permanent.`)) deleteUserMut.mutate(u.id); }} data-testid={`delete-${u.id}`}>
                                <Trash2 size={13} />
                              </BrutalButton>
                            </>
                          )}
                          {u.role === 'brand_partner' && !u.brand_approved && (
                            <BrutalButton variant="emerald" size="sm" onClick={() => approveBrandMut.mutate(u.id)} data-testid={`approve-${u.id}`}>Approve</BrutalButton>
                          )}
                          {u.role === 'brand_partner' && u.brand_approved && (
                            <BrutalButton variant="rose" size="sm" onClick={() => rejectBrandMut.mutate(u.id)}>Suspend</BrutalButton>
                          )}
                          {u.role === 'brand_partner' && !u.linked_brand_id && brands.length > 0 && (
                            <select onChange={(e) => { if (e.target.value) linkBrandMut.mutate({ userId: u.id, brandId: e.target.value }); }}
                              className="ml-1 border-2 border-black px-2 py-1 text-xs font-bold" defaultValue="">
                              <option value="">Link brand...</option>
                              {brands.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                            </select>
                          )}
                          {u.role === 'brand_partner' && u.linked_brand_id && <span className="text-xs text-gray-500 ml-1">Linked</span>}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody></table></div>
            </BrutalCard>
          </div>
        )}

        {/* =================== COUPONS TAB =================== */}
        {activeTab === 'coupons' && (
          <div className="space-y-6" data-testid="coupons-tab">
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2"><PlusCircle size={22} /> Create Coupon</h3>
              <form onSubmit={(e) => { e.preventDefault(); createCouponMutation.mutate({ ...couponForm, value: parseFloat(couponForm.value), max_uses: parseInt(couponForm.max_uses) }); }} className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <BrutalInput label="Coupon Code" value={couponForm.code} onChange={(e) => setCouponForm({ ...couponForm, code: e.target.value.toUpperCase() })} placeholder="e.g. WELCOME50" data-testid="coupon-code" />
                  <div>
                    <label className="block font-bold text-sm uppercase mb-2">Type</label>
                    <select value={couponForm.coupon_type} onChange={(e) => setCouponForm({ ...couponForm, coupon_type: e.target.value })} className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="coupon-type">
                      <option value="wallet_credit">Wallet Credit ($)</option>
                      <option value="free_stories">Free Stories (count)</option>
                      <option value="free_students">Free Student Seats</option>
                      <option value="free_days">Free Premium Days</option>
                    </select>
                  </div>
                </div>
                <div className="grid md:grid-cols-3 gap-4">
                  <BrutalInput label="Value" type="number" step="0.01" value={couponForm.value} onChange={(e) => setCouponForm({ ...couponForm, value: e.target.value })} placeholder="Amount" data-testid="coupon-value" />
                  <BrutalInput label="Max Uses" type="number" min="1" value={couponForm.max_uses} onChange={(e) => setCouponForm({ ...couponForm, max_uses: e.target.value })} data-testid="coupon-max-uses" />
                  <BrutalInput label="Description" value={couponForm.description} onChange={(e) => setCouponForm({ ...couponForm, description: e.target.value })} placeholder="Optional..." />
                </div>
                <BrutalButton type="submit" variant="indigo" fullWidth disabled={!couponForm.code || !couponForm.value || createCouponMutation.isPending} data-testid="create-coupon-btn">
                  {createCouponMutation.isPending ? 'Creating...' : 'Create Coupon'}
                </BrutalButton>
              </form>
            </BrutalCard>
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4">Active Coupons ({coupons.length})</h3>
              {coupons.length === 0 ? <p className="text-center py-6 text-gray-500 font-bold">No coupons yet</p> : (
                <div className="space-y-2">
                  {coupons.map((c) => (
                    <div key={c.id} className="flex items-center justify-between p-3 border-2 border-black" data-testid={`coupon-${c.id}`}>
                      <div className="flex items-center gap-3">
                        <BrutalBadge variant="indigo" size="sm">{c.code}</BrutalBadge>
                        <span className="font-bold text-sm">{c.coupon_type === 'wallet_credit' ? `$${c.value}` : `${c.value} ${c.coupon_type.replace('free_', '')}`}</span>
                        <span className="text-xs text-gray-500">{c.uses_count}/{c.max_uses} used</span>
                        {c.description && <span className="text-xs text-gray-400">— {c.description}</span>}
                      </div>
                      <BrutalButton variant="rose" size="sm" onClick={() => deleteCouponMutation.mutate(c.id)}><Trash2 size={14} /></BrutalButton>
                    </div>
                  ))}
                </div>
              )}
            </BrutalCard>
          </div>
        )}

        {/* =================== PLANS TAB =================== */}
        {activeTab === 'plans' && (
          <div className="space-y-6" data-testid="plans-tab">
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2"><PlusCircle size={22} /> Create Subscription Plan</h3>
              <form onSubmit={(e) => { e.preventDefault(); createPlanMutation.mutate({ ...planForm, price_monthly: parseFloat(planForm.price_monthly) || 0, student_seats: parseInt(planForm.student_seats), story_limit: parseInt(planForm.story_limit) }); }} className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <BrutalInput label="Plan Name" value={planForm.name} onChange={(e) => setPlanForm({ ...planForm, name: e.target.value })} placeholder="e.g. Family Plan" data-testid="plan-name" />
                  <BrutalInput label="Monthly Price ($)" type="number" step="0.01" value={planForm.price_monthly} onChange={(e) => setPlanForm({ ...planForm, price_monthly: e.target.value })} placeholder="0.00" data-testid="plan-price" />
                </div>
                <div className="grid md:grid-cols-3 gap-4">
                  <BrutalInput label="Student Seats" type="number" value={planForm.student_seats} onChange={(e) => setPlanForm({ ...planForm, student_seats: e.target.value })} data-testid="plan-seats" />
                  <BrutalInput label="Story Limit (-1=unlimited)" type="number" value={planForm.story_limit} onChange={(e) => setPlanForm({ ...planForm, story_limit: e.target.value })} data-testid="plan-stories" />
                  <BrutalInput label="Description" value={planForm.description} onChange={(e) => setPlanForm({ ...planForm, description: e.target.value })} placeholder="Optional..." />
                </div>
                <BrutalButton type="submit" variant="indigo" fullWidth disabled={!planForm.name || createPlanMutation.isPending} data-testid="create-plan-btn">
                  {createPlanMutation.isPending ? 'Creating...' : 'Create Plan'}
                </BrutalButton>
              </form>
            </BrutalCard>
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4">Subscription Plans ({plans.length})</h3>
              {plans.length === 0 ? <p className="text-center py-6 text-gray-500 font-bold">No plans yet</p> : (
                <div className="grid md:grid-cols-2 gap-4">
                  {plans.map((p) => (
                    <div key={p.id} className="border-4 border-black p-4" data-testid={`plan-${p.id}`}>
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-black text-lg">{p.name}</h4>
                        <BrutalButton variant="rose" size="sm" onClick={() => deletePlanMutation.mutate(p.id)}><Trash2 size={14} /></BrutalButton>
                      </div>
                      <p className="text-2xl font-black text-indigo-600">${p.price_monthly}/mo</p>
                      <p className="text-sm mt-1">{p.student_seats} seats | {p.story_limit === -1 ? 'Unlimited' : p.story_limit} stories</p>
                      {p.description && <p className="text-xs text-gray-500 mt-1">{p.description}</p>}
                    </div>
                  ))}
                </div>
              )}
            </BrutalCard>
          </div>
        )}


        {/* =================== BILLING/ROI TAB =================== */}
        {activeTab === 'billing' && (
          <div className="space-y-6" data-testid="billing-tab">
            <BrutalCard shadow="xl" className="max-w-2xl">
              <h3 className="text-2xl font-black uppercase mb-6">Billing & ROI Configuration</h3>
              <form onSubmit={(e) => { e.preventDefault(); updateBillingMutation.mutate(billingForm); }} className="space-y-6">
                <div className="border-4 border-black p-4">
                  <h4 className="font-black uppercase mb-4">Pricing Model</h4>
                  <div className="space-y-2">
                    {[
                      { v: 'per_seat', l: 'Per Seat', d: 'Charge a flat monthly fee per student seat' },
                      { v: 'roi_markup', l: 'ROI Markup', d: 'Charge a % markup on actual AI costs per user' },
                      { v: 'flat_fee', l: 'Flat Fee Per Story', d: 'Charge a fixed price per story generated' },
                    ].map(opt => (
                      <label key={opt.v} className={`block p-3 border-4 border-black cursor-pointer ${billingForm.pricing_model === opt.v ? 'bg-indigo-100' : 'bg-white'}`}>
                        <input type="radio" name="pricing" value={opt.v} checked={billingForm.pricing_model === opt.v}
                          onChange={() => setBillingForm({ ...billingForm, pricing_model: opt.v })} className="mr-2" />
                        <span className="font-black">{opt.l}</span>
                        <p className="text-xs text-gray-500 ml-5">{opt.d}</p>
                      </label>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block font-bold text-sm uppercase mb-2">Per Seat Price ($/mo)</label>
                    <input type="number" step="0.01" value={billingForm.per_seat_price} onChange={(e) => setBillingForm({ ...billingForm, per_seat_price: parseFloat(e.target.value) || 0 })} className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="per-seat-price" /></div>
                  <div><label className="block font-bold text-sm uppercase mb-2">ROI Markup (%)</label>
                    <input type="number" value={billingForm.roi_markup_percent} onChange={(e) => setBillingForm({ ...billingForm, roi_markup_percent: parseFloat(e.target.value) || 0 })} className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="roi-markup" />
                    <p className="text-xs text-gray-500 mt-1">300% = charge 3x AI cost</p></div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block font-bold text-sm uppercase mb-2">Flat Fee Per Story ($)</label>
                    <input type="number" step="0.01" value={billingForm.flat_fee_per_story} onChange={(e) => setBillingForm({ ...billingForm, flat_fee_per_story: parseFloat(e.target.value) || 0 })} className="w-full border-4 border-black px-4 py-3 font-bold" /></div>
                  <div><label className="block font-bold text-sm uppercase mb-2">Avg AI Cost/Story ($)</label>
                    <input type="number" step="0.01" value={billingForm.avg_cost_per_story} onChange={(e) => setBillingForm({ ...billingForm, avg_cost_per_story: parseFloat(e.target.value) || 0 })} className="w-full border-4 border-black px-4 py-3 font-bold" /></div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block font-bold text-sm uppercase mb-2">Free Tier Stories</label>
                    <input type="number" value={billingForm.free_tier_stories} onChange={(e) => setBillingForm({ ...billingForm, free_tier_stories: parseInt(e.target.value) || 0 })} className="w-full border-4 border-black px-4 py-3 font-bold" /></div>
                  <div><label className="block font-bold text-sm uppercase mb-2">Referral Reward ($)</label>
                    <input type="number" step="0.01" value={billingForm.referral_reward_amount} onChange={(e) => setBillingForm({ ...billingForm, referral_reward_amount: parseFloat(e.target.value) || 0 })} className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="referral-reward" /></div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block font-bold text-sm uppercase mb-2">Donation Cost/Story ($)</label>
                    <input type="number" step="0.01" value={billingForm.donation_cost_per_story} onChange={(e) => setBillingForm({ ...billingForm, donation_cost_per_story: parseFloat(e.target.value) || 0 })} className="w-full border-4 border-black px-4 py-3 font-bold" /></div>
                  <label className="flex items-center gap-2 p-3 border-4 border-black cursor-pointer self-end">
                    <input type="checkbox" checked={billingForm.remove_limits_on_paid} onChange={(e) => setBillingForm({ ...billingForm, remove_limits_on_paid: e.target.checked })} className="w-6 h-6" />
                    <span className="font-bold text-sm">Remove all limits for paid users</span>
                  </label>
                </div>
                <BrutalButton type="submit" variant="indigo" fullWidth size="lg" disabled={updateBillingMutation.isPending} data-testid="save-billing-btn">
                  {updateBillingMutation.isPending ? 'Saving...' : 'Save Billing Config'}
                </BrutalButton>
              </form>
            </BrutalCard>
          </div>
        )}

        {/* =================== FEATURE FLAGS TAB =================== */}
        {activeTab === 'features' && (
          <div className="space-y-6" data-testid="features-tab">
            <BrutalCard shadow="xl" className="max-w-2xl">
              <h3 className="text-2xl font-black uppercase mb-6">System-Wide Feature Flags</h3>
              <p className="text-sm text-gray-600 mb-4">Control which features are available across the entire platform.</p>
              <form onSubmit={(e) => { e.preventDefault(); updateFlagsMutation.mutate(flagsForm); }} className="space-y-3">
                {[
                  { key: 'belief_system_enabled', label: 'Belief System / Faith Integration', desc: 'Allow parents to set religious/belief preferences for stories' },
                  { key: 'cultural_context_enabled', label: 'Cultural Context', desc: 'Allow cultural localization for story generation' },
                  { key: 'multi_language_enabled', label: 'Multi-Language Support', desc: 'Allow stories in 20+ world languages' },
                  { key: 'donations_enabled', label: 'Sponsor a Reader (Donations)', desc: 'Enable the donation/sponsorship system' },
                  { key: 'referrals_enabled', label: 'Referral Program', desc: 'Enable invite & earn wallet credits' },
                  { key: 'word_definitions_enabled', label: 'Click-to-Define Words', desc: 'Allow students to tap any word for AI definitions' },
                  { key: 'accessibility_mode', label: 'Accessibility Mode', desc: 'Enable enhanced accessibility features for deaf/HoH users' },
                  { key: 'brand_sponsorship_enabled', label: 'Brand Story Integration', desc: 'Allow brands to be woven into stories (requires parent opt-in)' },
                  { key: 'classroom_sponsorship_enabled', label: 'Classroom Sponsorships', desc: 'Allow businesses to sponsor classrooms for unlimited stories' },
                ].map(flag => (
                  <label key={flag.key} className={`flex items-center justify-between p-4 border-4 border-black cursor-pointer transition-colors ${flagsForm[flag.key] ? 'bg-emerald-50' : 'bg-gray-50'}`}>
                    <div>
                      <span className="font-black">{flag.label}</span>
                      <p className="text-xs text-gray-500">{flag.desc}</p>
                    </div>
                    <input type="checkbox" checked={flagsForm[flag.key]} onChange={(e) => setFlagsForm({ ...flagsForm, [flag.key]: e.target.checked })}
                      className="w-6 h-6 accent-emerald-600" data-testid={`flag-${flag.key}`} />
                  </label>
                ))}
                <BrutalButton type="submit" variant="indigo" fullWidth size="lg" disabled={updateFlagsMutation.isPending} data-testid="save-features-btn">
                  {updateFlagsMutation.isPending ? 'Saving...' : 'Save Feature Flags'}
                </BrutalButton>
              </form>
            </BrutalCard>
          </div>
        )}

        {/* =================== LLM CONFIG TAB =================== */}
        {activeTab === 'config' && (
          <div className="space-y-6" data-testid="config-tab">
            <BrutalCard shadow="xl" className="max-w-2xl">
              <h3 className="text-2xl font-black uppercase mb-6">LLM Provider Configuration</h3>
              <form onSubmit={(e) => { e.preventDefault(); updateModelMutation.mutate(llmForm); }} className="space-y-6">
                <div>
                  <p className="font-bold text-sm uppercase mb-3">Provider</p>
                  <div className="flex gap-4">
                    <label className={`flex-1 p-4 border-4 border-black cursor-pointer ${llmForm.provider === 'emergent' ? 'bg-indigo-100 brutal-shadow-md' : 'bg-white'}`}>
                      <input type="radio" name="provider" value="emergent" checked={llmForm.provider === 'emergent'} onChange={() => setLlmForm({ ...llmForm, provider: 'emergent', model: 'gpt-5.2' })} className="mr-2" />
                      <span className="font-black text-lg">Emergent LLM</span>
                      <p className="text-sm font-medium text-gray-600 mt-1">Uses Universal Key. Models: GPT-5.2, GPT-4o</p>
                    </label>
                    <label className={`flex-1 p-4 border-4 border-black cursor-pointer ${llmForm.provider === 'openrouter' ? 'bg-emerald-100 brutal-shadow-md' : 'bg-white'}`}>
                      <input type="radio" name="provider" value="openrouter" checked={llmForm.provider === 'openrouter'} onChange={() => setLlmForm({ ...llmForm, provider: 'openrouter', model: 'openrouter/auto' })} className="mr-2" />
                      <span className="font-black text-lg">OpenRouter</span>
                      <p className="text-sm font-medium text-gray-600 mt-1">300+ models including free options</p>
                    </label>
                  </div>
                </div>
                <div>
                  <p className="font-bold text-sm uppercase mb-2">Model</p>
                  {llmForm.provider === 'emergent' ? (
                    <select value={llmForm.model} onChange={(e) => setLlmForm({ ...llmForm, model: e.target.value })} className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="model-select">
                      <option value="gpt-5.2">GPT-5.2 (Best quality)</option><option value="gpt-4o">GPT-4o (Good quality)</option><option value="gpt-4o-mini">GPT-4o Mini (Budget)</option>
                    </select>
                  ) : (
                    <select value={llmForm.model} onChange={(e) => setLlmForm({ ...llmForm, model: e.target.value })} className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="model-select">
                      <option value="openrouter/auto">Auto (Smart routing)</option>
                      <option value="qwen/qwen3-next-80b-a3b-instruct:free">Qwen3 80B (FREE)</option>
                      <option value="openai/gpt-oss-120b:free">GPT-OSS 120B (FREE)</option>
                      <option value="nvidia/nemotron-nano-9b-v2:free">Nemotron Nano 9B (FREE)</option>
                    </select>
                  )}
                </div>
                {llmForm.provider === 'openrouter' && (
                  <BrutalInput label="OpenRouter API Key" type="password" value={llmForm.openrouter_key} onChange={(e) => setLlmForm({ ...llmForm, openrouter_key: e.target.value })} placeholder="sk-or-v1-..." data-testid="openrouter-key-input" />
                )}
                <BrutalCard className="bg-amber-50 border-amber-500">
                  <p className="font-bold text-sm">Current Config:</p>
                  <p className="font-mono text-sm mt-1">Provider: {modelConfig?.provider || 'emergent'} | Model: {modelConfig?.model || 'gpt-5.2'}</p>
                </BrutalCard>
                <BrutalButton type="submit" variant="indigo" fullWidth size="lg" disabled={updateModelMutation.isPending} data-testid="save-config-btn">
                  {updateModelMutation.isPending ? 'Saving...' : 'Save Configuration'}
                </BrutalButton>
              </form>
            </BrutalCard>
          </div>
        )}

        {/* =================== APP SETTINGS TAB =================== */}
        {activeTab === 'settings' && (
          <div className="space-y-6" data-testid="settings-tab">
            <BrutalCard shadow="xl" className="max-w-2xl">
              <h3 className="text-2xl font-black uppercase mb-6">App Settings</h3>
              <form onSubmit={(e) => { e.preventDefault(); updateSettingsMutation.mutate(settingsForm); }} className="space-y-6">
                <div className="border-4 border-black p-4">
                  <h4 className="font-black uppercase text-lg mb-4">Spelling & Spellcheck</h4>
                  <div className="space-y-4">
                    <label className="flex items-center justify-between cursor-pointer p-3 border-2 border-black hover:bg-gray-50">
                      <div><span className="font-bold">Disable Browser Spellcheck</span><p className="text-sm text-gray-600">System-wide</p></div>
                      <input type="checkbox" checked={settingsForm.global_spellcheck_disabled} onChange={(e) => setSettingsForm({ ...settingsForm, global_spellcheck_disabled: e.target.checked })} className="w-6 h-6" data-testid="global-spellcheck-toggle" />
                    </label>
                    <div>
                      <p className="font-bold mb-2">Default Spelling Mode</p>
                      <div className="flex gap-4">
                        <label className={`flex-1 p-3 border-4 border-black cursor-pointer text-center ${settingsForm.global_spelling_mode === 'phonetic' ? 'bg-emerald-100' : 'bg-white'}`}>
                          <input type="radio" name="spelling" value="phonetic" checked={settingsForm.global_spelling_mode === 'phonetic'} onChange={() => setSettingsForm({ ...settingsForm, global_spelling_mode: 'phonetic' })} className="mr-2" />
                          <span className="font-bold">Phonetic OK</span>
                        </label>
                        <label className={`flex-1 p-3 border-4 border-black cursor-pointer text-center ${settingsForm.global_spelling_mode === 'exact' ? 'bg-indigo-100' : 'bg-white'}`}>
                          <input type="radio" name="spelling" value="exact" checked={settingsForm.global_spelling_mode === 'exact'} onChange={() => setSettingsForm({ ...settingsForm, global_spelling_mode: 'exact' })} className="mr-2" />
                          <span className="font-bold">Exact Required</span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="border-4 border-black p-4">
                  <h4 className="font-black uppercase text-lg mb-4">Free Account Limits</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div><label className="block font-bold text-sm uppercase mb-2">Max Stories</label>
                      <input type="number" min={1} max={100} value={settingsForm.free_account_story_limit} onChange={(e) => setSettingsForm({ ...settingsForm, free_account_story_limit: parseInt(e.target.value) || 5 })} className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="free-story-limit" />
                    </div>
                    <div><label className="block font-bold text-sm uppercase mb-2">Max Assessments</label>
                      <input type="number" min={1} max={100} value={settingsForm.free_account_assessment_limit} onChange={(e) => setSettingsForm({ ...settingsForm, free_account_assessment_limit: parseInt(e.target.value) || 10 })} className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="free-assessment-limit" />
                    </div>
                  </div>
                </div>
                <BrutalButton type="submit" variant="indigo" fullWidth size="lg" disabled={updateSettingsMutation.isPending} data-testid="save-settings-btn">
                  {updateSettingsMutation.isPending ? 'Saving...' : 'Save Settings'}
                </BrutalButton>
              </form>
            </BrutalCard>
          </div>
        )}
      </div>
    </div>
  );
};

// Stat card helper
const StatCard = ({ icon: Icon, label, value, sub, color = 'indigo' }) => {
  const bgMap = { indigo: 'bg-indigo-50', emerald: 'bg-emerald-50', amber: 'bg-amber-50', rose: 'bg-rose-50' };
  const textMap = { indigo: 'text-indigo-600', emerald: 'text-emerald-600', amber: 'text-amber-600', rose: 'text-rose-600' };
  return (
    <div className={`${bgMap[color]} border-4 border-black p-5 brutal-shadow-sm`}>
      <div className="flex items-center gap-2 mb-2"><Icon size={18} className={textMap[color]} /><p className="font-bold text-xs uppercase text-gray-600">{label}</p></div>
      <p className="text-3xl font-black">{value}{sub && <span className="text-sm text-gray-500 ml-1">{sub}</span>}</p>
    </div>
  );
};

export default AdminPortal;
