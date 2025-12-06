import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { buildApiUrl } from '../config';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import SmsSetupBanner from '../components/SmsSetupBanner';

interface Review {
  id: number;
  flashcard_id: number;
  user_response: string;
  was_correct: boolean;
  confidence_score: number;
  llm_feedback: string;
  next_review_date: string;
  created_at: string;
  flashcard: {
    concept: string;
    definition: string;
    tags: string | string[];
  };
}

const ReviewHistoryPage: React.FC = () => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    const fetchReviews = async () => {
      try {
        const response = await axios.get(buildApiUrl('/reviews/'), {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setReviews(response.data);
      } catch (err) {
        console.error('Failed to fetch reviews:', err);
        setError('Failed to load review history. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchReviews();
  }, [token]);

  const normalizeTags = (tags: string | string[] | undefined): string[] =>
    Array.isArray(tags)
      ? tags
      : typeof tags === 'string'
      ? tags.split(',').map((t: string) => t.trim())
      : [];

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-darkbg">
        <div className="text-xl text-gray-600 dark:text-gray-300">Loading review history...</div>
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

  if (reviews.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-darkbg">
        <div className="text-xl text-gray-600 dark:text-gray-300">No review history available.</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 bg-gray-50 dark:bg-darkbg min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-darktext">Review History</h1>
      
      {/* SMS Setup Banner */}
      <SmsSetupBanner />

      <div className="space-y-6">
        {reviews.map((review) => (
          <div key={review.id} className="bg-white dark:bg-darksurface rounded-lg shadow-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
              <div className="mb-4 md:mb-0">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-darktext">{review.flashcard?.concept || '[Flashcard Missing]'}</h3>
                <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600">
              <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {review.flashcard?.definition || ''}
              </ReactMarkdown>
            </div>
              </div>
              <div className="flex flex-wrap gap-4 text-sm text-gray-700 dark:text-gray-300">
                <div>
                  <strong>Your Answer:</strong> {review.user_response}
                </div>
                <div>
                  <strong>Result:</strong>{' '}
                  <span className={`font-medium ${review.was_correct ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    {review.was_correct ? '✅ Correct' : '❌ Incorrect'}
                  </span>
                </div>
                <div>
                  <strong>Confidence:</strong> {(review.confidence_score * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            <div className="mb-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600">
              <strong className="block text-lg font-medium text-gray-800 dark:text-darktext mb-2">LLM Feedback:</strong>
              <p className="mt-1 text-sm">{review.llm_feedback}</p>
            </div>

            {review.flashcard?.tags && (
              <div className="flex flex-wrap gap-2 mb-4">
                {normalizeTags(review.flashcard.tags).map((tag: string) => (
                  <span key={tag} className="px-3 py-1 bg-accent/10 text-accent dark:bg-accent/20 dark:text-accent rounded-full text-sm font-medium">
                    {tag}
                  </span>
                ))}
              </div>
            )}

            <div className="text-sm text-gray-500 dark:text-gray-400">
              Reviewed on {new Date(review.created_at).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReviewHistoryPage;
