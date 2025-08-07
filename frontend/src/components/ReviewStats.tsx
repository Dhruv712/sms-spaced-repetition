import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { buildApiUrl } from '../config';

interface ReviewStats {
  total: number;
  correct: number;
  average_confidence: number;
}

const ReviewStats: React.FC = () => {
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    const fetchStats = async () => {
      try {
        const response = await axios.get(buildApiUrl('/reviews/stats'), {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setStats(response.data);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
        setError('Failed to load review stats.');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [token]);

  if (error) return <div className="text-red-600">{error}</div>;
  if (loading) return <div>Loading review stats...</div>;
  if (!stats) return <div>No review stats available.</div>;

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
