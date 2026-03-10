import React, { useState, useEffect } from 'react';
import { X, ChevronRight, ChevronLeft, Check } from 'lucide-react';

const C = {
  bg: '#0A0F1E',
  card: '#1A2236',
  surface: '#111827',
  gold: '#D4A853',
  goldLight: '#F5D799',
  teal: '#38BDF8',
  cream: '#F8F5EE',
  muted: '#94A3B8',
  border: 'rgba(255,255,255,0.08)',
};

const OnboardingWizard = ({ steps, portalType, userId, onComplete }) => {
  const storageKey = `sv_onboarding_${portalType}_${userId}`;
  const [visible, setVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [direction, setDirection] = useState('next');

  useEffect(() => {
    const seen = localStorage.getItem(storageKey);
    if (!seen) setVisible(true);
  }, [storageKey]);

  const dismiss = () => {
    localStorage.setItem(storageKey, 'true');
    setVisible(false);
    onComplete?.();
  };

  const next = () => {
    if (currentStep < steps.length - 1) {
      setDirection('next');
      setCurrentStep((s) => s + 1);
    } else {
      dismiss();
    }
  };

  const prev = () => {
    if (currentStep > 0) {
      setDirection('prev');
      setCurrentStep((s) => s - 1);
    }
  };

  if (!visible || !steps?.length) return null;

  const step = steps[currentStep];
  const isLast = currentStep === steps.length - 1;
  const Icon = step.icon;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center overflow-y-auto p-4"
      style={{ background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)' }}
      data-testid="onboarding-wizard-overlay"
    >
      <div
        className="relative w-full max-w-lg rounded-2xl overflow-hidden my-auto"
        style={{
          background: C.card,
          border: `1px solid ${C.border}`,
          boxShadow: `0 0 60px rgba(212,168,83,0.08), 0 8px 32px rgba(0,0,0,0.4)`,
          maxHeight: '90vh',
          overflowY: 'auto',
        }}
        data-testid="onboarding-wizard-modal"
      >
        {/* Skip button */}
        <button
          onClick={dismiss}
          className="absolute top-3 right-3 z-10 flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all hover:scale-105"
          style={{
            color: C.muted,
            background: 'rgba(255,255,255,0.06)',
            border: `1px solid ${C.border}`,
          }}
          data-testid="onboarding-skip-btn"
        >
          Skip <X size={14} />
        </button>

        {/* Step indicator bar */}
        <div className="px-4 sm:px-6 pt-5 pb-0">
          <div className="flex gap-1.5">
            {steps.map((_, i) => (
              <div
                key={i}
                className="h-1 rounded-full flex-1 transition-all duration-500"
                style={{
                  background: i <= currentStep
                    ? `linear-gradient(90deg, ${C.gold}, ${C.goldLight})`
                    : 'rgba(255,255,255,0.08)',
                }}
                data-testid={`onboarding-step-indicator-${i}`}
              />
            ))}
          </div>
          <p className="text-xs mt-2" style={{ color: C.muted }}>
            Step {currentStep + 1} of {steps.length}
          </p>
        </div>

        {/* Content */}
        <div className="px-4 sm:px-6 pt-4 pb-2" style={{ minHeight: 220 }}>
          <div
            key={currentStep}
            className="animate-in fade-in-0 duration-300"
            style={{
              animationDirection: direction === 'next' ? 'normal' : 'reverse',
            }}
          >
            {/* Icon */}
            <div
              className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl flex items-center justify-center mb-4"
              style={{
                background: `linear-gradient(135deg, ${C.gold}22, ${C.gold}08)`,
                border: `1px solid ${C.gold}30`,
              }}
            >
              <Icon size={24} style={{ color: C.gold }} />
            </div>

            {/* Title */}
            <h2
              className="text-lg sm:text-xl font-bold mb-2"
              style={{ color: C.cream }}
              data-testid="onboarding-step-title"
            >
              {step.title}
            </h2>

            {/* Description */}
            <p
              className="text-sm leading-relaxed mb-4"
              style={{ color: C.muted }}
              data-testid="onboarding-step-description"
            >
              {step.description}
            </p>

            {/* Tips / bullet points */}
            {step.tips?.length > 0 && (
              <ul className="space-y-2">
                {step.tips.map((tip, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <div
                      className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                      style={{ background: `${C.gold}18` }}
                    >
                      <Check size={12} style={{ color: C.gold }} />
                    </div>
                    <span className="text-sm" style={{ color: C.cream, opacity: 0.85 }}>
                      {tip}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Footer navigation */}
        <div
          className="px-4 sm:px-6 py-4 flex items-center justify-between"
          style={{ borderTop: `1px solid ${C.border}` }}
        >
          <button
            onClick={prev}
            disabled={currentStep === 0}
            className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-all"
            style={{
              color: currentStep === 0 ? 'rgba(148,163,184,0.3)' : C.muted,
              background: currentStep === 0 ? 'transparent' : 'rgba(255,255,255,0.04)',
              cursor: currentStep === 0 ? 'not-allowed' : 'pointer',
            }}
            data-testid="onboarding-prev-btn"
          >
            <ChevronLeft size={16} /> Back
          </button>

          <button
            onClick={next}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-bold transition-all hover:scale-105 active:scale-95"
            style={{
              background: `linear-gradient(135deg, ${C.gold}, ${C.goldLight})`,
              color: '#000',
              boxShadow: `0 2px 12px ${C.gold}30`,
            }}
            data-testid="onboarding-next-btn"
          >
            {isLast ? (
              <>
                Get Started <Check size={16} />
              </>
            ) : (
              <>
                Next <ChevronRight size={16} />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;
