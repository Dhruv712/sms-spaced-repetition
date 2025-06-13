import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface ReviewStatsData {
  total: number;
  correct: number;
  average_confidence: number;
}

const ReviewStats: React.FC = () => {
  const [stats, setStats] = useState<ReviewStatsData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    axios
      .get('http://localhost:8000/reviews/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then((res) => setStats(res.data))
      .catch((err) => {
        console.error(err);
        setError('Failed to fetch stats');
      });
  }, [token]);

  if (error) return <div className="text-red-600">{error}</div>;
  if (!stats) return <div>Loading review stats...</div>;

  const winRate = ((stats.correct / stats.total) * 100).toFixed(1);
  const avgConfidence = (stats.average_confidence * 100).toFixed(1);

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
      <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-darktext">📊 Review Stats</h2>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-secondary-50 dark:bg-secondary-700 rounded-lg">
          <p className="text-sm text-secondary-600 dark:text-secondary-300">Total Reviews</p>
          <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">{stats.total}</p>
        </div>
        <div className="p-4 bg-secondary-50 dark:bg-secondary-700 rounded-lg">
          <p className="text-sm text-secondary-600 dark:text-secondary-300">Correct Answers</p>
          <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">{stats.correct}</p>
        </div>
        <div className="p-4 bg-secondary-50 dark:bg-secondary-700 rounded-lg">
          <p className="text-sm text-secondary-600 dark:text-secondary-300">Win Rate</p>
          <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">{winRate}%</p>
        </div>
        <div className="p-4 bg-secondary-50 dark:bg-secondary-700 rounded-lg">
          <p className="text-sm text-secondary-600 dark:text-secondary-300">Avg Confidence</p>
          <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">{avgConfidence}%</p>
        </div>
      </div>
    </div>
  );
};

export default ReviewStats;
