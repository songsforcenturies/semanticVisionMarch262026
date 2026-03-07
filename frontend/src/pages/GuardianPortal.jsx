import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalCard } from '@/components/brutal';

const GuardianPortal = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <BrutalCard shadow="xl" className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-black uppercase mb-4">Guardian Portal</h1>
        <p className="text-xl font-medium mb-8">
          Welcome, {user?.full_name}!
        </p>

        <div className="bg-amber-100 border-4 border-black p-6">
          <h2 className="text-2xl font-black uppercase mb-4">🚧 Coming in Phase 2</h2>
          <ul className="space-y-2 font-medium text-lg">
            <li>• Student Management</li>
            <li>• Word Bank Marketplace</li>
            <li>• Progress Analytics</li>
            <li>• Subscription Management</li>
          </ul>
        </div>
      </BrutalCard>
    </div>
  );
};

export default GuardianPortal;
