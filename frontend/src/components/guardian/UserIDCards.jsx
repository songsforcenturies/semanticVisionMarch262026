import React, { useRef, useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { userCardAPI, studentAPI } from '@/lib/api';
import { BrutalCard } from '@/components/brutal';
import { Download, CreditCard, Users, BookOpen, Copy, Check, Printer, User, Camera } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = import.meta.env.VITE_API_URL || '';

// Compress and resize an image file to 400x400 JPEG before upload
const compressImageFile = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        const maxSize = 400;
        const canvas = document.createElement('canvas');
        canvas.width = maxSize;
        canvas.height = maxSize;
        const ctx = canvas.getContext('2d');
        // Center-crop: pick the largest centered square from the source
        const srcSize = Math.min(img.width, img.height);
        const srcX = (img.width - srcSize) / 2;
        const srcY = (img.height - srcSize) / 2;
        ctx.drawImage(img, srcX, srcY, srcSize, srcSize, 0, 0, maxSize, maxSize);
        canvas.toBlob(
          (blob) => {
            if (!blob) { reject(new Error('Canvas is empty')); return; }
            resolve(new File([blob], file.name.replace(/\.[^.]+$/, '.jpg'), { type: 'image/jpeg' }));
          },
          'image/jpeg',
          0.85
        );
      };
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = reader.result;
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsDataURL(file);
  });
};

