import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalInput, BrutalBadge } from '@/components/brutal';
import { Music, Video, Upload, Trash2, Play, Settings, Power, DollarSign, Youtube } from 'lucide-react';
import { toast } from 'sonner';

const DigitalMediaTab = () => {
  const qc = useQueryClient();
  const [showUpload, setShowUpload] = useState(false);
  const [showYoutube, setShowYoutube] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadForm, setUploadForm] = useState({ title: '', artist: '', brand_id: '' });
  const [ytForm, setYtForm] = useState({ title: '', artist: '', youtube_url: '', brand_id: '', price_per_stream: 0, price_per_download: 0.99 });

  const { data: settings = {} } = useQuery({
    queryKey: ['media-settings'],
    queryFn: async () => (await adminAPI.getMediaSettings()).data,
  });

  const { data: media = [] } = useQuery({
    queryKey: ['brand-media'],
    queryFn: async () => (await adminAPI.listBrandMedia()).data,
  });

  const { data: brands = [] } = useQuery({
    queryKey: ['admin-brands'],
    queryFn: async () => (await adminAPI.getBrands()).data,
  });

  const settingsMut = useMutation({
    mutationFn: (data) => adminAPI.updateMediaSettings(data),
    onSuccess: () => { qc.invalidateQueries(['media-settings']); toast.success('Settings updated'); },
  });

  const uploadMut = useMutation({
    mutationFn: async (formData) => (await adminAPI.uploadBrandMedia(formData)).data,
    onSuccess: () => {
      qc.invalidateQueries(['brand-media']);
      toast.success('Media uploaded');
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
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  const deleteMut = useMutation({
    mutationFn: (id) => adminAPI.deleteBrandMedia(id),
    onSuccess: () => { qc.invalidateQueries(['brand-media']); toast.success('Deleted'); },
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }) => adminAPI.updateBrandMedia(id, data),
    onSuccess: () => { qc.invalidateQueries(['brand-media']); toast.success('Updated'); },
  });

  const handleUpload = (e) => {
    e.preventDefault();
    if (!uploadFile || !uploadForm.title) return;
    const fd = new FormData();
    fd.append('file', uploadFile);
    fd.append('title', uploadForm.title);
    fd.append('artist', uploadForm.artist);
    fd.append('brand_id', uploadForm.brand_id);
    uploadMut.mutate(fd);
  };

  const handleAddYoutube = (e) => {
    e.preventDefault();
    if (!ytForm.title || !ytForm.youtube_url) return;
    createYtMut.mutate({ ...ytForm, media_type: 'video' });
  };

  const brandName = (id) => brands.find(b => b.id === id)?.name || '—';

  return (
    <div className="space-y-6" data-testid="digital-media-tab">
      {/* Settings */}
      <BrutalCard shadow="xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-2xl font-black uppercase flex items-center gap-2">
            <Settings size={24} className="text-violet-500" /> Media Settings
          </h3>
          <BrutalButton
            variant={settings.digital_media_enabled ? 'emerald' : 'rose'}
            onClick={() => settingsMut.mutate({ digital_media_enabled: !settings.digital_media_enabled })}
            data-testid="media-master-toggle"
          >
            <Power size={16} className="mr-1" />
            {settings.digital_media_enabled ? 'ENABLED' : 'DISABLED'}
          </BrutalButton>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block font-bold text-sm uppercase mb-1">Price per Stream ($)</label>
            <input type="number" step="0.01" min="0" value={settings.default_price_per_stream ?? 0}
              onChange={(e) => settingsMut.mutate({ default_price_per_stream: parseFloat(e.target.value) || 0 })}
              className="w-full px-4 py-2 border-4 border-black font-bold" style={{ color: '#111' }}
              data-testid="price-per-stream" />
          </div>
          <div>
            <label className="block font-bold text-sm uppercase mb-1">Price per Download ($)</label>
            <input type="number" step="0.01" min="0" value={settings.default_price_per_download ?? 0.99}
              onChange={(e) => settingsMut.mutate({ default_price_per_download: parseFloat(e.target.value) || 0 })}
              className="w-full px-4 py-2 border-4 border-black font-bold" style={{ color: '#111' }}
              data-testid="price-per-download" />
          </div>
        </div>
      </BrutalCard>

      {/* Actions */}
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
                className="w-full px-4 py-2 border-4 border-black font-bold" style={{ color: '#111' }}>
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
                className="w-full px-4 py-2 border-4 border-black font-bold" style={{ color: '#111' }}>
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

      {/* Media List */}
      <h3 className="text-2xl font-black uppercase">All Media ({media.length})</h3>
      {media.length === 0 ? (
        <BrutalCard shadow="md" className="text-center py-8">
          <Music size={48} className="mx-auto text-gray-300 mb-3" />
          <p className="text-lg font-bold text-gray-500">No media added yet</p>
        </BrutalCard>
      ) : (
        <div className="space-y-3">
          {media.map((m) => (
            <BrutalCard key={m.id} shadow="md" data-testid={`media-${m.id}`}>
              <div className="flex items-center justify-between gap-3">
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
                      <span className="text-xs text-gray-400">
                        <Play size={10} className="inline" /> {m.total_streams || 0} streams | {m.total_likes || 0} likes | {m.total_downloads || 0} downloads
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-1 flex-shrink-0">
                  <BrutalButton variant="dark" size="sm"
                    onClick={() => { if (window.confirm('Delete?')) deleteMut.mutate(m.id); }}>
                    <Trash2 size={14} />
                  </BrutalButton>
                </div>
              </div>
            </BrutalCard>
          ))}
        </div>
      )}
    </div>
  );
};

export default DigitalMediaTab;
