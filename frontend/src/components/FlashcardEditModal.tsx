import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import TagSelector from './TagSelector';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string | string[];
  deck_id: number | null;
  source_url?: string;
}

interface Deck {
  id: number;
  name: string;
  user_id: number;
  created_at: string;
  flashcards_count: number;
  image_url?: string;
}

interface Props {
  flashcard: Flashcard | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const FlashcardEditModal: React.FC<Props> = ({ flashcard, isOpen, onClose, onSuccess }) => {
  const [concept, setConcept] = useState('');
  const [definition, setDefinition] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [sourceUrl, setSourceUrl] = useState('');
  const [decks, setDecks] = useState<Deck[]>([]);
  const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    if (isOpen && flashcard) {
      setConcept(flashcard.concept);
      setDefinition(flashcard.definition);
      setTags(Array.isArray(flashcard.tags) ? flashcard.tags : flashcard.tags ? flashcard.tags.split(',').map(t => t.trim()) : []);
      setSourceUrl(flashcard.source_url || '');
      setSelectedDeckId(flashcard.deck_id);
    }
  }, [isOpen, flashcard]);

  const fetchDecks = useCallback(async () => {
    try {
      const response = await axios.get(buildApiUrl('/decks/'), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setDecks(response.data);
    } catch (err) {
      console.error('Error fetching decks:', err);
    }
  }, [token]);

  useEffect(() => {
    if (isOpen && token) {
      fetchDecks();
    }
  }, [isOpen, token, fetchDecks]);

  const handleSave = async () => {
    if (!flashcard || !token) return;
    
    setIsSaving(true);
    setError('');
    
    try {
      await axios.put(
        buildApiUrl(`/flashcards/${flashcard.id}`),
        {
          concept,
          definition,
          tags,
          deck_id: selectedDeckId,
          source_url: sourceUrl
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error updating flashcard:', err);
      setError('Failed to update flashcard. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAssignToDeck = async (deckId: number | null) => {
    if (!flashcard || !token) return;
    
    try {
      if (deckId === null) {
        // Remove from deck
        await axios.patch(
          buildApiUrl(`/flashcards/${flashcard.id}/assign-deck`),
          { deck_id: null },
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
      } else {
        // Assign to deck
        await axios.patch(
          buildApiUrl(`/flashcards/${flashcard.id}/assign-deck`),
          { deck_id: deckId },
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
      }
      
      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error assigning flashcard to deck:', err);
      setError('Failed to assign flashcard to deck. Please try again.');
    }
  };

  if (!isOpen || !flashcard) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-darksurface rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-darktext">Edit Flashcard</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200 rounded-md">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Concept</label>
              <input
                type="text"
                value={concept}
                onChange={(e) => setConcept(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
                placeholder="Enter concept"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Definition</label>
              <textarea
                value={definition}
                onChange={(e) => setDefinition(e.target.value)}
                rows={4}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
                placeholder="Enter definition"
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
              <TagSelector selectedTags={tags} onChange={setTags} />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Source URL</label>
              <input
                type="url"
                value={sourceUrl}
                onChange={(e) => setSourceUrl(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
                placeholder="Enter source URL"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Deck Assignment</label>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handleAssignToDeck(null)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors duration-200 ${
                    selectedDeckId === null
                      ? 'bg-accent text-white'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  No Deck
                </button>
                {decks.map(deck => (
                  <button
                    key={deck.id}
                    onClick={() => handleAssignToDeck(deck.id)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors duration-200 ${
                      selectedDeckId === deck.id
                        ? 'bg-accent text-white'
                        : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                    }`}
                  >
                    {deck.name}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 transition-colors duration-200"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving || !concept.trim() || !definition.trim()}
              className="px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-opacity-50 transition-colors duration-200"
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FlashcardEditModal; 