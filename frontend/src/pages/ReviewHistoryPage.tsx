import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Review {
  id: number;
  flashcard: {
    concept: string;
  };
  user_response: string;
  was_correct: boolean;
  confidence_score: number;
  llm_feedback: string;
  created_at: string;
}

const ReviewHistoryPage: React.FC = () => {
  const [reviews, setReviews] = useState<Review[]>([]);

  useEffect(() => {
    axios
      .get('http://localhost:8000/reviews/1') // Replace 1 with dynamic user ID later
      .then((res) => setReviews(res.data))
      .catch((err) => console.error('Error fetching reviews:', err));
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Review History</h2>
      <ul>
        {reviews.map((r) => (
          <li key={r.id} className="mb-3 p-3 border rounded shadow">
            <div><strong>Concept:</strong> {r.flashcard?.concept || 'Unknown'}</div>
            <div><strong>Your Answer:</strong> {r.user_response}</div>
            <div><strong>Result:</strong> {r.was_correct ? '✅ Correct' : '❌ Incorrect'}</div>
            <div><strong>Confidence:</strong> {(r.confidence_score * 100).toFixed(0)}%</div>
            <div><strong>Date:</strong> {new Date(r.created_at).toLocaleString()}</div>
            <div><strong>LLM Feedback:</strong> {r.llm_feedback}</div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ReviewHistoryPage;
