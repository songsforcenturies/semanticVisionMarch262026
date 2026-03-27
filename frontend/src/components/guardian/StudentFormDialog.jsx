import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { studentAPI, subscriptionAPI, wordBankAPI } from '@/lib/api';
import { Dialog } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { X, Check, ChevronRight, ChevronLeft, User, Heart, Sparkles, BookOpen, Globe, Camera } from 'lucide-react';

const GRADE_LEVELS = [
  { value: 'pre-k', label: 'Pre-K' },
  { value: 'k', label: 'Kindergarten' },
  ...Array.from({ length: 12 }, (_, i) => ({ value: `${i + 1}`, label: `Grade ${i + 1}` })),
  { value: 'college', label: 'College' },
  { value: 'adult', label: 'Adult' },
];

const LANGUAGES = [
  'English', 'Mandarin Chinese', 'Spanish', 'Hindi', 'Arabic', 'Bengali', 'Portuguese',
  'Russian', 'Japanese', 'Punjabi', 'German', 'Javanese', 'Korean', 'French', 'Turkish',
  'Vietnamese', 'Italian', 'Swahili', 'Malay', 'Thai',
];

const BELIEF_SYSTEMS = [
  '', "Baha'i", 'Buddhist', 'Christian - Baptist', 'Christian - Catholic', 'Christian - Methodist',
  'Christian - Non-Denominational', 'Christian - Orthodox', 'Christian - Pentecostal', 'Christian - Presbyterian',
  'Hindu', 'Islamic - Sunni', 'Islamic - Shia', 'Jewish - Orthodox', 'Jewish - Reform', 'Jewish - Conservative',
  'Sikh', 'Taoist', 'Shinto', 'Indigenous Spiritual', 'Secular / Humanist', 'Other',
];

const CULTURAL_CONTEXTS = [
  'African American', 'African (Sub-Saharan)', 'Arab / Middle Eastern', 'Caribbean',
  'East Asian', 'European', 'Hispanic / Latino', 'Indigenous / Native American',
  'Pacific Islander', 'South Asian', 'Southeast Asian', 'Mixed Heritage', 'Other',
];

const CULTURE_LEARNING_TOPICS = [
  { value: 'black_history', label: 'Black History & Culture', desc: 'African American heritage, leaders, and contributions' },
  { value: 'black_women', label: 'Black Women in History', desc: 'Trailblazing Black women and their achievements' },
  { value: 'hispanic_heritage', label: 'Hispanic Heritage', desc: 'Latino/Latina culture, traditions, and leaders' },
  { value: 'asian_pacific', label: 'Asian & Pacific Islander Heritage', desc: 'Diverse cultures across Asia and the Pacific' },
  { value: 'native_american', label: 'Native American Heritage', desc: 'Indigenous peoples, traditions, and history' },
  { value: 'womens_history', label: "Women's History", desc: 'Women who changed the world across cultures' },
  { value: 'african_culture', label: 'African Culture & History', desc: 'Rich traditions and history across the African continent' },
  { value: 'middle_eastern', label: 'Middle Eastern Culture', desc: 'Ancient civilizations, art, and modern contributions' },
  { value: 'european_history', label: 'European History & Culture', desc: 'European traditions, inventions, and diversity' },
  { value: 'caribbean_culture', label: 'Caribbean Culture', desc: 'Island traditions, music, food, and stories' },
  { value: 'lgbtq_history', label: 'LGBTQ+ History', desc: 'Stories of courage, identity, and acceptance' },
  { value: 'disability_awareness', label: 'Disability Awareness', desc: 'Celebrating abilities and understanding differences' },
  { value: 'world_religions', label: 'World Religions & Spirituality', desc: 'Understanding different faith traditions' },
  { value: 'stem_pioneers', label: 'STEM Pioneers of Color', desc: 'Scientists and innovators from diverse backgrounds' },
  { value: 'civil_rights', label: 'Civil Rights Movement', desc: 'The fight for equality and justice' },
  { value: 'immigration_stories', label: 'Immigration Stories', desc: 'Journeys of courage and new beginnings' },
];

