import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { wordBankAPI, subscriptionAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalBadge, BrutalInput } from '@/components/brutal';
import { Search, Gift, Eye, Check, ShoppingCart } from 'lucide-react';
import { toast } from 'sonner';
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

  // Purchase mutation
  const purchaseMutation = useMutation({
    mutationFn: (bankId) => wordBankAPI.purchase(user?.id, bankId),
    onSuccess: (_, bankId) => {
      queryClient.invalidateQueries(['subscription']);
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
      // For paid banks, show confirmation
      if (window.confirm(`Purchase ${bank.name} for $${(bank.price / 100).toFixed(2)}?`)) {
        purchaseMutation.mutate(bank.id);
      }
    }
  };

  const formatPrice = (priceInCents) => {
    if (priceInCents === 0) return 'FREE';
    return `$${(priceInCents / 100).toFixed(2)}`;
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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-black uppercase">Word Bank Marketplace</h2>
          <p className="text-lg font-medium mt-1">
            {ownedBankIds.length} banks in your library
          </p>
        </div>
      </div>

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
                    <p className="text-2xl font-black">{formatPrice(bank.price)}</p>
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
