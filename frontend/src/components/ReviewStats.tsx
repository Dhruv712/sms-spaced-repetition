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
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">📊 Review Stats</h2>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-gray-600">Total Reviews</p>
          <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
        </div>
        <div className="p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-gray-600">Correct Answers</p>
          <p className="text-2xl font-bold text-green-600">{stats.correct}</p>
        </div>
        <div className="p-4 bg-purple-50 rounded-lg">
          <p className="text-sm text-gray-600">Win Rate</p>
          <p className="text-2xl font-bold text-purple-600">{winRate}%</p>
        </div>
        <div className="p-4 bg-yellow-50 rounded-lg">
          <p className="text-sm text-gray-600">Avg Confidence</p>
          <p className="text-2xl font-bold text-yellow-600">{avgConfidence}%</p>
        </div>
      </div>
    </div>
  );
};

export default ReviewStats;
