import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { adminAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalBadge, BrutalInput } from '@/components/brutal';
import { Home, LogOut, DollarSign, Cpu, Users, BarChart3, Settings } from 'lucide-react';
import { toast } from 'sonner';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts';

const COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899'];

const AdminPortal = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('costs');

  const { data: costs } = useQuery({
    queryKey: ['admin-costs'],
    queryFn: async () => (await adminAPI.getCosts()).data,
  });

  const { data: modelConfig } = useQuery({
    queryKey: ['admin-models'],
    queryFn: async () => (await adminAPI.getModels()).data,
  });

  const [llmForm, setLlmForm] = useState({
    provider: 'emergent',
    model: 'gpt-5.2',
    openrouter_key: '',
  });

  const updateModelMutation = useMutation({
    mutationFn: (data) => adminAPI.updateModels(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-models']);
      toast.success('LLM configuration updated!');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to update config'),
  });

  React.useEffect(() => {
    if (modelConfig) {
      setLlmForm({
        provider: modelConfig.provider || 'emergent',
        model: modelConfig.model || 'gpt-5.2',
        openrouter_key: modelConfig.openrouter_key || '',
      });
    }
  }, [modelConfig]);

  const handleLogout = () => { logout(); navigate('/login'); };

  const tabs = [
    { id: 'costs', label: 'Cost Tracking', icon: DollarSign },
    { id: 'config', label: 'LLM Config', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-50" data-testid="admin-portal">
      <header className="bg-white border-b-6 border-black brutal-shadow-md">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/')} className="p-3 border-4 border-black bg-rose-100 brutal-shadow-sm hover:brutal-shadow-md brutal-active">
                <Home size={24} />
              </button>
              <div>
                <h1 className="text-4xl font-black uppercase flex items-center gap-2">
                  <Cpu size={32} className="text-rose-600" /> Admin Dashboard
                </h1>
                <p className="text-lg font-medium mt-1">{user?.full_name}</p>
              </div>
            </div>
            <BrutalButton variant="dark" onClick={handleLogout} className="flex items-center gap-2">
              <LogOut size={20} /> Logout
            </BrutalButton>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="flex gap-4 mb-8 flex-wrap">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <BrutalButton key={tab.id} variant={activeTab === tab.id ? 'rose' : 'default'} size="lg"
                onClick={() => setActiveTab(tab.id)} className="flex items-center gap-2" data-testid={`tab-${tab.id}`}>
                <Icon size={24} /> {tab.label}
              </BrutalButton>
            );
          })}
        </div>

        {/* Cost Tracking Tab */}
        {activeTab === 'costs' && (
          <div className="space-y-6" data-testid="costs-tab">
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-rose-50 border-4 border-black p-5 brutal-shadow-sm" data-testid="stat-total-cost">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign size={18} className="text-rose-600" />
                  <p className="font-bold text-xs uppercase text-gray-600">Total Cost</p>
                </div>
                <p className="text-3xl font-black">${costs?.total_cost?.toFixed(4) || '0.0000'}</p>
              </div>
              <div className="bg-indigo-50 border-4 border-black p-5 brutal-shadow-sm" data-testid="stat-total-stories">
                <div className="flex items-center gap-2 mb-2">
                  <BarChart3 size={18} className="text-indigo-600" />
                  <p className="font-bold text-xs uppercase text-gray-600">Total Stories</p>
                </div>
                <p className="text-3xl font-black">{costs?.total_stories || 0}</p>
              </div>
              <div className="bg-amber-50 border-4 border-black p-5 brutal-shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <Users size={18} className="text-amber-600" />
                  <p className="font-bold text-xs uppercase text-gray-600">Users</p>
                </div>
                <p className="text-3xl font-black">{costs?.per_user?.length || 0}</p>
              </div>
              <div className="bg-emerald-50 border-4 border-black p-5 brutal-shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <Cpu size={18} className="text-emerald-600" />
                  <p className="font-bold text-xs uppercase text-gray-600">Avg/Story</p>
                </div>
                <p className="text-3xl font-black">
                  ${costs?.total_stories ? (costs.total_cost / costs.total_stories).toFixed(4) : '0.0000'}
                </p>
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Cost per User */}
              <BrutalCard shadow="lg">
                <h3 className="text-xl font-black uppercase mb-4">Cost by User</h3>
                {costs?.per_user?.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={costs.per_user.slice(0, 10)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="user_name" tick={{ fontSize: 11, fontWeight: 700 }} angle={-20} textAnchor="end" height={60} />
                        <YAxis tick={{ fontSize: 12 }} tickFormatter={v => `$${v.toFixed(3)}`} />
                        <Tooltip formatter={v => `$${Number(v).toFixed(4)}`} />
                        <Bar dataKey="total_cost" fill="#6366f1" stroke="#000" strokeWidth={2} radius={[4, 4, 0, 0]} name="Cost" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="text-center py-8 text-gray-500 font-bold">No cost data yet</p>
                )}
              </BrutalCard>

              {/* Cost per Model */}
              <BrutalCard shadow="lg">
                <h3 className="text-xl font-black uppercase mb-4">Cost by Model</h3>
                {costs?.per_model?.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={costs.per_model} cx="50%" cy="50%" outerRadius={80} dataKey="total_cost"
                          label={({ model, total_cost }) => `${model}: $${total_cost.toFixed(4)}`}>
                          {costs.per_model.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="#000" strokeWidth={2} />)}
                        </Pie>
                        <Tooltip formatter={v => `$${Number(v).toFixed(4)}`} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="text-center py-8 text-gray-500 font-bold">No model data yet</p>
                )}
              </BrutalCard>
            </div>

            {/* Recent Logs Table */}
            <BrutalCard shadow="lg">
              <h3 className="text-xl font-black uppercase mb-4">Recent Generation Logs</h3>
              {costs?.recent_logs?.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b-4 border-black">
                        <th className="py-3 px-3 font-black text-xs uppercase">Date</th>
                        <th className="py-3 px-3 font-black text-xs uppercase">Student</th>
                        <th className="py-3 px-3 font-black text-xs uppercase">Model</th>
                        <th className="py-3 px-3 font-black text-xs uppercase">Tokens</th>
                        <th className="py-3 px-3 font-black text-xs uppercase">Cost</th>
                        <th className="py-3 px-3 font-black text-xs uppercase">Time</th>
                        <th className="py-3 px-3 font-black text-xs uppercase">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {costs.recent_logs.map((log, i) => (
                        <tr key={log.id || i} className="border-b-2 border-gray-200" data-testid={`cost-log-${i}`}>
                          <td className="py-2 px-3 text-sm">{new Date(log.created_date).toLocaleDateString()}</td>
                          <td className="py-2 px-3 font-bold text-sm">{log.student_name}</td>
                          <td className="py-2 px-3 text-sm font-mono">{log.model}</td>
                          <td className="py-2 px-3 text-sm">{log.total_tokens}</td>
                          <td className="py-2 px-3 text-sm font-bold">${log.estimated_cost?.toFixed(4)}</td>
                          <td className="py-2 px-3 text-sm">{log.duration_seconds}s</td>
                          <td className="py-2 px-3">
                            <BrutalBadge variant={log.success ? 'emerald' : 'rose'} size="sm">
                              {log.success ? 'OK' : 'FAIL'}
                            </BrutalBadge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-center py-8 text-gray-500 font-bold">No generation logs yet. Costs will appear here after stories are generated.</p>
              )}
            </BrutalCard>
          </div>
        )}

        {/* LLM Config Tab */}
        {activeTab === 'config' && (
          <div className="space-y-6" data-testid="config-tab">
            <BrutalCard shadow="xl" className="max-w-2xl">
              <h3 className="text-2xl font-black uppercase mb-6">LLM Provider Configuration</h3>
              <form onSubmit={(e) => { e.preventDefault(); updateModelMutation.mutate(llmForm); }} className="space-y-6">
                <div>
                  <p className="font-bold text-sm uppercase mb-3">Provider</p>
                  <div className="flex gap-4">
                    <label className={`flex-1 p-4 border-4 border-black cursor-pointer ${llmForm.provider === 'emergent' ? 'bg-indigo-100 brutal-shadow-md' : 'bg-white'}`}>
                      <input type="radio" name="provider" value="emergent" checked={llmForm.provider === 'emergent'}
                        onChange={() => setLlmForm({ ...llmForm, provider: 'emergent', model: 'gpt-5.2' })} className="mr-2" />
                      <span className="font-black text-lg">Emergent LLM</span>
                      <p className="text-sm font-medium text-gray-600 mt-1">Uses Universal Key. Models: GPT-5.2, GPT-4o</p>
                    </label>
                    <label className={`flex-1 p-4 border-4 border-black cursor-pointer ${llmForm.provider === 'openrouter' ? 'bg-emerald-100 brutal-shadow-md' : 'bg-white'}`}>
                      <input type="radio" name="provider" value="openrouter" checked={llmForm.provider === 'openrouter'}
                        onChange={() => setLlmForm({ ...llmForm, provider: 'openrouter', model: 'openrouter/auto' })} className="mr-2" />
                      <span className="font-black text-lg">OpenRouter</span>
                      <p className="text-sm font-medium text-gray-600 mt-1">300+ models including free options</p>
                    </label>
                  </div>
                </div>

                <div>
                  <p className="font-bold text-sm uppercase mb-2">Model</p>
                  {llmForm.provider === 'emergent' ? (
                    <select value={llmForm.model} onChange={(e) => setLlmForm({ ...llmForm, model: e.target.value })}
                      className="w-full border-4 border-black px-4 py-3 font-bold" data-testid="model-select">
                      <option value="gpt-5.2">GPT-5.2 (Best quality, ~$0.04/story)</option>
                      <option value="gpt-4o">GPT-4o (Good quality, ~$0.01/story)</option>
                      <option value="gpt-4o-mini">GPT-4o Mini (Budget, ~$0.001/story)</option>
                    </select>
                  ) : (
                    <div>
                      <select value={llmForm.model} onChange={(e) => setLlmForm({ ...llmForm, model: e.target.value })}
                        className="w-full border-4 border-black px-4 py-3 font-bold mb-2" data-testid="model-select">
                        <option value="openrouter/auto">Auto (Smart routing)</option>
                        <option value="qwen/qwen3-next-80b-a3b-instruct:free">Qwen3 80B (FREE)</option>
                        <option value="openai/gpt-oss-120b:free">GPT-OSS 120B (FREE)</option>
                        <option value="nvidia/nemotron-nano-9b-v2:free">Nemotron Nano 9B (FREE)</option>
                        <option value="stepfun/step-3.5-flash:free">Step 3.5 Flash (FREE)</option>
                        <option value="openai/gpt-4o-mini">GPT-4o Mini ($)</option>
                        <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet ($$)</option>
                      </select>
                      <p className="text-xs font-medium text-gray-500">Free models have rate limits but $0 cost</p>
                    </div>
                  )}
                </div>

                {llmForm.provider === 'openrouter' && (
                  <BrutalInput
                    label="OpenRouter API Key"
                    type="password"
                    value={llmForm.openrouter_key}
                    onChange={(e) => setLlmForm({ ...llmForm, openrouter_key: e.target.value })}
                    placeholder="sk-or-v1-..."
                    data-testid="openrouter-key-input"
                  />
                )}

                <BrutalCard className="bg-amber-50 border-amber-500">
                  <p className="font-bold text-sm">Current Config:</p>
                  <p className="font-mono text-sm mt-1">Provider: {modelConfig?.provider || 'emergent'} | Model: {modelConfig?.model || 'gpt-5.2'}</p>
                </BrutalCard>

                <BrutalButton type="submit" variant="indigo" fullWidth size="lg" disabled={updateModelMutation.isPending} data-testid="save-config-btn">
                  {updateModelMutation.isPending ? 'Saving...' : 'Save Configuration'}
                </BrutalButton>
              </form>
            </BrutalCard>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPortal;
