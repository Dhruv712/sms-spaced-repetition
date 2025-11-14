import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { buildApiUrl } from '../config';

interface ReviewStatsData {
  total: number;
  correct: number;
}

const ReviewStats: React.FC = () => {
  const [stats, setStats] = useState<ReviewStatsData | null>(null);
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

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
      <h2 className="text-lg font-light mb-3 text-gray-800 dark:text-darktext">Review Stats</h2>
      <div className="flex flex-wrap gap-3">
        <div className="flex-1 min-w-[120px] p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-xs text-gray-600 dark:text-gray-400">Total Reviews</p>
          <p className="text-xl font-light text-gray-900 dark:text-gray-100">{stats.total}</p>
        </div>
        <div className="flex-1 min-w-[120px] p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-xs text-gray-600 dark:text-gray-400">Correct</p>
          <p className="text-xl font-light text-gray-900 dark:text-gray-100">{stats.correct}</p>
        </div>
        <div className="flex-1 min-w-[120px] p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-xs text-gray-600 dark:text-gray-400">Accuracy</p>
          <p className="text-xl font-light text-gray-900 dark:text-gray-100">{winRate}%</p>
        </div>
      </div>
    </div>
  );
};

export default ReviewStats;
