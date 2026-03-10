import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { messagesAPI } from '@/lib/api';
import { Bell, X, AlertTriangle, Info, ArrowLeft } from 'lucide-react';

const C = {
  card: '#1A2236', cream: '#F8F5EE', muted: '#94A3B8', gold: '#D4A853',
};

const NotificationBell = ({ isStudent = false, studentId = null }) => {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [selectedMsg, setSelectedMsg] = useState(null);
  const ref = useRef(null);

  const { data } = useQuery({
    queryKey: ['notifications', isStudent, studentId],
    queryFn: async () => {
      if (isStudent && studentId) {
        return (await messagesAPI.getStudentNotifications(studentId)).data;
      }
      return (await messagesAPI.getNotifications()).data;
    },
    refetchInterval: 30000,
    enabled: isStudent ? !!studentId : true,
  });

  const markReadMutation = useMutation({
    mutationFn: (id) => {
      if (isStudent && studentId) return messagesAPI.markStudentRead(id, studentId);
      return messagesAPI.markRead(id);
    },
    onSuccess: () => queryClient.invalidateQueries(['notifications']),
  });

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
        setSelectedMsg(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const messages = data?.messages || [];
  const unreadCount = data?.unread_count || 0;

  const priorityIcon = (p) => {
    if (p === 'urgent') return <AlertTriangle size={14} style={{ color: '#EF4444' }} />;
    if (p === 'high') return <AlertTriangle size={14} style={{ color: '#F59E0B' }} />;
    return <Info size={14} style={{ color: '#38BDF8' }} />;
  };

  const priorityLabel = (p) => {
    const colors = { urgent: '#EF4444', high: '#F59E0B', normal: '#38BDF8', low: '#94A3B8' };
    return (
      <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: `${colors[p] || colors.normal}20`, color: colors[p] || colors.normal }}>
        {p?.toUpperCase()}
      </span>
    );
  };

  const openMessage = (msg) => {
    setSelectedMsg(msg);
    if (!msg.is_read) markReadMutation.mutate(msg.id);
  };

  return (
    <div className="relative" ref={ref}>
      <button onClick={() => { setOpen(!open); setSelectedMsg(null); }}
        className="relative p-2 rounded-lg transition-all"
        style={{ color: unreadCount > 0 ? C.gold : C.muted, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)' }}
        data-testid="notification-bell">
        <Bell size={18} />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full text-xs font-bold flex items-center justify-center text-black"
            style={{ background: '#EF4444', fontSize: '10px' }}
            data-testid="notification-count">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 rounded-xl overflow-hidden z-[100] shadow-2xl"
          style={{ background: C.card, border: '1px solid rgba(255,255,255,0.15)', maxHeight: '70vh' }}
          data-testid="notification-panel">

          {/* Header */}
          <div className="px-4 py-3 flex items-center justify-between" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            {selectedMsg ? (
              <button onClick={() => setSelectedMsg(null)} className="flex items-center gap-2 text-sm font-bold hover:opacity-80 transition-all" style={{ color: C.gold }}
                data-testid="notification-back-btn">
                <ArrowLeft size={16} /> Back
              </button>
            ) : (
              <h3 className="text-sm font-bold" style={{ color: C.cream }}>
                Notifications {unreadCount > 0 && `(${unreadCount})`}
              </h3>
            )}
            <button onClick={() => { setOpen(false); setSelectedMsg(null); }} className="p-1" style={{ color: C.muted }}>
              <X size={16} />
            </button>
          </div>

          <div className="overflow-y-auto" style={{ maxHeight: '60vh' }}>
            {/* Full Message View */}
            {selectedMsg ? (
              <div className="p-4 space-y-3" data-testid="notification-detail">
                <div className="flex items-center gap-2 flex-wrap">
                  {priorityIcon(selectedMsg.priority)}
                  {priorityLabel(selectedMsg.priority)}
                </div>
                <h4 className="text-base font-bold leading-snug" style={{ color: C.cream }} data-testid="notification-detail-title">
                  {selectedMsg.title}
                </h4>
                <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: 'rgba(248,245,238,0.8)' }} data-testid="notification-detail-body">
                  {selectedMsg.body}
                </p>
                <div className="pt-2" style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                  <p className="text-xs" style={{ color: 'rgba(148,163,184,0.6)' }}>
                    From {selectedMsg.sent_by_name || 'Admin'} &middot; {new Date(selectedMsg.created_date).toLocaleString()}
                  </p>
                </div>
              </div>
            ) : (
              /* Message List */
              messages.length === 0 ? (
                <div className="p-6 text-center">
                  <Bell size={24} className="mx-auto mb-2" style={{ color: C.muted }} />
                  <p className="text-sm" style={{ color: C.muted }}>No notifications</p>
                </div>
              ) : (
                messages.map((msg) => (
                  <div key={msg.id}
                    className="px-4 py-3 cursor-pointer transition-all hover:bg-white/5"
                    style={{
                      borderBottom: '1px solid rgba(255,255,255,0.05)',
                      background: msg.is_read ? 'transparent' : 'rgba(212,168,83,0.06)',
                    }}
                    onClick={() => openMessage(msg)}
                    data-testid={`notification-${msg.id}`}>
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 flex-shrink-0">
                        {priorityIcon(msg.priority)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-bold truncate" style={{ color: C.cream }}>{msg.title}</p>
                          {!msg.is_read && (
                            <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: C.gold }} />
                          )}
                        </div>
                        <p className="text-xs mt-0.5 line-clamp-2" style={{ color: C.muted }}>{msg.body}</p>
                        <p className="text-xs mt-1" style={{ color: 'rgba(148,163,184,0.5)' }}>
                          {new Date(msg.created_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
