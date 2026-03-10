import React, { useState, useEffect } from 'react';
import { getOfflineStories, removeOfflineStory, getOfflineStorageInfo, isOnline } from '@/lib/offlineCache';
import { WifiOff, Wifi, Trash2, BookOpen, HardDrive, Play } from 'lucide-react';
import { toast } from 'sonner';

const C = {
  bg: '#0A0F1E', card: '#1A2236', surface: '#111827',
  gold: '#D4A853', teal: '#38BDF8', cream: '#F8F5EE', muted: '#94A3B8',
};

const OfflineLibrary = ({ studentId, onReadStory }) => {
  const [stories, setStories] = useState([]);
  const [storageInfo, setStorageInfo] = useState(null);
  const [online, setOnline] = useState(true);

  const loadData = async () => {
    const s = await getOfflineStories(studentId || null);
    setStories(s);
    const info = await getOfflineStorageInfo();
    setStorageInfo(info);
    setOnline(isOnline());
  };

  useEffect(() => {
    loadData();
    const onlineHandler = () => setOnline(true);
    const offlineHandler = () => setOnline(false);
    window.addEventListener('online', onlineHandler);
    window.addEventListener('offline', offlineHandler);
    return () => {
      window.removeEventListener('online', onlineHandler);
      window.removeEventListener('offline', offlineHandler);
    };
  }, [studentId]);

  const handleRemove = async (id) => {
    await removeOfflineStory(id);
    toast.success('Removed from offline library');
    loadData();
  };

  return (
    <div className="space-y-4" data-testid="offline-library">
      {/* Status bar */}
      <div className="flex items-center justify-between p-3 rounded-xl"
        style={{
          background: online ? 'rgba(52,211,153,0.08)' : 'rgba(245,158,11,0.08)',
          border: online ? '1px solid rgba(52,211,153,0.25)' : '1px solid rgba(245,158,11,0.25)',
        }}>
        <div className="flex items-center gap-2">
          {online ? <Wifi size={18} style={{ color: '#34D399' }} /> : <WifiOff size={18} style={{ color: '#FBBF24' }} />}
          <span className="text-sm font-bold" style={{ color: online ? '#34D399' : '#FBBF24' }}>
            {online ? 'Online' : 'Offline Mode'}
          </span>
        </div>
        {storageInfo && (
          <div className="flex items-center gap-1.5 text-xs font-medium" style={{ color: C.muted }}>
            <HardDrive size={14} />
            {storageInfo.count} stories ({storageInfo.sizeMB} MB)
          </div>
        )}
      </div>

      {/* Stories */}
      {stories.length === 0 ? (
        <div className="text-center py-12 rounded-2xl" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }}>
          <WifiOff size={40} className="mx-auto mb-3" style={{ color: C.muted }} />
          <h3 className="text-lg font-bold mb-1" style={{ color: C.cream }}>No Offline Stories</h3>
          <p className="text-sm font-medium" style={{ color: C.muted }}>Save stories while online to read them anytime.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {stories.map(story => (
            <div key={story.id} className="p-4 rounded-xl" data-testid={`offline-story-${story.id}`}
              style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }}>
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ background: 'rgba(99,102,241,0.12)' }}>
                    <BookOpen size={18} style={{ color: '#818CF8' }} />
                  </div>
                  <div className="min-w-0">
                    <p className="font-bold text-sm truncate" style={{ color: C.cream }}>{story.title}</p>
                    <p className="text-xs" style={{ color: C.muted }}>
                      {story.chapters?.length || 0} chapters &middot; Saved {new Date(story.saved_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  {onReadStory && (
                    <button onClick={() => onReadStory(story)}
                      className="p-2 rounded-lg transition-all hover:scale-105"
                      style={{ background: 'rgba(99,102,241,0.12)', color: '#818CF8' }}
                      data-testid={`read-offline-${story.id}`}>
                      <Play size={16} />
                    </button>
                  )}
                  <button onClick={() => handleRemove(story.id)}
                    className="p-2 rounded-lg transition-all hover:scale-105"
                    style={{ background: 'rgba(239,68,68,0.12)', color: '#EF4444' }}
                    data-testid={`remove-offline-${story.id}`}>
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default OfflineLibrary;
