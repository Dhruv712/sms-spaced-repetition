import React, { useEffect, useState } from 'react';
import axios from 'axios';
import FlashcardForm from '../components/FlashcardForm';
import ReviewStats from '../components/ReviewStats';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string;
  next_review_date?: string | null; // optional because it might be null
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
      .get('http://localhost:8000/flashcards/with-reviews/1') // assuming user_id=1
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
    <div className="container">
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
            className={`btn-secondary mr-2 ${selectedTag === null ? 'opacity-70' : ''}`}
          >
            All
          </button>
          {allTags.map((tag) => (
            <button
              key={tag}
              onClick={() => setSelectedTag(tag)}
              className={`btn-secondary mr-2 ${selectedTag === tag ? 'opacity-70' : ''}`}
            >
              {tag}
            </button>
          ))}
        </div>
      )}

      <ul>
        {visibleFlashcards.map((card) => (
          <li key={card.id} className="card">
          <div className="font-semibold">{card.concept}</div>
          <hr />
          <ReactMarkdown
          children={card.definition}
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
          />

          {/* <div className="text-gray-700">{card.definition}</div> */}
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
          <div><strong>Next Review:</strong> {card.next_review_date ? new Date(card.next_review_date).toLocaleString() : "Not reviewed yet"}</div>
          <button
            onClick={() => {
              axios
                .post(`http://localhost:8000/flashcards/${card.id}/mark-reviewed`)
                .then(() => loadFlashcards())
                .catch((err) => console.error('Error marking reviewed:', err));
            }}
            className="btn-secondary mr-2"
          >
            Mark Reviewed
          </button>

          <button onClick={() => handleDelete(card.id)} className="btn">
            Delete
          </button>
        </li>
        ))}
      </ul>
    </div>
  );
};

export default FlashcardsPage;
