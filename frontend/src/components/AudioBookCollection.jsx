import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { audioBooksAPI } from '@/lib/api';
import { BrutalCard, BrutalBadge } from '@/components/brutal';
import { Headphones, Play, Pause, Heart, User, Clock } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const AudioBookCollection = ({ embedded = false }) => {
  const [playing, setPlaying] = useState(null);
  const [audioEl, setAudioEl] = useState(null);
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['audio-books', page],
    queryFn: async () => (await audioBooksAPI.getAll(page)).data,
  });

  const likeMut = useMutation({
    mutationFn: (id) => audioBooksAPI.like(id),
  });

  const playBook = (id) => {
    if (playing === id && audioEl) { audioEl.pause(); setPlaying(null); return; }
    if (audioEl) audioEl.pause();
    const audio = new Audio(`${API_BASE}/api/audio-books/${id}/stream`);
    audio.play();
    audio.onended = () => setPlaying(null);
    setAudioEl(audio);
    setPlaying(id);
  };

  if (data && data.enabled === false && !embedded) {
    return <div className="text-center py-16 text-gray-500 font-bold">Audio Book Collection is currently unavailable.</div>;
  }

  const books = data?.audio_books || [];
  const total = data?.total || 0;

  const Wrapper = embedded ? 'div' : 'div';

  return (
    <div className={embedded ? 'space-y-4' : 'max-w-4xl mx-auto p-6 space-y-6'} data-testid="audio-book-collection">
      {!embedded && (
        <div className="text-center mb-8">
          <Headphones size={48} className="mx-auto text-indigo-600 mb-3" />
          <h1 className="text-3xl font-black uppercase">Audio Book Collection</h1>
          <p className="text-gray-500 font-medium mt-2">Listen to stories narrated by real kids. Cute, inspiring, and full of heart.</p>
        </div>
      )}

      {embedded && (
        <BrutalCard shadow="xl" className="bg-gradient-to-r from-amber-50 to-orange-50">
          <div className="flex items-center gap-3">
            <Headphones size={24} className="text-amber-600" />
            <div>
              <h2 className="text-xl font-black uppercase">Audio Book Collection</h2>
              <p className="text-sm text-gray-600 font-medium">Listen to stories read aloud by children on our platform</p>
            </div>
          </div>
        </BrutalCard>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto mb-3" />
        </div>
      ) : books.length === 0 ? (
        <BrutalCard shadow="lg" className="text-center py-12">
          <Headphones size={48} className="mx-auto text-gray-300 mb-3" />
          <h3 className="text-lg font-black">No Audio Books Yet</h3>
          <p className="text-gray-500 text-sm font-medium">Be the first to share a recording!</p>
        </BrutalCard>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {books.map(book => (
            <BrutalCard key={book.id} shadow="md" className="hover:shadow-lg transition-all" data-testid={`audiobook-${book.id}`}>
              <div className="flex items-start gap-3">
                <button onClick={() => playBook(book.id)}
                  className="w-12 h-12 flex-shrink-0 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white flex items-center justify-center hover:scale-105 transition-transform"
                  data-testid={`play-book-${book.id}`}>
                  {playing === book.id ? <Pause size={18} /> : <Play size={18} className="ml-0.5" />}
                </button>
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-sm truncate">{book.narrative_title}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    <User size={10} className="inline mr-1" />{book.student_name}, age {book.student_age}
                    {book.chapter_number > 0 && <> &middot; Ch. {book.chapter_number}</>}
                  </p>
                  <div className="flex items-center gap-3 mt-2">
                    {book.diction_scores && (
                      <BrutalBadge variant="emerald" size="sm">{book.diction_scores.overall}% diction</BrutalBadge>
                    )}
                    <span className="text-xs text-gray-400">{book.listens || 0} listens</span>
                    <button onClick={() => likeMut.mutate(book.id)}
                      className="flex items-center gap-1 text-xs text-gray-400 hover:text-red-500 transition-all">
                      <Heart size={12} /> {book.likes || 0}
                    </button>
                  </div>
                </div>
              </div>
            </BrutalCard>
          ))}
        </div>
      )}

      {total > 20 && (
        <div className="flex justify-center gap-2 mt-4">
          <button onClick={() => setPage(p => Math.max(1, p-1))} disabled={page === 1}
            className="px-3 py-1 text-sm font-bold bg-gray-100 rounded-lg disabled:opacity-40">Prev</button>
          <span className="px-3 py-1 text-sm font-bold">Page {page}</span>
          <button onClick={() => setPage(p => p+1)} disabled={books.length < 20}
            className="px-3 py-1 text-sm font-bold bg-gray-100 rounded-lg disabled:opacity-40">Next</button>
        </div>
      )}
    </div>
  );
};

export default AudioBookCollection;
