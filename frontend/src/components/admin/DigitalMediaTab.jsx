import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalInput, BrutalBadge } from '@/components/brutal';
import { Music, Video, Upload, Trash2, Play, Settings, DollarSign, Youtube, HardDrive, Save, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const DigitalMediaTab = () => {
  const qc = useQueryClient();
  const [showUpload, setShowUpload] = useState(false);
  const [showYoutube, setShowYoutube] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadForm, setUploadForm] = useState({ title: '', artist: '', brand_id: '' });
  const [ytForm, setYtForm] = useState({ title: '', artist: '', youtube_url: '', brand_id: '', price_per_stream: 0, price_per_download: 0.99 });
  const [localSettings, setLocalSettings] = useState(null);
  const [settingsDirty, setSettingsDirty] = useState(false);

  const { data: settings = {} } = useQuery({
    queryKey: ['media-settings'],
    queryFn: async () => (await adminAPI.getMediaSettings()).data,
  });

  // Sync server settings to local state
  useEffect(() => {
    if (settings && !localSettings) {
      setLocalSettings({ ...settings });
    }
  }, [settings, localSettings]);

  const { data: media = [] } = useQuery({
    queryKey: ['brand-media'],
    queryFn: async () => (await adminAPI.listBrandMedia()).data,
  });

  const { data: brands = [] } = useQuery({
    queryKey: ['admin-brands'],
    queryFn: async () => (await adminAPI.getBrands()).data,
  });

  const { data: storageStats = {} } = useQuery({
    queryKey: ['storage-stats'],
    queryFn: async () => (await adminAPI.getStorageStats()).data,
  });

  const settingsMut = useMutation({
    mutationFn: (data) => adminAPI.updateMediaSettings(data),
    onSuccess: () => {
      qc.invalidateQueries(['media-settings']);
      setSettingsDirty(false);
      toast.success('Settings saved');
    },
  });

  const uploadMut = useMutation({
    mutationFn: async (formData) => (await adminAPI.uploadBrandMedia(formData)).data,
    onSuccess: () => {
      qc.invalidateQueries(['brand-media']);
      qc.invalidateQueries(['storage-stats']);
      toast.success('Media uploaded successfully');
      setShowUpload(false);
      setUploadFile(null);
      setUploadForm({ title: '', artist: '', brand_id: '' });
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Upload failed'),
  });

  const createYtMut = useMutation({
    mutationFn: (data) => adminAPI.createBrandMedia(data),
    onSuccess: () => {
      qc.invalidateQueries(['brand-media']);
      toast.success('YouTube video added');
      setShowYoutube(false);
      setYtForm({ title: '', artist: '', youtube_url: '', brand_id: '', price_per_stream: 0, price_per_download: 0.99 });
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to add'),
  });

  const deleteMut = useMutation({
    mutationFn: (id) => adminAPI.deleteBrandMedia(id),
    onSuccess: () => {
      qc.invalidateQueries(['brand-media']);
      qc.invalidateQueries(['storage-stats']);
      toast.success('Deleted');
    },
  });

  const handleUpload = (e) => {
    e.preventDefault();
    if (!uploadFile) return toast.error('Select a file');
    if (!uploadForm.title) return toast.error('Title required');
    const fd = new FormData();
    fd.append('file', uploadFile);
    fd.append('title', uploadForm.title);
    fd.append('artist', uploadForm.artist);
    fd.append('brand_id', uploadForm.brand_id);
    uploadMut.mutate(fd);
  };

  const handleAddYoutube = (e) => {
    e.preventDefault();
    createYtMut.mutate(ytForm);
  };

  const updateLocalSetting = (key, value) => {
    setLocalSettings(prev => ({ ...prev, [key]: value }));
    setSettingsDirty(true);
  };

  const handleSaveSettings = () => {
    settingsMut.mutate(localSettings);
  };

  const brandName = (id) => brands.find(b => b.id === id)?.name || '';

  const s = localSettings || settings;

  return (
    <div className="space-y-6" data-testid="digital-media-tab">
      {/* How It Works Banner */}
      <BrutalCard shadow="lg" className="border-indigo-500">
        <h3 className="text-lg font-black uppercase flex items-center gap-2 mb-2">
          <Music size={20} className="text-indigo-500" /> How Media Works in Stories
        </h3>
        <p className="text-sm font-medium text-gray-600">
          Media you add here (audio, video, YouTube) is automatically available for AI story generation.
          When a story is created, the AI can embed your approved media directly into the narrative.
          Students hear/see the media as they read. Parents can opt-out per student in their Media Settings.
        </p>
      </BrutalCard>

      {/* Settings Card */}
      <BrutalCard shadow="lg" data-testid="media-settings-card">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-black uppercase flex items-center gap-2">
            <Settings size={20} className="text-gray-500" /> Media &amp; Storage Settings
          </h3>
          <BrutalButton
            variant={settingsDirty ? "emerald" : "default"}
            size="sm"
            onClick={handleSaveSettings}
            disabled={!settingsDirty || settingsMut.isPending}
            data-testid="save-settings-btn"
          >
            <Save size={14} className="mr-1" />
            {settingsMut.isPending ? 'Saving...' : settingsDirty ? 'Save Changes' : 'Saved'}
          </BrutalButton>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block font-bold text-sm uppercase mb-1">Default Price per Stream ($)</label>
            <input type="number" step="0.01" min="0"
              value={s.default_price_per_stream ?? 0.01}
              onChange={(e) => updateLocalSetting('default_price_per_stream', parseFloat(e.target.value) || 0)}
              className="w-full px-4 py-2 border-4 border-black font-bold bg-white text-gray-900"
              data-testid="price-per-stream" />
          </div>
          <div>
            <label className="block font-bold text-sm uppercase mb-1">Default Price per Download ($)</label>
            <input type="number" step="0.01" min="0"
              value={s.default_price_per_download ?? 0.99}
              onChange={(e) => updateLocalSetting('default_price_per_download', parseFloat(e.target.value) || 0)}
              className="w-full px-4 py-2 border-4 border-black font-bold bg-white text-gray-900"
              data-testid="price-per-download" />
          </div>
        </div>
        <div className="grid md:grid-cols-3 gap-4 mt-4">
          <div>
            <label className="block font-bold text-sm uppercase mb-1">Max Storage per User (MB)</label>
            <input type="number" min="0"
              value={s.max_storage_per_user_mb ?? 500}
              onChange={(e) => updateLocalSetting('max_storage_per_user_mb', parseInt(e.target.value) || 0)}
              className="w-full px-4 py-2 border-4 border-black font-bold bg-white text-gray-900" />
          </div>
          <div>
            <label className="block font-bold text-sm uppercase mb-1">Max Recording Duration (sec)</label>
            <input type="number" min="0"
              value={s.max_recording_duration_sec ?? 600}
              onChange={(e) => updateLocalSetting('max_recording_duration_sec', parseInt(e.target.value) || 0)}
              className="w-full px-4 py-2 border-4 border-black font-bold bg-white text-gray-900" />
          </div>
          <div>
            <label className="block font-bold text-sm uppercase mb-1">Auto-Delete After (days)</label>
            <input type="number" min="0"
              value={s.auto_delete_recordings_days ?? 0}
              onChange={(e) => updateLocalSetting('auto_delete_recordings_days', parseInt(e.target.value) || 0)}
              className="w-full px-4 py-2 border-4 border-black font-bold bg-white text-gray-900" />
            <p className="text-xs text-gray-400 mt-1">0 = never delete</p>
          </div>
        </div>
        {settingsDirty && (
          <p className="text-sm font-bold text-amber-600 mt-3">You have unsaved changes</p>
        )}
      </BrutalCard>

      {/* Storage Stats */}
      <BrutalCard shadow="lg">
        <h3 className="text-lg font-black uppercase flex items-center gap-2 mb-3">
          <HardDrive size={20} className="text-blue-500" /> Storage Usage
        </h3>
        <div className="grid md:grid-cols-4 gap-4">
          <div className="text-center p-3 border-4 border-black">
            <p className="text-2xl font-black">{storageStats.total_storage_mb || 0} MB</p>
            <p className="text-xs font-bold text-gray-500">TOTAL</p>
          </div>
          <div className="text-center p-3 border-4 border-black">
            <p className="text-2xl font-black">{storageStats.recordings_storage_mb || 0} MB</p>
            <p className="text-xs font-bold text-gray-500">RECORDINGS ({storageStats.recordings_count || 0})</p>
          </div>
          <div className="text-center p-3 border-4 border-black">
            <p className="text-2xl font-black">{storageStats.media_storage_mb || 0} MB</p>
            <p className="text-xs font-bold text-gray-500">MEDIA ({storageStats.media_count || 0})</p>
          </div>
          <div className="text-center p-3 border-4 border-black">
            <p className="text-2xl font-black">{storageStats.support_storage_mb || 0} MB</p>
            <p className="text-xs font-bold text-gray-500">SUPPORT FILES</p>
          </div>
        </div>
      </BrutalCard>

      {/* Add Media Buttons */}
      <div className="flex gap-3 flex-wrap">
        <BrutalButton variant="indigo" onClick={() => { setShowUpload(!showUpload); setShowYoutube(false); }} data-testid="upload-audio-btn">
          <Upload size={16} className="mr-1" /> Upload Audio/Video
        </BrutalButton>
        <BrutalButton variant="rose" onClick={() => { setShowYoutube(!showYoutube); setShowUpload(false); }} data-testid="add-youtube-btn">
          <Youtube size={16} className="mr-1" /> Add YouTube Video
        </BrutalButton>
      </div>

      {/* Upload Form */}
      {showUpload && (
        <BrutalCard shadow="lg">
          <h4 className="text-lg font-black uppercase mb-3">Upload Audio / Video File</h4>
          <form onSubmit={handleUpload} className="space-y-3">
            <input type="file" accept="audio/*,video/*" onChange={(e) => setUploadFile(e.target.files[0])}
              className="w-full border-4 border-black p-2" data-testid="media-file-input" />
            <BrutalInput label="Title *" required value={uploadForm.title}
              onChange={(e) => setUploadForm({ ...uploadForm, title: e.target.value })} data-testid="media-title" />
            <BrutalInput label="Artist" value={uploadForm.artist}
              onChange={(e) => setUploadForm({ ...uploadForm, artist: e.target.value })} data-testid="media-artist" />
            <div>
              <label className="block font-bold text-sm uppercase mb-1">Link to Brand</label>
              <select value={uploadForm.brand_id} onChange={(e) => setUploadForm({ ...uploadForm, brand_id: e.target.value })}
                className="w-full px-4 py-2 border-4 border-black font-bold bg-white text-gray-900">
                <option value="">— No Brand —</option>
                {brands.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>
            <BrutalButton type="submit" variant="emerald" disabled={uploadMut.isPending} data-testid="submit-upload">
              {uploadMut.isPending ? 'Uploading...' : 'Upload'}
            </BrutalButton>
          </form>
        </BrutalCard>
      )}

      {/* YouTube Form */}
      {showYoutube && (
        <BrutalCard shadow="lg">
          <h4 className="text-lg font-black uppercase mb-3">Add YouTube Video</h4>
          <form onSubmit={handleAddYoutube} className="space-y-3">
            <BrutalInput label="Title *" required value={ytForm.title}
              onChange={(e) => setYtForm({ ...ytForm, title: e.target.value })} />
            <BrutalInput label="Artist" value={ytForm.artist}
              onChange={(e) => setYtForm({ ...ytForm, artist: e.target.value })} />
            <BrutalInput label="YouTube URL *" required value={ytForm.youtube_url}
              onChange={(e) => setYtForm({ ...ytForm, youtube_url: e.target.value })}
              placeholder="https://www.youtube.com/watch?v=..." data-testid="youtube-url-input" />
            <div>
              <label className="block font-bold text-sm uppercase mb-1">Link to Brand</label>
              <select value={ytForm.brand_id} onChange={(e) => setYtForm({ ...ytForm, brand_id: e.target.value })}
                className="w-full px-4 py-2 border-4 border-black font-bold bg-white text-gray-900">
                <option value="">— No Brand —</option>
                {brands.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>
            <BrutalButton type="submit" variant="emerald" disabled={createYtMut.isPending} data-testid="submit-youtube">
              {createYtMut.isPending ? 'Adding...' : 'Add Video'}
            </BrutalButton>
          </form>
        </BrutalCard>
      )}

      {/* Media Library / Playlist */}
      <BrutalCard shadow="xl" data-testid="media-library">
        <h3 className="text-xl font-black uppercase flex items-center gap-2 mb-1">
          <Play size={20} className="text-emerald-500" /> Media Library ({media.length})
        </h3>
        <p className="text-sm text-gray-500 font-medium mb-4">
          All approved media below is automatically injected into AI-generated stories system-wide.
        </p>
        {media.length === 0 ? (
          <div className="text-center py-8 border-4 border-dashed border-gray-300">
            <Music size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="text-lg font-bold text-gray-400">No media added yet</p>
            <p className="text-sm text-gray-400">Upload audio/video or add YouTube links above</p>
          </div>
        ) : (
          <div className="space-y-3">
            {media.map((m) => (
              <div key={m.id} className="flex items-center justify-between gap-3 p-3 border-4 border-black bg-white" data-testid={`media-${m.id}`}>
                <div className="flex items-center gap-3 min-w-0">
                  <div className={`w-10 h-10 flex items-center justify-center border-4 border-black flex-shrink-0 ${m.media_type === 'video' ? 'bg-rose-100' : 'bg-indigo-100'}`}>
                    {m.media_type === 'video' ? <Video size={20} className="text-rose-600" /> : <Music size={20} className="text-indigo-600" />}
                  </div>
                  <div className="min-w-0">
                    <p className="font-black text-base truncate">{m.title}</p>
                    <p className="text-xs text-gray-500">{m.artist || 'Unknown Artist'} {m.brand_id ? `| ${brandName(m.brand_id)}` : ''}</p>
                    <div className="flex gap-2 mt-1 flex-wrap">
                      <BrutalBadge variant={m.status === 'approved' ? 'emerald' : 'amber'} size="sm">{m.status}</BrutalBadge>
                      <BrutalBadge variant="default" size="sm">{m.source}</BrutalBadge>
                      {m.source === 'youtube' && <BrutalBadge variant="rose" size="sm">YouTube</BrutalBadge>}
                      <span className="text-xs text-gray-400">
                        <Play size={10} className="inline" /> {m.total_streams || 0} streams | {m.total_likes || 0} likes | {m.total_downloads || 0} downloads
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-1 flex-shrink-0">
                  <BrutalButton variant="dark" size="sm"
                    onClick={() => { if (window.confirm('Delete this media?')) deleteMut.mutate(m.id); }}>
                    <Trash2 size={14} />
                  </BrutalButton>
                </div>
              </div>
            ))}
          </div>
        )}
      </BrutalCard>
    </div>
  );
};

export default DigitalMediaTab;
