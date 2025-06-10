import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface ReviewStatsData {
  total: number;
  correct: number;
  average_confidence: number;
}

const ReviewStats: React.FC<{ userId: number }> = ({ userId }) => {
  const [stats, setStats] = useState<ReviewStatsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    axios
      .get(`http://localhost:8000/reviews/stats/${userId}`)
      .then((res) => setStats(res.data))
      .catch((err) => {
        console.error(err);
        setError('Failed to fetch stats');
      });
  }, [userId]);

  if (error) return <div className="text-red-600">{error}</div>;
  if (!stats) return <div>Loading review stats...</div>;

  const winRate = ((stats.correct / stats.total) * 100).toFixed(1);
  const avgConfidence = (stats.average_confidence * 100).toFixed(1);

  return (
    <div className="mt-6 p-4 border rounded shadow bg-white dark:bg-gray-800 dark:text-white">
      <h2 className="text-xl font-semibold mb-2">📊 Review Stats</h2>
      <p>Total Reviews: {stats.total}</p>
      <p>Correct Answers: {stats.correct}</p>
      <p>Win Rate: {winRate}%</p>
      <p>Avg Confidence: {avgConfidence}%</p>
    </div>
  );
};

export default ReviewStats;
