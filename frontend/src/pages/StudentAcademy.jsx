import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { BrutalCard } from '@/components/brutal';

const StudentAcademy = () => {
  const { student } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-yellow-50 p-8">
      <BrutalCard shadow="xl" className="max-w-4xl mx-auto bg-white">
        <h1 className="text-4xl font-black uppercase mb-4">Student Academy</h1>
        <p className="text-xl font-medium mb-8">
          Welcome, {student?.full_name}!
        </p>

        <div className="bg-emerald-100 border-4 border-black p-6">
          <h2 className="text-2xl font-black uppercase mb-4">🚧 Coming Soon</h2>
          <ul className="space-y-2 font-medium text-lg">
            <li>• Dashboard with Progress</li>
            <li>• Story Generation</li>
            <li>• Chapter Reading</li>
            <li>• Vocabulary Assessments</li>
          </ul>
        </div>
      </BrutalCard>
    </div>
  );
};

export default StudentAcademy;
