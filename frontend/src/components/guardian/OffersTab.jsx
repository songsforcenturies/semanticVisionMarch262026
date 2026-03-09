import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { parentOffersAPI } from '@/lib/api';
import { Gift, ExternalLink, Tag, ToggleLeft, ToggleRight, X } from 'lucide-react';
import { toast } from 'sonner';

const OffersTab = () => {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['parent-offers'],
    queryFn: async () => (await parentOffersAPI.getAvailable()).data,
  });

  const toggleMutation = useMutation({
    mutationFn: (enabled) => parentOffersAPI.updatePreferences({ offers_enabled: enabled }),
    onSuccess: () => { queryClient.invalidateQueries(['parent-offers']); toast.success('Preferences updated'); },
  });

  const clickMutation = useMutation({
    mutationFn: (id) => parentOffersAPI.trackClick(id),
  });

  const dismissMutation = useMutation({
    mutationFn: (id) => parentOffersAPI.updatePreferences({ dismiss_offer_id: id }),
    onSuccess: () => queryClient.invalidateQueries(['parent-offers']),
  });

  const offersEnabled = data?.offers_enabled !== false;
  const offers = data?.offers || [];
  const freeOffers = offers.filter(o => o.offer_type === 'free');
  const paidOffers = offers.filter(o => o.offer_type === 'paid');

  const card = { background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '16px', padding: '20px' };

  if (isLoading) return <div className="text-center py-12" style={{ color: '#94A3B8' }}>Loading offers...</div>;

  return (
    <div className="space-y-6" data-testid="offers-tab">
      {/* Header with toggle */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold" style={{ color: '#F8F5EE' }}>Brand Offers</h2>
          <p className="text-sm" style={{ color: '#94A3B8' }}>Special offers from brands featured in your child's stories</p>
        </div>
        <button
          onClick={() => toggleMutation.mutate(!offersEnabled)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all"
          style={{ color: offersEnabled ? '#10B981' : '#EF4444', border: `1px solid ${offersEnabled ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`, background: offersEnabled ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)' }}
          data-testid="toggle-offers"
        >
          {offersEnabled ? <ToggleRight size={18} /> : <ToggleLeft size={18} />}
          {offersEnabled ? 'Offers On' : 'Offers Off'}
        </button>
      </div>

      {!offersEnabled ? (
        <div style={card} className="text-center py-12">
          <Gift size={40} className="mx-auto mb-3" style={{ color: '#64748B' }} />
          <p className="font-semibold" style={{ color: '#94A3B8' }}>Offers are turned off</p>
          <p className="text-sm mt-1" style={{ color: '#64748B' }}>Turn on offers to see special deals from educational brands.</p>
        </div>
      ) : offers.length === 0 ? (
        <div style={card} className="text-center py-12">
          <Gift size={40} className="mx-auto mb-3" style={{ color: '#D4A853' }} />
          <p className="font-semibold" style={{ color: '#F8F5EE' }}>No offers available right now</p>
          <p className="text-sm mt-1" style={{ color: '#94A3B8' }}>Check back later for deals from brands in your child's stories.</p>
        </div>
      ) : (
        <>
          {/* Free Offers */}
          {freeOffers.length > 0 && (
            <div>
              <h3 className="text-sm font-bold uppercase mb-3" style={{ color: '#10B981' }}>Free Offers</h3>
              <div className="grid gap-3">
                {freeOffers.map(offer => (
                  <OfferCard key={offer.id} offer={offer} onDismiss={() => dismissMutation.mutate(offer.id)} onClick={() => clickMutation.mutate(offer.id)} />
                ))}
              </div>
            </div>
          )}

          {/* Paid Offers */}
          {paidOffers.length > 0 && (
            <div>
              <h3 className="text-sm font-bold uppercase mb-3" style={{ color: '#D4A853' }}>Premium Offers</h3>
              <div className="grid gap-3">
                {paidOffers.map(offer => (
                  <OfferCard key={offer.id} offer={offer} onDismiss={() => dismissMutation.mutate(offer.id)} onClick={() => clickMutation.mutate(offer.id)} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

const OfferCard = ({ offer, onDismiss, onClick }) => {
  const handleClick = () => {
    onClick();
    if (offer.external_link) {
      window.open(offer.external_link, '_blank');
    }
  };

  return (
    <div className="rounded-xl p-4 transition-all hover:scale-[1.005]"
      style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}
      data-testid={`offer-${offer.id}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-bold px-2 py-0.5 rounded" style={{
              color: offer.offer_type === 'free' ? '#10B981' : '#D4A853',
              background: offer.offer_type === 'free' ? 'rgba(16,185,129,0.1)' : 'rgba(212,168,83,0.1)'
            }}>
              {offer.offer_type === 'free' ? 'FREE' : `$${offer.price}`}
            </span>
            <span className="text-xs font-semibold" style={{ color: '#64748B' }}>from {offer.brand_name}</span>
          </div>
          <h4 className="text-base font-bold" style={{ color: '#F8F5EE' }}>{offer.title}</h4>
          <p className="text-sm mt-1" style={{ color: '#94A3B8' }}>{offer.description}</p>
          {offer.internal_promo_code && (
            <div className="mt-2 flex items-center gap-2">
              <Tag size={14} style={{ color: '#D4A853' }} />
              <span className="text-sm font-mono font-bold" style={{ color: '#D4A853' }}>Code: {offer.internal_promo_code}</span>
            </div>
          )}
        </div>
        <div className="flex flex-col gap-2 flex-shrink-0">
          {(offer.external_link || offer.internal_promo_code) && (
            <button onClick={handleClick}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold text-black"
              style={{ background: '#D4A853' }} data-testid={`claim-offer-${offer.id}`}
            >
              {offer.external_link ? <><ExternalLink size={14} /> Visit</> : 'Use Code'}
            </button>
          )}
          <button onClick={onDismiss} className="p-1.5 rounded-lg hover:bg-white/5 self-end" title="Dismiss">
            <X size={14} style={{ color: '#64748B' }} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default OffersTab;