const VIRTUE_OPTIONS = [
  { value: 'patience', label: 'Patience', desc: 'Waiting calmly and handling delays with grace' },
  { value: 'kindness', label: 'Kindness', desc: 'Showing care and compassion toward others' },
  { value: 'honesty', label: 'Honesty', desc: 'Being truthful even when it is difficult' },
  { value: 'courage', label: 'Courage', desc: 'Facing fears and standing up for what is right' },
  { value: 'responsibility', label: 'Responsibility', desc: 'Taking ownership of actions and commitments' },
  { value: 'respect', label: 'Respect', desc: 'Valuing others, their belongings, and their feelings' },
  { value: 'perseverance', label: 'Perseverance', desc: 'Keeping going even when things get hard' },
  { value: 'gratitude', label: 'Gratitude', desc: 'Appreciating what they have and expressing thanks' },
  { value: 'self-control', label: 'Self-Control', desc: 'Managing emotions and impulses thoughtfully' },
  { value: 'generosity', label: 'Generosity', desc: 'Willingness to share and give to others' },
  { value: 'humility', label: 'Humility', desc: 'Staying humble and open to learning from mistakes' },
  { value: 'empathy', label: 'Empathy', desc: 'Understanding and sharing others\' feelings' },
  { value: 'forgiveness', label: 'Forgiveness', desc: 'Letting go of anger and giving second chances' },
  { value: 'fairness', label: 'Fairness', desc: 'Treating everyone equally and playing by the rules' },
  { value: 'trustworthiness', label: 'Trustworthiness', desc: 'Being someone others can rely on and believe in' },
  { value: 'teamwork', label: 'Teamwork', desc: 'Working well with others toward a common goal' },
  { value: 'compassion', label: 'Compassion', desc: 'Deep awareness of others\' suffering and desire to help' },
  { value: 'integrity', label: 'Integrity', desc: 'Doing the right thing even when no one is watching' },
  { value: 'loyalty', label: 'Loyalty', desc: 'Standing by those you care about through thick and thin' },
  { value: 'wisdom', label: 'Wisdom', desc: 'Making thoughtful decisions based on knowledge and experience' },
  { value: 'creativity', label: 'Creativity', desc: 'Thinking outside the box and expressing ideas uniquely' },
  { value: 'diligence', label: 'Diligence', desc: 'Careful and persistent work toward a goal' },
  { value: 'optimism', label: 'Optimism', desc: 'Seeing the bright side and believing things will work out' },
  { value: 'resilience', label: 'Resilience', desc: 'Bouncing back from setbacks and adversity' },
  { value: 'self-discipline', label: 'Self-Discipline', desc: 'Staying focused and doing what needs to be done' },
  { value: 'tolerance', label: 'Tolerance', desc: 'Accepting differences in people and perspectives' },
  { value: 'mindfulness', label: 'Mindfulness', desc: 'Being present and aware of thoughts and surroundings' },
  { value: 'adaptability', label: 'Adaptability', desc: 'Adjusting well to new situations and changes' },
  { value: 'curiosity', label: 'Curiosity', desc: 'Eager desire to learn and explore new things' },
  { value: 'independence', label: 'Independence', desc: 'Thinking and acting for oneself with confidence' },
  { value: 'cooperation', label: 'Cooperation', desc: 'Working harmoniously with others' },
  { value: 'determination', label: 'Determination', desc: 'Firm resolve to achieve goals no matter what' },
];

