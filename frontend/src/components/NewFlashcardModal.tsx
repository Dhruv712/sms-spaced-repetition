import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import TagSelector from './TagSelector';

interface Deck {
  id: number;
  name: string;
  flashcards_count?: number;
}

interface NewFlashcardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  preselectedDeckId?: number | null;
}

type Mode = 'single' | 'batch';

const NewFlashcardModal: React.FC<NewFlashcardModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  preselectedDeckId = null,
}) => {
  const [mode, setMode] = useState<Mode>('single');
  const [concept, setConcept] = useState('');
  const [definition, setDefinition] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [sourceUrl, setSourceUrl] = useState('');
  const [batchText, setBatchText] = useState('');
  const [selectedDeckIds, setSelectedDeckIds] = useState<number[]>([]);
  const [decks, setDecks] = useState<Deck[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const [nlInput, setNlInput] = useState('');
  const [nlLoading, setNlLoading] = useState(false);
  const { token, user } = useAuth();
  const [limits, setLimits] = useState<any>(null);

  const fetchDecks = useCallback(async () => {
    if (!token) return;
    try {
      const response = await axios.get(buildApiUrl('/decks/'), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setDecks(response.data);
      
      // If preselected deck, set it
      if (preselectedDeckId && response.data.find((d: Deck) => d.id === preselectedDeckId)) {
        setSelectedDeckIds([preselectedDeckId]);
      }
    } catch (err) {
      console.error('Error fetching decks:', err);
    }
  }, [token, preselectedDeckId]);

  useEffect(() => {
    if (isOpen) {
      fetchDecks();
      // Reset form when modal opens
      setConcept('');
      setDefinition('');
      setTags([]);
      setSourceUrl('');
      setBatchText('');
      setError('');
      setNlInput('');
      setMode('single');
      if (preselectedDeckId) {
        setSelectedDeckIds([preselectedDeckId]);
      } else {
        setSelectedDeckIds([]);
      }
    }
  }, [isOpen, fetchDecks, preselectedDeckId]);

  useEffect(() => {
    if (!token) return;
    const fetchLimits = async () => {
      try {
        const response = await axios.get(buildApiUrl('/subscription/limits'), {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        setLimits(response.data);
      } catch (err) {
        console.error('Error fetching limits:', err);
      }
    };
    fetchLimits();
  }, [token]);

  const handleSingleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting || !token) return;

    setSubmitting(true);
    setError('');

    try {
      await axios.post(
        buildApiUrl('/flashcards/'),
        {
          concept,
          definition,
          tags: tags,
          deck_id: selectedDeckIds.length === 1 ? selectedDeckIds[0] : null,
          source_url: sourceUrl,
        },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error creating flashcard:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to create flashcard. Please try again.';
      setError(errorMessage);

      if (errorMessage.includes('free tier limit') || errorMessage.includes('Upgrade to Premium')) {
        setTimeout(() => {
          if (window.confirm('You\'ve reached the free tier limit. Would you like to upgrade to Premium?')) {
            window.location.href = '/premium';
          }
        }, 100);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleBatchSubmit = async () => {
    if (processing || !token || !batchText.trim()) return;

    setProcessing(true);
    setError('');

    try {
      const response = await axios.post(
        buildApiUrl('/flashcards/batch-create'),
        {
          raw_text: batchText,
          deck_ids: selectedDeckIds,
        },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (response.data.success) {
        onSuccess();
        onClose();
      } else {
        setError(`Created ${response.data.created_count} cards, but some errors occurred.`);
      }
    } catch (err: any) {
      console.error('Error creating flashcards:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to create flashcards. Please try again.';
      setError(errorMessage);

      if (errorMessage.includes('free tier limit') || errorMessage.includes('Upgrade to Premium')) {
        setTimeout(() => {
          if (window.confirm('You\'ve reached the free tier limit. Would you like to upgrade to Premium?')) {
            window.location.href = '/premium';
          }
        }, 100);
      }
    } finally {
      setProcessing(false);
    }
  };

  const handleNaturalSubmit = async () => {
    if (!token || !nlInput.trim()) return;

    setNlLoading(true);
    setError('');

    try {
      const res = await axios.post(
        buildApiUrl('/natural_flashcards/generate_flashcard'),
        {
          text: nlInput,
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      const { concept: genConcept, definition: genDefinition, tags: receivedTags, source_url } = res.data;
      setConcept(genConcept);
      setDefinition(genDefinition);
      setSourceUrl(source_url || '');
      setTags(
        Array.isArray(receivedTags)
          ? receivedTags
          : typeof receivedTags === 'string'
          ? receivedTags.split(',').map((t: string) => t.trim()).filter((t: string) => t)
          : []
      );
      setNlInput('');
      setMode('single');
    } catch (err) {
      console.error('Error generating flashcard:', err);
      setError('Failed to generate flashcard. Please try again.');
    } finally {
      setNlLoading(false);
    }
  };

  const handleDeckToggle = (deckId: number) => {
    setSelectedDeckIds((prev) =>
      prev.includes(deckId) ? prev.filter((id) => id !== deckId) : [...prev, deckId]
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 dark:bg-opacity-70 overflow-y-auto">
      <div className="bg-white dark:bg-darksurface rounded-lg shadow-xl p-6 max-w-3xl w-full mx-4 my-8 border border-gray-200 dark:border-gray-700 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-darktext">Create Flashcard(s)</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200 rounded">
            {error}
          </div>
        )}

        {/* Mode Toggle */}
        <div className="mb-6 flex gap-2">
          <button
            onClick={() => setMode('single')}
            className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
              mode === 'single'
                ? 'bg-accent text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            Single Card
          </button>
          <button
            onClick={() => setMode('batch')}
            className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
              mode === 'batch'
                ? 'bg-accent text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            Batch from Text
          </button>
        </div>

        {/* Deck Selection (for both modes) */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Deck(s) {mode === 'batch' && '(optional, can select multiple)'}
          </label>
          <div className="space-y-2 max-h-40 overflow-y-auto border border-gray-300 dark:border-gray-600 rounded-lg p-2">
            {decks.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">No decks available. Create a deck first.</p>
            ) : (
              decks.map((deck) => (
                <label
                  key={deck.id}
                  className="flex items-center space-x-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded cursor-pointer"
                >
                  <input
                    type={mode === 'batch' ? 'checkbox' : 'radio'}
                    checked={selectedDeckIds.includes(deck.id)}
                    onChange={() => handleDeckToggle(deck.id)}
                    className="text-accent focus:ring-accent"
                  />
                  <span className="text-sm text-gray-900 dark:text-darktext">
                    {deck.name} {deck.flashcards_count !== undefined ? `(${deck.flashcards_count} cards)` : ''}
                  </span>
                </label>
              ))
            )}
          </div>
        </div>

        {mode === 'single' ? (
          <>
            {/* Natural Language Input (Single Mode) */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Or ask GPT to generate a card:
              </h3>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g., 'make a card for the fundamental theorem of calculus'"
                  value={nlInput}
                  onChange={(e) => setNlInput(e.target.value)}
                  className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600"
                />
                <button
                  type="button"
                  onClick={handleNaturalSubmit}
                  disabled={nlLoading || !token || !nlInput.trim()}
                  className="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 transition-colors"
                >
                  {nlLoading ? 'Generating...' : 'Generate'}
                </button>
              </div>
            </div>

            {/* Manual Single Card Form */}
            <form onSubmit={handleSingleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Concept / Front
                </label>
                <input
                  type="text"
                  placeholder="What you're trying to remember"
                  value={concept}
                  onChange={(e) => setConcept(e.target.value)}
                  required
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Definition / Back
                </label>
                <textarea
                  placeholder="The answer or explanation"
                  value={definition}
                  onChange={(e) => setDefinition(e.target.value)}
                  required
                  rows={4}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600"
                />
                {definition && (
                  <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600">
                    <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                      {definition}
                    </ReactMarkdown>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Source URL (optional)
                </label>
                <input
                  type="text"
                  placeholder="https://..."
                  value={sourceUrl}
                  onChange={(e) => setSourceUrl(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600"
                />
              </div>

              <div>
                <TagSelector selectedTags={tags} onChange={setTags} />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || !token}
                  className="flex-1 px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90 disabled:opacity-50 transition-colors"
                >
                  {submitting ? 'Saving...' : 'Save Flashcard'}
                </button>
              </div>
            </form>
          </>
        ) : (
          <>
            {/* Batch Mode */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Paste your text (lists, notes, etc.)
                </label>
                <textarea
                  placeholder="Example:&#10;Tokyo - Capital of Japan&#10;Paris - Capital of France&#10;&#10;Or:&#10;Japanese words:&#10;こんにちは - Hello&#10;ありがとう - Thank you"
                  value={batchText}
                  onChange={(e) => setBatchText(e.target.value)}
                  rows={12}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600 font-mono text-sm"
                />
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  GPT will automatically parse and structure your text into flashcards.
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleBatchSubmit}
                  disabled={processing || !token || !batchText.trim()}
                  className="flex-1 px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90 disabled:opacity-50 transition-colors"
                >
                  {processing ? 'Processing...' : 'Create Flashcards'}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default NewFlashcardModal;

