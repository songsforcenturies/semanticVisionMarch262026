import React, { useState, useEffect } from 'react';
import { saveStoryOffline, isStorySaved, removeOfflineStory } from '@/lib/offlineCache';
import { Download, Check, WifiOff } from 'lucide-react';
import { toast } from 'sonner';

const SaveOfflineButton = ({ narrative, compact = false }) => {
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (narrative?.id) {
      isStorySaved(narrative.id).then(setSaved);
    }
  }, [narrative?.id]);

  const handleSave = async () => {
    if (saved) {
      await removeOfflineStory(narrative.id);
      setSaved(false);
      toast.success('Removed from offline library');
      return;
    }
    setSaving(true);
    try {
      await saveStoryOffline(narrative);
      setSaved(true);
      toast.success('Saved for offline reading!');
    } catch (err) {
      toast.error('Could not save story offline');
    } finally {
      setSaving(false);
    }
  };

  if (compact) {
    return (
      <button onClick={handleSave} disabled={saving}
        className="p-2 rounded-lg transition-all"
        style={{
          background: saved ? 'rgba(52,211,153,0.15)' : 'rgba(255,255,255,0.04)',
          color: saved ? '#34D399' : '#94A3B8',
          border: saved ? '1px solid rgba(52,211,153,0.3)' : '1px solid rgba(255,255,255,0.1)',
        }}
        title={saved ? 'Remove from offline' : 'Save for offline'}
        data-testid="save-offline-btn">
        {saved ? <Check size={16} /> : saving ? <Download size={16} className="animate-bounce" /> : <Download size={16} />}
      </button>
    );
  }

  return (
    <button onClick={handleSave} disabled={saving}
      className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all"
      style={{
        background: saved ? 'rgba(52,211,153,0.12)' : 'rgba(255,255,255,0.04)',
        color: saved ? '#34D399' : '#94A3B8',
        border: saved ? '1px solid rgba(52,211,153,0.3)' : '1px solid rgba(255,255,255,0.1)',
      }}
      data-testid="save-offline-btn">
      {saved ? <><Check size={14} /> Saved Offline</> :
       saving ? <><Download size={14} className="animate-bounce" /> Saving...</> :
       <><WifiOff size={14} /> Save Offline</>}
    </button>
  );
};

export default SaveOfflineButton;
