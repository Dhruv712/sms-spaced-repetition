import React, { useEffect, useState } from 'react';
import axios from 'axios';
import FlashcardForm from '../components/FlashcardForm';
import ReviewStats from '../components/ReviewStats';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { useAuth } from '../contexts/AuthContext';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string | string[];
  next_review_date?: string | null; // optional because it might be null
}

const FlashcardsPage: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const { token, isAuthenticated } = useAuth();

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

  const loadFlashcards = () => {
    if (!token) {
      console.log('No token available, skipping flashcard load');
      return;
    }
    
    console.log('Loading flashcards with token:', token);
    axios
      .get('http://localhost:8000/flashcards/with-reviews', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then((res) => {
        console.log('Flashcards loaded successfully:', res.data);
        setFlashcards(res.data);
      })
      .catch((err) => {
        console.error('Error fetching flashcards:', err);
      });
  };

  useEffect(() => {
    console.log('Token changed, attempting to load flashcards');
    if (token) {
      loadFlashcards();
    }
  }, [token]);

  // 🔍 Extract unique tags
  const allTags = Array.from(
    new Set(
      flashcards
        .flatMap((card) =>
          typeof card.tags === 'string'
            ? card.tags.split(',').map((tag) => tag.trim())
            : []
        )
        .filter((tag) => tag.length > 0)
    )
  );

  const normalizeTags = (tags: string | string[] | undefined): string[] =>
    Array.isArray(tags)
      ? tags
      : typeof tags === 'string'
      ? tags.split(',').map((t) => t.trim())
      : [];

  // 🧠 Filtered flashcards
  const visibleFlashcards = selectedTag
    ? flashcards.filter((card) =>
      normalizeTags(card.tags).includes(selectedTag)
      )
    : flashcards;

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

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Your Flashcards</h1>
        <div className="flex items-center space-x-2">
          <label className="switch">
            <input
              type="checkbox"
              checked={darkMode}
              onChange={() => setDarkMode(!darkMode)}
            />
            <span className="slider" />
          </label>
          <span>Dark Mode</span>
        </div>
      </div>

      <div className="mb-8">
        <ReviewStats />
      </div>

      <div className="mb-8">
        <FlashcardForm onSuccess={loadFlashcards} />
      </div>

      {/* 🔘 Tag Filters */}
      {allTags.length > 0 && (
        <div className="mb-6">
          <strong className="mr-2">Filter by tag:</strong>
          <button
            onClick={() => setSelectedTag(null)}
            className={`px-3 py-1 rounded mr-2 ${
              selectedTag === null
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            All
          </button>
          {allTags.map((tag) => (
            <button
              key={tag}
              onClick={() => setSelectedTag(tag)}
              className={`px-3 py-1 rounded mr-2 ${
                selectedTag === tag
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 hover:bg-gray-300'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      )}

      <div className="grid gap-6">
        {visibleFlashcards.map((card) => (
          <div key={card.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="font-semibold text-lg mb-2">{card.concept}</div>
            <hr className="my-2" />
            <div className="prose max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {card.definition}
              </ReactMarkdown>
            </div>
            <div className="text-sm text-blue-600 mt-2">
              Tags:{' '}
              {(
                Array.isArray(card.tags)
                  ? card.tags
                  : (card.tags as string).split(',').map((t: string) => t.trim())
              ).filter(Boolean).join(', ') || 'No tags'}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              <strong>Next Review:</strong>{' '}
              {card.next_review_date
                ? new Date(card.next_review_date).toLocaleString()
                : 'Not reviewed yet'}
            </div>
            <div className="mt-4 flex space-x-2">
              <button
                onClick={() => handleMarkReviewed(card.id)}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Mark Reviewed
              </button>
              <button
                onClick={() => handleDelete(card.id)}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FlashcardsPage;
