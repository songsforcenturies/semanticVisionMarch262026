import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { BookOpen } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const HomeHeader = ({ showAuth = true }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <header className="bg-white border-b-6 border-black brutal-shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-3 brutal-active hover:opacity-80 transition-opacity"
          >
            <div className="bg-indigo-500 p-3 border-4 border-black brutal-shadow-sm">
              <BookOpen size={32} className="text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black uppercase leading-none">LexiMaster</h1>
              <p className="text-xs font-bold text-gray-600">{t('common.platform')}</p>
            </div>
          </button>

          <div className="flex gap-3 items-center">
            <LanguageSwitcher />
            {showAuth && (
              <>
                <button
                  onClick={() => navigate('/login')}
                  className="px-4 py-2 border-4 border-black bg-white font-bold uppercase brutal-shadow-sm hover:brutal-shadow-md transition-all brutal-active"
                  data-testid="header-guardian-login"
                >
                  {t('landing.guardianLogin')}
                </button>
                <button
                  onClick={() => navigate('/student-login')}
                  className="px-4 py-2 border-4 border-black bg-amber-400 font-bold uppercase brutal-shadow-sm hover:brutal-shadow-md transition-all brutal-active"
                  data-testid="header-student-login"
                >
                  {t('landing.studentLogin')}
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default HomeHeader;
