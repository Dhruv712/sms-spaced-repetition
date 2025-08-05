import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import FlashcardForm from '../components/FlashcardForm';
import ReviewStats from '../components/ReviewStats';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { useAuth } from '../contexts/AuthContext';
import { useLocation, useNavigate } from 'react-router-dom';

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

const DeckTile: React.FC<{ deck: DeckOut; onClick: () => void; isActive: boolean }> = ({ deck, onClick, isActive }) => {
  return (
    <div
      onClick={onClick}
      className={`deck-tile p-4 rounded-lg shadow cursor-pointer border-2 ${isActive ? 'border-primary-600' : 'border-transparent'} bg-white dark:bg-secondary-800 transition-all flex flex-col items-center`}
      style={{ minWidth: 160, minHeight: 120 }}
    >
      {/* Deck image - use uploaded image or fallback */}
      <img
        src={deck.image_url || "https://futureoflife.org/wp-content/uploads/2020/08/elon_musk_royal_society.jpg"}
        alt={`${deck.name} preview`}
        className="rounded mb-2 object-cover w-full h-20"
        onError={(e) => {
          console.error('Image failed to load:', deck.image_url);
          e.currentTarget.src = "https://futureoflife.org/wp-content/uploads/2020/08/elon_musk_royal_society.jpg";
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
  const { token, isAuthenticated } = useAuth();
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

      const response = await axios.get('http://localhost:8000/flashcards/with-reviews', {
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
      const decksResponse = await axios.get('http://localhost:8000/decks/', {
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
      await axios.delete(`http://localhost:8000/flashcards/${cardId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setFlashcards((prev) => prev.filter((card) => card.id !== cardId));
    } catch (err) {
      console.error("Failed to delete flashcard", err);
    }
  };

  const handleMarkReviewed = async (cardId: number) => {
    if (!token) return;
    
    try {
      await axios.post(
        `http://localhost:8000/flashcards/${cardId}/mark-reviewed`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      loadFlashcards();
    } catch (err) {
      console.error('Error marking reviewed:', err);
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

  return (
    <div className="container mx-auto px-4 py-8 bg-gray-50 dark:bg-darkbg min-h-screen relative">
      {/* ReviewStats in top right */}
      <div className="fixed top-8 right-0 w-64 z-10 mr-8">
        <ReviewStats />
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
            <div key={card.id} className="bg-white dark:bg-secondary-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 transform hover:scale-102 transition-transform duration-200">
              <div className="font-semibold text-lg mb-2 text-gray-900 dark:text-gray-100">{card.concept}</div>
              <hr className="my-2 border-gray-200 dark:border-gray-600" />
              <div className="prose max-w-none text-gray-700 dark:text-gray-200">
                <ReactMarkdown
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {card.definition}
                </ReactMarkdown>
              </div>
              <div className="text-sm text-blue-600 dark:text-blue-300 mt-2">
                Tags:{' '}
                {normalizeTags(card.tags).join(', ') || 'No tags'}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                <strong>Next Review:</strong>{' '}
                {card.next_review_date
                  ? new Date(card.next_review_date).toLocaleString()
                  : 'Not reviewed yet'}
              </div>
              <div className="mt-4 flex space-x-2">
                <button
                  onClick={() => handleMarkReviewed(card.id)}
                  className="px-4 py-2 bg-secondary-500 text-white rounded hover:bg-secondary-600 focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:ring-opacity-50 transition-colors duration-200"
                >
                  Mark Reviewed
                </button>
                <button
                  onClick={() => handleDelete(card.id)}
                  className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 transition-colors duration-200"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FlashcardsPage;
