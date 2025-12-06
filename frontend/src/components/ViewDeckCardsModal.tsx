import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import FlashcardEditModal from './FlashcardEditModal';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string | string[];
  next_review_date?: string | null;
  deck_id: number | null;
}

interface ViewDeckCardsModalProps {
  isOpen: boolean;
  onClose: () => void;
  deckId: number;
  deckName: string;
  onSuccess: () => void;
}

const FlashcardCard: React.FC<{
  card: Flashcard;
  onEdit: (card: Flashcard) => void;
  onDelete: (id: number) => void;
}> = ({ card, onEdit, onDelete }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const normalizeTags = (tags: string | string[] | undefined): string[] =>
    Array.isArray(tags)
      ? tags
      : typeof tags === 'string'
      ? tags.split(',').map((t: string) => t.trim())
      : [];

  const shouldTruncate = card.definition.length > 200;
  const displayDefinition = shouldTruncate && !isExpanded
    ? card.definition.substring(0, 200) + '...'
    : card.definition;

  return (
    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
      <div className="font-semibold text-lg mb-2 text-gray-900 dark:text-gray-100">
        {card.concept}
      </div>
      <hr className="my-2 border-gray-200 dark:border-gray-600" />
      <div className="prose max-w-none text-gray-700 dark:text-gray-200 text-sm">
        <ReactMarkdown
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
        >
          {displayDefinition}
        </ReactMarkdown>
      </div>
      {shouldTruncate && (
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-blue-600 dark:text-blue-400 text-sm hover:underline mt-2"
        >
          {isExpanded ? 'Show Less' : 'More'}
        </button>
      )}

      {/* Tags */}
      <div className="text-xs text-blue-600 dark:text-blue-300 mt-2">
        Tags: {normalizeTags(card.tags).join(', ') || 'No tags'}
      </div>

      {/* Next Review */}
      {card.next_review_date && (
        <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">
          Next Review: {new Date(card.next_review_date).toLocaleString()}
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-4 flex space-x-2">
        <button
          onClick={() => onEdit(card)}
          className="flex-1 px-3 py-1.5 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
        >
          Edit
        </button>
        <button
          onClick={() => onDelete(card.id)}
          className="flex-1 px-3 py-1.5 bg-red-500 text-white rounded text-sm hover:bg-red-600 transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
};

const ViewDeckCardsModal: React.FC<ViewDeckCardsModalProps> = ({
  isOpen,
  onClose,
  deckId,
  deckName,
  onSuccess,
}) => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingFlashcard, setEditingFlashcard] = useState<Flashcard | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const { token } = useAuth();

  const fetchFlashcards = useCallback(async () => {
    if (!token || !isOpen) return;

    setLoading(true);
    setError('');

    try {
      const response = await axios.get(buildApiUrl(`/flashcards/with-reviews`), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        params: { deck_id: deckId },
      });
      setFlashcards(response.data);
    } catch (err) {
      console.error('Error fetching flashcards:', err);
      setError('Failed to load flashcards. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [token, deckId, isOpen]);

  useEffect(() => {
    if (isOpen) {
      fetchFlashcards();
    }
  }, [isOpen, fetchFlashcards]);

  const handleDelete = async (cardId: number) => {
    if (!token) return;

    if (!window.confirm('Are you sure you want to delete this flashcard?')) {
      return;
    }

    try {
      await axios.delete(buildApiUrl(`/flashcards/${cardId}`), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setFlashcards((prev) => prev.filter((card) => card.id !== cardId));
      onSuccess();
    } catch (err) {
      console.error('Failed to delete flashcard', err);
      alert('Failed to delete flashcard. Please try again.');
    }
  };

  const handleEditFlashcard = (card: Flashcard) => {
    setEditingFlashcard(card);
    setIsEditModalOpen(true);
  };

  const handleEditModalClose = () => {
    setIsEditModalOpen(false);
    setEditingFlashcard(null);
  };

  const handleEditSuccess = () => {
    fetchFlashcards();
    onSuccess();
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 dark:bg-opacity-70 overflow-y-auto">
        <div className="bg-white dark:bg-darksurface rounded-lg shadow-xl p-6 max-w-5xl w-full mx-4 my-8 border border-gray-200 dark:border-gray-700 max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-darktext">
                {deckName}
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {flashcards.length} {flashcards.length === 1 ? 'card' : 'cards'}
              </p>
            </div>
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

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-accent"></div>
            </div>
          ) : flashcards.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              <p className="text-lg mb-2">No flashcards in this deck yet.</p>
              <p className="text-sm">Click "New" to create flashcards for this deck.</p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {flashcards.map((card) => (
                <FlashcardCard
                  key={card.id}
                  card={card}
                  onEdit={handleEditFlashcard}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      <FlashcardEditModal
        flashcard={editingFlashcard}
        isOpen={isEditModalOpen}
        onClose={handleEditModalClose}
        onSuccess={handleEditSuccess}
      />
    </>
  );
};

export default ViewDeckCardsModal;

