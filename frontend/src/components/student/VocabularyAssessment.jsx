import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { assessmentAPI } from '@/lib/api';
import { BrutalButton, BrutalCard, BrutalInput, BrutalBadge, BrutalProgress } from '@/components/brutal';
import { BookOpen, CheckCircle, XCircle, Award, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

const VocabularyAssessment = ({ narrative, student, onClose }) => {
  const queryClient = useQueryClient();
  const [assessmentId, setAssessmentId] = useState(null);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const wordsToTest = narrative.tokens_to_verify || [];
  const currentWord = wordsToTest[currentWordIndex];
  const totalWords = wordsToTest.length;
  const progress = ((currentWordIndex + 1) / totalWords) * 100;

  // Create assessment mutation
  const createAssessmentMutation = useMutation({
    mutationFn: (data) => assessmentAPI.create(data),
    onSuccess: (response) => {
      setAssessmentId(response.data.id);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create assessment');
    }
  });

  // Start assessment
  React.useEffect(() => {
    if (!assessmentId) {
      createAssessmentMutation.mutate({
        student_id: student.id,
        narrative_id: narrative.id,
        type: "token_verification"
      });
    }
  }, []);

  const handleAnswerChange = (field, value) => {
    setAnswers(prev => ({
      ...prev,
      [currentWord]: {
        ...prev[currentWord],
        word: currentWord,
        [field]: value
      }
    }));
  };

  const handleNext = () => {
    const currentAnswer = answers[currentWord];
    if (!currentAnswer?.definition?.trim() || !currentAnswer?.sentence?.trim()) {
      toast.error('Please provide both a definition and a sentence');
      return;
    }

    if (currentWordIndex < totalWords - 1) {
      setCurrentWordIndex(prev => prev + 1);
    } else {
      // Submit all answers
      handleSubmit();
    }
  };

  const handlePrevious = () => {
    if (currentWordIndex > 0) {
      setCurrentWordIndex(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    // Convert answers object to array
    const answersArray = wordsToTest.map(word => answers[word] || { word, definition: '', sentence: '' });
    
    try {
      const response = await assessmentAPI.evaluate(assessmentId, { answers: answersArray });
      setResults(response.data);
      setShowResults(true);
      
      // Invalidate student data to refresh stats
      queryClient.invalidateQueries(['student-detail']);
      
      toast.success('Assessment evaluated! 🎉');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to evaluate assessment');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!assessmentId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-indigo-50">
        <BrutalCard shadow="xl">
          <p className="text-2xl font-bold">Preparing your assessment...</p>
        </BrutalCard>
      </div>
    );
  }

  if (showResults && results) {
    const masteredCount = results.tokens_mastered?.length || 0;
    const accuracy = results.accuracy_percentage || 0;
    const passed = accuracy >= 80;

    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 p-8">
        <div className="container mx-auto max-w-4xl">
          {/* Results Header */}
          <BrutalCard shadow="xl" className="text-center mb-8">
            <div className="flex justify-center mb-6">
              {passed ? (
                <div className="bg-emerald-100 p-8 border-6 border-black brutal-shadow-xl">
                  <Award size={100} className="text-emerald-600" />
                </div>
              ) : (
                <div className="bg-amber-100 p-8 border-6 border-black brutal-shadow-xl">
                  <BookOpen size={100} className="text-amber-600" />
                </div>
              )}
            </div>

            <h1 className="text-5xl font-black uppercase mb-4">
              {passed ? '🎉 Excellent Work!' : '📚 Keep Learning!'}
            </h1>

            <p className="text-2xl font-bold mb-6">
              You scored {Math.round(accuracy)}%
            </p>

            <div className="grid md:grid-cols-3 gap-4 mb-6">
              <BrutalCard variant="indigo" className="text-center">
                <p className="text-xs font-bold uppercase">Words Tested</p>
                <p className="text-4xl font-black">{totalWords}</p>
              </BrutalCard>
              
              <BrutalCard variant="emerald" className="text-center">
                <p className="text-xs font-bold uppercase">Correct</p>
                <p className="text-4xl font-black">{results.correct_count}</p>
              </BrutalCard>
              
              <BrutalCard variant="amber" className="text-center">
                <p className="text-xs font-bold uppercase">Mastered</p>
                <p className="text-4xl font-black">{masteredCount}</p>
              </BrutalCard>
            </div>

            {passed ? (
              <BrutalCard variant="emerald" className="bg-emerald-100">
                <p className="text-lg font-bold">
                  ✅ You've mastered {masteredCount} new vocabulary words! They've been added to your profile.
                </p>
              </BrutalCard>
            ) : (
              <BrutalCard variant="amber" className="bg-amber-100">
                <p className="text-lg font-bold">
                  💪 You need 80%+ to master these words. Review the feedback below and try again!
                </p>
              </BrutalCard>
            )}
          </BrutalCard>

          {/* Detailed Results */}
          <h2 className="text-3xl font-black uppercase mb-4">Your Answers</h2>
          
          <div className="space-y-4 mb-8">
            {results.questions.map((question, idx) => (
              <BrutalCard
                key={idx}
                shadow="lg"
                variant={question.is_correct ? 'emerald' : 'rose'}
                className={question.is_correct ? 'bg-emerald-50' : 'bg-rose-50'}
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-2xl font-black uppercase">{question.word}</h3>
                  {question.is_correct ? (
                    <BrutalBadge variant="emerald" className="flex items-center gap-1">
                      <CheckCircle size={16} />
                      Correct
                    </BrutalBadge>
                  ) : (
                    <BrutalBadge variant="rose" className="flex items-center gap-1">
                      <XCircle size={16} />
                      Needs Practice
                    </BrutalBadge>
                  )}
                </div>

                <div className="space-y-3">
                  <div>
                    <p className="font-bold text-sm uppercase mb-1">Your Definition:</p>
                    <p className="font-medium">{question.student_definition}</p>
                  </div>

                  <div>
                    <p className="font-bold text-sm uppercase mb-1">Your Sentence:</p>
                    <p className="font-medium italic">"{question.student_sentence}"</p>
                  </div>

                  {question.feedback && (
                    <BrutalCard className="bg-white">
                      <p className="font-bold text-xs uppercase mb-1">Feedback:</p>
                      <p className="font-medium text-sm">{question.feedback}</p>
                    </BrutalCard>
                  )}
                </div>
              </BrutalCard>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <BrutalButton
              variant="indigo"
              size="lg"
              fullWidth
              onClick={onClose}
              className="flex items-center justify-center gap-2"
            >
              <ArrowLeft size={24} />
              Back to Dashboard
            </BrutalButton>
          </div>
        </div>
      </div>
    );
  }

  // Assessment Form
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white border-b-6 border-black brutal-shadow-md sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-black uppercase">Vocabulary Assessment</h1>
              <p className="text-sm font-medium text-gray-600">
                Word {currentWordIndex + 1} of {totalWords}
              </p>
            </div>
            
            <BrutalBadge variant="indigo" size="lg">
              {Math.round(progress)}%
            </BrutalBadge>
          </div>

          <BrutalProgress
            value={currentWordIndex + 1}
            max={totalWords}
            variant="indigo"
          />
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <BrutalCard shadow="xl">
          <div className="mb-6">
            <h2 className="text-4xl font-black uppercase mb-4">{currentWord}</h2>
            <p className="text-lg font-bold text-gray-700">
              Show us you've mastered this word! 📚
            </p>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block mb-3 font-bold uppercase text-sm">
                Write a definition in your own words:
              </label>
              <textarea
                value={answers[currentWord]?.definition || ''}
                onChange={(e) => handleAnswerChange('definition', e.target.value)}
                placeholder="What does this word mean?"
                rows={4}
                className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-indigo-500 resize-none"
              />
            </div>

            <div>
              <label className="block mb-3 font-bold uppercase text-sm">
                Use the word in a sentence:
              </label>
              <textarea
                value={answers[currentWord]?.sentence || ''}
                onChange={(e) => handleAnswerChange('sentence', e.target.value)}
                placeholder="Write a sentence using this word..."
                rows={3}
                className="w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-indigo-500 resize-none"
              />
            </div>
          </div>

          {/* Navigation */}
          <div className="flex gap-4 mt-8">
            {currentWordIndex > 0 && (
              <BrutalButton
                variant="ghost"
                size="lg"
                onClick={handlePrevious}
              >
                ← Previous
              </BrutalButton>
            )}

            <BrutalButton
              variant="indigo"
              size="lg"
              fullWidth
              onClick={handleNext}
              disabled={isSubmitting}
              className="flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin">⏳</div>
                  Evaluating...
                </>
              ) : currentWordIndex === totalWords - 1 ? (
                <>
                  Submit Assessment
                  <CheckCircle size={24} />
                </>
              ) : (
                'Next Word →'
              )}
            </BrutalButton>
          </div>
        </BrutalCard>
      </div>
    </div>
  );
};

export default VocabularyAssessment;
