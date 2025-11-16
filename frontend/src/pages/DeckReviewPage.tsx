import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { buildApiUrl } from '../config';
import SmsSetupBanner from '../components/SmsSetupBanner';

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
  const [isSubmitting, setIsSubmitting] = useState(false);
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
    setIsSubmitting(true);
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
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNextCard = () => {
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setFeedback(null);
      setAnswer('');
      setError('');
    }
  };

  const handlePreviousCard = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setFeedback(null);
      setAnswer('');
      setError('');
    }
  };

  const handleSkip = () => {
    // Skip the current card without creating a review - just move to next
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setAnswer('');
      setFeedback(null);
      setError('');
    }
  };

  if (!token) return <div>Please log in.</div>;
  if (isLoading) return <div>Loading flashcards...</div>;
  if (error) return <div>{error}</div>;
  if (flashcards.length === 0) return <div>No flashcards in this deck.</div>;

  const currentCard = flashcards[currentIndex];

  return (
    <div className="max-w-xl mx-auto p-6">
      {/* SMS Setup Banner */}
      <SmsSetupBanner />
      
      <div className="bg-white dark:bg-gray-900 rounded shadow p-6">
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
          disabled={isSubmitting || !!feedback}
        />
      </div>
      <div className="flex gap-2">
        <button
          className="bg-primary-500 text-white px-4 py-2 rounded flex items-center flex-1"
          onClick={handleSubmit}
          disabled={isSubmitting || !!feedback || !answer.trim()}
        >
          {isSubmitting ? (
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
        {!feedback && (
          <button
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            onClick={handleSkip}
            disabled={isSubmitting}
          >
            Skip
          </button>
        )}
        
        {feedback && (
          <>
            {currentIndex > 0 && (
              <button
                className="bg-gray-500 text-white px-4 py-2 rounded"
                onClick={handlePreviousCard}
                disabled={isSubmitting}
              >
                Previous Card
              </button>
            )}
            {currentIndex < flashcards.length - 1 ? (
              <button
                className="bg-green-500 text-white px-4 py-2 rounded"
                onClick={handleNextCard}
                disabled={isSubmitting}
              >
                Next Card
              </button>
            ) : (
              <button
                className="bg-blue-500 text-white px-4 py-2 rounded"
                onClick={() => window.location.href = '/decks'}
                disabled={isSubmitting}
              >
                Finish Review
              </button>
            )}
          </>
        )}
      </div>
      {feedback && (
        <div className="mt-4 p-3 bg-gray-100 rounded">
          <div><strong>LLM Feedback:</strong> {feedback}</div>
        </div>
      )}
      </div>
    </div>
  );
};

export default DeckReviewPage; 