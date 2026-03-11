import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supportAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalBadge, BrutalInput } from '@/components/brutal';
import { MessageCircle, Send, Image, Mic, Video, ChevronDown, ChevronUp, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const statusColors = {
  open: 'amber', in_progress: 'indigo', replied: 'emerald', resolved: 'emerald', closed: 'default',
};

const AdminSupportTab = () => {
  const qc = useQueryClient();
  const [expanded, setExpanded] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [filter, setFilter] = useState('all');

  const { data: tickets = [] } = useQuery({
    queryKey: ['admin-support-tickets'],
    queryFn: async () => (await supportAPI.listTickets()).data,
  });

  const replyMut = useMutation({
    mutationFn: ({ ticketId, message }) => supportAPI.adminReply(ticketId, { message }),
    onSuccess: () => {
      qc.invalidateQueries(['admin-support-tickets']);
      toast.success('Reply sent & user notified');
      setReplyText('');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed'),
  });

  const statusMut = useMutation({
    mutationFn: ({ ticketId, status }) => supportAPI.updateStatus(ticketId, { status }),
    onSuccess: () => { qc.invalidateQueries(['admin-support-tickets']); toast.success('Status updated'); },
  });

  const filtered = filter === 'all' ? tickets : tickets.filter(t => t.status === filter);

  const attIcon = (type) => {
    if (type?.startsWith('image')) return <Image size={14} className="text-blue-500" />;
    if (type?.startsWith('audio')) return <Mic size={14} className="text-emerald-500" />;
    if (type?.startsWith('video')) return <Video size={14} className="text-rose-500" />;
    return null;
  };

  return (
    <div className="space-y-4" data-testid="admin-support-tab">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h3 className="text-2xl font-black uppercase flex items-center gap-2">
          <MessageCircle size={24} className="text-amber-500" /> Support Tickets ({tickets.length})
        </h3>
        <div className="flex gap-1">
          {['all', 'open', 'in_progress', 'replied', 'resolved'].map(s => (
            <button key={s} onClick={() => setFilter(s)}
              className={`px-2 py-1 text-xs font-bold rounded ${filter === s ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
              {s === 'all' ? 'All' : s.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <BrutalCard shadow="md" className="text-center py-8">
          <CheckCircle size={48} className="mx-auto text-emerald-300 mb-3" />
          <p className="text-lg font-bold text-gray-500">No tickets{filter !== 'all' ? ` (${filter})` : ''}</p>
        </BrutalCard>
      ) : filtered.map(t => (
        <BrutalCard key={t.id} shadow="md" data-testid={`ticket-${t.id}`}>
          <div className="cursor-pointer" onClick={() => setExpanded(expanded === t.id ? null : t.id)}>
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <p className="font-black text-base">{t.subject}</p>
                  <BrutalBadge variant={statusColors[t.status] || 'default'} size="sm">{t.status}</BrutalBadge>
                  <BrutalBadge variant="default" size="sm">{t.type}</BrutalBadge>
                </div>
                <p className="text-xs text-gray-500">
                  {t.user_name} ({t.user_email}) &middot; {t.user_role} &middot; {new Date(t.created_date).toLocaleString()}
                </p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                {t.attachments?.length > 0 && (
                  <span className="text-xs font-bold text-gray-400">{t.attachments.length} attachment{t.attachments.length > 1 ? 's' : ''}</span>
                )}
                {expanded === t.id ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </div>
            </div>
          </div>

          {expanded === t.id && (
            <div className="mt-3 pt-3" style={{ borderTop: '2px dashed #e5e7eb' }}>
              <p className="text-sm mb-3 whitespace-pre-wrap">{t.message}</p>

              {/* Attachments */}
              {t.attachments?.length > 0 && (
                <div className="mb-3 space-y-2">
                  <p className="text-xs font-bold uppercase text-gray-500">Attachments</p>
                  {t.attachments.map(att => (
                    <div key={att.id} className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg border">
                      {attIcon(att.content_type)}
                      {att.content_type?.startsWith('image') ? (
                        <a href={`${API_BASE}${att.url}`} target="_blank" rel="noreferrer" className="text-blue-600 text-xs font-bold hover:underline">
                          View Screenshot
                        </a>
                      ) : (
                        <a href={`${API_BASE}${att.url}`} target="_blank" rel="noreferrer" className="text-blue-600 text-xs font-bold hover:underline">
                          {att.original_name}
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Admin replies */}
              {t.admin_replies?.map(r => (
                <div key={r.id} className="mb-2 p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                  <p className="text-xs font-bold text-emerald-700">{r.admin_name} — {new Date(r.created_date).toLocaleString()}</p>
                  <p className="text-sm mt-1">{r.message}</p>
                </div>
              ))}

              {/* Reply form */}
              <div className="flex gap-2 mt-3">
                <input value={replyText} onChange={(e) => setReplyText(e.target.value)}
                  placeholder="Type your reply..."
                  className="flex-1 px-3 py-2 border-4 border-black text-sm font-medium text-gray-900 bg-white"
                  data-testid={`reply-input-${t.id}`}
                  onKeyDown={(e) => { if (e.key === 'Enter' && replyText.trim()) replyMut.mutate({ ticketId: t.id, message: replyText }); }} />
                <BrutalButton variant="emerald" size="sm" disabled={!replyText.trim() || replyMut.isPending}
                  onClick={() => replyMut.mutate({ ticketId: t.id, message: replyText })}
                  data-testid={`reply-btn-${t.id}`}>
                  <Send size={14} />
                </BrutalButton>
              </div>

              {/* Status actions */}
              <div className="flex gap-2 mt-3">
                {['in_progress', 'resolved', 'closed'].map(s => (
                  t.status !== s && (
                    <BrutalButton key={s} variant={s === 'resolved' ? 'emerald' : 'dark'} size="sm"
                      onClick={() => statusMut.mutate({ ticketId: t.id, status: s })}>
                      {s.replace('_', ' ').toUpperCase()}
                    </BrutalButton>
                  )
                ))}
              </div>
            </div>
          )}
        </BrutalCard>
      ))}
    </div>
  );
};

export default AdminSupportTab;
