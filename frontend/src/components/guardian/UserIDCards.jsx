import React, { useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { userCardAPI } from '@/lib/api';
import { BrutalCard } from '@/components/brutal';
import { Download, CreditCard, Users, BookOpen, Copy, Check } from 'lucide-react';
import { toast } from 'sonner';

const CardFace = ({ data, type }) => {
  const isStudent = type === 'student';
  const bg = isStudent ? 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%)' : 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)';
  const accent = isStudent ? '#818CF8' : '#D4A853';

  return (
    <div
      className="relative w-full max-w-[400px] aspect-[1.6/1] rounded-2xl overflow-hidden select-none"
      style={{ background: bg, border: `2px solid ${accent}40`, boxShadow: `0 8px 32px ${accent}20` }}
      data-testid={`id-card-${type}-${data.name?.replace(/\s/g, '-')}`}
    >
      {/* Subtle pattern */}
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: 'radial-gradient(circle at 25% 25%, white 1px, transparent 1px)',
        backgroundSize: '20px 20px',
      }} />

      {/* Header bar */}
      <div className="relative px-5 pt-4 pb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: `${accent}25`, border: `1px solid ${accent}40` }}>
            {isStudent ? <BookOpen size={16} style={{ color: accent }} /> : <Users size={16} style={{ color: accent }} />}
          </div>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest" style={{ color: `${accent}90` }}>Semantic Vision</p>
            <p className="text-[9px] font-medium" style={{ color: 'rgba(255,255,255,0.4)' }}>{isStudent ? 'Student ID' : 'Member Card'}</p>
          </div>
        </div>
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${accent}15`, border: `1px solid ${accent}30` }}>
          <CreditCard size={18} style={{ color: accent }} />
        </div>
      </div>

      {/* Main content */}
      <div className="relative px-5 pb-4 pt-1">
        <p className="text-white font-black text-lg tracking-wide truncate">{data.name}</p>

        <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1">
          {isStudent ? (
            <>
              <div>
                <p className="text-[9px] font-bold uppercase" style={{ color: `${accent}70` }}>Student Code</p>
                <p className="text-sm font-mono font-black text-white tracking-wider">{data.student_code}</p>
              </div>
              <div>
                <p className="text-[9px] font-bold uppercase" style={{ color: `${accent}70` }}>Reading Level</p>
                <p className="text-sm font-bold text-white capitalize">{data.reading_level}</p>
              </div>
              <div className="col-span-2 mt-1">
                <p className="text-[9px] font-bold uppercase" style={{ color: `${accent}70` }}>Login At</p>
                <p className="text-[11px] font-mono font-medium" style={{ color: 'rgba(255,255,255,0.6)' }}>{data.login_url}</p>
              </div>
            </>
          ) : (
            <>
              <div>
                <p className="text-[9px] font-bold uppercase" style={{ color: `${accent}70` }}>Referral Code</p>
                <p className="text-sm font-mono font-black text-white tracking-wider">{data.referral_code}</p>
              </div>
              <div>
                <p className="text-[9px] font-bold uppercase" style={{ color: `${accent}70` }}>Students</p>
                <p className="text-sm font-bold text-white">{data.student_count}</p>
              </div>
              <div className="col-span-2 mt-1">
                <p className="text-[9px] font-bold uppercase" style={{ color: `${accent}70` }}>Invite Link</p>
                <p className="text-[11px] font-mono font-medium truncate" style={{ color: 'rgba(255,255,255,0.6)' }}>{data.referral_url}</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Bottom accent line */}
      <div className="absolute bottom-0 left-0 right-0 h-1" style={{ background: `linear-gradient(90deg, ${accent}, transparent)` }} />
    </div>
  );
};

const UserIDCards = () => {
  const [copied, setCopied] = React.useState(null);
  const cardRefs = useRef({});

  const { data, isLoading } = useQuery({
    queryKey: ['user-card-data'],
    queryFn: async () => (await userCardAPI.getCardData()).data,
  });

  const copyCode = (code, label) => {
    navigator.clipboard.writeText(code);
    setCopied(label);
    toast.success(`${label} copied!`);
    setTimeout(() => setCopied(null), 2000);
  };

  const downloadCard = async (cardEl, name) => {
    try {
      const { default: html2canvas } = await import('html2canvas');
      const canvas = await html2canvas(cardEl, { scale: 2, backgroundColor: null, useCORS: true });
      const link = document.createElement('a');
      link.download = `${name.replace(/\s/g, '_')}_ID_Card.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      toast.success('Card downloaded!');
    } catch (e) {
      toast.error('Download failed. Try taking a screenshot instead.');
    }
  };

  if (isLoading) return (
    <div className="text-center py-8">
      <div className="animate-spin w-6 h-6 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto mb-2" />
      <p className="font-bold text-gray-500 text-sm">Loading cards...</p>
    </div>
  );

  if (!data) return null;

  return (
    <div className="space-y-6" data-testid="user-id-cards">
      {/* Guardian Card */}
      {data.guardian_card && (
        <BrutalCard shadow="lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-black text-sm uppercase">Your Member Card</h4>
            <div className="flex gap-2">
              <button
                onClick={() => copyCode(data.guardian_card.referral_code, 'Referral code')}
                className="flex items-center gap-1 px-2 py-1 text-xs font-bold bg-gray-100 rounded-lg hover:bg-gray-200 transition-all"
                data-testid="copy-referral-code"
              >
                {copied === 'Referral code' ? <Check size={12} /> : <Copy size={12} />} Code
              </button>
              <button
                onClick={() => cardRefs.current['guardian'] && downloadCard(cardRefs.current['guardian'], data.guardian_card.name)}
                className="flex items-center gap-1 px-2 py-1 text-xs font-bold bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-all"
                data-testid="download-guardian-card"
              >
                <Download size={12} /> Save
              </button>
            </div>
          </div>
          <div ref={el => cardRefs.current['guardian'] = el} className="flex justify-center">
            <CardFace data={data.guardian_card} type="guardian" />
          </div>
        </BrutalCard>
      )}

      {/* Student Cards */}
      {data.student_cards?.map((student, i) => (
        <BrutalCard key={i} shadow="lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-black text-sm uppercase">{student.name}'s Student ID</h4>
            <div className="flex gap-2">
              <button
                onClick={() => copyCode(student.student_code, `${student.name}'s code`)}
                className="flex items-center gap-1 px-2 py-1 text-xs font-bold bg-gray-100 rounded-lg hover:bg-gray-200 transition-all"
                data-testid={`copy-student-code-${i}`}
              >
                {copied === `${student.name}'s code` ? <Check size={12} /> : <Copy size={12} />} Code
              </button>
              <button
                onClick={() => cardRefs.current[`student-${i}`] && downloadCard(cardRefs.current[`student-${i}`], student.name)}
                className="flex items-center gap-1 px-2 py-1 text-xs font-bold bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-all"
                data-testid={`download-student-card-${i}`}
              >
                <Download size={12} /> Save
              </button>
            </div>
          </div>
          <div ref={el => cardRefs.current[`student-${i}`] = el} className="flex justify-center">
            <CardFace data={student} type="student" />
          </div>
        </BrutalCard>
      ))}

      {data.student_cards?.length === 0 && (
        <BrutalCard shadow="md" className="text-center py-6">
          <p className="text-gray-500 font-medium text-sm">No students added yet. Add a student to generate their ID card.</p>
        </BrutalCard>
      )}
    </div>
  );
};

export default UserIDCards;
