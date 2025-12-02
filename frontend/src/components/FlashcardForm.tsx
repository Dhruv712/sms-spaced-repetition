import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import TagSelector from './TagSelector';

interface Props {
  onSuccess: () => void;
}

interface Deck {
  id: number;
  name: string;
  flashcards_count?: number;
}

const FlashcardForm: React.FC<Props> = ({ onSuccess }) => {
  const [concept, setConcept] = useState('');
  const [definition, setDefinition] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [nlInput, setNlInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [decks, setDecks] = useState<Deck[]>([]);
  const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null);
  const formEndRef = useRef<HTMLDivElement | null>(null);
  const { token, user } = useAuth();
  const [sourceUrl, setSourceUrl] = useState<string>('');
  const [limits, setLimits] = useState<any>(null);
  const [deckFlashcardCount, setDeckFlashcardCount] = useState<number>(0);

  const fetchDecks = useCallback(async () => {
    if (!token) return;
    try {
      const response = await axios.get(buildApiUrl('/decks/'), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setDecks(response.data);
      // Optionally set a default deck if available
      if (response.data.length > 0 && !selectedDeckId) {
        setSelectedDeckId(response.data[0].id);
      }
    } catch (err) {
      console.error('Error fetching decks:', err);
    }
  }, [token, selectedDeckId]);

  useEffect(() => {
    fetchDecks();
  }, [fetchDecks]);

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

  useEffect(() => {
    if (!selectedDeckId || !decks.length) return;
    const deck = decks.find(d => d.id === selectedDeckId);
    if (deck) {
      // Get flashcard count from the deck object
      // We'll need to fetch this or get it from the decks list
      setDeckFlashcardCount(deck.flashcards_count || 0);
    }
  }, [selectedDeckId, decks]);

  const handleManualSubmit = async (e: React.FormEvent) => {
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
          deck_id: selectedDeckId,
          source_url: sourceUrl
        },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      setConcept('');
      setDefinition('');
      setTags([]);
      setSourceUrl('');
      // Refetch decks to update card counts
      await fetchDecks();
      onSuccess();
    } catch (err: any) {
      console.error('Error creating flashcard:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to create flashcard. Please try again.';
      setError(errorMessage);
      
      // If it's a premium limit error, suggest upgrading
      if (errorMessage.includes('free tier limit') || errorMessage.includes('Upgrade to Premium')) {
        setTimeout(() => {
          if (window.confirm('You\'ve reached the free tier limit for flashcards in this deck. Would you like to upgrade to Premium?')) {
            window.location.href = '/premium';
          }
        }, 100);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleNaturalSubmit = async () => {
    if (!token) return;
    
    setLoading(true);
    setError('');
    try {
      const res = await axios.post(
        buildApiUrl('/natural_flashcards/generate_flashcard'),
        {
          text: nlInput,
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const { concept, definition, tags: receivedTags, source_url } = res.data;
      setConcept(concept);
      setDefinition(definition);
      setSourceUrl(source_url || '');
      setTags(Array.isArray(receivedTags) ? receivedTags : (typeof receivedTags === 'string' ? receivedTags.split(',').map(t => t.trim()).filter(t => t) : []));
      scrollToBottom();
    } catch (err) {
      console.error('Error generating flashcard:', err);
      setError('Failed to generate flashcard. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      formEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg shadow-md p-6 border border-gray-300 dark:border-gray-600">
      <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-darktext">Add a New Flashcard</h2>
      
      {/* Natural Language Section */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-3 text-gray-700 dark:text-gray-300">Ask GPT to make a card for you.</h3>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200 rounded">
          {error}
        </div>
      )}

        <div className="space-y-4">
          <textarea
            placeholder="Type something like: 'make a card for the fundamental theorem of calculus'"
            value={nlInput}
            onChange={(e) => setNlInput(e.target.value)}
            rows={3}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
          />
          <button
            type="button"
            onClick={handleNaturalSubmit}
            disabled={loading || !token}
            className="w-full px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50 transition-colors duration-200"
          >
            {loading ? 'Generating...' : 'Generate from Natural Language'}
          </button>
        </div>
      </div>
      
      {/* Manual Creation Section */}
      <div className="mb-4">
        <h3 className="text-lg font-medium mb-3 text-gray-700 dark:text-gray-300">Or create manually:</h3>
        
        <form onSubmit={handleManualSubmit} className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-1">
            <label htmlFor="deck-select" className="block text-sm font-medium text-secondary-700 dark:text-secondary-300">Select Deck (Optional)</label>
            {selectedDeckId && limits && !user?.is_premium && (
              <span className="text-xs text-secondary-600 dark:text-secondary-400">
                {deckFlashcardCount} / 20 flashcards
              </span>
            )}
          </div>
          <select
            id="deck-select"
            value={selectedDeckId || ''}
            onChange={(e) => setSelectedDeckId(e.target.value ? Number(e.target.value) : null)}
            className="mt-1 block w-full rounded-md border-secondary-300 dark:border-secondary-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-secondary-700 dark:text-white sm:text-sm"
          >
            <option value="">No Deck</option>
            {decks.map(deck => (
              <option key={deck.id} value={deck.id}>
                {deck.name} {deck.flashcards_count !== undefined ? `(${deck.flashcards_count} cards)` : ''}
              </option>
            ))}
          </select>
        </div>
        <div>
          <input
            type="text"
            placeholder="Concept"
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            required
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
          />
        </div>
        <div>
          <textarea
            placeholder="Definition"
            value={definition}
            onChange={(e) => setDefinition(e.target.value)}
            required
            rows={4}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
          />
          {definition && (
            <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600">
              <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {definition}
              </ReactMarkdown>
            </div>
          )}
        </div>
        <div>
          <input
            type="text"
            placeholder="Source URL"
            value={sourceUrl}
            onChange={(e) => setSourceUrl(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
          />
        </div>
        <div>
          <TagSelector selectedTags={tags} onChange={setTags} />
        </div>
        <button
          type="submit"
          disabled={submitting || !token}
          className="w-full px-4 py-2 bg-secondary-500 text-white rounded-md hover:bg-secondary-600 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:ring-opacity-50 transition-colors duration-200"
        >
          {submitting ? 'Saving...' : 'Save Flashcard'}
        </button>
        </form>
      </div>
      <div ref={formEndRef} />
    </div>
  );
};

export default FlashcardForm;