const EMOTION_OPTIONS = [
  { value: 'joy', label: 'Joy', desc: 'Deep happiness and delight' },
  { value: 'love', label: 'Love', desc: 'Warm affection and deep caring for others' },
  { value: 'hope', label: 'Hope', desc: 'Optimistic expectation for good things ahead' },
  { value: 'pride', label: 'Pride', desc: 'Satisfaction from one\'s own achievements' },
  { value: 'contentment', label: 'Contentment', desc: 'Peaceful satisfaction with what one has' },
  { value: 'excitement', label: 'Excitement', desc: 'Enthusiasm and eagerness about something' },
  { value: 'wonder', label: 'Wonder', desc: 'Amazement and awe at the world around us' },
  { value: 'confidence', label: 'Confidence', desc: 'Trust in one\'s own abilities and worth' },
  { value: 'calm', label: 'Calm', desc: 'Inner peace and tranquility' },
  { value: 'belonging', label: 'Belonging', desc: 'Feeling accepted and part of a group' },
  { value: 'sadness', label: 'Sadness', desc: 'Understanding and processing feelings of loss' },
  { value: 'anger', label: 'Anger', desc: 'Learning to recognize and manage frustration' },
  { value: 'fear', label: 'Fear', desc: 'Acknowledging fears and finding courage within' },
  { value: 'anxiety', label: 'Anxiety', desc: 'Coping with worry and nervous feelings' },
  { value: 'frustration', label: 'Frustration', desc: 'Dealing with things that don\'t go as planned' },
  { value: 'loneliness', label: 'Loneliness', desc: 'Navigating feelings of isolation and finding connection' },
  { value: 'jealousy', label: 'Jealousy', desc: 'Understanding envy and learning to appreciate oneself' },
  { value: 'embarrassment', label: 'Embarrassment', desc: 'Handling moments of self-consciousness with grace' },
  { value: 'disappointment', label: 'Disappointment', desc: 'Processing unmet expectations with maturity' },
  { value: 'guilt', label: 'Guilt', desc: 'Recognizing wrongs and making amends' },
  { value: 'grief', label: 'Grief', desc: 'Processing deep loss and finding healing' },
  { value: 'confusion', label: 'Confusion', desc: 'Navigating uncertainty and finding clarity' },
  { value: 'surprise', label: 'Surprise', desc: 'Handling unexpected events positively' },
  { value: 'sympathy', label: 'Sympathy', desc: 'Feeling concern for others\' misfortunes' },
  { value: 'trust', label: 'Trust', desc: 'Building and maintaining faith in others' },
  { value: 'awe', label: 'Awe', desc: 'Experiencing reverence and wonder' },
  { value: 'relief', label: 'Relief', desc: 'Feeling comfort after stress or worry passes' },
  { value: 'nostalgia', label: 'Nostalgia', desc: 'Bittersweet longing for happy memories' },
  { value: 'determination-emotion', label: 'Determination', desc: 'Strong resolve when facing emotional challenges' },
  { value: 'acceptance', label: 'Acceptance', desc: 'Embracing reality and finding peace with it' },
];

const STEPS = [
  { id: 'basic', label: 'Basic Info', icon: User },
  { id: 'virtues', label: 'Virtues', icon: Heart },
  { id: 'strengths', label: 'Strengths & Growth', icon: Sparkles },
  { id: 'culture', label: 'Faith & Culture', icon: Globe },
  { id: 'banks', label: 'Word Banks', icon: BookOpen },
];

