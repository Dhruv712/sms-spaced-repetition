import React, { useEffect, useState } from 'react';
import axios from 'axios';
import FlashcardForm from '../components/FlashcardForm';
import ReviewStats from '../components/ReviewStats';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string; // stored as comma-separated string
}

const FlashcardsPage: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState<boolean>(false);

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
    axios
      .get('http://localhost:8000/admin/flashcards')
      .then((res) => setFlashcards(res.data))
      .catch((err) => console.error('Error fetching flashcards:', err));
  };

  useEffect(() => {
    loadFlashcards();
  }, []);

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

  // 🧠 Filtered flashcards
  const visibleFlashcards = selectedTag
    ? flashcards.filter((card) =>
        (card.tags || '').split(',').map((t) => t.trim()).includes(selectedTag)
      )
    : flashcards;

    const handleDelete = async (cardId: number) => {
      try {
        await axios.delete(`http://localhost:8000/flashcards/${cardId}`);
        setFlashcards((prev) => prev.filter((card) => card.id !== cardId));
      } catch (err) {
        console.error("Failed to delete flashcard", err);
      }
    };
    

  return (
    <div className="p-4">
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
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
      <div><ReviewStats userId={1} /></div>
      <h1 className="text-2xl font-bold mb-4">Your Flashcards</h1>
      <FlashcardForm onSuccess={loadFlashcards} />

      {/* 🔘 Tag Filters */}
      {allTags.length > 0 && (
        <div className="mb-4">
          <strong>Filter by tag:</strong>{' '}
          <button
            onClick={() => setSelectedTag(null)}
            className={`mr-2 px-2 py-1 border rounded ${
              selectedTag === null ? 'bg-blue-200' : ''
            }`}
          >
            All
          </button>
          {allTags.map((tag) => (
            <button
              key={tag}
              onClick={() => setSelectedTag(tag)}
              className={`mr-2 px-2 py-1 border rounded ${
                selectedTag === tag ? 'bg-blue-300' : ''
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      )}

      <ul>
        {visibleFlashcards.map((card) => (
          <li key={card.id} className="mb-3 p-3 border rounded shadow">
          <div className="font-semibold">{card.concept}</div>
          <div className="text-gray-700">{card.definition}</div>
          <div className="text-sm text-blue-600 mt-1">
            Tags:{' '}
            {card.tags
              ? card.tags
                  .split(',')
                  .map((t) => t.trim())
                  .filter(Boolean)
                  .join(', ')
              : 'No tags'}
          </div>
          <button
            onClick={() => handleDelete(card.id)}
            className="mt-2 px-2 py-1 text-sm bg-red-500 text-white rounded"
          >
            Delete
          </button>
        </li>
        ))}
      </ul>
    </div>
  );
};

export default FlashcardsPage;
