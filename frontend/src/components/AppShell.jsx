import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, LogOut } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const C = {
  bg: '#0A0F1E',
  surface: '#111827',
  card: '#1A2236',
  gold: '#D4A853',
  goldLight: '#F5D799',
  teal: '#38BDF8',
  cream: '#F8F5EE',
  muted: '#94A3B8',
};

const AppShell = ({ children, title, subtitle, onLogout, rightContent, showLogo = true }) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen sv-dark" style={{ background: C.bg, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Header */}
      <header className="sticky top-0 z-50" style={{ background: C.surface, borderBottom: '1px solid rgba(212,168,83,0.15)' }}>
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {showLogo && (
                <button onClick={() => navigate('/')} className="flex items-center gap-3 group" data-testid="app-logo">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center transition-transform group-hover:scale-105" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }}>
                    <Eye size={22} className="text-black" />
                  </div>
                  <span className="text-lg font-bold tracking-tight hidden sm:block" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>
                    Semantic Vision
                  </span>
                </button>
              )}
              {(title || subtitle) && (
                <div className="ml-2" style={{ borderLeft: '1px solid rgba(255,255,255,0.1)', paddingLeft: '16px' }}>
                  {title && <h1 className="text-lg font-bold" style={{ color: C.cream }} data-testid="portal-title">{title}</h1>}
                  {subtitle && <p className="text-xs" style={{ color: C.muted }} data-testid="welcome-user">{subtitle}</p>}
                </div>
              )}
            </div>
            <div className="flex items-center gap-3">
              {rightContent}
              <LanguageSwitcher />
              {onLogout && (
                <button onClick={onLogout}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all hover:scale-105"
                  style={{ color: C.muted, border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.04)' }}
                  data-testid="logout-btn">
                  <LogOut size={16} /> Logout
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main>
        {children}
      </main>
    </div>
  );
};

export { AppShell, C as theme };
export default AppShell;
