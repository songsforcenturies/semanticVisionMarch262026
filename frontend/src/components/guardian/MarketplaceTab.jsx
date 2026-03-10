import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { wordBankAPI, subscriptionAPI, walletAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalInput } from '@/components/brutal';
import { Search, Eye, Check, ShoppingCart, Wallet, PlusCircle, X } from 'lucide-react';
import { toast } from 'sonner';
import { useCurrency } from '@/contexts/CurrencyContext';
import WordBankPreviewDialog from './WordBankPreviewDialog';

const CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'general', label: 'General' },
  { value: 'academic', label: 'Academic' },
  { value: 'professional', label: 'Professional' },
  { value: 'specialized', label: 'Specialized' }
];

const MarketplaceTab = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [previewBank, setPreviewBank] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '', description: '', category: 'general', specialty: '',
    baseline_words: '', target_words: '', stretch_words: '',
    visibility: 'public', price: 0,
  });

  // Check if parent word bank creation is enabled
  const { data: parentWbFlag } = useQuery({
    queryKey: ['parent-wordbank-flag'],
    queryFn: async () => (await wordBankAPI.canParentCreate()).data,
  });
  const canCreateWordBank = parentWbFlag?.parent_wordbank_creation_enabled === true;

  // Create word bank mutation
  const createWbMutation = useMutation({
    mutationFn: (data) => wordBankAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['marketplace-word-banks']);
      toast.success('Word bank created successfully!');
      setShowCreateForm(false);
      setCreateForm({ name: '', description: '', category: 'general', specialty: '', baseline_words: '', target_words: '', stretch_words: '', visibility: 'public', price: 0 });
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to create word bank'),
  });

  // Fetch wallet balance
  const { data: walletData } = useQuery({
    queryKey: ['wallet-balance'],
    queryFn: async () => (await walletAPI.getBalance()).data,
  });
  const { formatAmount } = useCurrency();

  // Fetch subscription to know what's already purchased
  const { data: subscription } = useQuery({
    queryKey: ['subscription', user?.id],
    queryFn: async () => {
      const response = await subscriptionAPI.get(user?.id);
      return response.data;
    },
    enabled: !!user?.id
  });

  // Fetch word banks
  const { data: wordBanks = [], isLoading } = useQuery({
    queryKey: ['marketplace-word-banks', categoryFilter, searchQuery],
    queryFn: async () => {
      const params = {};
      if (categoryFilter) params.category = categoryFilter;
      if (searchQuery) params.search = searchQuery;
      
      const response = await wordBankAPI.getAll(params);
      return response.data;
    }
  });

  // Purchase mutation — uses wallet for paid banks
  const purchaseMutation = useMutation({
    mutationFn: (bankId) => {
      const bank = wordBanks.find(b => b.id === bankId);
      if (bank && bank.price > 0) {
        return walletAPI.purchaseBank({ guardian_id: user?.id, bank_id: bankId });
      }
      return wordBankAPI.purchase(user?.id, bankId);
    },
    onSuccess: (res, bankId) => {
      queryClient.invalidateQueries(['subscription']);
      queryClient.invalidateQueries(['wallet-balance']);
      const bank = wordBanks.find(b => b.id === bankId);
      toast.success(`${bank?.name} added to your library!`);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Purchase failed');
    }
  });

  const ownedBankIds = subscription?.bank_access || [];

  const handlePurchase = (bank) => {
    if (bank.price === 0) {
      purchaseMutation.mutate(bank.id);
    } else {
      const priceDollars = (bank.price / 100).toFixed(2);
      const balance = walletData?.balance ?? 0;
      if (balance < bank.price / 100) {
        toast.error(`Insufficient balance (${formatAmount(balance)}). Please add funds in the Wallet tab.`);
        return;
      }
      if (window.confirm(`Purchase ${bank.name} for ${formatAmount(priceDollars)}? (Wallet: ${formatAmount(balance)})`)) {
        purchaseMutation.mutate(bank.id);
      }
    }
  };

  const formatPrice = (priceInCents) => {
    if (priceInCents === 0) return 'FREE';
    return formatAmount(priceInCents / 100);
  };

  const getCategoryColor = (category) => {
    const colors = {
      general: 'indigo',
      academic: 'emerald',
      professional: 'amber',
      specialized: 'rose'
    };
    return colors[category] || 'default';
  };

  if (isLoading) {
    return <div className="text-center py-12 text-2xl font-bold">Loading marketplace...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-3xl font-black uppercase">Word Bank Marketplace</h2>
          <p className="text-lg font-medium mt-1">
            {ownedBankIds.length} banks in your library
          </p>
        </div>
        <div className="flex items-center gap-3">
          {canCreateWordBank && (
            <BrutalButton variant="emerald" size="sm" onClick={() => setShowCreateForm(!showCreateForm)}
              className="flex items-center gap-2" data-testid="create-wordbank-btn">
              {showCreateForm ? <X size={18} /> : <PlusCircle size={18} />}
              {showCreateForm ? 'Cancel' : 'Create Word Bank'}
            </BrutalButton>
          )}
          <div className="flex items-center gap-2 px-4 py-2 border-4 border-black bg-amber-50 brutal-shadow-sm">
            <Wallet size={18} className="text-amber-700" />
            <span className="font-black text-lg" data-testid="marketplace-balance">
              {formatAmount(walletData?.balance ?? 0)}
            </span>
          </div>
        </div>
      </div>

      {/* Create Word Bank Form */}
      {canCreateWordBank && showCreateForm && (
        <BrutalCard shadow="xl" className="border-emerald-500" data-testid="create-wordbank-form">
          <h3 className="text-2xl font-black uppercase mb-4">Create Your Own Word Bank</h3>
          <form onSubmit={(e) => {
            e.preventDefault();
            const parseWords = (str) => str.split(',').map(w => w.trim()).filter(Boolean).map(w => ({
              word: w, definition: '', part_of_speech: '', example_sentence: ''
            }));
            const payload = {
              name: createForm.name,
              description: createForm.description || createForm.name,
              category: createForm.category,
              specialty: createForm.specialty || undefined,
              baseline_words: parseWords(createForm.baseline_words),
              target_words: parseWords(createForm.target_words),
              stretch_words: parseWords(createForm.stretch_words),
              visibility: 'global',
              price: 0,
            };
            if (!payload.name || payload.target_words.length === 0) {
              toast.error('Please provide a name and at least some target words.');
              return;
            }
            createWbMutation.mutate(payload);
          }} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <BrutalInput label="Bank Name" required value={createForm.name}
                onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                placeholder="e.g. Space Vocabulary" data-testid="wb-name" />
              <div>
                <label className="block font-bold text-sm uppercase mb-2">Category</label>
                <select value={createForm.category}
                  onChange={(e) => setCreateForm({ ...createForm, category: e.target.value })}
                  className="w-full px-4 py-3 border-4 border-black font-bold focus:outline-none focus:ring-4 focus:ring-emerald-500 bg-white"
                  data-testid="wb-category">
                  <option value="general">General</option>
                  <option value="academic">Academic</option>
                  <option value="professional">Professional</option>
                  <option value="specialized">Specialized</option>
                </select>
              </div>
            </div>
            <BrutalInput label="Description" value={createForm.description}
              onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
              placeholder="Brief description of this word bank" data-testid="wb-description" />
            <BrutalInput label="Specialty (optional)" value={createForm.specialty}
              onChange={(e) => setCreateForm({ ...createForm, specialty: e.target.value })}
              placeholder="e.g. Science, History" data-testid="wb-specialty" />
            <div>
              <label className="block font-bold text-sm uppercase mb-2">Baseline Words (comma-separated)</label>
              <textarea value={createForm.baseline_words}
                onChange={(e) => setCreateForm({ ...createForm, baseline_words: e.target.value })}
                placeholder="word1, word2, word3..."
                className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-emerald-500 min-h-[60px]"
                data-testid="wb-baseline" />
            </div>
            <div>
              <label className="block font-bold text-sm uppercase mb-2">Target Words (comma-separated) *</label>
              <textarea value={createForm.target_words}
                onChange={(e) => setCreateForm({ ...createForm, target_words: e.target.value })}
                placeholder="word1, word2, word3..."
                className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-emerald-500 min-h-[60px]"
                data-testid="wb-target" />
            </div>
            <div>
              <label className="block font-bold text-sm uppercase mb-2">Stretch Words (comma-separated)</label>
              <textarea value={createForm.stretch_words}
                onChange={(e) => setCreateForm({ ...createForm, stretch_words: e.target.value })}
                placeholder="word1, word2, word3..."
                className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-emerald-500 min-h-[60px]"
                data-testid="wb-stretch" />
            </div>
            <BrutalButton type="submit" variant="emerald" fullWidth size="lg"
              disabled={createWbMutation.isPending} data-testid="wb-submit">
              {createWbMutation.isPending ? 'Creating...' : 'Create Word Bank'}
            </BrutalButton>
          </form>
        </BrutalCard>
      )}

      {/* Filters */}
      <BrutalCard shadow="md">
        <div className="grid md:grid-cols-2 gap-4">
          <div className="relative">
            <BrutalInput
              placeholder="Search word banks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pr-12"
            />
            <Search className="absolute right-6 top-1/2 -translate-y-1/2 text-gray-400" size={24} />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="w-full px-4 py-3 border-4 border-black font-bold uppercase focus:outline-none focus:ring-4 focus:ring-indigo-500 bg-white"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>
      </BrutalCard>

      {/* Word Banks Grid */}
      {wordBanks.length === 0 ? (
        <BrutalCard shadow="xl" className="text-center py-12">
          <p className="text-2xl font-bold">No word banks found</p>
          <p className="text-lg font-medium mt-2">Try adjusting your filters</p>
        </BrutalCard>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {wordBanks.map((bank) => {
            const isOwned = ownedBankIds.includes(bank.id);
            const isFree = bank.price === 0;

            return (
              <BrutalCard
                key={bank.id}
                shadow="lg"
                hover
                className="relative flex flex-col"
              >
                {/* Header */}
                <div className="mb-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-xl font-black uppercase flex-1">
                      {bank.name}
                    </h3>
                    {isOwned && (
                      <BrutalBadge variant="emerald" size="sm" className="flex items-center gap-1">
                        <Check size={14} />
                        Owned
                      </BrutalBadge>
                    )}
                  </div>

                  <div className="flex items-center gap-2 mb-3">
                    <BrutalBadge variant={getCategoryColor(bank.category)} size="sm">
                      {bank.category}
                    </BrutalBadge>
                    {bank.specialty && (
                      <BrutalBadge variant="default" size="sm">
                        {bank.specialty}
                      </BrutalBadge>
                    )}
                  </div>

                  <p className="text-sm font-medium text-gray-700 line-clamp-2">
                    {bank.description}
                  </p>
                </div>

                {/* Stats */}
                <div className="border-t-4 border-black pt-3 mb-4">
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div>
                      <p className="text-xs font-bold uppercase text-gray-600">Words</p>
                      <p className="text-lg font-black">{bank.total_tokens}</p>
                    </div>
                    <div>
                      <p className="text-xs font-bold uppercase text-gray-600">Rating</p>
                      <p className="text-lg font-black">⭐ {bank.rating}</p>
                    </div>
                    <div>
                      <p className="text-xs font-bold uppercase text-gray-600">Users</p>
                      <p className="text-lg font-black">{bank.purchase_count}</p>
                    </div>
                  </div>
                </div>

                {/* Price */}
                <div className="mb-4">
                  <div className={`text-center py-2 border-4 border-black ${isFree ? 'bg-emerald-100' : 'bg-amber-100'}`}>
                    <p className="text-2xl font-black" style={{ color: isFree ? '#064e3b' : '#78350f' }}>{formatPrice(bank.price)}</p>
                  </div>
                </div>

                {/* Actions */}
                <div className="space-y-2 mt-auto">
                  <BrutalButton
                    variant="indigo"
                    size="sm"
                    fullWidth
                    onClick={() => setPreviewBank(bank)}
                    className="flex items-center justify-center gap-2"
                  >
                    <Eye size={18} />
                    Preview
                  </BrutalButton>

                  {isOwned ? (
                    <BrutalButton
                      variant="emerald"
                      size="sm"
                      fullWidth
                      disabled
                      className="flex items-center justify-center gap-2"
                    >
                      <Check size={18} />
                      In Your Library
                    </BrutalButton>
                  ) : (
                    <BrutalButton
                      variant={isFree ? 'emerald' : 'amber'}
                      size="sm"
                      fullWidth
                      onClick={() => handlePurchase(bank)}
                      disabled={purchaseMutation.isPending}
                      className="flex items-center justify-center gap-2"
                    >
                      <ShoppingCart size={18} />
                      {isFree ? 'Add to Library' : `Buy for ${formatPrice(bank.price)}`}
                    </BrutalButton>
                  )}
                </div>
              </BrutalCard>
            );
          })}
        </div>
      )}

      {/* Preview Dialog */}
      {previewBank && (
        <WordBankPreviewDialog
          bank={previewBank}
          isOpen={!!previewBank}
          onClose={() => setPreviewBank(null)}
          isOwned={ownedBankIds.includes(previewBank.id)}
          onPurchase={() => {
            handlePurchase(previewBank);
            setPreviewBank(null);
          }}
        />
      )}
    </div>
  );
};

export default MarketplaceTab;
