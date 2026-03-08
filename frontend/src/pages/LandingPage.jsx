import React, { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion, useInView } from 'framer-motion';
import {
  BookOpen, Eye, Sparkles, Users, GraduationCap, Shield,
  Globe, ArrowRight, ChevronRight, Brain, Layers, Heart,
  Megaphone, Zap, TrendingUp, Star, Check
} from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const fadeUp = { hidden: { opacity: 0, y: 40 }, visible: { opacity: 1, y: 0 } };
const fadeIn = { hidden: { opacity: 0 }, visible: { opacity: 1 } };
const stagger = { visible: { transition: { staggerChildren: 0.15 } } };

function Section({ children, className = '', id }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });
  return (
    <motion.section ref={ref} id={id} initial="hidden" animate={inView ? 'visible' : 'hidden'} variants={stagger} className={className}>
      {children}
    </motion.section>
  );
}

const HERO_IMG = 'https://static.prod-images.emergentagent.com/jobs/d53a056c-422b-4e0c-b8e4-a07558693bb6/images/03582229e0be380a6c098b8a96ab41371358a0238fa5c0c58dea3cb93237dfc0.png';
const BRAND_IMG = 'https://static.prod-images.emergentagent.com/jobs/a7f4a6e3-cc2b-4b52-b065-85c816bf5f24/images/fab4bc5cad3f11db957dba9d1ea3837612ddd3a1a1acf696e4acabcb3be81e9e.png';
const CULTURE_IMG = 'https://static.prod-images.emergentagent.com/jobs/d53a056c-422b-4e0c-b8e4-a07558693bb6/images/535aaa1914ba5e98959665413a19273c5d5d9cb4a349b3c5d6d04f77b0ce7fbb.png';

const C = {
  bg: '#0A0F1E', surface: '#111827', card: '#1A2236',
  gold: '#D4A853', goldLight: '#F5D799', teal: '#38BDF8',
  cream: '#F8F5EE', muted: '#94A3B8', white: '#FFFFFF',
};

