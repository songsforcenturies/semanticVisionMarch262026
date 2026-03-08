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

/* ── tiny animation helpers ─── */
const fadeUp = { hidden: { opacity: 0, y: 40 }, visible: { opacity: 1, y: 0 } };
const fadeIn = { hidden: { opacity: 0 }, visible: { opacity: 1 } };
const stagger = { visible: { transition: { staggerChildren: 0.15 } } };

function Section({ children, className = '', id }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });
  return (
    <motion.section
      ref={ref}
      id={id}
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      variants={stagger}
      className={className}
    >
      {children}
    </motion.section>
  );
}

/* ── images ─── */
const HERO_IMG = 'https://static.prod-images.emergentagent.com/jobs/d53a056c-422b-4e0c-b8e4-a07558693bb6/images/03582229e0be380a6c098b8a96ab41371358a0238fa5c0c58dea3cb93237dfc0.png';
const BRAND_IMG = 'https://static.prod-images.emergentagent.com/jobs/d53a056c-422b-4e0c-b8e4-a07558693bb6/images/d3738f3eb2b980bba13007153d4e26065736f898b6c7a7fccabfabd70d2d4c0f.png';
const CULTURE_IMG = 'https://static.prod-images.emergentagent.com/jobs/d53a056c-422b-4e0c-b8e4-a07558693bb6/images/535aaa1914ba5e98959665413a19273c5d5d9cb4a349b3c5d6d04f77b0ce7fbb.png';

/* ── color tokens ─── */
const C = {
  bg: '#0A0F1E',
  surface: '#111827',
  card: '#1A2236',
  gold: '#D4A853',
  goldLight: '#F5D799',
  teal: '#38BDF8',
  cream: '#F8F5EE',
  muted: '#94A3B8',
  white: '#FFFFFF',
};

