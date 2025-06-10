import React, { useEffect, useState } from 'react';
import axios from 'axios';
import FlashcardForm from '../components/FlashcardForm';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string; // stored as comma-separated string
}

const FlashcardsPage: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

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

  return (
    <div className="p-4">
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
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FlashcardsPage;
