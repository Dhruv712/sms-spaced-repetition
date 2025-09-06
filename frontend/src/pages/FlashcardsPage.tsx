import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import FlashcardForm from '../components/FlashcardForm';
import FlashcardEditModal from '../components/FlashcardEditModal';
import ReviewStats from '../components/ReviewStats';
import DailySummary from '../components/DailySummary';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { useAuth } from '../contexts/AuthContext';
import { useLocation, useNavigate } from 'react-router-dom';
import { buildApiUrl } from '../config';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string | string[];
  next_review_date?: string | null; // optional because it might be null
  deck_id: number | null;
}

// Define the DeckOut interface here for now
interface DeckOut {
  id: number;
  name: string;
  user_id: number;
  created_at: string;
  flashcards_count: number;
  image_url?: string;
}

const FlashcardCard: React.FC<{ 
  card: Flashcard; 
  decks: DeckOut[]; 
  onEdit: (card: Flashcard) => void; 
  onDelete: (id: number) => void 
}> = ({ card, decks, onEdit, onDelete }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const getDeckName = (deckId: number | null) => {
    if (!deckId) return null;
    const deck = decks.find(d => d.id === deckId);
    return deck?.name || null;
  };
  
  const normalizeTags = (tags: string | string[] | undefined): string[] =>
    Array.isArray(tags)
      ? tags
      : typeof tags === 'string'
      ? tags.split(',').map((t: string) => t.trim())
      : [];
  
  const deckName = getDeckName(card.deck_id);
  const shouldTruncate = card.definition.length > 200;
  const displayDefinition = shouldTruncate && !isExpanded 
    ? card.definition.substring(0, 200) + '...' 
    : card.definition;

  return (
    <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 transform hover:scale-102 transition-transform duration-200">
      <div className="font-semibold text-lg mb-2 text-gray-900 dark:text-gray-100">{card.concept}</div>
      <hr className="my-2 border-gray-200 dark:border-gray-600" />
      <div className="prose max-w-none text-gray-700 dark:text-gray-200">
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
      
      {/* Deck Badge */}
      {deckName && (
        <div className="mt-3">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
            📚 {deckName}
          </span>
        </div>
      )}
      
      {/* Tags */}
      <div className="text-sm text-blue-600 dark:text-blue-300 mt-2">
        Tags:{' '}
        {normalizeTags(card.tags).join(', ') || 'No tags'}
      </div>
      
      {/* Next Review */}
      <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
        <strong>Next Review:</strong>{' '}
        {card.next_review_date
          ? new Date(card.next_review_date).toLocaleString()
          : 'Not reviewed yet'}
      </div>
      
      {/* Action Buttons */}
      <div className="mt-4 flex space-x-2">
        <button
          onClick={() => onEdit(card)}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors duration-200"
        >
          Edit
        </button>
        <button
          onClick={() => onDelete(card.id)}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 transition-colors duration-200"
        >
          Delete
        </button>
      </div>
    </div>
  );
};

const DeckTile: React.FC<{ deck: DeckOut; onClick: () => void; isActive: boolean }> = ({ deck, onClick, isActive }) => {
  return (
    <div
      onClick={onClick}
      className={`deck-tile p-4 rounded-lg shadow cursor-pointer border-2 ${isActive ? 'border-primary-600' : 'border-transparent'} bg-white dark:bg-secondary-800 transition-all flex flex-col items-center`}
      style={{ minWidth: 160, minHeight: 120 }}
    >
      {/* Deck image - use uploaded image or fallback */}
      <img
        src={deck.image_url || "/cue_default_image.jpeg"}
        alt={`${deck.name} preview`}
        className="rounded mb-2 object-cover w-full h-20"
        onError={(e) => {
          console.error('Image failed to load:', deck.image_url);
          e.currentTarget.src = "/cue_default_image.jpeg";
        }}
      />
      <div className="font-bold text-lg mb-1 text-center">{deck.name}</div>
      <div className="text-xs text-gray-500">{deck.flashcards_count} cards</div>
    </div>
  );
};