const LandingPage = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", background: C.bg, color: C.cream }} className="min-h-screen overflow-x-hidden">

      {/* ════════════ NAVBAR ════════════ */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl" style={{ background: 'rgba(10,15,30,0.85)', borderBottom: '1px solid rgba(212,168,83,0.12)' }}>
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          <button onClick={() => navigate('/')} className="flex items-center gap-3 group" data-testid="nav-logo">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }}>
              <Eye size={22} className="text-black" />
            </div>
            <span className="text-xl font-bold tracking-tight" style={{ fontFamily: "'Sora', sans-serif", color: C.cream }}>
              Semantic Vision
            </span>
          </button>
          <div className="flex items-center gap-3">
            <LanguageSwitcher />
            <button
              onClick={() => navigate('/login')}
              className="hidden sm:inline-flex px-5 py-2.5 rounded-full text-sm font-semibold transition-all duration-300 hover:scale-105"
              style={{ color: C.gold, border: `1.5px solid ${C.gold}` }}
              data-testid="nav-login-btn"
            >
              Sign In
            </button>
            <button
              onClick={() => navigate('/register')}
              className="px-5 py-2.5 rounded-full text-sm font-bold text-black transition-all duration-300 hover:scale-105 hover:shadow-lg"
              style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}
              data-testid="nav-get-started-btn"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* ════════════ HERO ════════════ */}
      <Section className="relative pt-32 pb-20 sm:pt-40 sm:pb-32" id="hero">
        {/* Background glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-1/4 w-96 h-96 rounded-full opacity-20 blur-3xl" style={{ background: C.gold }} />
          <div className="absolute bottom-0 right-1/4 w-72 h-72 rounded-full opacity-10 blur-3xl" style={{ background: C.teal }} />
        </div>

        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left — copy */}
            <div>
              <motion.div variants={fadeUp} className="mb-6">
                <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase" style={{ background: 'rgba(212,168,83,0.12)', color: C.gold, border: `1px solid rgba(212,168,83,0.25)` }}>
                  <Sparkles size={14} /> Patented AI Technology
                </span>
              </motion.div>

              <motion.h1
                variants={fadeUp}
                className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-[1.08] tracking-tight mb-8"
                style={{ fontFamily: "'Sora', sans-serif" }}
                data-testid="landing-title"
              >
                If glasses are for your{' '}
                <span style={{ color: C.teal }}>eyes</span>,<br />
                words are vision for your{' '}
                <span className="relative inline-block">
                  <span style={{ color: C.gold }}>mind</span>
                  <span className="absolute -bottom-1 left-0 right-0 h-1 rounded-full" style={{ background: `linear-gradient(90deg, ${C.gold}, transparent)` }} />
                </span>.
              </motion.h1>

              <motion.p variants={fadeUp} className="text-base sm:text-lg leading-relaxed mb-10 max-w-lg" style={{ color: C.muted }}>
                Semantic Vision generates personalized AI stories that teach vocabulary, reflect your family's culture and values, and seamlessly weave real brands as problem-solving heroes inside the narrative.
              </motion.p>

              <motion.div variants={fadeUp} className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full mb-8" style={{ background: 'rgba(56,189,248,0.1)', border: '1px solid rgba(56,189,248,0.25)' }}>
                <Globe size={18} style={{ color: C.teal }} />
                <span className="text-sm font-semibold" style={{ color: C.teal }}>Your child can learn in 20+ languages</span>
              </motion.div>

              <motion.div variants={fadeUp} className="flex flex-wrap gap-4">
                <button
                  onClick={() => navigate('/register')}
                  className="group flex items-center gap-2 px-7 py-3.5 rounded-full text-base font-bold text-black transition-all duration-300 hover:scale-105 hover:shadow-2xl"
                  style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}
                  data-testid="get-started-btn"
                >
                  Start Free <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
                </button>
                <button
                  onClick={() => navigate('/login')}
                  className="flex items-center gap-2 px-7 py-3.5 rounded-full text-base font-semibold transition-all duration-300 hover:scale-105"
                  style={{ color: C.cream, border: `1.5px solid rgba(248,245,238,0.2)`, background: 'rgba(255,255,255,0.04)' }}
                  data-testid="guardian-login-btn"
                >
                  Parent / School Login
                </button>
              </motion.div>

              {/* Quick links */}
              <motion.div variants={fadeUp} className="flex flex-wrap gap-4 mt-6 text-sm" style={{ color: C.muted }}>
                <button onClick={() => navigate('/student-login')} className="hover:underline flex items-center gap-1" data-testid="student-login-btn">
                  <GraduationCap size={14} /> Student Login
                </button>
                <button onClick={() => navigate('/teacher-login')} className="hover:underline flex items-center gap-1" data-testid="teacher-login-link">
                  <Users size={14} /> Teacher Login
                </button>
                <button onClick={() => navigate('/donate')} className="hover:underline flex items-center gap-1" data-testid="donate-link">
                  <Heart size={14} /> Sponsor a Reader
                </button>
                <button onClick={() => navigate('/register?role=brand_partner')} className="hover:underline flex items-center gap-1" data-testid="brand-partner-link">
                  <Megaphone size={14} /> Brand Partners
                </button>
              </motion.div>
            </div>

            {/* Right — hero image */}
            <motion.div variants={fadeIn} transition={{ duration: 0.8 }} className="relative flex justify-center lg:justify-end">
              <div className="relative w-full max-w-lg">
                <div className="absolute -inset-4 rounded-3xl opacity-30 blur-2xl" style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.teal})` }} />
                <img
                  src={HERO_IMG}
                  alt="Child reading as words become stars"
                  className="relative rounded-2xl w-full object-cover shadow-2xl"
                  style={{ border: `1px solid rgba(212,168,83,0.2)` }}
                />
              </div>
            </motion.div>
          </div>
        </div>
      </Section>

      {/* ════════════ STATS BAR ════════════ */}
      <Section className="py-12" style={{ background: C.surface, borderTop: `1px solid rgba(255,255,255,0.05)`, borderBottom: `1px solid rgba(255,255,255,0.05)` }}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { val: '20+', label: 'Languages' },
              { val: '5', label: 'User Roles' },
              { val: '60/30/10', label: 'Learning Tiers' },
              { val: '50+', label: 'Currencies' },
            ].map((s, i) => (
              <motion.div key={i} variants={fadeUp}>
                <div className="text-3xl sm:text-4xl font-extrabold" style={{ fontFamily: "'Sora', sans-serif", color: C.gold }}>{s.val}</div>
                <div className="text-sm mt-1" style={{ color: C.muted }}>{s.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* ════════════ PHILOSOPHY ════════════ */}
      <Section className="py-24 sm:py-32" id="philosophy">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-6" style={{ color: C.teal }}>
            Our Philosophy
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight mb-8" style={{ fontFamily: "'Sora', sans-serif" }}>
            See the whole world with{' '}
            <span style={{ color: C.gold }}>Semantic Vision</span>
          </motion.h2>
          <motion.p variants={fadeUp} className="text-base sm:text-lg leading-relaxed mx-auto max-w-2xl" style={{ color: C.muted }}>
            Reading increases vocabulary. Vocabulary is how you understand the world — it's{' '}
            <em style={{ color: C.cream }}>vision for your mind</em>. Semantic Vision harnesses AI to build that vision, one personalized story at a time — stories that honor who you are, where you come from, and what you believe.
          </motion.p>
        </div>
      </Section>

      {/* ════════════ HOW IT WORKS ════════════ */}
      <Section className="py-24 sm:py-32" id="how-it-works" style={{ background: C.surface }}>
        <div className="max-w-7xl mx-auto px-6">
          <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4 text-center" style={{ color: C.teal }}>
            How It Works
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold text-center mb-16" style={{ fontFamily: "'Sora', sans-serif" }}>
            Three steps to a new world of words
          </motion.h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Users size={28} />,
                step: '01',
                title: 'Build a Profile',
                desc: 'Tell us about your child — age, interests, belief system, cultural background, and language. We listen deeply.',
              },
              {
                icon: <Brain size={28} />,
                step: '02',
                title: 'AI Generates Your Story',
                desc: 'Our engine picks vocabulary from the 60/30/10 tier system, selects eligible brand sponsors, and builds a 5-chapter story personalized to your child.',
              },
              {
                icon: <Eye size={28} />,
                step: '03',
                title: 'Read, Learn, See More',
                desc: 'Your child reads chapters, answers comprehension checks, masters new words — and gains vision to see the whole world.',
              },
            ].map((item, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                className="relative p-8 rounded-2xl transition-all duration-300 hover:-translate-y-1 group"
                style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }}
              >
                <div className="absolute top-6 right-6 text-5xl font-black opacity-10" style={{ fontFamily: "'Sora', sans-serif", color: C.gold }}>{item.step}</div>
                <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-6 transition-all group-hover:scale-110" style={{ background: 'rgba(212,168,83,0.12)', color: C.gold }}>
                  {item.icon}
                </div>
                <h3 className="text-xl font-bold mb-3" style={{ fontFamily: "'Sora', sans-serif" }}>{item.title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: C.muted }}>{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* ════════════ INNOVATION: BRAND INTEGRATION ════════════ */}
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
              <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4" style={{ color: C.gold }}>
                Patent-Pending Technology
              </motion.p>
              <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold leading-tight mb-6" style={{ fontFamily: "'Sora', sans-serif" }}>
                Brands become <span style={{ color: C.teal }}>heroes</span> inside the story
              </motion.h2>
              <motion.p variants={fadeUp} className="text-base leading-relaxed mb-8" style={{ color: C.muted }}>
                Our AI doesn't show ads. It weaves real products into the narrative as solutions to problems the characters face. A character needs healthy energy? A real snack brand saves the day. Need to build something? A real tool brand appears naturally. It's education meets ethical sponsorship — and it's unlike anything else on the market.
              </motion.p>
              <motion.ul variants={stagger} className="space-y-4">
                {[
                  'Guardian consent required — you control what your child sees',
                  'Age-appropriate filtering and category blocking',
                  'Real-time budget tracking and impression economics',
                  'Products appear as narrative solutions, never as ads',
                ].map((item, i) => (
                  <motion.li key={i} variants={fadeUp} className="flex items-start gap-3 text-sm" style={{ color: C.cream }}>
                    <Check size={18} className="mt-0.5 flex-shrink-0" style={{ color: C.teal }} />
                    {item}
                  </motion.li>
                ))}
              </motion.ul>
            </div>
          </div>
        </div>
      </Section>

      {/* ════════════ INNOVATION: CULTURAL AWARENESS ════════════ */}
      <Section className="py-24 sm:py-32" style={{ background: C.surface }}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="order-2 lg:order-1">
              <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4" style={{ color: C.gold }}>
                Every Family, Every Faith
              </motion.p>
              <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold leading-tight mb-6" style={{ fontFamily: "'Sora', sans-serif" }}>
                Stories that honor <span style={{ color: C.gold }}>who you are</span>
              </motion.h2>
              <motion.p variants={fadeUp} className="text-base leading-relaxed mb-8" style={{ color: C.muted }}>
                Semantic Vision is the only platform where your child's stories reflect their belief system, cultural heritage, and mother tongue. Whether your family observes Ramadan, celebrates Diwali, honors the Sabbath, or embraces secular humanism — the AI adapts the narrative's values, settings, and lessons accordingly.
              </motion.p>
              <motion.div variants={stagger} className="grid grid-cols-2 gap-4">
                {[
                  { icon: <Globe size={20} />, label: '20+ languages' },
                  { icon: <Shield size={20} />, label: 'Belief-system aware' },
                  { icon: <Layers size={20} />, label: 'Cultural context' },
                  { icon: <Star size={20} />, label: 'Virtue education' },
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

      {/* ════════════ STRENGTHS & WEAKNESSES ════════════ */}
      <Section className="py-24 sm:py-32" id="personalized">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4" style={{ color: C.gold }}>
                Truly Personalized
              </motion.p>
              <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold leading-tight mb-6" style={{ fontFamily: "'Sora', sans-serif" }}>
                Stories that know your child's{' '}
                <span style={{ color: C.teal }}>superpowers</span> and help them{' '}
                <span style={{ color: C.gold }}>grow</span>
              </motion.h2>
              <motion.p variants={fadeUp} className="text-base leading-relaxed mb-6" style={{ color: C.muted }}>
                As a parent, you know your child better than anyone. You know they're brilliant at art but struggle with patience. You know they lead their friends but need help sharing. Semantic Vision lets you tell the AI exactly that.
              </motion.p>
              <motion.p variants={fadeUp} className="text-base leading-relaxed mb-8" style={{ color: C.muted }}>
                The AI weaves your child's <strong style={{ color: C.cream }}>strengths</strong> into the story as the hero's superpowers — and gently models growth in their <strong style={{ color: C.cream }}>weak areas</strong> through the character's journey. Combined with their interests, beliefs, culture, vocabulary goals, and even real brand products — every story is as unique as your child.
              </motion.p>
              <motion.div variants={stagger} className="space-y-3">
                {[
                  { label: 'Strengths become the hero\'s superpowers', color: C.teal },
                  { label: 'Growth areas are modeled with empathy, never shame', color: C.gold },
                  { label: 'Combined with beliefs, culture, interests & vocabulary', color: C.teal },
                  { label: 'Every story is one-of-a-kind — just like your child', color: C.gold },
                ].map((item, i) => (
                  <motion.div key={i} variants={fadeUp} className="flex items-center gap-3 text-sm" style={{ color: C.cream }}>
                    <Check size={18} className="flex-shrink-0" style={{ color: item.color }} />
                    {item.label}
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

      {/* ════════════ 60/30/10 SYSTEM ════════════ */}
      <Section className="py-24 sm:py-32" id="system">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4" style={{ color: C.teal }}>
            Vocabulary Science
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold mb-6" style={{ fontFamily: "'Sora', sans-serif" }}>
            The <span style={{ color: C.gold }}>60 / 30 / 10</span> Learning System
          </motion.h2>
          <motion.p variants={fadeUp} className="text-base mb-16 max-w-2xl mx-auto" style={{ color: C.muted }}>
            Every story distributes vocabulary across three tiers — reinforcing mastery, building growth, and inspiring aspiration.
          </motion.p>

          <motion.div variants={stagger} className="grid md:grid-cols-3 gap-6">
            {[
              { pct: '60%', tier: 'Baseline', color: C.teal, desc: 'Foundation words your child already knows — reinforced for lasting mastery.' },
              { pct: '30%', tier: 'Target', color: C.gold, desc: 'Growth words just above their level — the sweet spot for learning.' },
              { pct: '10%', tier: 'Stretch', color: '#EC4899', desc: 'Challenge words that inspire curiosity and expand the horizon.' },
            ].map((t, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                className="p-8 rounded-2xl text-center transition-all hover:-translate-y-1"
                style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }}
              >
                <div className="text-5xl font-extrabold mb-2" style={{ fontFamily: "'Sora', sans-serif", color: t.color }}>{t.pct}</div>
                <div className="text-lg font-bold mb-3" style={{ fontFamily: "'Sora', sans-serif" }}>{t.tier}</div>
                <p className="text-sm leading-relaxed" style={{ color: C.muted }}>{t.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </Section>

      {/* ════════════ FOR EVERYONE ════════════ */}
      <Section className="py-24 sm:py-32" style={{ background: C.surface }}>
        <div className="max-w-7xl mx-auto px-6">
          <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-[0.2em] mb-4 text-center" style={{ color: C.teal }}>
            Built For Everyone
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold text-center mb-16" style={{ fontFamily: "'Sora', sans-serif" }}>
            One platform, many perspectives
          </motion.h2>

          <motion.div variants={stagger} className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: <Shield size={24} />,
                title: 'Parents & Schools',
                desc: 'Manage students, assign word banks, control ad preferences, track progress, earn referral rewards.',
                action: () => navigate('/register'),
                color: C.gold,
              },
              {
                icon: <GraduationCap size={24} />,
                title: 'Students',
                desc: 'Read AI stories, master vocabulary through comprehension checks, and level up your vision of the world.',
                action: () => navigate('/student-login'),
                color: C.teal,
              },
              {
                icon: <BookOpen size={24} />,
                title: 'Teachers',
                desc: 'Create live classroom sessions, track cohort progress, and run real-time vocabulary exercises over WebSocket.',
                action: () => navigate('/teacher-login'),
                color: '#A78BFA',
              },
              {
                icon: <Megaphone size={24} />,
                title: 'Brand Partners',
                desc: 'Fund education while marketing ethically. Your products appear as story solutions, not banner ads.',
                action: () => navigate('/register?role=brand_partner'),
                color: '#F472B6',
              },
            ].map((r, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                onClick={r.action}
                className="p-6 rounded-2xl cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-xl group"
                style={{ background: C.card, border: '1px solid rgba(255,255,255,0.06)' }}
                data-testid={`role-card-${i}`}
              >
                <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-5 transition-all group-hover:scale-110" style={{ background: `${r.color}18`, color: r.color }}>
                  {r.icon}
                </div>
                <h3 className="text-lg font-bold mb-2" style={{ fontFamily: "'Sora', sans-serif" }}>{r.title}</h3>
                <p className="text-sm leading-relaxed mb-4" style={{ color: C.muted }}>{r.desc}</p>
                <span className="inline-flex items-center gap-1 text-sm font-semibold transition-all group-hover:gap-2" style={{ color: r.color }}>
                  Enter <ChevronRight size={14} />
                </span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </Section>

      {/* ════════════ CTA ════════════ */}
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
                Give your child the gift of <span style={{ color: C.gold }}>vision</span>
              </h2>
              <p className="text-base mb-8 max-w-md mx-auto" style={{ color: C.muted }}>
                Join thousands of families who are building vocabulary through personalized, culturally respectful AI stories.
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <button
                  onClick={() => navigate('/register')}
                  className="group flex items-center gap-2 px-8 py-4 rounded-full text-base font-bold text-black transition-all duration-300 hover:scale-105 hover:shadow-2xl"
                  style={{ background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})` }}
                  data-testid="cta-get-started-btn"
                >
                  Get Started Free <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
                </button>
                <button
                  onClick={() => navigate('/donate')}
                  className="flex items-center gap-2 px-8 py-4 rounded-full text-base font-semibold transition-all duration-300 hover:scale-105"
                  style={{ color: C.cream, border: `1.5px solid rgba(248,245,238,0.2)`, background: 'rgba(255,255,255,0.04)' }}
                  data-testid="cta-sponsor-btn"
                >
                  <Heart size={18} /> Sponsor a Reader
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </Section>

      {/* ════════════ FOOTER ════════════ */}
      <footer className="py-10" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Eye size={18} style={{ color: C.gold }} />
            <span className="text-sm font-semibold" style={{ fontFamily: "'Sora', sans-serif" }}>Semantic Vision</span>
          </div>
          <p className="text-sm" style={{ color: C.muted }}>
            &copy; 2026 Semantic Vision. Building vocabulary, one story at a time.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
