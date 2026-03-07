import React from 'react';
import { BrutalCard } from '@/components/brutal';
import { TrendingUp } from 'lucide-react';

const ProgressTab = () => {
  return (
    <div className="space-y-6">
      <BrutalCard shadow="xl" variant="amber" className="text-center py-16">
        <TrendingUp size={64} className="mx-auto mb-6 text-amber-600" />
        <h2 className="text-4xl font-black uppercase mb-4">Student Progress Analytics</h2>
        <p className="text-xl font-bold mb-8">Coming in Phase 6!</p>
        
        <div className="max-w-2xl mx-auto text-left">
          <div className="bg-white border-4 border-black p-6 brutal-shadow-md">
            <h3 className="text-2xl font-black uppercase mb-4">Features Coming Soon:</h3>
            <ul className="space-y-2 text-lg font-medium">
              <li>✅ Select student to view detailed analytics</li>
              <li>✅ Vocabulary mastery visualization (word clouds)</li>
              <li>✅ Reading statistics (time, words, WPM)</li>
              <li>✅ Assessment results and accuracy</li>
              <li>✅ Agentic Reach Score breakdown</li>
              <li>✅ Biological vocabulary targets</li>
              <li>✅ Story-specific vocabulary breakdown</li>
              <li>✅ Export student data (JSON format)</li>
              <li>✅ View misspelled words per assessment</li>
            </ul>
          </div>
        </div>
      </BrutalCard>
    </div>
  );
};

export default ProgressTab;
