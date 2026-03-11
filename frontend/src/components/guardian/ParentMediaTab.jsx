import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mediaAPI, studentAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalBadge } from '@/components/brutal';
import { Music, Heart, Video, Power, User } from 'lucide-react';
import { toast } from 'sonner';

const ParentMediaTab = () => {
  const qc = useQueryClient();

  const { data: childrenMedia = [] } = useQuery({
    queryKey: ['children-media'],
    queryFn: async () => (await mediaAPI.getChildrenMedia()).data,
  });

  const { data: students = [] } = useQuery({
    queryKey: ['my-students'],
    queryFn: async () => (await studentAPI.getAll()).data,
  });

  const toggleMut = useMutation({
    mutationFn: ({ studentId, enabled }) => mediaAPI.updateMediaPreference(studentId, enabled),
    onSuccess: (_, { enabled }) => {
      qc.invalidateQueries(['my-students']);
      toast.success(`Digital media ${enabled ? 'enabled' : 'disabled'}`);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  // Group media by student
  const byStudent = {};
  childrenMedia.forEach(m => {
    if (!byStudent[m.student_id]) byStudent[m.student_id] = { name: m.student_name, items: [] };
    byStudent[m.student_id].items.push(m);
  });

  return (
    <div className="space-y-6" data-testid="parent-media-tab">
      {/* Per-student media toggle */}
      {students.length > 0 && (
        <BrutalCard shadow="lg">
          <h3 className="text-xl font-black uppercase mb-3">Media Controls</h3>
          <p className="text-sm text-gray-500 mb-4">Allow or block digital media (songs, videos) in your children's stories.</p>
          <div className="space-y-2">
            {students.map(s => (
              <div key={s.id} className="flex items-center justify-between p-3 border-4 border-black" data-testid={`media-toggle-${s.id}`}>
                <div className="flex items-center gap-2">
                  <User size={16} />
                  <span className="font-bold">{s.full_name}</span>
                </div>
                <BrutalButton
                  variant={s.digital_media_enabled !== false ? 'emerald' : 'rose'}
                  size="sm"
                  onClick={() => toggleMut.mutate({ studentId: s.id, enabled: s.digital_media_enabled === false })}
                >
                  <Power size={14} className="mr-1" />
                  {s.digital_media_enabled !== false ? 'ON' : 'OFF'}
                </BrutalButton>
              </div>
            ))}
          </div>
        </BrutalCard>
      )}

      {/* Children's media history */}
      {Object.keys(byStudent).length === 0 ? (
        <BrutalCard shadow="md" className="text-center py-8">
          <Music size={48} className="mx-auto text-gray-300 mb-3" />
          <p className="text-lg font-bold text-gray-500">No media activity yet</p>
          <p className="text-sm text-gray-400">When your children listen to songs or watch videos in stories, they'll appear here.</p>
        </BrutalCard>
      ) : (
        Object.entries(byStudent).map(([studentId, { name, items }]) => (
          <div key={studentId} className="space-y-3">
            <h3 className="text-xl font-black uppercase">{name}'s Music ({items.length})</h3>
            {items.map(item => (
              <BrutalCard key={`${studentId}-${item.media_id}`} shadow="sm">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 flex items-center justify-center border-4 border-black flex-shrink-0 ${item.media_type === 'video' ? 'bg-rose-100' : 'bg-indigo-100'}`}>
                    {item.media_type === 'video' ? <Video size={18} className="text-rose-600" /> : <Music size={18} className="text-indigo-600" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-black text-sm truncate">{item.title}</p>
                    <p className="text-xs text-gray-500">{item.artist || 'Unknown'}</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {item.liked && <Heart size={16} className="text-rose-500 fill-rose-500" />}
                    {item.downloaded && <BrutalBadge variant="emerald" size="sm">Downloaded</BrutalBadge>}
                    <span className="text-xs text-gray-400">{item.listen_count}x</span>
                  </div>
                </div>
              </BrutalCard>
            ))}
          </div>
        ))
      )}
    </div>
  );
};

export default ParentMediaTab;
