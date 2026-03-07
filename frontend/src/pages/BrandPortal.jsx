import React, { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { brandPortalAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalInput } from '@/components/brutal';
import {
  Home, LogOut, BarChart3, Megaphone, DollarSign, PlusCircle, Trash2,
  Play, Pause, CreditCard, TrendingUp, Eye, Upload, Package,
  Globe, FileText, ChevronRight, ChevronLeft, Check, Pencil, X, Building2,
} from 'lucide-react';
import { toast } from 'sonner';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const AD_CATEGORIES = [
  'technology', 'education', 'food', 'sports', 'arts', 'health',
  'games', 'books', 'science', 'music', 'nature', 'travel',
];

const COUNTRIES = [
  'United States', 'Canada', 'United Kingdom', 'Australia', 'Germany',
  'France', 'India', 'Japan', 'Brazil', 'Mexico', 'South Korea',
  'Nigeria', 'South Africa', 'Kenya', 'Ghana',
];

const LANGUAGES = [
  'English', 'Spanish', 'French', 'Chinese', 'Hindi', 'Arabic',
  'Bengali', 'Portuguese', 'Russian', 'Japanese', 'German', 'Korean',
  'Turkish', 'Vietnamese', 'Italian', 'Thai', 'Polish', 'Dutch', 'Swahili', 'Malay',
];

const BrandPortal = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('dashboard');

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get('session_id');
    const payment = params.get('payment');
    if (sessionId && payment === 'success') {
      pollTopup(sessionId);
      window.history.replaceState({}, '', '/brand-portal');
    } else if (payment === 'cancelled') {
      toast.error('Payment cancelled');
      window.history.replaceState({}, '', '/brand-portal');
    }
  }, []);

  const pollTopup = async (sessionId, attempts = 0) => {
    if (attempts >= 5) { toast.info('Payment still processing...'); return; }
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

  const brand = dashboard?.brand;
  const stats = dashboard?.stats || {};
  const campaigns = dashboard?.campaigns || [];
  const notApproved = user?.role === 'brand_partner' && !user?.brand_approved;

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'brand-profile', label: 'Brand Profile', icon: Building2 },
    { id: 'products', label: 'Products', icon: Package },
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
              <button onClick={() => navigate('/')} className="p-3 border-4 border-black bg-amber-100 brutal-shadow-sm hover:brutal-shadow-md brutal-active" data-testid="home-btn">
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
            <div className="flex items-center gap-3">
              <LanguageSwitcher />
              <BrutalButton variant="dark" onClick={() => { logout(); navigate('/login'); }} className="flex items-center gap-2" data-testid="logout-btn">
                <LogOut size={20} /> Logout
              </BrutalButton>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {notApproved && (
          <BrutalCard shadow="lg" className="bg-amber-50 border-amber-400 mb-6">
            <p className="font-bold text-lg">Your brand partner account is pending admin approval.</p>
            <p className="text-sm text-gray-600 mt-1">You can still set up your brand profile while waiting for approval.</p>
          </BrutalCard>
        )}

        {/* Show onboarding prompt if not completed */}
        {brand && !brand.onboarding_completed && activeTab === 'dashboard' && (
          <BrutalCard shadow="lg" className="bg-indigo-50 border-indigo-400 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-bold text-lg">Complete Your Brand Setup</p>
                <p className="text-sm text-gray-600 mt-1">Set up your brand profile, add products, and upload your logo to start appearing in stories.</p>
              </div>
              <BrutalButton variant="amber" onClick={() => setActiveTab('brand-profile')} className="flex items-center gap-2" data-testid="start-onboarding-btn">
                Get Started <ChevronRight size={18} />
              </BrutalButton>
            </div>
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

        {activeTab === 'dashboard' && <DashboardTab brand={brand} stats={stats} campaigns={campaigns} dashboard={dashboard} />}
        {activeTab === 'brand-profile' && <BrandProfileTab brand={brand} queryClient={queryClient} />}
        {activeTab === 'products' && <ProductsTab brand={brand} queryClient={queryClient} />}
        {activeTab === 'campaigns' && <CampaignsTab brand={brand} campaigns={campaigns} notApproved={notApproved} queryClient={queryClient} />}
        {activeTab === 'budget' && <BudgetTab stats={stats} />}
        {activeTab === 'impressions' && <ImpressionsTab stats={stats} dashboard={dashboard} />}
      </div>
    </div>
  );
};


