import React, { useState, useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { supportAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalInput } from '@/components/brutal';
import { MessageCircle, X, Send, Camera, Mic, Video, Paperclip, Loader2, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { toast } from 'sonner';

const SupportWidget = () => {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ subject: '', message: '', type: 'text' });
  const [attachments, setAttachments] = useState([]);
  const [recording, setRecording] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const mediaRecorder = useRef(null);
  const chunks = useRef([]);
  const fileInput = useRef(null);

  const { data: tickets = [] } = useQuery({
    queryKey: ['my-support-tickets'],
    queryFn: async () => (await supportAPI.listTickets()).data,
    enabled: open && showHistory,
  });

  const createMut = useMutation({
    mutationFn: async () => {
      const res = await supportAPI.createTicket(form);
      const ticketId = res.data.id;
      for (const att of attachments) {
        const fd = new FormData();
        fd.append('file', att.file);
        await supportAPI.addAttachment(ticketId, fd);
      }
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries(['my-support-tickets']);
      toast.success('Support message sent! Admin will respond soon.');
      setForm({ subject: '', message: '', type: 'text' });
      setAttachments([]);
      setOpen(false);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to send'),
  });

  const handleScreenshot = async () => {
    try {
      const canvas = await import('html2canvas').then(m => m.default(document.body, { scale: 0.5, useCORS: true }));
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], `screenshot-${Date.now()}.png`, { type: 'image/png' });
          setAttachments(prev => [...prev, { file, name: file.name, type: 'image' }]);
          toast.success('Screenshot captured!');
        }
      });
    } catch {
      toast.error('Could not capture screenshot');
    }
  };

  const startAudioRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      chunks.current = [];
      mediaRecorder.current.ondataavailable = (e) => chunks.current.push(e.data);
      mediaRecorder.current.onstop = () => {
        const blob = new Blob(chunks.current, { type: 'audio/webm' });
        const file = new File([blob], `audio-${Date.now()}.webm`, { type: 'audio/webm' });
        setAttachments(prev => [...prev, { file, name: file.name, type: 'audio' }]);
        stream.getTracks().forEach(t => t.stop());
        setRecording(false);
        toast.success('Audio recorded!');
      };
      mediaRecorder.current.start();
      setRecording(true);
    } catch {
      toast.error('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current?.state === 'recording') mediaRecorder.current.stop();
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const type = file.type.startsWith('image') ? 'image' : file.type.startsWith('audio') ? 'audio' : 'video';
      setAttachments(prev => [...prev, { file, name: file.name, type }]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.subject.trim() || !form.message.trim()) { toast.error('Please fill in subject and message'); return; }
    createMut.mutate();
  };

  const myRepliedTickets = tickets.filter(t => t.admin_replies?.length > 0);

  return (
    <>
      {/* Floating button */}
      <button onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center shadow-xl transition-all hover:scale-110"
        style={{ background: '#D4A853', color: '#1A2236', border: '3px solid #1A2236' }}
        data-testid="support-widget-btn">
        {open ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {/* Panel */}
      {open && (
        <div className="fixed bottom-24 right-6 z-50 w-[360px] max-h-[75vh] overflow-y-auto rounded-xl shadow-2xl"
          style={{ background: '#1A2236', border: '2px solid rgba(212,168,83,0.3)' }}
          data-testid="support-panel">
          <div className="px-4 py-3 flex items-center justify-between" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <h3 className="text-sm font-bold" style={{ color: '#F8F5EE' }}>Contact Support</h3>
            <button onClick={() => setShowHistory(!showHistory)} className="text-xs font-bold px-2 py-1 rounded"
              style={{ color: '#D4A853', background: 'rgba(212,168,83,0.1)' }}>
              {showHistory ? 'New Message' : `History (${tickets.length})`}
            </button>
          </div>

          {showHistory ? (
            <div className="p-3 space-y-2">
              {myRepliedTickets.length === 0 ? (
                <p className="text-sm text-center py-4" style={{ color: '#94A3B8' }}>No replies yet</p>
              ) : myRepliedTickets.map(t => (
                <div key={t.id} className="p-3 rounded-lg" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
                  <p className="font-bold text-sm" style={{ color: '#F8F5EE' }}>{t.subject}</p>
                  <p className="text-xs mt-1" style={{ color: '#94A3B8' }}>{t.message}</p>
                  {t.admin_replies.map(r => (
                    <div key={r.id} className="mt-2 p-2 rounded" style={{ background: 'rgba(212,168,83,0.1)', borderLeft: '3px solid #D4A853' }}>
                      <p className="text-xs font-bold" style={{ color: '#D4A853' }}>{r.admin_name}</p>
                      <p className="text-xs mt-0.5" style={{ color: '#F8F5EE' }}>{r.message}</p>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="p-3 space-y-3">
              <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}
                className="w-full px-3 py-2 rounded-lg text-sm font-bold bg-white text-gray-900 border-2 border-gray-200" data-testid="ticket-type">
                <option value="text">General Message</option>
                <option value="bug">Bug Report</option>
                <option value="feedback">Feedback</option>
                <option value="feature_request">Feature Request</option>
              </select>
              <input value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })}
                placeholder="Subject" className="w-full px-3 py-2 rounded-lg text-sm font-medium bg-white text-gray-900 border-2 border-gray-200"
                data-testid="ticket-subject" />
              <textarea value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })}
                placeholder="Describe your issue or message..." rows={3}
                className="w-full px-3 py-2 rounded-lg text-sm font-medium bg-white text-gray-900 border-2 border-gray-200 resize-none"
                data-testid="ticket-message" />

              {/* Attachment buttons */}
              <div className="flex gap-2">
                <button type="button" onClick={handleScreenshot} className="flex items-center gap-1 px-2 py-1.5 rounded text-xs font-bold transition-all hover:scale-105"
                  style={{ background: 'rgba(212,168,83,0.15)', color: '#D4A853' }} data-testid="screenshot-btn">
                  <Camera size={14} /> Screenshot
                </button>
                <button type="button" onClick={recording ? stopRecording : startAudioRecording}
                  className="flex items-center gap-1 px-2 py-1.5 rounded text-xs font-bold transition-all hover:scale-105"
                  style={{ background: recording ? 'rgba(239,68,68,0.2)' : 'rgba(212,168,83,0.15)', color: recording ? '#EF4444' : '#D4A853' }}
                  data-testid="audio-record-btn">
                  <Mic size={14} /> {recording ? 'Stop' : 'Audio'}
                </button>
                <button type="button" onClick={() => fileInput.current?.click()}
                  className="flex items-center gap-1 px-2 py-1.5 rounded text-xs font-bold transition-all hover:scale-105"
                  style={{ background: 'rgba(212,168,83,0.15)', color: '#D4A853' }} data-testid="attach-file-btn">
                  <Paperclip size={14} /> File
                </button>
                <input ref={fileInput} type="file" accept="image/*,audio/*,video/*" className="hidden" onChange={handleFileSelect} />
              </div>

              {/* Attachment list */}
              {attachments.length > 0 && (
                <div className="space-y-1">
                  {attachments.map((att, i) => (
                    <div key={i} className="flex items-center justify-between px-2 py-1 rounded text-xs"
                      style={{ background: 'rgba(255,255,255,0.05)' }}>
                      <span style={{ color: '#F8F5EE' }} className="truncate">{att.name}</span>
                      <button type="button" onClick={() => setAttachments(prev => prev.filter((_, j) => j !== i))}
                        className="ml-2 flex-shrink-0" style={{ color: '#EF4444' }}><X size={12} /></button>
                    </div>
                  ))}
                </div>
              )}

              <button type="submit" disabled={createMut.isPending}
                className="w-full py-2.5 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-all hover:scale-[1.02]"
                style={{ background: '#D4A853', color: '#1A2236' }} data-testid="send-ticket-btn">
                {createMut.isPending ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                {createMut.isPending ? 'Sending...' : 'Send to Admin'}
              </button>
            </form>
          )}
        </div>
      )}
    </>
  );
};

export default SupportWidget;
