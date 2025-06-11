import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

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
        const response = await axios.get('http://localhost:8000/reviews', {
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

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading review history...</div>
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

  if (reviews.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">No review history available.</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Review History</h1>

      <div className="space-y-4">
        {reviews.map((review) => (
          <div key={review.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold">{review.flashcard?.concept || '[Flashcard Missing]'}</h3>
                <p className="text-gray-600 mt-1">{review.flashcard?.definition || ''}</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-700">
                  <strong>Your Answer:</strong> {review.user_response}
                </div>
                <div className="text-sm text-gray-700">
                  <strong>Result:</strong> {review.was_correct ? '✅ Correct' : '❌ Incorrect'}
                </div>
                <div className="text-sm text-gray-700">
                  <strong>Confidence:</strong> {(review.confidence_score * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            <div className="mb-4 p-3 bg-gray-50 rounded-lg text-gray-700">
              <strong>LLM Feedback:</strong>
              <p className="mt-1 text-sm">{review.llm_feedback}</p>
            </div>

            {review.flashcard?.tags && (
              <div className="flex flex-wrap gap-2 mb-4">
                {(
                  Array.isArray(review.flashcard.tags)
                    ? review.flashcard.tags
                    : (review.flashcard.tags as string).split(',').map((t: string) => t.trim())
                ).filter(Boolean).map((tag: string) => (
                  <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                    {tag}
                  </span>
                ))}
              </div>
            )}

            <div className="text-sm text-gray-500">
              Reviewed on {new Date(review.created_at).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReviewHistoryPage;
