import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { LANGUAGES } from '@/i18n';
import { Globe } from 'lucide-react';

const LanguageSwitcher = ({ className = '' }) => {
  const { i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const current = LANGUAGES.find(l => l.code === i18n.language) || LANGUAGES[0];

  const changeLanguage = (code) => {
    i18n.changeLanguage(code);
    const lang = LANGUAGES.find(l => l.code === code);
    document.documentElement.dir = lang?.dir || 'ltr';
    setOpen(false);
  };

  return (
    <div className={`relative ${className}`} ref={ref} data-testid="language-switcher">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-2 border-4 border-black bg-white font-bold text-sm uppercase brutal-shadow-sm hover:brutal-shadow-md transition-all brutal-active"
        data-testid="language-switcher-btn"
      >
        <Globe size={16} />
        <span className="hidden sm:inline">{current.nativeName}</span>
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-2 w-56 max-h-80 overflow-y-auto bg-white border-4 border-black brutal-shadow-lg z-50" data-testid="language-dropdown">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => changeLanguage(lang.code)}
              className={`w-full text-left px-4 py-2 text-sm font-bold hover:bg-indigo-50 transition-colors flex justify-between items-center ${
                i18n.language === lang.code ? 'bg-indigo-100 text-indigo-700' : ''
              }`}
              data-testid={`lang-${lang.code}`}
            >
              <span>{lang.nativeName}</span>
              <span className="text-xs text-gray-400">{lang.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default LanguageSwitcher;
