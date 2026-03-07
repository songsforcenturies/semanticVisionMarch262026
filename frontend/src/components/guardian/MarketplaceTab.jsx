import React from 'react';
import { BrutalCard } from '@/components/brutal';
import { ShoppingBag } from 'lucide-react';

const MarketplaceTab = () => {
  return (
    <div className="space-y-6">
      <BrutalCard shadow="xl" variant="emerald" className="text-center py-16">
        <ShoppingBag size={64} className="mx-auto mb-6 text-emerald-600" />
        <h2 className="text-4xl font-black uppercase mb-4">Word Bank Marketplace</h2>
        <p className="text-xl font-bold mb-8">Coming in Phase 3!</p>
        
        <div className="max-w-2xl mx-auto text-left">
          <div className="bg-white border-4 border-black p-6 brutal-shadow-md">
            <h3 className="text-2xl font-black uppercase mb-4">Features Coming Soon:</h3>
            <ul className="space-y-2 text-lg font-medium">
              <li>✅ Browse specialized word banks (Aviation, Medicine, Law, etc.)</li>
              <li>✅ Search and filter by category</li>
              <li>✅ Purchase word banks for your students</li>
              <li>✅ Gift word banks to other guardians</li>
              <li>✅ Preview word bank contents before buying</li>
              <li>✅ View purchased word banks</li>
            </ul>
          </div>
        </div>
      </BrutalCard>
    </div>
  );
};

export default MarketplaceTab;
