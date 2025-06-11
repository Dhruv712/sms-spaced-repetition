import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string | string[];
}

const ManualReviewPage: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showDefinition, setShowDefinition] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState<string | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    const fetchFlashcards = async () => {
      try {
        const response = await axios.get('http://localhost:8000/flashcards', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setFlashcards(response.data);
      } catch (err) {
        console.error('Failed to fetch flashcards:', err);
        setError('Failed to load flashcards. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchFlashcards();
  }, [token]);

  const handleSubmit = async () => {
    if (!token || currentIndex >= flashcards.length || !answer.trim()) return;
    setError('');
    setFeedback(null);
    try {
      const response = await axios.post('http://localhost:8000/reviews/manual_review', {
        flashcard_id: flashcards[currentIndex].id,
        answer,
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setFeedback(response.data.llm_feedback || response.data.feedback || 'No feedback returned.');
      setAnswer('');
    } catch (err) {
      console.error('Failed to submit review:', err);
      setError('Failed to submit review. Please try again.');
    }
  };

  const handleNext = () => {
    setFeedback(null);
    setAnswer('');
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowDefinition(false);
    } else {
      setError('You have completed all flashcards!');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading flashcards...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  if (flashcards.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">No flashcards available for review.</div>
      </div>
    );
  }

  const currentFlashcard = flashcards[currentIndex];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Manual Review</h1>

      <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl mx-auto">
        <div className="mb-4">
          <div className="text-sm text-gray-500 mb-2">
            Card {currentIndex + 1} of {flashcards.length}
          </div>
          <div className="text-xl font-semibold mb-4">
            {currentFlashcard.concept}
          </div>

          {!feedback && (
            <div className="mt-4">
              <textarea
                className="w-full p-2 border border-gray-300 rounded mb-2"
                placeholder="Type your answer here..."
                value={answer}
                onChange={e => setAnswer(e.target.value)}
                rows={3}
              />
              <button
                onClick={handleSubmit}
                className="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                disabled={!answer.trim()}
              >
                Submit Answer
              </button>
            </div>
          )}

          {feedback && (
            <div className="mt-4 p-3 border-t">
              <strong>LLM Feedback:</strong>
              <p>{feedback}</p>
              <div className="text-lg mb-4 mt-4">Definition: {currentFlashcard.definition}</div>
              <div className="flex flex-wrap gap-2 mb-4">
                {(
                  Array.isArray(currentFlashcard.tags)
                    ? currentFlashcard.tags
                    : (currentFlashcard.tags as string).split(',').map((t: string) => t.trim())
                ).filter(Boolean).map((tag: string) => (
                  <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {tag}
                  </span>
                ))}
              </div>
              <button
                onClick={handleNext}
                className="mt-4 w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Next Card
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ManualReviewPage;
