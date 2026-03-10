import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { audioBooksAPI } from '@/lib/api';
import { BrutalCard, BrutalBadge } from '@/components/brutal';
import { Headphones, Check, X, Trash2, Eye, EyeOff, Settings } from 'lucide-react';
import { toast } from 'sonner';

const AdminAudioBooksTab = () => {
  const queryClient = useQueryClient();
  const [showSettings, setShowSettings] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['admin-audio-books'],
    queryFn: async () => (await audioBooksAPI.adminGetAll()).data,
  });

  const { data: settings } = useQuery({
    queryKey: ['audio-book-settings'],
    queryFn: async () => (await audioBooksAPI.adminGetSettings()).data,
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }) => audioBooksAPI.adminUpdate(id, data),
    onSuccess: () => { queryClient.invalidateQueries(['admin-audio-books']); toast.success('Updated'); },
  });

  const deleteMut = useMutation({
    mutationFn: (id) => audioBooksAPI.adminDelete(id),
    onSuccess: () => { queryClient.invalidateQueries(['admin-audio-books']); toast.success('Deleted'); },
  });

  const settingsMut = useMutation({
    mutationFn: (data) => audioBooksAPI.adminUpdateSettings(data),
    onSuccess: () => { queryClient.invalidateQueries(['audio-book-settings']); toast.success('Settings saved'); },
  });

  const books = data?.audio_books || [];
  const pending = books.filter(b => b.status === 'pending');
  const approved = books.filter(b => b.status === 'approved');

  return (
    <div className="space-y-6" data-testid="admin-audio-books">
      {/* Header */}
      <BrutalCard shadow="xl" className="bg-gradient-to-r from-amber-50 to-orange-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Headphones size={28} className="text-amber-600" />
            <div>
              <h2 className="text-2xl font-black uppercase">Audio Book Collection</h2>
              <p className="text-sm text-gray-600 font-medium">{pending.length} pending review &middot; {approved.length} published</p>
            </div>
          </div>
          <button onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded-lg bg-white border-2 border-gray-200 hover:border-amber-400 transition-all"
            data-testid="audio-settings-btn">
            <Settings size={18} />
          </button>
        </div>
      </BrutalCard>

      {/* Settings */}
      {showSettings && (
        <BrutalCard shadow="lg" data-testid="audio-settings-panel">
          <h3 className="font-black uppercase mb-3">Collection Settings</h3>
          <div className="space-y-3">
            <label className="flex items-center gap-3">
              <input type="checkbox" checked={settings?.enabled ?? true}
                onChange={(e) => settingsMut.mutate({ ...settings, enabled: e.target.checked })}
                className="w-4 h-4 rounded" />
              <span className="font-bold text-sm">Enable Audio Book Collection</span>
            </label>
            <label className="flex items-center gap-3">
              <input type="checkbox" checked={settings?.auto_approve ?? false}
                onChange={(e) => settingsMut.mutate({ ...settings, auto_approve: e.target.checked })}
                className="w-4 h-4 rounded" />
              <span className="font-bold text-sm">Auto-approve submissions</span>
            </label>
            <label className="flex items-center gap-3">
              <input type="checkbox" checked={settings?.show_on_landing ?? true}
                onChange={(e) => settingsMut.mutate({ ...settings, show_on_landing: e.target.checked })}
                className="w-4 h-4 rounded" />
              <span className="font-bold text-sm">Show on Landing Page</span>
            </label>
          </div>
        </BrutalCard>
      )}

      {/* Pending */}
      {pending.length > 0 && (
        <div>
          <h3 className="font-black uppercase text-amber-600 mb-3">Pending Review ({pending.length})</h3>
          <div className="space-y-2">
            {pending.map(book => (
              <BrutalCard key={book.id} shadow="sm" className="bg-amber-50" data-testid={`pending-${book.id}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-bold text-sm">{book.narrative_title}</p>
                    <p className="text-xs text-gray-500">by {book.student_name}, age {book.student_age} &middot; {new Date(book.created_date).toLocaleDateString()}</p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => updateMut.mutate({ id: book.id, data: { status: 'approved', is_visible: true } })}
                      className="p-2 bg-emerald-100 text-emerald-700 rounded-lg hover:bg-emerald-200" data-testid={`approve-${book.id}`}>
                      <Check size={16} />
                    </button>
                    <button onClick={() => updateMut.mutate({ id: book.id, data: { status: 'rejected', is_visible: false } })}
                      className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200" data-testid={`reject-${book.id}`}>
                      <X size={16} />
                    </button>
                  </div>
                </div>
              </BrutalCard>
            ))}
          </div>
        </div>
      )}

      {/* Published */}
      <div>
        <h3 className="font-black uppercase text-emerald-600 mb-3">Published ({approved.length})</h3>
        {approved.length === 0 ? (
          <p className="text-gray-500 text-sm font-medium">No published audio books yet.</p>
        ) : (
          <div className="space-y-2">
            {approved.map(book => (
              <BrutalCard key={book.id} shadow="sm" data-testid={`published-${book.id}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-bold text-sm">{book.narrative_title}</p>
                    <p className="text-xs text-gray-500">
                      {book.student_name}, age {book.student_age} &middot; {book.listens} listens &middot; {book.likes} likes
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => updateMut.mutate({ id: book.id, data: { is_visible: !book.is_visible } })}
                      className={`p-2 rounded-lg ${book.is_visible ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'}`}
                      data-testid={`toggle-vis-${book.id}`}>
                      {book.is_visible ? <Eye size={16} /> : <EyeOff size={16} />}
                    </button>
                    <button onClick={() => { if (window.confirm('Delete this audio book?')) deleteMut.mutate(book.id); }}
                      className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200" data-testid={`delete-${book.id}`}>
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </BrutalCard>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminAudioBooksTab;
