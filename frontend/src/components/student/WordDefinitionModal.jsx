import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { wordAPI } from '@/lib/api';
import { BrutalCard, BrutalButton, BrutalBadge } from '@/components/brutal';
import { BookOpen, Volume2, X, Loader2 } from 'lucide-react';

const WordDefinitionModal = ({ word, context, onClose }) => {
  const [definition, setDefinition] = useState(null);

  const defineMutation = useMutation({
    mutationFn: () => wordAPI.define(word, context),
    onSuccess: (res) => setDefinition(res.data),
    onError: () => setDefinition({ word, definition: 'Could not load definition. Try again later.', part_of_speech: '', example_sentence: '', synonyms: [] }),
  });

  React.useEffect(() => {
    defineMutation.mutate();
  }, [word]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} className="w-full max-w-md" data-testid="word-definition-modal">
        <BrutalCard shadow="xl" className="bg-white">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <BookOpen size={20} className="text-indigo-600" />
              <h3 className="text-2xl font-black uppercase">{word}</h3>
            </div>
            <button onClick={onClose} className="p-1 border-2 border-black hover:bg-gray-100">
              <X size={18} />
            </button>
          </div>

          {defineMutation.isPending ? (
            <div className="flex items-center justify-center py-8 gap-2">
              <Loader2 size={24} className="animate-spin text-indigo-600" />
              <span className="font-bold">Looking up definition...</span>
            </div>
          ) : definition ? (
            <div className="space-y-3">
              {definition.part_of_speech && (
                <BrutalBadge variant="indigo" size="sm">{definition.part_of_speech}</BrutalBadge>
              )}
              <p className="text-lg font-medium leading-relaxed" data-testid="word-definition">{definition.definition}</p>
              {definition.pronunciation_hint && (
                <p className="text-sm text-gray-500 flex items-center gap-1">
                  <Volume2 size={14} /> /{definition.pronunciation_hint}/
                </p>
              )}
              {definition.example_sentence && (
                <div className="border-l-4 border-indigo-400 pl-3 bg-indigo-50 p-2">
                  <p className="text-sm italic font-medium">"{definition.example_sentence}"</p>
                </div>
              )}
              {definition.synonyms?.length > 0 && (
                <div>
                  <p className="text-xs font-bold uppercase text-gray-500 mb-1">Synonyms</p>
                  <div className="flex flex-wrap gap-1">
                    {definition.synonyms.map((s, i) => (
                      <BrutalBadge key={i} variant="emerald" size="sm">{s}</BrutalBadge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}

          <BrutalButton variant="dark" fullWidth size="md" onClick={onClose} className="mt-4" data-testid="close-definition-btn">
            Got It
          </BrutalButton>
        </BrutalCard>
      </div>
    </div>
  );
};

export default WordDefinitionModal;
