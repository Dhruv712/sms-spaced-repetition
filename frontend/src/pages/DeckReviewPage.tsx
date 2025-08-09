import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { buildApiUrl } from '../config';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string[];
}

const DeckReviewPage: React.FC = () => {
  const { deck_id } = useParams<{ deck_id: string }>();
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState<string | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    if (!token || !deck_id) return;

    const fetchFlashcards = async () => {
      try {
        const response = await axios.get(buildApiUrl(`/flashcards/decks/${deck_id}/all-flashcards`), {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setFlashcards(response.data);
        if (response.data.length > 0) {
          setCurrentIndex(0);
        } else {
          setError('No flashcards in this deck.');
        }
      } catch (err) {
        console.error('Failed to fetch flashcards:', err);
        setError('Failed to load flashcards. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchFlashcards();
  }, [token, deck_id]);

  const handleSubmit = async () => {
    if (!token || currentIndex >= flashcards.length || !answer.trim()) return;
    setError('');
    setFeedback(null);
    try {
      const res = await axios.post(buildApiUrl('/reviews/manual_review'), {
        flashcard_id: flashcards[currentIndex].id,
        answer,
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setFeedback(res.data.llm_feedback || res.data.feedback || 'No feedback returned.');
      setAnswer('');
    } catch (err) {
      console.error('Failed to submit review:', err);
      setError('Failed to submit review. Please try again.');
    }
  };

  if (!token) return <div>Please log in.</div>;
  if (isLoading) return <div>Loading flashcards...</div>;
  if (error) return <div>{error}</div>;
  if (flashcards.length === 0) return <div>No flashcards in this deck.</div>;

  const currentCard = flashcards[currentIndex];

  return (
    <div className="max-w-xl mx-auto p-6 bg-white dark:bg-gray-900 rounded shadow">
      <h2 className="text-xl font-bold mb-4">Review Deck</h2>
      <div className="mb-2 text-sm text-gray-500 dark:text-gray-300">Card {currentIndex + 1} of {flashcards.length}</div>
      <div className="mb-4">
        <div className="font-semibold">Concept:</div>
        <div>{currentCard.concept}</div>
      </div>
      <div className="mb-4">
        <div className="font-semibold">Your Answer:</div>
        <textarea
          className="w-full border rounded p-2"
          rows={3}
          value={answer}
          onChange={e => setAnswer(e.target.value)}
          disabled={isLoading || !!feedback}
        />
      </div>
      <button
        className="bg-primary-500 text-white px-4 py-2 rounded mr-2 flex items-center"
        onClick={handleSubmit}
        disabled={isLoading || !!feedback}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
          </>
        ) : (
          'Submit Answer'
        )}
      </button>
      {feedback && (
        <div className="mt-4 p-3 bg-gray-100 rounded">
          <div><strong>LLM Feedback:</strong> {feedback}</div>
        </div>
      )}
    </div>
  );
};

export default DeckReviewPage; 