// ==================== DASHBOARD TAB ====================
const DashboardTab = ({ brand, stats, campaigns, dashboard }) => (
  <div className="space-y-6" data-testid="brand-dashboard-tab">
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatCard icon={Eye} label="Impressions" value={stats.total_impressions || 0} color="indigo" />
      <StatCard icon={DollarSign} label="Spent" value={`$${(stats.total_spent || 0).toFixed(2)}`} color="rose" />
      <StatCard icon={DollarSign} label="Budget Left" value={`$${(stats.budget_remaining || 0).toFixed(2)}`} color="emerald" />
      <StatCard icon={Megaphone} label="Active Campaigns" value={stats.active_campaigns || 0} color="amber" />
    </div>
    {brand && (
      <BrutalCard shadow="lg">
        <h3 className="text-xl font-black uppercase mb-3">Brand Overview</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="flex items-center gap-4">
            {brand.logo_url ? (
              <img src={brand.logo_url} alt={brand.name} className="w-16 h-16 object-contain border-2 border-black" data-testid="brand-logo-preview" />
            ) : (
              <div className="w-16 h-16 bg-gray-100 border-2 border-dashed border-gray-400 flex items-center justify-center">
                <Building2 size={24} className="text-gray-400" />
              </div>
            )}
            <div>
              <p className="text-lg font-black">{brand.name}</p>
              <p className="text-sm text-gray-500">{brand.website || 'No website set'}</p>
            </div>
          </div>
          {brand.problem_statement && (
            <div>
              <p className="text-sm font-bold text-gray-500">Problem We Solve</p>
              <p className="text-sm mt-1">{brand.problem_statement}</p>
            </div>
          )}
          <div>
            <p className="text-sm font-bold text-gray-500">Products</p>
            <div className="flex flex-wrap gap-1 mt-1">
              {brand.products?.map((p, i) => <BrutalBadge key={i} variant="indigo" size="sm">{p.name}</BrutalBadge>)}
              {(!brand.products || brand.products.length === 0) && <span className="text-gray-400 text-sm">None added yet</span>}
            </div>
          </div>
          <div>
            <p className="text-sm font-bold text-gray-500">Target Regions</p>
            <div className="flex flex-wrap gap-1 mt-1">
              {brand.target_regions?.map((r, i) => (
                <BrutalBadge key={i} variant="emerald" size="sm">
                  {[r.country, r.state, r.city].filter(Boolean).join(', ')}
                </BrutalBadge>
              ))}
              {(!brand.target_regions || brand.target_regions.length === 0) && <span className="text-gray-400 text-sm">Global</span>}
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
);


// ==================== BRAND PROFILE TAB ====================
const BrandProfileTab = ({ brand, queryClient }) => {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    name: brand?.name || '',
    website: brand?.website || '',
    problem_statement: brand?.problem_statement || '',
    target_categories: brand?.target_categories || [],
    target_languages: brand?.target_languages || [],
  });
  const [regions, setRegions] = useState(brand?.target_regions || []);
  const [newRegion, setNewRegion] = useState({ country: '', state: '', city: '', zip_code: '' });
  const fileRef = useRef(null);
  const [uploading, setUploading] = useState(false);

  React.useEffect(() => {
    if (brand) {
      setForm({
        name: brand.name || '',
        website: brand.website || '',
        problem_statement: brand.problem_statement || '',
        target_categories: brand.target_categories || [],
        target_languages: brand.target_languages || [],
      });
      setRegions(brand.target_regions || []);
    }
  }, [brand]);

  const updateMut = useMutation({
    mutationFn: (data) => brandPortalAPI.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['brand-dashboard']);
      toast.success('Brand profile updated!');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to update'),
  });

  const handleSaveStep = (nextStep) => {
    const payload = { ...form, target_regions: regions };
    if (nextStep > 3) payload.onboarding_completed = true;
    updateMut.mutate(payload);
    if (nextStep <= 3) setStep(nextStep);
  };

  const handleLogoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File too large. Maximum size is 10MB');
      return;
    }
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      await brandPortalAPI.uploadLogo(fd);
      queryClient.invalidateQueries(['brand-dashboard']);
      toast.success('Logo uploaded!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const addRegion = () => {
    if (!newRegion.country) { toast.error('Select a country'); return; }
    setRegions([...regions, { ...newRegion }]);
    setNewRegion({ country: '', state: '', city: '', zip_code: '' });
  };

  const removeRegion = (idx) => setRegions(regions.filter((_, i) => i !== idx));

  const steps = [
    { num: 1, label: 'Brand Info', icon: FileText },
    { num: 2, label: 'Logo & Media', icon: Upload },
    { num: 3, label: 'Targeting', icon: Globe },
  ];

  return (
    <div className="space-y-6" data-testid="brand-profile-tab">
      {/* Step indicator */}
      <div className="flex items-center justify-center gap-2 mb-4">
        {steps.map((s, i) => {
          const Icon = s.icon;
          return (
            <React.Fragment key={s.num}>
              <button onClick={() => setStep(s.num)}
                className={`flex items-center gap-2 px-4 py-2 border-4 border-black font-bold text-sm transition-all ${step === s.num ? 'bg-amber-200 brutal-shadow-sm' : step > s.num ? 'bg-emerald-100' : 'bg-white'}`}
                data-testid={`step-${s.num}-btn`}>
                {step > s.num ? <Check size={16} className="text-emerald-600" /> : <Icon size={16} />}
                {s.label}
              </button>
              {i < steps.length - 1 && <ChevronRight size={20} className="text-gray-400" />}
            </React.Fragment>
          );
        })}
      </div>

      {/* Step 1: Brand Info */}
      {step === 1 && (
        <BrutalCard shadow="lg" data-testid="step-1-content">
          <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
            <FileText size={22} /> Brand Information
          </h3>
          <div className="space-y-4">
            <BrutalInput label="Brand Name" value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Your Brand Name" data-testid="brand-name-input" />
            <BrutalInput label="Website" value={form.website}
              onChange={(e) => setForm({ ...form, website: e.target.value })}
              placeholder="https://yourbrand.com" data-testid="brand-website-input" />
            <div>
              <label className="block font-bold text-sm uppercase mb-2">What problem does your brand solve?</label>
              <textarea
                className="w-full border-4 border-black px-4 py-3 font-medium text-base min-h-[120px] focus:outline-none focus:ring-2 focus:ring-amber-400"
                value={form.problem_statement}
                onChange={(e) => setForm({ ...form, problem_statement: e.target.value })}
                placeholder="e.g., We help children develop healthy reading habits through engaging, interactive e-readers that make learning fun and accessible..."
                data-testid="problem-statement-input"
              />
              <p className="text-xs text-gray-500 mt-1">This will be woven into stories where your brand naturally solves a character's problem.</p>
            </div>
            <div>
              <label className="block font-bold text-sm uppercase mb-2">Target Categories</label>
              <div className="flex flex-wrap gap-2">
                {AD_CATEGORIES.map((cat) => (
                  <button key={cat} type="button" onClick={() => {
                    const cats = form.target_categories.includes(cat)
                      ? form.target_categories.filter(c => c !== cat)
                      : [...form.target_categories, cat];
                    setForm({ ...form, target_categories: cats });
                  }}
                    className={`px-3 py-1 border-2 border-black font-bold text-sm transition-all ${form.target_categories.includes(cat) ? 'bg-amber-200' : 'bg-white hover:bg-gray-50'}`}
                    data-testid={`cat-${cat}`}
                  >{cat}</button>
                ))}
              </div>
            </div>
            <div className="flex justify-end">
              <BrutalButton variant="amber" onClick={() => handleSaveStep(2)} className="flex items-center gap-2"
                disabled={updateMut.isPending} data-testid="next-step-1-btn">
                {updateMut.isPending ? 'Saving...' : 'Save & Continue'} <ChevronRight size={18} />
              </BrutalButton>
            </div>
          </div>
        </BrutalCard>
      )}

      {/* Step 2: Logo Upload */}
      {step === 2 && (
        <BrutalCard shadow="lg" data-testid="step-2-content">
          <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
            <Upload size={22} /> Logo & Media
          </h3>
          <div className="space-y-4">
            <div className="flex items-center gap-6">
              <div className="flex-shrink-0">
                {brand?.logo_url ? (
                  <img src={brand.logo_url} alt="Logo" className="w-32 h-32 object-contain border-4 border-black p-2" data-testid="logo-display" />
                ) : (
                  <div className="w-32 h-32 border-4 border-dashed border-gray-400 flex flex-col items-center justify-center gap-2 bg-gray-50">
                    <Upload size={32} className="text-gray-400" />
                    <span className="text-xs text-gray-400 font-bold">No Logo</span>
                  </div>
                )}
              </div>
              <div className="flex-1">
                <p className="font-bold mb-2">Upload your brand logo</p>
                <p className="text-sm text-gray-500 mb-3">Max 10MB. Supported: PNG, JPG, WebP, SVG</p>
                <input ref={fileRef} type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml"
                  onChange={handleLogoUpload} className="hidden" data-testid="logo-file-input" />
                <BrutalButton variant="default" onClick={() => fileRef.current?.click()}
                  disabled={uploading} data-testid="upload-logo-btn">
                  {uploading ? 'Uploading...' : brand?.logo_url ? 'Replace Logo' : 'Choose File'}
                </BrutalButton>
              </div>
            </div>
            <div className="flex justify-between">
              <BrutalButton variant="default" onClick={() => setStep(1)} className="flex items-center gap-2" data-testid="back-step-2-btn">
                <ChevronLeft size={18} /> Back
              </BrutalButton>
              <BrutalButton variant="amber" onClick={() => handleSaveStep(3)} className="flex items-center gap-2"
                disabled={updateMut.isPending} data-testid="next-step-2-btn">
                {updateMut.isPending ? 'Saving...' : 'Save & Continue'} <ChevronRight size={18} />
              </BrutalButton>
            </div>
          </div>
        </BrutalCard>
      )}

      {/* Step 3: Targeting */}
      {step === 3 && (
        <BrutalCard shadow="lg" data-testid="step-3-content">
          <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2">
            <Globe size={22} /> Targeting & Regions
          </h3>
          <div className="space-y-5">
            {/* Target Languages */}
            <div>
              <label className="block font-bold text-sm uppercase mb-2">Target Languages</label>
              <div className="flex flex-wrap gap-2">
                {LANGUAGES.map((lang) => (
                  <button key={lang} type="button" onClick={() => {
                    const langs = form.target_languages.includes(lang)
                      ? form.target_languages.filter(l => l !== lang)
                      : [...form.target_languages, lang];
                    setForm({ ...form, target_languages: langs });
                  }}
                    className={`px-3 py-1 border-2 border-black font-bold text-sm transition-all ${form.target_languages.includes(lang) ? 'bg-indigo-200' : 'bg-white hover:bg-gray-50'}`}
                    data-testid={`lang-${lang}`}
                  >{lang}</button>
                ))}
              </div>
            </div>

            {/* Target Regions */}
            <div>
              <label className="block font-bold text-sm uppercase mb-2">Marketing Regions</label>
              {regions.length > 0 && (
                <div className="space-y-2 mb-3">
                  {regions.map((r, i) => (
                    <div key={i} className="flex items-center justify-between p-2 border-2 border-black bg-white">
                      <span className="text-sm font-medium">
                        {[r.country, r.state, r.city, r.zip_code].filter(Boolean).join(' > ')}
                      </span>
                      <button onClick={() => removeRegion(i)} className="text-rose-600 hover:text-rose-800" data-testid={`remove-region-${i}`}>
                        <X size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div>
                  <label className="block text-xs font-bold text-gray-500 mb-1">Country</label>
                  <select className="w-full border-2 border-black px-3 py-2 font-medium text-sm"
                    value={newRegion.country} onChange={(e) => setNewRegion({ ...newRegion, country: e.target.value })} data-testid="region-country">
                    <option value="">Select...</option>
                    {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <BrutalInput label="State/Province" value={newRegion.state}
                  onChange={(e) => setNewRegion({ ...newRegion, state: e.target.value })}
                  placeholder="e.g. California" data-testid="region-state" />
                <BrutalInput label="City" value={newRegion.city}
                  onChange={(e) => setNewRegion({ ...newRegion, city: e.target.value })}
                  placeholder="e.g. Los Angeles" data-testid="region-city" />
                <BrutalInput label="ZIP Code" value={newRegion.zip_code}
                  onChange={(e) => setNewRegion({ ...newRegion, zip_code: e.target.value })}
                  placeholder="e.g. 90001" data-testid="region-zip" />
              </div>
              <BrutalButton variant="default" size="sm" onClick={addRegion} className="mt-2 flex items-center gap-1" data-testid="add-region-btn">
                <PlusCircle size={14} /> Add Region
              </BrutalButton>
            </div>

            <div className="flex justify-between">
              <BrutalButton variant="default" onClick={() => setStep(2)} className="flex items-center gap-2" data-testid="back-step-3-btn">
                <ChevronLeft size={18} /> Back
              </BrutalButton>
              <BrutalButton variant="amber" onClick={() => handleSaveStep(4)} className="flex items-center gap-2"
                disabled={updateMut.isPending} data-testid="finish-onboarding-btn">
                {updateMut.isPending ? 'Saving...' : 'Complete Setup'} <Check size={18} />
              </BrutalButton>
            </div>
          </div>
        </BrutalCard>
      )}
    </div>
  );
};


// ==================== PRODUCTS TAB ====================
const ProductsTab = ({ brand, queryClient }) => {
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState({ name: '', description: '', category: '' });

  const products = brand?.products || [];

  const addMut = useMutation({
    mutationFn: (data) => brandPortalAPI.addProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['brand-dashboard']);
      toast.success('Product added!');
      setForm({ name: '', description: '', category: '' });
      setShowForm(false);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }) => brandPortalAPI.updateProduct(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['brand-dashboard']);
      toast.success('Product updated!');
      setEditId(null);
      setForm({ name: '', description: '', category: '' });
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  const deleteMut = useMutation({
    mutationFn: (id) => brandPortalAPI.deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['brand-dashboard']);
      toast.success('Product deleted');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  const startEdit = (p) => {
    setEditId(p.id);
    setForm({ name: p.name, description: p.description || '', category: p.category || '' });
    setShowForm(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name.trim()) { toast.error('Product name is required'); return; }
    if (editId) {
      updateMut.mutate({ id: editId, data: form });
    } else {
      addMut.mutate(form);
    }
  };

  const cancelEdit = () => {
    setEditId(null);
    setForm({ name: '', description: '', category: '' });
    setShowForm(false);
  };

  return (
    <div className="space-y-6" data-testid="products-tab">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-black uppercase flex items-center gap-2">
          <Package size={22} /> Brand Products ({products.length})
        </h3>
        {!showForm && (
          <BrutalButton variant="amber" onClick={() => { setShowForm(true); setEditId(null); setForm({ name: '', description: '', category: '' }); }}
            className="flex items-center gap-2" data-testid="add-product-btn">
            <PlusCircle size={18} /> Add Product
          </BrutalButton>
        )}
      </div>

      {showForm && (
        <BrutalCard shadow="lg" data-testid="product-form">
          <h4 className="font-black uppercase mb-3">{editId ? 'Edit Product' : 'New Product'}</h4>
          <form onSubmit={handleSubmit} className="space-y-3">
            <BrutalInput label="Product Name" value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="e.g. Smart E-Reader Pro" data-testid="product-name-input" />
            <BrutalInput label="Description" value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="What does this product do?" data-testid="product-desc-input" />
            <BrutalInput label="Category" value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              placeholder="e.g. education, technology" data-testid="product-category-input" />
            <div className="flex gap-3">
              <BrutalButton type="submit" variant="amber" disabled={addMut.isPending || updateMut.isPending} data-testid="save-product-btn">
                {addMut.isPending || updateMut.isPending ? 'Saving...' : editId ? 'Update Product' : 'Add Product'}
              </BrutalButton>
              <BrutalButton type="button" variant="default" onClick={cancelEdit} data-testid="cancel-product-btn">Cancel</BrutalButton>
            </div>
          </form>
        </BrutalCard>
      )}

      {products.length === 0 && !showForm ? (
        <BrutalCard shadow="lg" className="text-center py-10">
          <Package size={48} className="mx-auto text-gray-300 mb-3" />
          <p className="font-bold text-gray-500">No products yet</p>
          <p className="text-sm text-gray-400 mt-1">Add your products so they can be featured in educational stories.</p>
        </BrutalCard>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {products.map((p) => (
            <BrutalCard key={p.id} shadow="md" data-testid={`product-${p.id}`}>
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-black text-lg">{p.name}</h4>
                <div className="flex gap-1">
                  <button onClick={() => startEdit(p)} className="p-1 border-2 border-black hover:bg-amber-100 transition-all" data-testid={`edit-product-${p.id}`}>
                    <Pencil size={14} />
                  </button>
                  <button onClick={() => deleteMut.mutate(p.id)} className="p-1 border-2 border-black hover:bg-rose-100 transition-all" data-testid={`delete-product-${p.id}`}>
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
              {p.description && <p className="text-sm text-gray-600 mb-2">{p.description}</p>}
              {p.category && <BrutalBadge variant="indigo" size="sm">{p.category}</BrutalBadge>}
            </BrutalCard>
          ))}
        </div>
      )}
    </div>
  );
};


// ==================== CAMPAIGNS TAB ====================
const CampaignsTab = ({ brand, campaigns, notApproved, queryClient }) => {
  const [campaignForm, setCampaignForm] = useState({
    name: '', description: '', products_text: '',
    target_categories: [], budget: '', cost_per_impression: '0.05',
  });

  const createMut = useMutation({
    mutationFn: (data) => brandPortalAPI.createCampaign(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['brand-dashboard']);
      toast.success('Campaign created!');
      setCampaignForm({ name: '', description: '', products_text: '', target_categories: [], budget: '', cost_per_impression: '0.05' });
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }) => brandPortalAPI.updateCampaign(id, data),
    onSuccess: () => { queryClient.invalidateQueries(['brand-dashboard']); toast.success('Campaign updated'); },
  });

  const deleteMut = useMutation({
    mutationFn: (id) => brandPortalAPI.deleteCampaign(id),
    onSuccess: () => { queryClient.invalidateQueries(['brand-dashboard']); toast.success('Campaign deleted'); },
  });

  return (
    <div className="space-y-6" data-testid="campaigns-tab">
      <BrutalCard shadow="lg">
        <h3 className="text-xl font-black uppercase mb-4 flex items-center gap-2"><PlusCircle size={22} /> New Campaign</h3>
        <form onSubmit={(e) => {
          e.preventDefault();
          const products = campaignForm.products_text ? campaignForm.products_text.split(',').map(p => ({ name: p.trim(), category: '' })) : [];
          createMut.mutate({
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
                  data-testid={`camp-cat-${cat}`}
                >{cat}</button>
              ))}
            </div>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <BrutalInput label="Budget ($)" type="number" step="0.01" value={campaignForm.budget} onChange={(e) => setCampaignForm({ ...campaignForm, budget: e.target.value })} placeholder="100.00" data-testid="campaign-budget" />
            <BrutalInput label="Cost Per Impression ($)" type="number" step="0.01" value={campaignForm.cost_per_impression} onChange={(e) => setCampaignForm({ ...campaignForm, cost_per_impression: e.target.value })} />
          </div>
          <BrutalButton type="submit" variant="amber" fullWidth disabled={!campaignForm.name || createMut.isPending || notApproved} data-testid="create-campaign-btn">
            {createMut.isPending ? 'Creating...' : 'Launch Campaign'}
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
                      onClick={() => updateMut.mutate({ id: c.id, data: { status: c.status === 'active' ? 'paused' : 'active' } })}>
                      {c.status === 'active' ? <Pause size={14} /> : <Play size={14} />}
                    </BrutalButton>
                    <BrutalButton variant="rose" size="sm" onClick={() => deleteMut.mutate(c.id)}><Trash2 size={14} /></BrutalButton>
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
  );
};


// ==================== BUDGET TAB ====================
const BudgetTab = ({ stats }) => {
  const [topupAmount, setTopupAmount] = useState('');

  const topupMut = useMutation({
    mutationFn: (amount) => brandPortalAPI.topup({ amount: parseFloat(amount), origin_url: window.location.origin }),
    onSuccess: (res) => { if (res.data.url) window.location.href = res.data.url; },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  return (
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
  );
};


// ==================== IMPRESSIONS TAB ====================
const ImpressionsTab = ({ stats, dashboard }) => (
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
                <td className="py-2 px-3 text-sm">{imp.products_featured?.join(', ') || '-'}</td>
                <td className="py-2 px-3 text-sm font-bold">${imp.cost?.toFixed(3)}</td>
              </tr>
            ))}
          </tbody></table>
        </div>
      )}
    </BrutalCard>
  </div>
);


// ==================== STAT CARD COMPONENT ====================
const StatCard = ({ icon: Icon, label, value, color = 'indigo' }) => {
  const bgMap = { indigo: 'bg-indigo-50', emerald: 'bg-emerald-50', amber: 'bg-amber-50', rose: 'bg-rose-50' };
  const textMap = { indigo: 'text-indigo-600', emerald: 'text-emerald-600', amber: 'text-amber-600', rose: 'text-rose-600' };
  return (
    <div className={`${bgMap[color]} border-4 border-black p-5 brutal-shadow-sm`} data-testid={`stat-${label.toLowerCase().replace(/\s/g, '-')}`}>
      <div className="flex items-center gap-2 mb-2"><Icon size={18} className={textMap[color]} /><p className="font-bold text-xs uppercase text-gray-600">{label}</p></div>
      <p className="text-3xl font-black">{value}</p>
    </div>
  );
};

export default BrandPortal;