// Dark-themed input component
const DarkInput = ({ label, hint, children, ...props }) => (
  <div>
    {label && <label className="block mb-1.5 text-sm font-semibold text-slate-200">{label}</label>}
    {children || (
      <input
        {...props}
        className="w-full px-4 py-3 rounded-lg text-white bg-slate-800 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-amber-500/60 focus:border-amber-500 placeholder:text-slate-500"
      />
    )}
    {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
  </div>
);

const DarkTextarea = ({ label, hint, ...props }) => (
  <div>
    {label && <label className="block mb-1.5 text-sm font-semibold text-slate-200">{label}</label>}
    <textarea
      {...props}
      className="w-full px-4 py-3 rounded-lg text-white bg-slate-800 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-amber-500/60 focus:border-amber-500 placeholder:text-slate-500 resize-none"
    />
    {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
  </div>
);

const DarkSelect = ({ label, hint, children, ...props }) => (
  <div>
    {label && <label className="block mb-1.5 text-sm font-semibold text-slate-200">{label}</label>}
    <select
      {...props}
      className="w-full px-4 py-3 rounded-lg text-white bg-slate-800 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-amber-500/60 focus:border-amber-500"
    >
      {children}
    </select>
    {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
  </div>
);

const StudentFormDialog = ({ isOpen, onClose, student, guardianId, focusOnBanks = false }) => {
  const queryClient = useQueryClient();
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState({
    full_name: '', age: '', grade_level: '', interests: '',
    virtues: [], strengths: '', weaknesses: '',
    assigned_banks: [], belief_system: '', cultural_context: [], custom_heritage: '',
    language: 'English', culture_learning: [],
  });

  const { data: subscription } = useQuery({
    queryKey: ['subscription', guardianId],
    queryFn: async () => (await subscriptionAPI.get(guardianId)).data,
    enabled: !!guardianId && isOpen,
  });

  const { data: availableBanks = [] } = useQuery({
    queryKey: ['available-banks'],
    queryFn: async () => (await wordBankAPI.getAll({})).data,
    enabled: isOpen,
  });

  useEffect(() => {
    if (!isOpen) return;
    if (student) {
      setFormData({
        full_name: student.full_name || '', age: student.age?.toString() || '',
        grade_level: student.grade_level || '', interests: student.interests?.join(', ') || '',
        virtues: student.virtues || [], strengths: student.strengths || '',
        weaknesses: student.weaknesses || '', assigned_banks: student.assigned_banks || [],
        belief_system: student.belief_system || '',
        cultural_context: Array.isArray(student.cultural_context) ? student.cultural_context : (student.cultural_context ? [student.cultural_context] : []),
        custom_heritage: student.custom_heritage || '',
        language: student.language || 'English',
        culture_learning: student.culture_learning || [],
      });
      setStep(focusOnBanks ? 4 : 0);
    } else {
      setFormData({
        full_name: '', age: '', grade_level: '', interests: '',
        virtues: [], strengths: '', weaknesses: '',
        assigned_banks: [], belief_system: '', cultural_context: [], custom_heritage: '',
        language: 'English', culture_learning: [],
      });
      setStep(0);
    }
  }, [student, isOpen, focusOnBanks]);

  const createMutation = useMutation({
    mutationFn: (data) => studentAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['students']);
      queryClient.invalidateQueries(['subscription']);
      toast.success('Student created successfully!');
      onClose();
    },
    onError: (error) => toast.error(error.response?.data?.detail || 'Failed to create student'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => studentAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['students']);
      toast.success('Student updated successfully!');
      onClose();
    },
    onError: (error) => toast.error(error.response?.data?.detail || 'Failed to update student'),
  });

  const assignBanksMutation = useMutation({
    mutationFn: ({ studentId, bankIds }) => wordBankAPI.assignToStudent(studentId, bankIds),
    onSuccess: () => {
      queryClient.invalidateQueries(['students']);
      toast.success('Word banks assigned!');
    },
    onError: (error) => toast.error(error.response?.data?.detail || 'Failed to assign banks'),
  });

  const handleSubmit = () => {
    const interestsArray = formData.interests.split(',').map(i => i.trim()).filter(Boolean);
    const virtuesArray = Array.isArray(formData.virtues) ? formData.virtues : formData.virtues.split(',').map(v => v.trim()).filter(Boolean);
    const submitData = {
      full_name: formData.full_name, age: formData.age ? parseInt(formData.age) : null,
      grade_level: formData.grade_level || null, interests: interestsArray, virtues: virtuesArray,
      guardian_id: guardianId, belief_system: formData.belief_system,
      cultural_context: formData.cultural_context, custom_heritage: formData.custom_heritage,
      language: formData.language, culture_learning: formData.culture_learning,
      strengths: formData.strengths, weaknesses: formData.weaknesses,
    };
    if (student) {
      const { guardian_id, ...updateData } = submitData;
      updateMutation.mutate({ id: student.id, data: updateData });
    } else {
      createMutation.mutate(submitData);
    }
  };

  const handleBankToggle = (bankId) => {
    setFormData(prev => ({
      ...prev,
      assigned_banks: prev.assigned_banks.includes(bankId)
        ? prev.assigned_banks.filter(id => id !== bankId)
        : [...prev.assigned_banks, bankId],
    }));
  };

  const handleSaveBanks = () => {
    if (student) {
      assignBanksMutation.mutate({ studentId: student.id, bankIds: formData.assigned_banks });
    }
  };

  const handleVirtueToggle = (virtue) => {
    setFormData(prev => {
      const current = Array.isArray(prev.virtues) ? prev.virtues : [];
      return {
        ...prev,
        virtues: current.includes(virtue) ? current.filter(v => v !== virtue) : [...current, virtue],
      };
    });
  };

  const ownedBankIds = subscription?.bank_access || [];
  const ownedBanks = availableBanks.filter(b => ownedBankIds.includes(b.id) || b.visibility === 'global');
  const isLoading = createMutation.isPending || updateMutation.isPending || assignBanksMutation.isPending;
  const isLastStep = step === STEPS.length - 1;
  const canGoNext = step === 0 ? formData.full_name.trim() : true;

  // For existing students, show all steps; for new, skip banks (step 4)
  const maxStep = student ? STEPS.length - 1 : STEPS.length - 2;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.7)' }}>
      <div className="w-full max-w-2xl rounded-2xl overflow-hidden shadow-2xl" style={{ background: '#1A2236', border: '1px solid rgba(212,168,83,0.2)', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}>

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4" style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <h2 className="text-xl font-bold text-white" data-testid="student-form-title">
            {student ? 'Edit Student' : 'Add New Student'}
          </h2>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition" data-testid="close-student-form">
            <X size={20} />
          </button>
        </div>

        {/* Step Indicators */}
        <div className="flex items-center gap-1 px-6 py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          {STEPS.slice(0, maxStep + 1).map((s, i) => {
            const Icon = s.icon;
            const isActive = i === step;
            const isDone = i < step;
            return (
              <React.Fragment key={s.id}>
                {i > 0 && <div className="flex-1 h-px" style={{ background: isDone ? '#D4A853' : 'rgba(255,255,255,0.1)' }} />}
                <button
                  onClick={() => setStep(i)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-all ${
                    isActive ? 'text-black' : isDone ? 'text-amber-400' : 'text-slate-500'
                  }`}
                  style={isActive ? { background: '#D4A853' } : {}}
                  data-testid={`step-${s.id}`}
                >
                  <Icon size={14} />
                  <span className="hidden sm:inline">{s.label}</span>
                </button>
              </React.Fragment>
            );
          })}
        </div>

        {/* Step Content */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5" style={{ minHeight: 0 }}>

          {/* STEP 0: Basic Info */}
          {step === 0 && (
            <>
              {/* Student Photo */}
              <div className="flex items-center gap-4">
                <div className="w-20 h-20 rounded-full overflow-hidden flex-shrink-0 flex items-center justify-center"
                  style={{ background: 'rgba(255,255,255,0.08)', border: '2px solid rgba(212,168,83,0.4)' }}>
                  {student?.photo_url ? (
                    <img src={`${process.env.REACT_APP_BACKEND_URL}${student.photo_url}`} alt={student.full_name}
                      className="w-full h-full object-cover" />
                  ) : (
                    <User size={32} className="text-slate-500" />
                  )}
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-200 mb-1">Student Photo</p>
                  <label className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold bg-purple-600 text-white rounded-lg hover:bg-purple-700 cursor-pointer transition-colors">
                    <Camera size={14} /> {student?.photo_url ? 'Change Photo' : 'Upload Photo'}
                    <input type="file" accept="image/*" className="hidden" onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file || !student) return;
                      try {
                        await studentAPI.uploadPhoto(student.id, file);
                        queryClient.invalidateQueries(['students']);
                        toast.success('Photo uploaded!');
                      } catch (err) {
                        toast.error('Upload failed: ' + (err.response?.data?.detail || err.message));
                      }
                      e.target.value = '';
                    }} />
                  </label>
                  {!student && <p className="text-xs text-slate-500 mt-1">Save student first, then add photo</p>}
                </div>
              </div>

              <DarkInput label="Full Name *" type="text" required value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })} placeholder="John Doe" data-testid="student-name" />
              <div className="grid grid-cols-2 gap-4">
                <DarkInput label="Age" type="number" min="3" max="100" value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: e.target.value })} placeholder="10" />
                <DarkSelect label="Grade Level" value={formData.grade_level}
                  onChange={(e) => setFormData({ ...formData, grade_level: e.target.value })}>
                  <option value="">Select grade...</option>
                  {GRADE_LEVELS.map(g => <option key={g.value} value={g.value}>{g.label}</option>)}
                </DarkSelect>
              </div>
              <DarkTextarea label="Interests (comma-separated)" value={formData.interests}
                onChange={(e) => setFormData({ ...formData, interests: e.target.value })}
                placeholder="space, dinosaurs, robots, science" rows={2}
                hint="Used to personalize AI-generated stories" />
              {student && (
                <div className="rounded-xl p-4" style={{ background: 'rgba(212,168,83,0.08)', border: '1px solid rgba(212,168,83,0.2)' }}>
                  <p className="text-xs font-semibold uppercase text-amber-400 mb-2">Student Login Credentials</p>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Student Code</p>
                      <p className="text-lg font-bold font-mono text-white tracking-wider">{student.student_code}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">PIN</p>
                      <p className="text-lg font-bold font-mono text-white tracking-wider">{student.access_pin}</p>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {/* STEP 1: Virtues & Emotions */}
          {step === 1 && (
            <>
              <div className="rounded-xl p-4" style={{ background: 'rgba(212,168,83,0.06)', border: '1px solid rgba(212,168,83,0.15)' }}>
                <h3 className="text-base font-bold text-amber-400 mb-1">Virtues & Emotional Intelligence</h3>
                <p className="text-sm text-slate-400">Select unlimited virtues and emotions you'd like the AI to weave into your child's stories. You can also add custom ones.</p>
              </div>

              {/* Search */}
              <DarkInput type="text" placeholder="Search virtues & emotions..."
                value={formData._virtueSearch || ''}
                onChange={(e) => setFormData({ ...formData, _virtueSearch: e.target.value })} />

              {/* Selected count */}
              {(Array.isArray(formData.virtues) ? formData.virtues : []).length > 0 && (
                <p className="text-sm text-amber-400 font-medium">
                  {(Array.isArray(formData.virtues) ? formData.virtues : []).length} selected — no limit!
                </p>
              )}

              {/* Custom Virtue Input */}
              <div className="flex gap-2">
                <DarkInput type="text" placeholder="Add a custom virtue or emotion..."
                  value={formData._customVirtue || ''}
                  onChange={(e) => setFormData({ ...formData, _customVirtue: e.target.value })} />
                <button type="button" onClick={() => {
                  const val = (formData._customVirtue || '').trim().toLowerCase();
                  if (val) {
                    handleVirtueToggle(val);
                    setFormData(prev => ({ ...prev, _customVirtue: '' }));
                  }
                }}
                  className="px-4 py-2 rounded-lg text-sm font-bold flex-shrink-0"
                  style={{ background: '#D4A853', color: '#000' }}>
                  Add
                </button>
              </div>

              {/* Virtues Section */}
              <div>
                <p className="text-xs font-bold uppercase text-amber-400 mb-2">Character Virtues</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {VIRTUE_OPTIONS
                    .filter(v => !formData._virtueSearch || v.label.toLowerCase().includes((formData._virtueSearch || '').toLowerCase()))
                    .map(v => {
                    const virtuesArr = Array.isArray(formData.virtues) ? formData.virtues : [];
                    const selected = virtuesArr.includes(v.value);
                    return (
                      <button key={v.value} type="button" onClick={() => handleVirtueToggle(v.value)}
                        className={`flex items-start gap-3 p-3 rounded-xl text-left transition-all ${
                          selected ? 'ring-2 ring-amber-500' : 'hover:bg-white/5'
                        }`}
                        style={{ background: selected ? 'rgba(212,168,83,0.12)' : 'rgba(255,255,255,0.03)', border: '1px solid ' + (selected ? 'rgba(212,168,83,0.4)' : 'rgba(255,255,255,0.06)') }}
                        data-testid={`virtue-${v.value}`}
                      >
                        <div className={`w-5 h-5 mt-0.5 rounded flex-shrink-0 flex items-center justify-center ${
                          selected ? 'bg-amber-500 text-black' : 'border border-slate-600'
                        }`}>
                          {selected && <Check size={14} />}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-white">{v.label}</p>
                          <p className="text-xs text-slate-400 mt-0.5">{v.desc}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Emotions Section */}
              <div>
                <p className="text-xs font-bold uppercase text-sky-400 mb-2">Emotional Intelligence</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {EMOTION_OPTIONS
                    .filter(v => !formData._virtueSearch || v.label.toLowerCase().includes((formData._virtueSearch || '').toLowerCase()))
                    .map(v => {
                    const virtuesArr = Array.isArray(formData.virtues) ? formData.virtues : [];
                    const selected = virtuesArr.includes(v.value);
                    return (
                      <button key={v.value} type="button" onClick={() => handleVirtueToggle(v.value)}
                        className={`flex items-start gap-3 p-3 rounded-xl text-left transition-all ${
                          selected ? 'ring-2 ring-sky-500' : 'hover:bg-white/5'
                        }`}
                        style={{ background: selected ? 'rgba(56,189,248,0.12)' : 'rgba(255,255,255,0.03)', border: '1px solid ' + (selected ? 'rgba(56,189,248,0.4)' : 'rgba(255,255,255,0.06)') }}
                        data-testid={`emotion-${v.value}`}
                      >
                        <div className={`w-5 h-5 mt-0.5 rounded flex-shrink-0 flex items-center justify-center ${
                          selected ? 'bg-sky-500 text-black' : 'border border-slate-600'
                        }`}>
                          {selected && <Check size={14} />}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-white">{v.label}</p>
                          <p className="text-xs text-slate-400 mt-0.5">{v.desc}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </>
          )}

          {/* STEP 2: Strengths & Growth Areas */}
          {step === 2 && (
            <>
              <div className="rounded-xl p-4" style={{ background: 'rgba(56,189,248,0.06)', border: '1px solid rgba(56,189,248,0.15)' }}>
                <h3 className="text-base font-bold text-sky-400 mb-1">Tell us what makes your child special</h3>
                <p className="text-sm text-slate-400">The AI will celebrate their strengths as "superpowers" in stories and gently model growth in their challenge areas — never through shame.</p>
              </div>
              <div className="rounded-xl p-4 space-y-4" style={{ background: 'rgba(56,189,248,0.04)', border: '1px solid rgba(56,189,248,0.1)' }}>
                <DarkTextarea
                  label="Strengths — What your child excels at"
                  value={formData.strengths}
                  onChange={(e) => setFormData({ ...formData, strengths: e.target.value })}
                  placeholder="e.g., Very creative and imaginative. Great at math. Natural leader among friends. Loves helping younger kids."
                  rows={3} data-testid="student-strengths"
                  hint="Story characters will exhibit these as superpowers"
                />
              </div>
              <div className="rounded-xl p-4 space-y-4" style={{ background: 'rgba(212,168,83,0.04)', border: '1px solid rgba(212,168,83,0.1)' }}>
                <DarkTextarea
                  label="Growth Areas — Where your child needs support"
                  value={formData.weaknesses}
                  onChange={(e) => setFormData({ ...formData, weaknesses: e.target.value })}
                  placeholder="e.g., Struggles with patience. Gets frustrated with hard tasks. Needs to work on sharing with siblings."
                  rows={3} data-testid="student-weaknesses"
                  hint="Stories will model growth in these areas with empathy and encouragement"
                />
              </div>
            </>
          )}

          {/* STEP 3: Faith & Culture */}
          {step === 3 && (
            <>
              <div className="rounded-xl p-4" style={{ background: 'rgba(167,139,250,0.06)', border: '1px solid rgba(167,139,250,0.15)' }}>
                <h3 className="text-base font-bold text-violet-400 mb-1">Story Worldview & Culture</h3>
                <p className="text-sm text-slate-400">Stories will reflect your family's faith, heritage, and language. Select as many as apply.</p>
              </div>
              <DarkSelect label="Belief System / Faith" value={formData.belief_system}
                onChange={(e) => setFormData({ ...formData, belief_system: e.target.value })}
                hint="Stories will reflect values from this tradition" data-testid="belief-system-select">
                <option value="">None / Secular</option>
                {BELIEF_SYSTEMS.filter(Boolean).map(b => <option key={b} value={b}>{b}</option>)}
              </DarkSelect>

              {/* Multi-select Heritage */}
              <div>
                <label className="block mb-1.5 text-sm font-semibold text-slate-200">Heritage / Cultural Background</label>
                <p className="text-xs text-slate-400 mb-2">Select all that apply — stories will include elements from each</p>
                <div className="flex flex-wrap gap-2" data-testid="heritage-multi-select">
                  {CULTURAL_CONTEXTS.map(c => {
                    const selected = formData.cultural_context.includes(c);
                    return (
                      <button key={c} type="button"
                        onClick={() => setFormData(prev => ({
                          ...prev,
                          cultural_context: selected ? prev.cultural_context.filter(x => x !== c) : [...prev.cultural_context, c],
                        }))}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${
                          selected ? 'bg-violet-600 border-violet-500 text-white' : 'bg-slate-800 border-slate-600 text-slate-400 hover:border-violet-500'
                        }`}>
                        {c}
                      </button>
                    );
                  })}
                </div>
                <DarkInput label="" placeholder="Write in additional heritage (e.g., Jamaican, Nigerian Yoruba, Creole...)"
                  value={formData.custom_heritage}
                  onChange={(e) => setFormData({ ...formData, custom_heritage: e.target.value })}
                  hint="Separate multiple with commas" data-testid="custom-heritage-input"
                  style={{ marginTop: '8px' }} />
              </div>

              {/* Culture Learning Preferences */}
              <div>
                <label className="block mb-1.5 text-sm font-semibold text-slate-200">Culture Learning Topics</label>
                <p className="text-xs text-slate-400 mb-2">Choose cultures and topics you'd like your child to learn about through stories</p>
                <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto pr-1" data-testid="culture-learning-select">
                  {CULTURE_LEARNING_TOPICS.map(t => {
                    const selected = formData.culture_learning.includes(t.value);
                    return (
                      <button key={t.value} type="button"
                        onClick={() => setFormData(prev => ({
                          ...prev,
                          culture_learning: selected ? prev.culture_learning.filter(x => x !== t.value) : [...prev.culture_learning, t.value],
                        }))}
                        className={`text-left px-3 py-2 rounded-lg text-xs border transition-all ${
                          selected ? 'bg-amber-600/20 border-amber-500/50 text-amber-200' : 'bg-slate-800 border-slate-600 text-slate-400 hover:border-amber-500/50'
                        }`}>
                        <span className="font-bold">{t.label}</span>
                        <span className="block text-[10px] opacity-70 mt-0.5">{t.desc}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <DarkSelect label="Story Language" value={formData.language}
                onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                hint="AI stories will be generated in this language" data-testid="language-select">
                {LANGUAGES.map(l => <option key={l} value={l}>{l}</option>)}
              </DarkSelect>
            </>
          )}

          {/* STEP 4: Word Banks (Edit mode only) */}
          {step === 4 && student && (
            <>
              <div className="rounded-xl p-4" style={{ background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.15)' }}>
                <h3 className="text-base font-bold text-emerald-400 mb-1">Assign Word Banks</h3>
                <p className="text-sm text-slate-400">Select which vocabulary word banks this student will use for their stories. Each bank contains age-appropriate words across baseline, target, and stretch tiers.</p>
              </div>
              {ownedBanks.length === 0 ? (
                <div className="rounded-xl p-6 text-center" style={{ background: 'rgba(212,168,83,0.06)', border: '1px solid rgba(212,168,83,0.15)' }}>
                  <BookOpen size={32} className="mx-auto text-amber-400 mb-3" />
                  <p className="text-sm text-slate-300">No word banks available yet.</p>
                  <p className="text-xs text-slate-500 mt-1">Visit the Word Bank tab to add word banks to your library.</p>
                </div>
              ) : (
                <>
                  <p className="text-sm font-medium text-slate-300">{formData.assigned_banks.length} of {ownedBanks.length} banks selected</p>
                  <div className="grid gap-2">
                    {ownedBanks.map(bank => {
                      const selected = formData.assigned_banks.includes(bank.id);
                      return (
                        <button key={bank.id} type="button" onClick={() => handleBankToggle(bank.id)}
                          className={`flex items-center gap-3 p-4 rounded-xl text-left transition-all ${
                            selected ? 'ring-2 ring-emerald-500' : 'hover:bg-white/5'
                          }`}
                          style={{ background: selected ? 'rgba(16,185,129,0.1)' : 'rgba(255,255,255,0.02)', border: '1px solid ' + (selected ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.06)') }}
                          data-testid={`bank-${bank.id}`}
                        >
                          <div className={`w-6 h-6 rounded flex-shrink-0 flex items-center justify-center ${
                            selected ? 'bg-emerald-500 text-black' : 'border border-slate-600'
                          }`}>
                            {selected && <Check size={16} />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-white truncate">{bank.name}</p>
                            <p className="text-xs text-slate-400">{bank.total_tokens || 0} words &middot; {bank.specialty || bank.category || 'General'}</p>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                  <button type="button" onClick={handleSaveBanks} disabled={assignBanksMutation.isPending}
                    className="w-full py-3 rounded-xl text-sm font-bold transition-all hover:scale-[1.01]"
                    style={{ background: '#10B981', color: 'black' }}
                    data-testid="save-banks-btn">
                    {assignBanksMutation.isPending ? 'Saving...' : 'Save Bank Assignments'}
                  </button>
                </>
              )}
            </>
          )}
        </div>

        {/* Footer Navigation */}
        <div className="flex items-center justify-between px-6 py-4" style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <div className="flex gap-2">
            {step > 0 && (
              <button type="button" onClick={() => setStep(s => s - 1)}
                className="flex items-center gap-1 px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-300 hover:bg-white/5 transition"
                data-testid="wizard-back">
                <ChevronLeft size={16} /> Back
              </button>
            )}
          </div>
          <div className="flex gap-2">
            {!student && step < maxStep && (
              <button type="button" onClick={() => { handleSubmit(); }}
                className="px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-400 hover:text-white hover:bg-white/5 transition"
                data-testid="wizard-skip">
                Skip & Save
              </button>
            )}
            {step < maxStep ? (
              <button type="button" onClick={() => setStep(s => s + 1)} disabled={!canGoNext}
                className="flex items-center gap-1 px-6 py-2.5 rounded-xl text-sm font-bold text-black transition-all hover:scale-[1.02] disabled:opacity-40"
                style={{ background: '#D4A853' }}
                data-testid="wizard-next">
                Next <ChevronRight size={16} />
              </button>
            ) : (
              <button type="button" onClick={handleSubmit} disabled={isLoading || !formData.full_name.trim()}
                className="flex items-center gap-1 px-6 py-2.5 rounded-xl text-sm font-bold text-black transition-all hover:scale-[1.02] disabled:opacity-40"
                style={{ background: '#D4A853' }}
                data-testid="wizard-save">
                {isLoading ? 'Saving...' : student ? 'Update Student' : 'Create Student'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentFormDialog;
