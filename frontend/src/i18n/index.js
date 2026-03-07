import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import es from './locales/es.json';
import fr from './locales/fr.json';
import zh from './locales/zh.json';
import hi from './locales/hi.json';
import ar from './locales/ar.json';
import bn from './locales/bn.json';
import pt from './locales/pt.json';
import ru from './locales/ru.json';
import ja from './locales/ja.json';
import de from './locales/de.json';
import ko from './locales/ko.json';
import tr from './locales/tr.json';
import vi from './locales/vi.json';
import it from './locales/it.json';
import th from './locales/th.json';
import pl from './locales/pl.json';
import nl from './locales/nl.json';
import sw from './locales/sw.json';
import ms from './locales/ms.json';

export const LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English', dir: 'ltr' },
  { code: 'es', name: 'Spanish', nativeName: 'Espanol', dir: 'ltr' },
  { code: 'fr', name: 'French', nativeName: 'Francais', dir: 'ltr' },
  { code: 'zh', name: 'Chinese', nativeName: '\u4E2D\u6587', dir: 'ltr' },
  { code: 'hi', name: 'Hindi', nativeName: '\u0939\u093F\u0928\u094D\u0926\u0940', dir: 'ltr' },
  { code: 'ar', name: 'Arabic', nativeName: '\u0627\u0644\u0639\u0631\u0628\u064A\u0629', dir: 'rtl' },
  { code: 'bn', name: 'Bengali', nativeName: '\u09AC\u09BE\u0982\u09B2\u09BE', dir: 'ltr' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Portugues', dir: 'ltr' },
  { code: 'ru', name: 'Russian', nativeName: '\u0420\u0443\u0441\u0441\u043A\u0438\u0439', dir: 'ltr' },
  { code: 'ja', name: 'Japanese', nativeName: '\u65E5\u672C\u8A9E', dir: 'ltr' },
  { code: 'de', name: 'German', nativeName: 'Deutsch', dir: 'ltr' },
  { code: 'ko', name: 'Korean', nativeName: '\uD55C\uAD6D\uC5B4', dir: 'ltr' },
  { code: 'tr', name: 'Turkish', nativeName: 'Turkce', dir: 'ltr' },
  { code: 'vi', name: 'Vietnamese', nativeName: 'Tieng Viet', dir: 'ltr' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano', dir: 'ltr' },
  { code: 'th', name: 'Thai', nativeName: '\u0E44\u0E17\u0E22', dir: 'ltr' },
  { code: 'pl', name: 'Polish', nativeName: 'Polski', dir: 'ltr' },
  { code: 'nl', name: 'Dutch', nativeName: 'Nederlands', dir: 'ltr' },
  { code: 'sw', name: 'Swahili', nativeName: 'Kiswahili', dir: 'ltr' },
  { code: 'ms', name: 'Malay', nativeName: 'Bahasa Melayu', dir: 'ltr' },
];

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      es: { translation: es },
      fr: { translation: fr },
      zh: { translation: zh },
      hi: { translation: hi },
      ar: { translation: ar },
      bn: { translation: bn },
      pt: { translation: pt },
      ru: { translation: ru },
      ja: { translation: ja },
      de: { translation: de },
      ko: { translation: ko },
      tr: { translation: tr },
      vi: { translation: vi },
      it: { translation: it },
      th: { translation: th },
      pl: { translation: pl },
      nl: { translation: nl },
      sw: { translation: sw },
      ms: { translation: ms },
    },
    fallbackLng: 'en',
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'leximaster_lang',
    },
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
