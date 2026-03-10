import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, LogOut, Menu, X } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import NotificationBell from '@/components/NotificationBell';

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

const AppShell = ({ children, title, subtitle, onLogout, rightContent, showLogo = true, isStudent = false, studentId = null }) => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen sv-dark" style={{ background: C.bg, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Header */}
      <header className="sticky top-0 z-50" style={{ background: C.surface, borderBottom: '1px solid rgba(212,168,83,0.15)' }}>
        <div className="container mx-auto px-3 sm:px-4 py-3">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 sm:gap-4 min-w-0">
              {showLogo && (
                <button onClick={() => navigate('/')} className="flex items-center gap-2 sm:gap-3 group flex-shrink-0" data-testid="app-logo">
                  <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg flex items-center justify-center transition-transform group-hover:scale-105" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }}>
                    <Eye size={18} className="text-black sm:hidden" />
                    <Eye size={22} className="text-black hidden sm:block" />
                  </div>
                  <span className="text-base sm:text-lg font-bold tracking-tight hidden md:block" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>
                    Semantic Vision
                  </span>
                </button>
              )}
              {(title || subtitle) && (
                <div className="min-w-0 ml-1 sm:ml-2" style={{ borderLeft: '1px solid rgba(255,255,255,0.1)', paddingLeft: '8px' }}>
                  {title && <h1 className="text-sm sm:text-lg font-bold truncate" style={{ color: C.cream }} data-testid="portal-title">{title}</h1>}
                  {subtitle && <p className="text-xs truncate hidden sm:block" style={{ color: C.muted }} data-testid="welcome-user">{subtitle}</p>}
                </div>
              )}
            </div>

            {/* Desktop actions */}
            <div className="hidden md:flex items-center gap-3 flex-shrink-0">
              {rightContent}
              <NotificationBell isStudent={isStudent} studentId={studentId} />
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

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg flex-shrink-0"
              style={{ color: C.muted, background: 'rgba(255,255,255,0.04)' }}
              data-testid="mobile-menu-btn"
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>

          {/* Mobile dropdown menu */}
          {mobileMenuOpen && (
            <div className="md:hidden mt-3 pt-3 pb-2 space-y-2" style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}>
              {rightContent && <div className="flex flex-wrap gap-2">{rightContent}</div>}
              <div className="flex items-center justify-between pt-2">
                <div className="flex items-center gap-2">
                  <NotificationBell isStudent={isStudent} studentId={studentId} />
                  <LanguageSwitcher />
                </div>
                {onLogout && (
                  <button onClick={onLogout}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold"
                    style={{ color: C.muted, border: '1px solid rgba(255,255,255,0.1)' }}
                    data-testid="logout-btn-mobile">
                    <LogOut size={16} /> Logout
                  </button>
                )}
              </div>
            </div>
          )}
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