const CardFace = ({ data, type, forPrint = false }) => {
  const isStudent = type === 'student';
  const bg = isStudent ? 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%)' : 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)';
  const accent = isStudent ? '#818CF8' : '#D4A853';

  const sizeClass = forPrint
    ? 'w-[3.5in] h-[2in]'
    : 'w-full max-w-[400px] aspect-[1.6/1]';

  return (
    <div
      className={`relative ${sizeClass} rounded-2xl overflow-hidden select-none`}
      style={{ background: bg, border: `2px solid ${accent}40`, boxShadow: forPrint ? 'none' : `0 8px 32px ${accent}20` }}
      data-testid={`id-card-${type}-${data.name?.replace(/\s/g, '-')}`}
    >
      {/* Subtle pattern */}
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: 'radial-gradient(circle at 25% 25%, white 1px, transparent 1px)',
        backgroundSize: '20px 20px',
      }} />

      {/* Header bar */}
      <div className="relative px-4 pt-2 pb-0 flex items-center justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest" style={{ color: `${accent}90` }}>
            {isStudent ? (data.logo_text || 'Semantic Vision') : 'Semantic Vision'}
          </p>
          <p className="text-[9px] font-medium" style={{ color: 'rgba(255,255,255,0.4)' }}>
            {isStudent ? 'Student ID' : 'Member Card'}
            {isStudent && data.year ? ` - ${data.year}` : ''}
          </p>
        </div>
        <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: `${accent}15`, border: `1px solid ${accent}30` }}>
          <CreditCard size={14} style={{ color: accent }} />
        </div>
      </div>

      {/* Main content — two-column layout for students */}
      <div className="relative px-4 pb-2 pt-1 flex gap-3">
        {/* Left side: info */}
        <div className="flex-1 min-w-0">
          <p className="text-white font-black text-base tracking-wide truncate">{data.name}</p>
          <div className="mt-1 grid grid-cols-2 gap-x-3 gap-y-0.5">
            {isStudent ? (
              <>
                <div>
                  <p className="text-[8px] font-bold uppercase" style={{ color: `${accent}70` }}>Student Code</p>
                  <p className="text-xs font-mono font-black text-white tracking-wider">{data.student_code}</p>
                </div>
                <div>
                  <p className="text-[8px] font-bold uppercase" style={{ color: `${accent}70` }}>Grade</p>
                  <p className="text-[10px] font-bold text-white capitalize">{data.grade_level || data.reading_level || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-[8px] font-bold uppercase" style={{ color: `${accent}70` }}>Start Date</p>
                  <p className="text-[10px] font-bold text-white">{data.start_date || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-[8px] font-bold uppercase" style={{ color: `${accent}70` }}>Age</p>
                  <p className="text-[10px] font-bold text-white">{data.age || 'N/A'}</p>
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

        {/* Right side: photo (students only) */}
        {isStudent && (
          <div className="flex-shrink-0 flex items-center">
            <div className="w-16 h-16 rounded-xl overflow-hidden" style={{ border: `2px solid ${accent}50`, background: `${accent}15` }}>
              {data.photo_url ? (
                <img
                  src={data.photo_url.startsWith('data:') ? data.photo_url : `${API_BASE}${data.photo_url}`}
                  alt={data.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <User size={28} style={{ color: `${accent}60` }} />
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Bottom bar with website */}
      <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between px-4 pb-1">
        {isStudent && (
          <p className="text-[8px] font-mono font-medium" style={{ color: `${accent}60` }}>
            {data.website_url || 'semanticvision.ai'}
          </p>
        )}
        <div className="flex-1" />
        <div className="h-[2px] flex-1" style={{ background: `linear-gradient(90deg, transparent, ${accent})` }} />
      </div>
    </div>
  );
};


/* ==================== PRINT VIEW COMPONENT ==================== */

const printStyleId = 'avery-5371-print-styles';

const injectPrintStyles = () => {
  if (document.getElementById(printStyleId)) return;
  const style = document.createElement('style');
  style.id = printStyleId;
  style.textContent = `
    @media print {
      body > *:not(#avery-print-overlay) { display: none !important; }
      #avery-print-overlay {
        display: block !important;
        position: fixed;
        inset: 0;
        z-index: 999999;
        background: white;
        overflow: visible;
      }
      @page {
        size: letter;
        margin: 0.5in 0.75in;
      }
      .avery-grid {
        display: grid !important;
        grid-template-columns: 3.5in 3.5in;
        grid-template-rows: repeat(5, 2in);
        gap: 0;
        width: 7in;
        height: 10in;
        page-break-after: always;
      }
      .avery-cell {
        width: 3.5in;
        height: 2in;
        overflow: hidden;
        box-sizing: border-box;
      }
      .avery-cell > div {
        width: 3.5in !important;
        height: 2in !important;
        max-width: 3.5in !important;
        border-radius: 8px !important;
      }
    }
  `;
  document.head.appendChild(style);
};

const removePrintStyles = () => {
  const el = document.getElementById(printStyleId);
  if (el) el.remove();
};

const PrintAllCards = ({ studentCards, guardianCard }) => {
  const printRef = useRef(null);

  const handlePrint = useCallback(() => {
    injectPrintStyles();
    // Create overlay
    let overlay = document.getElementById('avery-print-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'avery-print-overlay';
      overlay.style.display = 'none';
      document.body.appendChild(overlay);
    }

    // Build all cards: guardian first, then students
    const allCards = [];
    if (guardianCard) {
      allCards.push({ data: guardianCard, type: 'guardian' });
    }
    studentCards.forEach(s => {
      allCards.push({ data: s, type: 'student' });
    });

    // We need to render cards into the overlay using the printRef container
    // Copy the rendered HTML from our hidden container
    if (printRef.current) {
      overlay.innerHTML = printRef.current.innerHTML;
      overlay.style.display = 'block';
    }

    setTimeout(() => {
      window.print();
      setTimeout(() => {
        overlay.style.display = 'none';
        overlay.innerHTML = '';
        removePrintStyles();
      }, 500);
    }, 300);
  }, [studentCards, guardianCard]);

  // Build pages of 10 cards each
  const allCards = [];
  if (guardianCard) {
    allCards.push({ data: guardianCard, type: 'guardian' });
  }
  studentCards.forEach(s => {
    allCards.push({ data: s, type: 'student' });
  });

  const pages = [];
  for (let i = 0; i < allCards.length; i += 10) {
    pages.push(allCards.slice(i, i + 10));
  }

  return (
    <div>
      <button
        onClick={handlePrint}
        className="flex items-center gap-2 px-4 py-2 text-sm font-black uppercase bg-amber-100 text-amber-800 border-3 border-black rounded-xl hover:bg-amber-200 transition-all shadow-brutal-sm"
        data-testid="print-all-cards"
      >
        <Printer size={16} /> Print All Cards (Avery 5371)
      </button>

      {/* Hidden render container for print content */}
      <div ref={printRef} style={{ position: 'absolute', left: '-9999px', top: 0 }}>
        {pages.map((page, pi) => (
          <div key={pi} className="avery-grid">
            {page.map((card, ci) => (
              <div key={ci} className="avery-cell">
                <CardFace data={card.data} type={card.type} forPrint={true} />
              </div>
            ))}
            {/* Fill remaining cells with empty divs to maintain grid */}
            {Array.from({ length: 10 - page.length }).map((_, ei) => (
              <div key={`empty-${ei}`} className="avery-cell" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};


/* ==================== MAIN COMPONENT ==================== */

const UserIDCards = () => {
  const queryClient = useQueryClient();
  const [copied, setCopied] = useState(null);
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
      {/* Print All Cards Button */}
      {(data.student_cards?.length > 0 || data.guardian_card) && (
        <div className="flex justify-end">
          <PrintAllCards
            studentCards={data.student_cards || []}
            guardianCard={data.guardian_card}
          />
        </div>
      )}

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
              <label
                className="flex items-center gap-1 px-2 py-1 text-xs font-bold bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-all cursor-pointer"
                data-testid={`upload-photo-${i}`}
              >
                <Camera size={12} /> Photo
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (!file) return;
                    try {
                      const compressed = await compressImageFile(file);
                      await studentAPI.uploadPhoto(student.student_id || student.id, compressed);
                      queryClient.refetchQueries({ queryKey: ['user-card-data'] });
                      toast.success(`Photo uploaded for ${student.name}`);
                    } catch (err) {
                      toast.error('Photo upload failed: ' + (err.response?.data?.detail || err.message));
                    }
                    e.target.value = '';
                  }}
                />
              </label>
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
