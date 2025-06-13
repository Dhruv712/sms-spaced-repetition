import React, { useEffect, useState } from 'react';
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
}

const FlashcardsPage: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [currentDeckName, setCurrentDeckName] = useState<string | null>(null);
  const [selectedTag, setSelectedTag] = useState<string | null>(null); // New state for tag filter
  const [uniqueTags, setUniqueTags] = useState<string[]>([]); // New state for unique tags
  const [decks, setDecks] = useState<DeckOut[]>([]); // New state for decks
  const { token, isAuthenticated } = useAuth();
  const location = useLocation();
  const navigate = useNavigate(); // Initialize useNavigate hook
  const queryParams = new URLSearchParams(location.search);
  const deckId = queryParams.get('deckId');

  console.log('FlashcardsPage render:', { token, isAuthenticated });

  // Load dark mode preference from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('darkMode');
    if (stored) {
      setDarkMode(stored === 'true');
    }
  }, []);

  // Apply dark mode class to body
  useEffect(() => {
    document.body.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', darkMode.toString());
  }, [darkMode]);

  const loadFlashcards = async () => {
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

      if (deckId) {
        // Fetch deck name only if a deckId is present in URL
        const deckResponse = await axios.get(`http://localhost:8000/decks/${deckId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
        });
        setCurrentDeckName(deckResponse.data.name);
      } else {
        setCurrentDeckName(null);
      }
    } catch (err) {
      console.error('Error fetching flashcards:', err);
    }
  };

  useEffect(() => {
    console.log('Token, deckId, or selectedTag changed, attempting to load flashcards');
    if (token) {
      loadFlashcards();
    }
  }, [token, deckId, selectedTag]); // Rerun when token, deckId or selectedTag changes

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
    <div className="container mx-auto px-4 py-8 bg-gray-50 dark:bg-darkbg min-h-screen">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-darktext">
          {currentDeckName ? `Flashcards in ${currentDeckName}` : 'Your Flashcards'}
        </h1>
        <div className="flex items-center space-x-2">
          <label className="switch">
            <input
              type="checkbox"
              checked={darkMode}
              onChange={() => setDarkMode(!darkMode)}
            />
            <span className="slider" />
          </label>
          <span className="text-gray-700 dark:text-gray-300">Dark Mode</span>
        </div>
      </div>

      <div className="mb-8">
        <ReviewStats />
      </div>

      <div className="mb-8">
        <FlashcardForm onSuccess={loadFlashcards} />
      </div>

      {/* Tag Filters */}
      <div className="mb-8 p-4 bg-white dark:bg-darksurface rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-3 text-gray-800 dark:text-darktext">Filter by Tag</h2>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handleTagFilterClick(null)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedTag === null ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'} transition-colors duration-200`}
          >
            All Tags
          </button>
          {uniqueTags.map(tag => (
            <button
              key={tag}
              onClick={() => handleTagFilterClick(tag)}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedTag === tag ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'} transition-colors duration-200`}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* Deck Filters */}
      <div className="mb-8 p-4 bg-white dark:bg-darksurface rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-3 text-gray-800 dark:text-darktext">Filter by Deck</h2>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handleDeckFilterClick(null)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${!deckId ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'} transition-colors duration-200`}
          >
            All Decks
          </button>
          {decks.map(deck => (
            <button
              key={deck.id}
              onClick={() => handleDeckFilterClick(deck.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${deckId && parseInt(deckId) === deck.id ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'} transition-colors duration-200`}
            >
              {deck.name}
            </button>
          ))}
        </div>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {flashcards.length === 0 ? (
          <p className="text-gray-700 dark:text-gray-300 col-span-full">No flashcards found for this selection. Try adjusting your filters.</p>
        ) : (
          visibleFlashcards.map((card) => (
            <div key={card.id} className="bg-white dark:bg-darksurface rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 transform hover:scale-102 transition-transform duration-200">
              <div className="font-semibold text-lg mb-2 text-gray-900 dark:text-darktext">{card.concept}</div>
              <hr className="my-2 border-gray-200 dark:border-gray-600" />
              <div className="prose max-w-none text-gray-700 dark:text-gray-300">
                <ReactMarkdown
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {card.definition}
                </ReactMarkdown>
              </div>
              <div className="text-sm text-blue-600 dark:text-blue-400 mt-2">
                Tags:{' '}
                {normalizeTags(card.tags).join(', ') || 'No tags'}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
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
