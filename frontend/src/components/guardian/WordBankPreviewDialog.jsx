import React from 'react';
import { BrutalButton, BrutalCard, BrutalBadge } from '@/components/brutal';
import { X, BookOpen, Check } from 'lucide-react';

const WordBankPreviewDialog = ({ bank, isOpen, onClose, isOwned, onPurchase }) => {
  if (!isOpen || !bank) return null;

  const formatPrice = (priceInCents) => {
    if (priceInCents === 0) return 'FREE';
    return `$${(priceInCents / 100).toFixed(2)}`;
  };

  const getTierColor = (tier) => {
    const colors = {
      baseline: 'baseline',
      target: 'target',
      stretch: 'stretch'
    };
    return colors[tier] || 'default';
  };

  const renderWordList = (words, tier, tierName) => {
    if (!words || words.length === 0) return null;

    // Show first 5 words as preview
    const previewWords = words.slice(0, 5);
    const hasMore = words.length > 5;

    return (
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <BrutalBadge variant={getTierColor(tier)} size="lg">
            {tierName}
          </BrutalBadge>
          <span className="font-bold text-lg">({words.length} words)</span>
        </div>
        
        <div className="space-y-3">
          {previewWords.map((word, idx) => (
            <div key={idx} className="bg-gray-50 border-4 border-black p-4">
              <div className="flex items-start justify-between mb-2">
                <p className="text-xl font-black uppercase">{word.word}</p>
                <BrutalBadge size="sm">{word.part_of_speech}</BrutalBadge>
              </div>
              <p className="font-medium mb-2">{word.definition}</p>
              <p className="text-sm italic text-gray-600">"{word.example_sentence}"</p>
            </div>
          ))}
          
          {hasMore && (
            <p className="text-center font-bold text-gray-600">
              + {words.length - 5} more {tierName.toLowerCase()} words...
            </p>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 overflow-y-auto">
      <div className="w-full max-w-4xl my-8">
        <BrutalCard shadow="xl" className="bg-white max-h-[85vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-start justify-between mb-6 sticky top-0 bg-white pb-4 border-b-4 border-black">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <BookOpen size={32} className="text-indigo-600" />
                <h2 className="text-3xl font-black uppercase">{bank.name}</h2>
              </div>
              <p className="text-lg font-medium text-gray-700">{bank.description}</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 border-4 border-black brutal-active ml-4"
            >
              <X size={24} />
            </button>
          </div>

          {/* Info Grid */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <BrutalCard variant="indigo" className="text-center">
              <p className="text-xs font-bold uppercase mb-1">Category</p>
              <p className="text-lg font-black capitalize">{bank.category}</p>
            </BrutalCard>
            
            {bank.specialty && (
              <BrutalCard variant="emerald" className="text-center">
                <p className="text-xs font-bold uppercase mb-1">Specialty</p>
                <p className="text-lg font-black">{bank.specialty}</p>
              </BrutalCard>
            )}
            
            <BrutalCard variant="amber" className="text-center">
              <p className="text-xs font-bold uppercase mb-1">Total Words</p>
              <p className="text-lg font-black">{bank.total_tokens}</p>
            </BrutalCard>
            
            <BrutalCard variant="rose" className="text-center">
              <p className="text-xs font-bold uppercase mb-1">Price</p>
              <p className="text-lg font-black">{formatPrice(bank.price)}</p>
            </BrutalCard>
          </div>

          {/* Grade Range */}
          {bank.grade_range && (
            <BrutalCard className="mb-6 bg-blue-50">
              <p className="font-bold uppercase text-sm mb-1">Recommended Grade Range</p>
              <p className="text-xl font-black">
                {bank.grade_range.min} - {bank.grade_range.max}
              </p>
            </BrutalCard>
          )}

          {/* Vocabulary Tiers */}
          <div className="mb-6">
            <h3 className="text-2xl font-black uppercase mb-4">Vocabulary Preview</h3>
            
            {renderWordList(bank.baseline_words, 'baseline', 'BASELINE')}
            {renderWordList(bank.target_words, 'target', 'TARGET')}
            {renderWordList(bank.stretch_words, 'stretch', 'STRETCH')}
          </div>

          {/* Stats */}
          <BrutalCard className="mb-6 bg-gray-50">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs font-bold uppercase text-gray-600">Rating</p>
                <p className="text-2xl font-black">⭐ {bank.rating}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase text-gray-600">Purchases</p>
                <p className="text-2xl font-black">{bank.purchase_count}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase text-gray-600">Visibility</p>
                <p className="text-xl font-black capitalize">{bank.visibility}</p>
              </div>
            </div>
          </BrutalCard>

          {/* Actions */}
          <div className="flex gap-4">
            {isOwned ? (
              <BrutalButton
                variant="emerald"
                size="lg"
                fullWidth
                disabled
                className="flex items-center justify-center gap-2"
              >
                <Check size={24} />
                Already in Your Library
              </BrutalButton>
            ) : (
              <BrutalButton
                variant={bank.price === 0 ? 'emerald' : 'amber'}
                size="lg"
                fullWidth
                onClick={onPurchase}
                className="flex items-center justify-center gap-2"
              >
                {bank.price === 0 ? 'Add to Library (Free)' : `Purchase for ${formatPrice(bank.price)}`}
              </BrutalButton>
            )}
            
            <BrutalButton
              variant="ghost"
              size="lg"
              onClick={onClose}
            >
              Close
            </BrutalButton>
          </div>
        </BrutalCard>
      </div>
    </div>
  );
};

export default WordBankPreviewDialog;
