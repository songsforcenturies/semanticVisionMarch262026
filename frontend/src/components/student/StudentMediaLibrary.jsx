import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mediaAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalBadge } from '@/components/brutal';
import { Music, Video, Heart, Download, Play, Pause } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const extractYouTubeId = (url) => {
  if (!url) return null;
  const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : null;
};

const StudentMediaLibrary = ({ student }) => {
  const qc = useQueryClient();
  const [playing, setPlaying] = useState(null);
  const [audioRef, setAudioRef] = useState(null);

  const { data: library = [] } = useQuery({
    queryKey: ['student-media-library', student?.id],
    queryFn: async () => (await mediaAPI.getStudentLibrary(student.id)).data,
    enabled: !!student?.id,
  });

  const likeMut = useMutation({
    mutationFn: ({ mediaId, liked }) => mediaAPI.toggleLike(student.id, { media_id: mediaId, liked }),
    onSuccess: () => qc.invalidateQueries(['student-media-library']),
  });

  const downloadMut = useMutation({
    mutationFn: (mediaId) => mediaAPI.purchaseDownload(student.id, { media_id: mediaId }),
    onSuccess: (res) => {
      qc.invalidateQueries(['student-media-library']);
      toast.success(res.data.message);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Download failed'),
  });

  const playAudio = (item) => {
    if (playing === item.media_id) {
      audioRef?.pause();
      setPlaying(null);
      return;
    }
    if (audioRef) audioRef.pause();
    const audio = new Audio(`${API_BASE}${item.file_url}`);
    audio.play();
    audio.onended = () => setPlaying(null);
    setAudioRef(audio);
    setPlaying(item.media_id);
    mediaAPI.recordListen(student.id, item.media_id).catch(() => {});
  };

  const likedItems = library.filter(i => i.liked);
  const allItems = library;

  if (library.length === 0) {
    return (
      <BrutalCard shadow="md" className="text-center py-8" data-testid="media-library-empty">
        <Music size={48} className="mx-auto text-gray-300 mb-3" />
        <p className="text-lg font-bold text-gray-500">No music yet</p>
        <p className="text-sm text-gray-400">Songs and videos from your stories will appear here!</p>
      </BrutalCard>
    );
  }

  return (
    <div className="space-y-6" data-testid="student-media-library">
      {likedItems.length > 0 && (
        <>
          <h3 className="text-xl font-black uppercase flex items-center gap-2">
            <Heart size={20} className="text-rose-500 fill-rose-500" /> My Favorites ({likedItems.length})
          </h3>
          <div className="grid gap-3">
            {likedItems.map(item => (
              <MediaCard key={`fav-${item.media_id}`} item={item} playing={playing} onPlay={playAudio}
                onLike={likeMut.mutate} onDownload={downloadMut.mutate} studentId={student.id} />
            ))}
          </div>
        </>
      )}

      <h3 className="text-xl font-black uppercase">All Music ({allItems.length})</h3>
      <div className="grid gap-3">
        {allItems.map(item => (
          <MediaCard key={item.media_id} item={item} playing={playing} onPlay={playAudio}
            onLike={likeMut.mutate} onDownload={downloadMut.mutate} studentId={student.id} />
        ))}
      </div>
    </div>
  );
};

const MediaCard = ({ item, playing, onPlay, onLike, onDownload }) => {
  const [showVideo, setShowVideo] = useState(false);
  const ytId = extractYouTubeId(item.youtube_url);
  const isAudio = item.media_type === 'audio' || item.source === 'upload';

  return (
    <BrutalCard shadow="sm" data-testid={`media-item-${item.media_id}`}>
      <div className="flex items-center gap-3">
        <div className={`w-12 h-12 flex items-center justify-center border-4 border-black flex-shrink-0 cursor-pointer transition-all hover:scale-105 ${item.media_type === 'video' ? 'bg-rose-100' : 'bg-indigo-100'}`}
          onClick={() => isAudio ? onPlay(item) : setShowVideo(!showVideo)}>
          {isAudio ? (
            playing === item.media_id ? <Pause size={24} className="text-indigo-600" /> : <Play size={24} className="text-indigo-600" />
          ) : (
            <Video size={24} className="text-rose-600" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-black text-base truncate">{item.title}</p>
          <p className="text-xs text-gray-500">{item.artist || 'Unknown Artist'}</p>
          <p className="text-xs text-gray-400">Played {item.listen_count || 0} times</p>
        </div>
        <div className="flex gap-2 items-center flex-shrink-0">
          <button onClick={() => onLike({ mediaId: item.media_id, liked: !item.liked })}
            className="p-2 transition-all hover:scale-110" data-testid={`like-${item.media_id}`}>
            <Heart size={20} className={item.liked ? 'text-rose-500 fill-rose-500' : 'text-gray-300'} />
          </button>
          {!item.downloaded && (
            <BrutalButton variant="emerald" size="sm" onClick={() => {
              if (window.confirm(`Download "${item.title}" for $${item.price_per_download?.toFixed(2)}?`)) onDownload(item.media_id);
            }} data-testid={`download-${item.media_id}`}>
              <Download size={14} className="mr-1" />${item.price_per_download?.toFixed(2) || '0.99'}
            </BrutalButton>
          )}
          {item.downloaded && (
            <BrutalBadge variant="emerald" size="sm">Downloaded</BrutalBadge>
          )}
        </div>
      </div>
      {showVideo && ytId && (
        <div className="mt-3 aspect-video w-full">
          <iframe src={`https://www.youtube.com/embed/${ytId}?autoplay=1`}
            className="w-full h-full border-4 border-black" allow="autoplay; encrypted-media" allowFullScreen
            title={item.title} data-testid={`video-player-${item.media_id}`} />
        </div>
      )}
    </BrutalCard>
  );
};

export default StudentMediaLibrary;
