import React, { useState } from 'react';
import { BrutalButton, BrutalCard } from '@/components/brutal';
import { CheckCircle, XCircle } from 'lucide-react';

const VisionCheckModal = ({ visionCheck, chapterNumber, onComplete }) => {
  const [selectedOption, setSelectedOption] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);

  const handleSubmit = () => {
    if (selectedOption === null) return;
    
    const correct = selectedOption === visionCheck.correct_index;
    setIsCorrect(correct);
    setShowResult(true);
  };

  const handleContinue = () => {
    onComplete(isCorrect);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black" style={{ backdropFilter: 'blur(20px)' }}>
      <BrutalCard shadow="xl" className="w-full max-w-2xl bg-white">
        {!showResult ? (
          <>
            {/* Question */}
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-indigo-500 text-white font-black text-2xl w-12 h-12 flex items-center justify-center border-4 border-black">
                  ?
                </div>
                <h2 className="text-2xl font-black uppercase">Comprehension Check</h2>
              </div>
              <p className="text-lg font-bold mb-2">Chapter {chapterNumber} - Vision Check</p>
              <p className="text-xl font-medium">{visionCheck.question}</p>
            </div>

            {/* Options */}
            <div className="space-y-3 mb-6">
              {visionCheck.options.map((option, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedOption(idx)}
                  className={`w-full text-left p-4 border-4 border-black font-bold transition-all brutal-active ${
                    selectedOption === idx
                      ? 'bg-indigo-200 brutal-shadow-md'
                      : 'bg-white hover:bg-gray-50'
                  }`}
                >
                  <span className="inline-block w-8 h-8 border-4 border-black bg-white text-center font-black mr-3">
                    {String.fromCharCode(65 + idx)}
                  </span>
                  {option}
                </button>
              ))}
            </div>

            {/* Submit */}
            <BrutalButton
              variant="indigo"
              size="lg"
              fullWidth
              onClick={handleSubmit}
              disabled={selectedOption === null}
            >
              Submit Answer
            </BrutalButton>
          </>
        ) : (
          <>
            {/* Result */}
            <div className="text-center mb-6">
              <div className="flex justify-center mb-4">
                {isCorrect ? (
                  <div className="bg-emerald-100 p-6 border-6 border-black brutal-shadow-lg">
                    <CheckCircle size={80} className="text-emerald-600" />
                  </div>
                ) : (
                  <div className="bg-rose-100 p-6 border-6 border-black brutal-shadow-lg">
                    <XCircle size={80} className="text-rose-600" />
                  </div>
                )}
              </div>

              <h2 className="text-4xl font-black uppercase mb-4">
                {isCorrect ? '🎉 Correct!' : '❌ Not Quite'}
              </h2>

              <BrutalCard variant={isCorrect ? 'emerald' : 'rose'} className="mb-6">
                <p className="text-lg font-bold">
                  {isCorrect
                    ? 'Great job! You understood the chapter well.'
                    : 'The correct answer was: ' + visionCheck.options[visionCheck.correct_index]}
                </p>
              </BrutalCard>

              {!isCorrect && (
                <BrutalCard className="bg-amber-50 border-amber-500 mb-6">
                  <p className="font-medium text-sm">
                    💡 Try reading the chapter again to better understand the story!
                  </p>
                </BrutalCard>
              )}
            </div>

            {/* Continue */}
            <BrutalButton
              variant={isCorrect ? 'emerald' : 'amber'}
              size="lg"
              fullWidth
              onClick={handleContinue}
            >
              {isCorrect ? 'Continue to Next Chapter →' : 'Read Chapter Again'}
            </BrutalButton>
          </>
        )}
      </BrutalCard>
    </div>
  );
};

export default VisionCheckModal;
