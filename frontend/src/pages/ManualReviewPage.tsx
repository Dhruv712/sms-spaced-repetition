import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { buildApiUrl } from '../config';
import SmsSetupBanner from '../components/SmsSetupBanner';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string | string[];
  deck_id?: number | null;
  deck_name?: string | null;
}

const ManualReviewPage: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState<string | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    const fetchFlashcards = async () => {
      try {
        const response = await axios.get(buildApiUrl('/flashcards/due'), {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setFlashcards(response.data);
        if (response.data.length > 0) {
          setCurrentIndex(0);
        } else {
          setError('No flashcards due for review.');
        }
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
    if (!token || currentIndex >= flashcards.length || !answer.trim() || isSubmitting) return;
    setError('');
    setFeedback(null);
    setIsSubmitting(true);
    try {
      const response = await axios.post(
        buildApiUrl('/reviews/manual_review'),
        {
          flashcard_id: flashcards[currentIndex].id,
          answer,
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      setFeedback(response.data.llm_feedback || response.data.feedback || 'No feedback returned.');
      setAnswer('');
    } catch (err) {
      console.error('Failed to submit review:', err);
      setError('Failed to submit review. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNext = () => {
    setFeedback(null);
    setAnswer('');
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setError('You have completed all flashcards for today!');
      setCurrentIndex(0); // Reset for next session or no cards due message
    }
  };

  const handleSkip = () => {
    // Skip the current card without creating a review - just move to next
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setAnswer('');
      setFeedback(null);
      setError('');
    } else {
      setError('You have completed all flashcards for today!');
      setCurrentIndex(0);
    }
  };

  const normalizeTags = (tags: string | string[] | undefined): string[] =>
    Array.isArray(tags)
      ? tags
      : typeof tags === 'string'
      ? tags.split(',').map((t: string) => t.trim())
      : [];

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-darkbg">
        <div className="text-xl text-gray-600 dark:text-gray-300">Loading flashcards due for review...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-darkbg">
        <div className="text-xl text-red-600 dark:text-red-400">{error}</div>
      </div>
    );
  }

  if (flashcards.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-darkbg">
        <div className="text-xl text-gray-600 dark:text-gray-300">No flashcards due for review today. Great job!</div>
      </div>
    );
  }

  const currentFlashcard = flashcards[currentIndex];

  return (
    <div className="container mx-auto px-4 py-8 bg-gray-50 dark:bg-darkbg min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-darktext">Review Due Cards</h1>
      
      {/* SMS Setup Banner */}
      <SmsSetupBanner />

      <div className="bg-white dark:bg-darksurface rounded-lg shadow-xl p-8 max-w-2xl mx-auto border border-gray-200 dark:border-gray-700">
        <div className="mb-6">
          <div className="text-sm text-gray-500 dark:text-gray-400 mb-2">
            Card {currentIndex + 1} of {flashcards.length}
          </div>
          {currentFlashcard.deck_name && (
            <div className="mb-2">
              <span className="inline-block px-2 py-1 text-xs font-medium bg-accent/10 text-accent dark:bg-accent/20 dark:text-accent rounded">
                {currentFlashcard.deck_name}
              </span>
            </div>
          )}
          <div className="text-2xl font-semibold mb-4 text-gray-900 dark:text-darktext">
            {currentFlashcard.concept}
          </div>

          {!feedback ? (
            <div className="mt-4">
              <textarea
                className="w-full p-3 border border-gray-300 rounded-md mb-4 focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
                placeholder="Type your answer here..."
                value={answer}
                onChange={e => setAnswer(e.target.value)}
                rows={4}
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSubmit}
                  className="flex-1 px-4 py-3 bg-secondary-500 text-white rounded-md hover:bg-secondary-600 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:ring-opacity-50 transition-colors duration-200 flex items-center justify-center"
                  disabled={!answer.trim() || isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </>
                  ) : (
                    'Submit Answer'
                  )}
                </button>
                <button
                  onClick={handleSkip}
                  className="px-4 py-3 bg-gray-500 text-white rounded-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-opacity-50 transition-colors duration-200"
                  disabled={isSubmitting}
                >
                  Skip
                </button>
              </div>
            </div>
          ) : (
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-md border border-gray-200 dark:border-gray-600">
              <strong className="block text-lg font-medium text-gray-800 dark:text-darktext mb-2">LLM Feedback:</strong>
              <p className="mt-1 text-sm">{feedback}</p>
              <div className="text-lg font-semibold text-gray-900 dark:text-darktext mb-2">Definition:</div>
              <div className="prose max-w-none text-gray-700 dark:text-gray-300 mb-4">
                <ReactMarkdown
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {currentFlashcard.definition}
                </ReactMarkdown>
              </div>
              <div className="flex flex-wrap gap-2 mb-4">
                {normalizeTags(currentFlashcard.tags).map((tag: string) => (
                  <span key={tag} className="px-3 py-1 bg-accent/10 text-accent dark:bg-accent/20 dark:text-accent rounded-full text-sm font-medium">
                    {tag}
                  </span>
                ))}
              </div>
              <button
                onClick={handleNext}
                className="mt-4 w-full px-4 py-3 bg-accent text-white rounded-md hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-opacity-50 transition-colors duration-200"
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
