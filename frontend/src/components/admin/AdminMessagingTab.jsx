import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { messagesAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalInput, BrutalBadge } from '@/components/brutal';
import { Send, Trash2, Users, Mail, User, MessageSquare } from 'lucide-react';
import { toast } from 'sonner';

const AdminMessagingTab = () => {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    title: '', body: '', target: 'all', priority: 'normal',
    target_email: '', send_email: false,
  });

  const { data: messages = [] } = useQuery({
    queryKey: ['admin-messages'],
    queryFn: async () => (await messagesAPI.adminList()).data,
  });

  const sendMutation = useMutation({
    mutationFn: (data) => messagesAPI.adminCreate(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries(['admin-messages']);
      const emailNote = res.data?.email_sent ? ' + Email sent!' : '';
      toast.success(`Message sent!${emailNote}`);
      setForm({ title: '', body: '', target: 'all', priority: 'normal', target_email: '', send_email: false });
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to send'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => messagesAPI.adminDelete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-messages']);
      toast.success('Message deleted');
    },
  });

  const handleSend = (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.body.trim()) return;
    if (form.target === 'specific_user' && !form.target_email.trim()) {
      toast.error('Please enter the user\'s email address');
      return;
    }
    const payload = {
      title: form.title,
      body: form.body,
      target: form.target,
      priority: form.priority,
      send_email: form.send_email,
    };
    if (form.target === 'specific_user') {
      payload.target_email = form.target_email.trim();
    }
    sendMutation.mutate(payload);
  };

  const targetLabels = {
    all: 'Everyone', guardians: 'Parents', students: 'Students',
    teachers: 'Teachers', specific_user: 'Specific User',
  };

  return (
    <div className="space-y-6" data-testid="messaging-tab">
      <BrutalCard shadow="xl">
        <h3 className="text-2xl font-black uppercase mb-4 flex items-center gap-2">
          <Send size={24} className="text-blue-500" /> Send Message
        </h3>
        <form onSubmit={handleSend} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block font-bold text-sm uppercase mb-2">Send To</label>
              <select value={form.target} onChange={(e) => setForm({ ...form, target: e.target.value, target_email: '' })}
                className="w-full px-4 py-3 border-4 border-black font-bold focus:outline-none focus:ring-4 focus:ring-blue-500 bg-white"
                style={{ color: '#111827' }} data-testid="msg-target">
                <option value="specific_user">Specific User (by Email)</option>
                <option value="all">Everyone</option>
                <option value="guardians">Parents Only</option>
                <option value="students">Students Only</option>
                <option value="teachers">Teachers Only</option>
              </select>
            </div>
            <div>
              <label className="block font-bold text-sm uppercase mb-2">Priority</label>
              <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}
                className="w-full px-4 py-3 border-4 border-black font-bold focus:outline-none focus:ring-4 focus:ring-blue-500 bg-white"
                style={{ color: '#111827' }} data-testid="msg-priority">
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>

          {form.target === 'specific_user' && (
            <div>
              <label className="block font-bold text-sm uppercase mb-2">User Email Address *</label>
              <input type="email" required value={form.target_email}
                onChange={(e) => setForm({ ...form, target_email: e.target.value })}
                placeholder="Paste user's email address here"
                className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-blue-500"
                style={{ color: '#111827' }}
                data-testid="msg-target-email" />
            </div>
          )}

          <BrutalInput label="Subject *" required value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="e.g. New feature available!" data-testid="msg-title" />
          <div>
            <label className="block font-bold text-sm uppercase mb-2">Message *</label>
            <textarea value={form.body}
              onChange={(e) => setForm({ ...form, body: e.target.value })}
              placeholder="Write your message here..."
              rows={4}
              className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-blue-500 resize-none"
              style={{ color: '#111827' }}
              data-testid="msg-body" />
          </div>

          <label className="flex items-center gap-3 cursor-pointer p-3 border-4 border-black hover:bg-blue-50 transition-all"
            data-testid="msg-send-email-toggle">
            <input type="checkbox" checked={form.send_email}
              onChange={(e) => setForm({ ...form, send_email: e.target.checked })}
              className="w-5 h-5 accent-indigo-600" />
            <Mail size={18} className="text-indigo-500" />
            <span className="font-bold text-sm">Also send as email</span>
            <span className="text-xs text-gray-500">(requires Resend key in Integrations)</span>
          </label>

          <BrutalButton type="submit" variant="indigo" size="lg" fullWidth
            disabled={sendMutation.isPending} data-testid="msg-send-btn">
            {sendMutation.isPending ? 'Sending...' : 'Send Message'}
          </BrutalButton>
        </form>
      </BrutalCard>

      <h3 className="text-2xl font-black uppercase">Sent Messages ({messages.length})</h3>
      {messages.length === 0 ? (
        <BrutalCard shadow="md" className="text-center py-8">
          <MessageSquare size={48} className="mx-auto text-gray-300 mb-3" />
          <p className="text-lg font-bold text-gray-500">No messages sent yet</p>
        </BrutalCard>
      ) : (
        <div className="space-y-3">
          {messages.map((msg) => (
            <BrutalCard key={msg.id} shadow="md" data-testid={`msg-${msg.id}`}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <h4 className="font-black text-lg">{msg.title}</h4>
                    <BrutalBadge variant={msg.priority === 'urgent' ? 'rose' : msg.priority === 'high' ? 'amber' : 'default'} size="sm">
                      {msg.priority}
                    </BrutalBadge>
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-700">
                      {msg.target === 'specific_user' ? (
                        <><User size={12} className="inline mr-1" />{msg.target_user_name || msg.target_email}</>
                      ) : (
                        <><Users size={12} className="inline mr-1" />{targetLabels[msg.target] || msg.target}</>
                      )}
                    </span>
                    {msg.email_sent && (
                      <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-700">
                        <Mail size={12} className="inline mr-1" />Email Sent{msg.emails_sent_count > 0 ? ` (${msg.emails_sent_count})` : ''}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-2 whitespace-pre-wrap">{msg.body}</p>
                  <div className="flex items-center gap-3 text-xs text-gray-400">
                    <span>By {msg.sent_by_name}</span>
                    <span>{new Date(msg.created_date).toLocaleString()}</span>
                    <span>{(msg.read_by || []).length} read</span>
                  </div>
                </div>
                <BrutalButton variant="dark" size="sm"
                  onClick={() => { if (window.confirm('Delete this message?')) deleteMutation.mutate(msg.id); }}
                  data-testid={`delete-msg-${msg.id}`}>
                  <Trash2 size={14} />
                </BrutalButton>
              </div>
            </BrutalCard>
          ))}
        </div>
      )}
    </div>
  );
};

export default AdminMessagingTab;