const FlashcardsPage: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null); // New state for tag filter
  const [uniqueTags, setUniqueTags] = useState<string[]>([]); // New state for unique tags
  const [decks, setDecks] = useState<DeckOut[]>([]); // New state for decks
  const [editingFlashcard, setEditingFlashcard] = useState<Flashcard | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const { token, isAuthenticated, user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate(); // Initialize useNavigate hook
  const queryParams = new URLSearchParams(location.search);
  const deckId = queryParams.get('deckId');

  console.log('FlashcardsPage render:', { token, isAuthenticated });

  const loadFlashcards = useCallback(async () => {
    if (!token) {
      console.log('No token available, skipping flashcard load');
      return;
    }
    
    console.log('Loading flashcards with token:', token);
    try {
      const params: { deck_id?: string; tags?: string } = {};

      // Prioritize deckId from URL if present
      if (deckId) {
        params.deck_id = deckId;
      }
      // Add selected tag if present
      if (selectedTag) {
        params.tags = selectedTag;
      }

      const response = await axios.get(buildApiUrl('/flashcards/with-reviews'), {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: params,
      });
      console.log('Flashcards loaded successfully:', response.data);
      setFlashcards(response.data);

      // After loading flashcards, extract unique tags
      const allTags = new Set<string>();
      response.data.forEach((card: Flashcard) => {
        normalizeTags(card.tags).forEach(tag => allTags.add(tag));
      });
      setUniqueTags(Array.from(allTags));

      // Fetch all decks for filtering
      const decksResponse = await axios.get(buildApiUrl('/decks/'), {
        headers: {
          'Authorization': `Bearer ${token}`
        },
      });
      setDecks(decksResponse.data);

    } catch (err) {
      console.error('Error fetching flashcards:', err);
    }
  }, [token, deckId, selectedTag]);

  useEffect(() => {
    console.log('Token, deckId, or selectedTag changed, attempting to load flashcards');
    if (token) {
      loadFlashcards();
    }
  }, [loadFlashcards, token]); // Rerun when loadFlashcards or token changes

  const normalizeTags = (tags: string | string[] | undefined): string[] =>
    Array.isArray(tags)
      ? tags
      : typeof tags === 'string'
      ? tags.split(',').map((t: string) => t.trim())
      : [];

  const visibleFlashcards = flashcards; // Filtering by tags and deckId is now handled by the backend

  const handleDelete = async (cardId: number) => {
    if (!token) return;
    
    try {
      await axios.delete(buildApiUrl(`/flashcards/${cardId}`), {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setFlashcards((prev) => prev.filter((card) => card.id !== cardId));
    } catch (err) {
      console.error("Failed to delete flashcard", err);
    }
  };

  const handleTagFilterClick = (tag: string | null) => {
    setSelectedTag(tag);
  };

  const handleDeckFilterClick = (id: number | null) => {
    if (id === null) {
      navigate('/flashcards'); // Navigate to base flashcards page
    } else {
      navigate(`/flashcards?deckId=${id}`); // Navigate to flashcards with deckId
    }
    // The deckId from URL will automatically trigger loadFlashcards due to useEffect dependency
  };

  const handleEditFlashcard = (flashcard: Flashcard) => {
    setEditingFlashcard(flashcard);
    setIsEditModalOpen(true);
  };

  const handleEditModalClose = () => {
    setIsEditModalOpen(false);
    setEditingFlashcard(null);
  };

  const handleEditSuccess = () => {
    loadFlashcards(); // Reload flashcards to show updated data
  };

  return (
    <div className="container mx-auto px-4 py-8 bg-gray-50 dark:bg-darkbg min-h-screen">
      {/* SMS Banner for users without conversation state */}
      {user && user.phone_number && !user.has_sms_conversation && (
        <div className="mb-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-bold">📱</span>
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-medium text-blue-900 dark:text-blue-100 mb-2">
                Get Started with SMS Flashcards!
              </h3>
              <p className="text-blue-700 dark:text-blue-300 mb-4">
                You have a phone number set up, but haven't started using SMS yet. Text "START" to this link to begin receiving flashcard reminders and create cards via text:
              </p>
              <div className="flex items-center gap-2 mb-3">
                <a
                  href="imessage://sandbox.loopmessage.com@imsg.im"
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 text-sm font-mono bg-white dark:bg-gray-800 px-3 py-2 rounded border border-blue-300 dark:border-blue-600 break-all"
                >
                  imessage://sandbox.loopmessage.com@imsg.im
                </a>
              </div>
              <p className="text-sm text-blue-600 dark:text-blue-400">
                💡 On mobile, tap the link above to open Messages and send "START"
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* ReviewStats Banner at the top */}
      <div className="mb-8">
        <ReviewStats />
      </div>
      
      {/* Daily Summary */}
      <div className="mb-8">
        <DailySummary />
      </div>
      
      {/* Centered FlashcardForm */}
      <div className="flex flex-col items-center justify-center min-h-[40vh] mb-12">
        <div className="w-full max-w-2xl">
          <FlashcardForm onSuccess={loadFlashcards} />
        </div>
      </div>
      {/* Deck Tiles */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-3 text-gray-800">Your Decks</h2>
        <div className="flex flex-wrap gap-4">
          {decks.map(deck => (
            <DeckTile
              key={deck.id}
              deck={deck}
              onClick={() => handleDeckFilterClick(deck.id)}
              isActive={!!deckId && parseInt(deckId) === deck.id}
            />
          ))}
        </div>
      </div>
      {/* Tag Filters */}
      <div className="mb-8 p-4 bg-white dark:bg-secondary-800 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-3 text-gray-800">Filter by Tag</h2>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handleTagFilterClick(null)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedTag === null ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'} transition-colors duration-200`}
          >
            All Tags
          </button>
          {uniqueTags.map(tag => (
            <button
              key={tag}
              onClick={() => handleTagFilterClick(tag)}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedTag === tag ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'} transition-colors duration-200`}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>
      {/* Flashcard Grid with Drag-and-Drop */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {flashcards.length === 0 ? (
          <p className="text-gray-700 col-span-full">No flashcards found for this selection. Try adjusting your filters.</p>
        ) : (
          visibleFlashcards.map((card) => (
            <FlashcardCard 
              key={card.id} 
              card={card} 
              decks={decks}
              onEdit={handleEditFlashcard}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>
      
      {/* Edit Modal */}
      <FlashcardEditModal
        flashcard={editingFlashcard}
        isOpen={isEditModalOpen}
        onClose={handleEditModalClose}
        onSuccess={handleEditSuccess}
      />
    </div>
  );
};

export default FlashcardsPage;
