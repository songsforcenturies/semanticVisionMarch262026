import React from 'react';
import { BrutalButton, BrutalCard } from '@/components/brutal';
import { AlertTriangle } from 'lucide-react';

const DeleteConfirmDialog = ({ isOpen, onClose, onConfirm, title, message, isLoading }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <BrutalCard shadow="xl" variant="rose" className="w-full max-w-md">
        <div className="text-center mb-6">
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-rose-100 border-4 border-black brutal-shadow-md">
              <AlertTriangle size={48} className="text-rose-600" />
            </div>
          </div>
          <h2 className="text-2xl font-black uppercase mb-2">{title}</h2>
          <p className="text-lg font-medium">{message}</p>
        </div>

        <div className="flex gap-4">
          <BrutalButton
            variant="rose"
            fullWidth
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? 'Deleting...' : 'Delete'}
          </BrutalButton>
          <BrutalButton
            variant="default"
            fullWidth
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </BrutalButton>
        </div>
      </BrutalCard>
    </div>
  );
};

export default DeleteConfirmDialog;