const LandingPage = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", background: C.bg, color: C.cream }} className="min-h-screen overflow-x-hidden">

      {/* NAVBAR */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl" style={{ background: 'rgba(10,15,30,0.85)', borderBottom: '1px solid rgba(212,168,83,0.12)' }}>
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          <button onClick={() => navigate('/')} className="flex items-center gap-3 group" data-testid="nav-logo">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }}>
              <Eye size={22} className="text-black" />
            </div>
            <span className="text-xl font-bold tracking-tight" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>
              {t('landing.title')}
            </span>
          </button>
          <div className="flex items-center gap-3">
            <LanguageSwitcher />
            <button onClick={() => navigate('/login')} className="hidden sm:inline-flex px-5 py-2.5 rounded-full text-sm font-semibold transition-all duration-300 hover:scale-105" style={{ color: C.gold, border: `1.5px solid ${C.gold}` }} data-testid="nav-login-btn">
              {t('landing.signIn')}
            </button>
            <button onClick={() => navigate('/register')} className="px-5 py-2.5 rounded-full text-sm font-bold text-black transition-all duration-300 hover:scale-105 hover:shadow-lg" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }} data-testid="nav-get-started-btn">
              {t('landing.getStarted')}
            </button>
          </div>
        </div>
      </nav>

      {/* HERO */}
      <Section className="relative pt-32 pb-20 sm:pt-40 sm:pb-32" id="hero">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-1/4 w-96 h-96 rounded-full opacity-20 blur-3xl" style={{ background: C.gold }} />
          <div className="absolute bottom-0 right-1/4 w-72 h-72 rounded-full opacity-10 blur-3xl" style={{ background: C.teal }} />
        </div>
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <motion.div variants={fadeUp} className="mb-6">
                <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase" style={{ background: 'rgba(212,168,83,0.12)', color: C.gold, border: '1px solid rgba(212,168,83,0.25)' }}>
                  <Sparkles size={14} /> {t('landing.patentedAI')}
                </span>
              </motion.div>
              <motion.h1 variants={fadeUp} className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-[1.08] tracking-tight mb-8" style={{ fontFamily: "'Sora', sans-serif" }} data-testid="landing-title">
                {t('landing.heroLine1')}{' '}<span style={{ color: C.teal }}>{t('landing.eyes')}</span>,<br />
                {t('landing.heroLine2')}{' '}
                <span className="relative inline-block">
                  <span style={{ color: C.gold }}>{t('landing.mind')}</span>
                  <span className="absolute -bottom-1 left-0 right-0 h-1 rounded-full" style={{ background: `linear-gradient(90deg, ${C.gold}, transparent)` }} />
                </span>.
              </motion.h1>
              <motion.p variants={fadeUp} className="text-base sm:text-lg leading-relaxed mb-6 max-w-lg" style={{ color: C.muted }}>
                {t('landing.heroDesc')}
              </motion.p>
              <motion.div variants={fadeUp} className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full mb-8" style={{ background: 'rgba(56,189,248,0.1)', border: '1px solid rgba(56,189,248,0.25)' }}>
                <Globe size={18} style={{ color: C.teal }} />
                <span className="text-sm font-semibold" style={{ color: C.teal }}>{t('landing.learnIn20')}</span>
              </motion.div>
              <motion.div variants={fadeUp} className="flex flex-wrap gap-4">
                <button onClick={() => navigate('/register')} className="group flex items-center gap-2 px-7 py-3.5 rounded-full text-base font-bold text-black transition-all duration-300 hover:scale-105 hover:shadow-2xl" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }} data-testid="get-started-btn">
                  {t('landing.getStarted')} <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
                </button>
                <button onClick={() => navigate('/login')} className="flex items-center gap-2 px-7 py-3.5 rounded-full text-base font-semibold transition-all duration-300 hover:scale-105" style={{ color: C.cream, border: '1.5px solid rgba(248,245,238,0.2)', background: 'rgba(255,255,255,0.04)' }} data-testid="guardian-login-btn">
                  {t('landing.guardianLogin')}
                </button>
              </motion.div>
              <motion.div variants={fadeUp} className="flex flex-wrap gap-4 mt-6 text-sm" style={{ color: C.muted }}>
                <button onClick={() => navigate('/student-login')} className="hover:underline flex items-center gap-1" data-testid="student-login-btn"><GraduationCap size={14} /> {t('landing.studentLogin')}</button>
                <button onClick={() => navigate('/teacher-login')} className="hover:underline flex items-center gap-1" data-testid="teacher-login-link"><Users size={14} /> {t('landing.teacherLogin')}</button>
                <button onClick={() => navigate('/donate')} className="hover:underline flex items-center gap-1" data-testid="donate-link"><Heart size={14} /> {t('landing.sponsorReader')}</button>
                <button onClick={() => navigate('/register?role=brand_partner')} className="hover:underline flex items-center gap-1" data-testid="brand-partner-link"><Megaphone size={14} /> {t('landing.brandPartners')}</button>
              </motion.div>
            </div>
            <motion.div variants={fadeIn} transition={{ duration: 0.8 }} className="relative flex justify-center lg:justify-end">
              <div className="relative w-full max-w-lg">
                <div className="absolute -inset-4 rounded-3xl opacity-30 blur-2xl" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }} />
                <img src={HERO_IMG} alt="Child reading as words become stars" className="relative rounded-2xl w-full object-cover shadow-2xl" style={{ border: '1px solid rgba(212,168,83,0.2)' }} />
              </div>
            </motion.div>
          </div>
        </div>
      </Section>

      {/* STATS BAR */}
      <Section className="py-12" style={{ background: C.surface, borderTop: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[{ val: '20+', label: t('landing.languages') }, { val: '5', label: t('landing.userRoles') }, { val: '60/30/10', label: t('landing.learningTiers') }, { val: '50+', label: t('landing.currencies') }].map((s, i) => (
              <motion.div key={i} variants={fadeUp}>
                <div className="text-3xl sm:text-4xl font-extrabold" style={{ fontFamily: "'Sora', sans-serif", color: C.gold }}>{s.val}</div>
                <div className="text-sm mt-1" style={{ color: C.muted }}>{s.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* PHILOSOPHY */}
      <Section className="py-24 sm:py-32" id="philosophy">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-6" style={{ color: C.teal }}>{t('landing.philosophy')}</motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight mb-8" style={{ fontFamily: "'Sora', sans-serif" }}>
            {t('landing.philosophyTitle')}{' '}<span style={{ color: C.gold }}>{t('landing.title')}</span>
          </motion.h2>
          <motion.p variants={fadeUp} className="text-base sm:text-lg leading-relaxed mx-auto max-w-2xl" style={{ color: C.muted }}>
            {t('landing.philosophyDesc')}
          </motion.p>
        </div>
      </Section>

      {/* HOW IT WORKS */}
      <Section className="py-24 sm:py-32" id="how-it-works" style={{ background: C.surface }}>
        <div className="max-w-7xl mx-auto px-6">
          <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4 text-center" style={{ color: C.teal }}>{t('landing.howItWorks')}</motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold text-center mb-16" style={{ fontFamily: "'Sora', sans-serif" }}>{t('landing.howItWorksTitle')}</motion.h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: <Users size={28} />, step: '01', title: t('landing.step1Title'), desc: t('landing.step1Desc') },
              { icon: <Brain size={28} />, step: '02', title: t('landing.step2Title'), desc: t('landing.step2Desc') },
              { icon: <Eye size={28} />, step: '03', title: t('landing.step3Title'), desc: t('landing.step3Desc') },
            ].map((item, i) => (
              <motion.div key={i} variants={fadeUp} className="relative p-8 rounded-2xl transition-all duration-300 hover:-translate-y-1 group" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }}>
                <div className="absolute top-6 right-6 text-5xl font-black opacity-10" style={{ fontFamily: "'Sora', sans-serif", color: C.gold }}>{item.step}</div>
                <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-6 transition-all group-hover:scale-110" style={{ background: 'rgba(212,168,83,0.12)', color: C.gold }}>{item.icon}</div>
                <h3 className="text-xl font-bold mb-3" style={{ fontFamily: "'Sora', sans-serif" }}>{item.title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: C.muted }}>{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* BRAND INTEGRATION */}
      <Section className="py-24 sm:py-32" id="innovation">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <motion.div variants={fadeIn} transition={{ duration: 0.8 }}>
              <div className="relative">
                <div className="absolute -inset-4 rounded-3xl opacity-20 blur-2xl" style={{ background: C.teal }} />
                <img src={BRAND_IMG} alt="Brand integration in stories" className="relative rounded-2xl w-full shadow-2xl" style={{ border: '1px solid rgba(56,189,248,0.15)' }} />
              </div>
            </motion.div>
            <div>
              <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4" style={{ color: C.gold }}>{t('landing.patentPending')}</motion.p>
              <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold leading-tight mb-6" style={{ fontFamily: "'Sora', sans-serif" }}>
                {t('landing.brandsHeroes').split('heroes').map((part, i, arr) => i < arr.length - 1 ? <React.Fragment key={i}>{part}<span style={{ color: C.teal }}>heroes</span></React.Fragment> : part)}
              </motion.h2>
              <motion.p variants={fadeUp} className="text-base leading-relaxed mb-8" style={{ color: C.muted }}>{t('landing.brandsDesc')}</motion.p>
              <motion.ul variants={stagger} className="space-y-4">
                {[t('landing.brandCheck1'), t('landing.brandCheck2'), t('landing.brandCheck3'), t('landing.brandCheck4')].map((item, i) => (
                  <motion.li key={i} variants={fadeUp} className="flex items-start gap-3 text-sm" style={{ color: C.cream }}>
                    <Check size={18} className="mt-0.5 flex-shrink-0" style={{ color: C.teal }} />{item}
                  </motion.li>
                ))}
              </motion.ul>
            </div>
          </div>
        </div>
      </Section>

      {/* CULTURAL AWARENESS */}
      <Section className="py-24 sm:py-32" style={{ background: C.surface }}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="order-2 lg:order-1">
              <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4" style={{ color: C.gold }}>{t('landing.everyFamily')}</motion.p>
              <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold leading-tight mb-6" style={{ fontFamily: "'Sora', sans-serif" }}>
                {t('landing.cultureTitle').split('who you are').map((part, i, arr) => i < arr.length - 1 ? <React.Fragment key={i}>{part}<span style={{ color: C.gold }}>who you are</span></React.Fragment> : part)}
              </motion.h2>
              <motion.p variants={fadeUp} className="text-base leading-relaxed mb-8" style={{ color: C.muted }}>{t('landing.cultureDesc')}</motion.p>
              <motion.div variants={stagger} className="grid grid-cols-2 gap-4">
                {[
                  { icon: <Globe size={20} />, label: t('landing.languagesCount') },
                  { icon: <Shield size={20} />, label: t('landing.beliefAware') },
                  { icon: <Layers size={20} />, label: t('landing.culturalContext') },
                  { icon: <Star size={20} />, label: t('landing.virtueEd') },
                ].map((f, i) => (
                  <motion.div key={i} variants={fadeUp} className="flex items-center gap-3 p-3 rounded-xl" style={{ background: 'rgba(212,168,83,0.06)', border: '1px solid rgba(212,168,83,0.1)' }}>
                    <span style={{ color: C.gold }}>{f.icon}</span>
                    <span className="text-sm font-medium">{f.label}</span>
                  </motion.div>
                ))}
              </motion.div>
            </div>
            <motion.div variants={fadeIn} transition={{ duration: 0.8 }} className="order-1 lg:order-2">
              <div className="relative">
                <div className="absolute -inset-4 rounded-3xl opacity-20 blur-2xl" style={{ background: C.gold }} />
                <img src={CULTURE_IMG} alt="Cultural diversity in learning" className="relative rounded-2xl w-full shadow-2xl" style={{ border: '1px solid rgba(212,168,83,0.15)' }} />
              </div>
            </motion.div>
          </div>
        </div>
      </Section>

      {/* STRENGTHS & WEAKNESSES */}
      <Section className="py-24 sm:py-32" id="personalized">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4" style={{ color: C.gold }}>{t('landing.trulyPersonalized')}</motion.p>
              <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold leading-tight mb-6" style={{ fontFamily: "'Sora', sans-serif" }}>
                {t('landing.superpowersTitle').split('superpowers').map((part, i, arr) => i < arr.length - 1 ? <React.Fragment key={i}>{part}<span style={{ color: C.teal }}>superpowers</span></React.Fragment> : part)}
              </motion.h2>
              <motion.p variants={fadeUp} className="text-base leading-relaxed mb-6" style={{ color: C.muted }}>{t('landing.superpowersDesc1')}</motion.p>
              <motion.p variants={fadeUp} className="text-base leading-relaxed mb-8" style={{ color: C.muted }}>{t('landing.superpowersDesc2')}</motion.p>
              <motion.div variants={stagger} className="space-y-3">
                {[
                  { label: t('landing.superpowerCheck1'), color: C.teal },
                  { label: t('landing.superpowerCheck2'), color: C.gold },
                  { label: t('landing.superpowerCheck3'), color: C.teal },
                  { label: t('landing.superpowerCheck4'), color: C.gold },
                ].map((item, i) => (
                  <motion.div key={i} variants={fadeUp} className="flex items-center gap-3 text-sm" style={{ color: C.cream }}>
                    <Check size={18} className="flex-shrink-0" style={{ color: item.color }} />{item.label}
                  </motion.div>
                ))}
              </motion.div>
            </div>
            <motion.div variants={fadeIn} transition={{ duration: 0.8 }}>
              <div className="p-8 rounded-2xl space-y-4" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.08)' }}>
                <div className="text-sm font-semibold uppercase tracking-wide" style={{ color: C.muted }}>How the AI sees your child</div>
                <div className="p-4 rounded-xl" style={{ background: 'rgba(56,189,248,0.08)', border: '1px solid rgba(56,189,248,0.2)' }}>
                  <div className="text-xs font-bold uppercase mb-2" style={{ color: C.teal }}>Strengths</div>
                  <div className="text-sm" style={{ color: C.cream }}>"Creative and imaginative. Natural leader. Loves helping younger kids."</div>
                </div>
                <div className="p-4 rounded-xl" style={{ background: 'rgba(212,168,83,0.08)', border: '1px solid rgba(212,168,83,0.2)' }}>
                  <div className="text-xs font-bold uppercase mb-2" style={{ color: C.gold }}>Growth Areas</div>
                  <div className="text-sm" style={{ color: C.cream }}>"Struggles with patience. Gets frustrated with hard tasks."</div>
                </div>
                <div className="p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <div className="text-xs font-bold uppercase mb-2" style={{ color: C.muted }}>The AI Creates</div>
                  <div className="text-sm italic" style={{ color: C.cream }}>"Maya used her incredible imagination to design a bridge across the river. When the first attempt collapsed, she felt frustrated — but remembered what Grandma always said: 'Every great creator fails forward.' She took a deep breath, studied the problem, and tried again..."</div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </Section>

      {/* 60/30/10 SYSTEM */}
      <Section className="py-24 sm:py-32" id="system" style={{ background: C.surface }}>
        <div className="max-w-5xl mx-auto px-6 text-center">
          <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4" style={{ color: C.teal }}>{t('landing.vocabScience')}</motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold mb-6" style={{ fontFamily: "'Sora', sans-serif" }}>
            {t('landing.vocabTitle').split('60 / 30 / 10').map((part, i, arr) => i < arr.length - 1 ? <React.Fragment key={i}>{part}<span style={{ color: C.gold }}>60 / 30 / 10</span></React.Fragment> : part)}
          </motion.h2>
          <motion.p variants={fadeUp} className="text-base mb-16 max-w-2xl mx-auto" style={{ color: C.muted }}>{t('landing.vocabDesc')}</motion.p>
          <motion.div variants={stagger} className="grid md:grid-cols-3 gap-6">
            {[
              { pct: '60%', tier: t('landing.baseline'), color: C.teal, desc: t('landing.baselineDesc') },
              { pct: '30%', tier: t('landing.target'), color: C.gold, desc: t('landing.targetDesc') },
              { pct: '10%', tier: t('landing.stretch'), color: '#EC4899', desc: t('landing.stretchDesc') },
            ].map((ti, i) => (
              <motion.div key={i} variants={fadeUp} className="p-8 rounded-2xl text-center transition-all hover:-translate-y-1" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }}>
                <div className="text-5xl font-extrabold mb-2" style={{ fontFamily: "'Sora', sans-serif", color: ti.color }}>{ti.pct}</div>
                <div className="text-lg font-bold mb-3" style={{ fontFamily: "'Sora', sans-serif" }}>{ti.tier}</div>
                <p className="text-sm leading-relaxed" style={{ color: C.muted }}>{ti.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </Section>

      {/* FOR EVERYONE */}
      <Section className="py-24 sm:py-32">
        <div className="max-w-7xl mx-auto px-6">
          <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4 text-center" style={{ color: C.teal }}>{t('landing.builtForEveryone')}</motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold text-center mb-16" style={{ fontFamily: "'Sora', sans-serif" }}>{t('landing.onePlatform')}</motion.h2>
          <motion.div variants={stagger} className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: <Shield size={24} />, title: t('landing.roleParents'), desc: t('landing.roleParentsDesc'), action: () => navigate('/register'), color: C.gold },
              { icon: <GraduationCap size={24} />, title: t('landing.roleStudents'), desc: t('landing.roleStudentsDesc'), action: () => navigate('/student-login'), color: C.teal },
              { icon: <BookOpen size={24} />, title: t('landing.roleTeachers'), desc: t('landing.roleTeachersDesc'), action: () => navigate('/teacher-login'), color: '#A78BFA' },
              { icon: <Megaphone size={24} />, title: t('landing.roleBrands'), desc: t('landing.roleBrandsDesc'), action: () => navigate('/register?role=brand_partner'), color: '#F472B6' },
            ].map((r, i) => (
              <motion.div key={i} variants={fadeUp} onClick={r.action} className="p-6 rounded-2xl cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-xl group" style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }} data-testid={`role-card-${i}`}>
                <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-5 transition-all group-hover:scale-110" style={{ background: `${r.color}18`, color: r.color }}>{r.icon}</div>
                <h3 className="text-lg font-bold mb-2" style={{ fontFamily: "'Sora', sans-serif" }}>{r.title}</h3>
                <p className="text-sm leading-relaxed mb-4" style={{ color: C.muted }}>{r.desc}</p>
                <span className="inline-flex items-center gap-1 text-sm font-semibold transition-all group-hover:gap-2" style={{ color: r.color }}>{t('landing.enter')} <ChevronRight size={14} /></span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </Section>

      {/* CTA */}
      <Section className="py-24 sm:py-32">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <motion.div variants={fadeUp} className="p-12 sm:p-16 rounded-3xl relative overflow-hidden" style={{ background: C.card, border: '1px solid rgba(212,168,83,0.15)' }}>
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
              <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full opacity-10 blur-3xl" style={{ background: C.gold }} />
              <div className="absolute -bottom-20 -left-20 w-64 h-64 rounded-full opacity-10 blur-3xl" style={{ background: C.teal }} />
            </div>
            <div className="relative z-10">
              <Zap size={40} className="mx-auto mb-6" style={{ color: C.gold }} />
              <h2 className="text-3xl sm:text-4xl font-bold mb-4" style={{ fontFamily: "'Sora', sans-serif" }}>
                {t('landing.ctaTitle').split('vision').map((part, i, arr) => i < arr.length - 1 ? <React.Fragment key={i}>{part}<span style={{ color: C.gold }}>vision</span></React.Fragment> : part)}
              </h2>
              <p className="text-base mb-8 max-w-md mx-auto" style={{ color: C.muted }}>{t('landing.ctaDesc')}</p>
              <div className="flex flex-wrap justify-center gap-4">
                <button onClick={() => navigate('/register')} className="group flex items-center gap-2 px-8 py-4 rounded-full text-base font-bold text-black transition-all duration-300 hover:scale-105 hover:shadow-2xl" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }} data-testid="cta-get-started-btn">
                  {t('landing.getStarted')} <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
                </button>
                <button onClick={() => navigate('/register?role=brand_partner')} className="flex items-center gap-2 px-8 py-4 rounded-full text-base font-semibold transition-all duration-300 hover:scale-105" style={{ color: '#F472B6', border: '1.5px solid rgba(244,114,182,0.4)', background: 'rgba(244,114,182,0.06)' }} data-testid="cta-brand-btn">
                  <Megaphone size={18} /> Brand Partners
                </button>
                <button onClick={() => navigate('/donate')} className="flex items-center gap-2 px-8 py-4 rounded-full text-base font-semibold transition-all duration-300 hover:scale-105" style={{ color: C.cream, border: '1.5px solid rgba(248,245,238,0.2)', background: 'rgba(255,255,255,0.04)' }} data-testid="cta-sponsor-btn">
                  <Heart size={18} /> {t('landing.sponsorReader')}
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </Section>

      {/* FOOTER */}
      <footer className="py-10" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Eye size={18} style={{ color: C.gold }} />
            <span className="text-sm font-semibold" style={{ fontFamily: "'Sora', sans-serif" }}>{t('landing.title')}</span>
          </div>
          <p className="text-sm" style={{ color: C.muted }}>&copy; {t('landing.copyright')}</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
