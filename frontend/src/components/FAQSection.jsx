import React, { useState } from 'react';
import { ChevronDown, HelpCircle } from 'lucide-react';

const C = {
  card: '#1A2236',
  gold: '#D4A853',
  cream: '#F8F5EE',
  muted: '#94A3B8',
  border: 'rgba(255,255,255,0.08)',
};

const FAQSection = ({ items, title = 'Frequently Asked Questions' }) => {
  const [openIndex, setOpenIndex] = useState(null);

  const toggle = (i) => setOpenIndex(openIndex === i ? null : i);

  return (
    <div data-testid="faq-section">
      <div className="flex items-center gap-3 mb-5">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ background: `${C.gold}18` }}
        >
          <HelpCircle size={20} style={{ color: C.gold }} />
        </div>
        <h2 className="text-lg font-bold" style={{ color: C.cream }}>
          {title}
        </h2>
      </div>

      <div className="space-y-2">
        {items.map((item, i) => (
          <div
            key={i}
            className="rounded-xl overflow-hidden transition-all"
            style={{
              background: openIndex === i ? 'rgba(212,168,83,0.06)' : C.card,
              border: `1px solid ${openIndex === i ? 'rgba(212,168,83,0.2)' : C.border}`,
            }}
          >
            <button
              onClick={() => toggle(i)}
              className="w-full flex items-center justify-between px-5 py-4 text-left"
              data-testid={`faq-item-${i}`}
            >
              <span
                className="text-sm font-semibold pr-4"
                style={{ color: openIndex === i ? C.gold : C.cream }}
              >
                {item.q}
              </span>
              <ChevronDown
                size={18}
                className="flex-shrink-0 transition-transform duration-300"
                style={{
                  color: C.muted,
                  transform: openIndex === i ? 'rotate(180deg)' : 'rotate(0deg)',
                }}
              />
            </button>
            {openIndex === i && (
              <div className="px-5 pb-4">
                <p className="text-sm leading-relaxed" style={{ color: C.muted }}>
                  {item.a}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default FAQSection;
