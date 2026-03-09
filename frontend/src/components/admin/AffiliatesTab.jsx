import React, { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { adminAffiliateAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalInput } from '@/components/brutal';
import { DollarSign, CheckCircle, XCircle, Link2, Send } from 'lucide-react';
import { toast } from 'sonner';

const AffiliatesTab = () => {
  const queryClient = useQueryClient();
  const { data: affiliateData } = useQuery({
    queryKey: ['admin-affiliates'],
    queryFn: async () => (await adminAffiliateAPI.getAll()).data,
  });

  const affiliates = affiliateData?.affiliates || [];
  const [affSettingsForm, setAffSettingsForm] = useState({});
  const [payoutId, setPayoutId] = useState(null);
  const [payoutAmount, setPayoutAmount] = useState('');

  useEffect(() => {
    if (affiliateData?.settings) setAffSettingsForm(affiliateData.settings);
  }, [affiliateData]);

  return (
    <div className="space-y-6" data-testid="affiliates-tab">
      {/* Settings Card */}
      <BrutalCard shadow="xl">
        <h3 className="text-2xl font-black uppercase mb-4">Affiliate Program Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="text-xs font-bold uppercase text-gray-500">Default Reward Type</label>
            <select value={affSettingsForm.default_reward_type || 'flat_fee'} onChange={e => setAffSettingsForm({...affSettingsForm, default_reward_type: e.target.value})}
              className="w-full p-3 border-4 border-black font-bold" data-testid="aff-reward-type">
              <option value="flat_fee">Flat Fee</option>
              <option value="percentage">Percentage of Subscription</option>
              <option value="wallet_credits">Wallet Credits</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-bold uppercase text-gray-500">Flat Fee ($)</label>
            <BrutalInput type="number" step="0.01" value={affSettingsForm.default_flat_fee || 5} onChange={e => setAffSettingsForm({...affSettingsForm, default_flat_fee: parseFloat(e.target.value)})} />
          </div>
          <div>
            <label className="text-xs font-bold uppercase text-gray-500">Percentage Rate (%)</label>
            <BrutalInput type="number" step="0.1" value={affSettingsForm.default_percentage || 10} onChange={e => setAffSettingsForm({...affSettingsForm, default_percentage: parseFloat(e.target.value)})} />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="text-xs font-bold uppercase text-gray-500">Wallet Credits ($)</label>
            <BrutalInput type="number" step="0.01" value={affSettingsForm.default_wallet_credits || 5} onChange={e => setAffSettingsForm({...affSettingsForm, default_wallet_credits: parseFloat(e.target.value)})} />
          </div>
          <div>
            <label className="text-xs font-bold uppercase text-gray-500">Min Payout Threshold ($)</label>
            <BrutalInput type="number" step="1" value={affSettingsForm.min_payout_threshold || 25} onChange={e => setAffSettingsForm({...affSettingsForm, min_payout_threshold: parseFloat(e.target.value)})} />
          </div>
          <div className="flex items-end gap-4">
            <label className="flex items-center gap-2 cursor-pointer p-3 border-4 border-black flex-1">
              <input type="checkbox" checked={affSettingsForm.affiliate_program_enabled !== false} onChange={e => setAffSettingsForm({...affSettingsForm, affiliate_program_enabled: e.target.checked})} className="w-5 h-5" />
              <span className="font-bold text-sm">Program Active</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer p-3 border-4 border-black flex-1">
              <input type="checkbox" checked={affSettingsForm.auto_approve !== false} onChange={e => setAffSettingsForm({...affSettingsForm, auto_approve: e.target.checked})} className="w-5 h-5" />
              <span className="font-bold text-sm">Auto-Approve</span>
            </label>
          </div>
        </div>
        <BrutalButton variant="indigo" onClick={async () => {
          try { await adminAffiliateAPI.updateSettings(affSettingsForm); queryClient.invalidateQueries(['admin-affiliates']); toast.success('Settings saved!'); } catch(e) { toast.error('Failed to save'); }
        }} data-testid="save-aff-settings">Save Settings</BrutalButton>
      </BrutalCard>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Affiliates', value: affiliates.length, color: '#6366f1' },
          { label: 'Active', value: affiliates.filter(a => a.is_active).length, color: '#10b981' },
          { label: 'Total Referrals', value: affiliates.reduce((s,a) => s + (a.total_referrals||0), 0), color: '#f59e0b' },
          { label: 'Pending Payouts', value: '$' + affiliates.reduce((s,a) => s + (a.pending_balance||0), 0).toFixed(2), color: '#ef4444' },
        ].map(s => (
          <BrutalCard key={s.label}>
            <p className="text-xs font-bold uppercase text-gray-500">{s.label}</p>
            <p className="text-3xl font-black" style={{color: s.color}}>{s.value}</p>
          </BrutalCard>
        ))}
      </div>

      {/* Affiliates Table */}
      <BrutalCard shadow="xl">
        <h3 className="text-xl font-black uppercase mb-4">All Affiliates ({affiliates.length})</h3>
        {affiliates.length === 0 ? (
          <div className="text-center py-8">
            <Link2 size={40} className="mx-auto mb-3 text-gray-300" />
            <p className="text-gray-500">No affiliates yet. Share the affiliate signup link to grow your network.</p>
            <p className="text-xs text-gray-400 mt-2">Affiliates can sign up at: /register (any registration page)</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead><tr className="border-b-4 border-black">
                <th className="py-2 font-black">Name</th><th className="py-2 font-black">Code</th>
                <th className="py-2 font-black">Reward</th><th className="py-2 font-black">Referrals</th>
                <th className="py-2 font-black">Earned</th><th className="py-2 font-black">Pending</th>
                <th className="py-2 font-black">Status</th><th className="py-2 font-black">Actions</th>
              </tr></thead>
              <tbody>
                {affiliates.map(a => (
                  <tr key={a.id} className="border-b border-gray-200">
                    <td className="py-3"><p className="font-bold">{a.full_name}</p><p className="text-xs text-gray-500">{a.email}</p></td>
                    <td className="py-3 font-mono font-bold text-indigo-600">{a.affiliate_code}</td>
                    <td className="py-3 text-xs">
                      {a.reward_type === 'flat_fee' && `$${a.flat_fee_amount} flat`}
                      {a.reward_type === 'percentage' && `${a.percentage_rate}%`}
                      {a.reward_type === 'wallet_credits' && `$${a.wallet_credit_amount} credits`}
                    </td>
                    <td className="py-3 font-bold">{a.total_referrals || 0}</td>
                    <td className="py-3 font-bold text-emerald-600">${(a.total_earnings||0).toFixed(2)}</td>
                    <td className="py-3 font-bold text-amber-600">${(a.pending_balance||0).toFixed(2)}</td>
                    <td className="py-3">
                      {a.confirmed && a.is_active ? <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded">Active</span>
                      : !a.confirmed ? <span className="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded">Pending</span>
                      : <span className="text-xs font-bold text-red-600 bg-red-50 px-2 py-1 rounded">Inactive</span>}
                    </td>
                    <td className="py-3">
                      <div className="flex gap-1">
                        {!a.confirmed && (
                          <button onClick={async () => { await adminAffiliateAPI.update(a.id, {confirmed:true, is_active:true}); queryClient.invalidateQueries(['admin-affiliates']); toast.success('Approved!'); }}
                            className="p-1 text-emerald-600 hover:bg-emerald-50 rounded" title="Approve"><CheckCircle size={16}/></button>
                        )}
                        <button onClick={async () => { await adminAffiliateAPI.update(a.id, {is_active: !a.is_active}); queryClient.invalidateQueries(['admin-affiliates']); toast.success(a.is_active ? 'Deactivated' : 'Activated'); }}
                          className="p-1 text-gray-600 hover:bg-gray-50 rounded" title={a.is_active ? 'Deactivate' : 'Activate'}>{a.is_active ? <XCircle size={16}/> : <CheckCircle size={16}/>}</button>
                        {(a.pending_balance||0) > 0 && (
                          <button onClick={() => { setPayoutId(a.id); setPayoutAmount(a.pending_balance.toFixed(2)); }}
                            className="p-1 text-indigo-600 hover:bg-indigo-50 rounded" title="Record Payout"><DollarSign size={16}/></button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </BrutalCard>

      {/* Payout Modal */}
      {payoutId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setPayoutId(null)}>
          <div className="bg-white p-6 border-4 border-black shadow-xl max-w-sm w-full" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-black mb-4">Record Payout</h3>
            <BrutalInput type="number" step="0.01" value={payoutAmount} onChange={e => setPayoutAmount(e.target.value)} placeholder="Amount" />
            <div className="flex gap-2 mt-4">
              <BrutalButton variant="indigo" onClick={async () => {
                try { await adminAffiliateAPI.payout(payoutId, { amount: parseFloat(payoutAmount) }); queryClient.invalidateQueries(['admin-affiliates']); toast.success('Payout recorded!'); setPayoutId(null); } catch(e) { toast.error(e.response?.data?.detail || 'Failed'); }
              }}>Confirm Payout</BrutalButton>
              <BrutalButton variant="outline" onClick={() => setPayoutId(null)}>Cancel</BrutalButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AffiliatesTab;
