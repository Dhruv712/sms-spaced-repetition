import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';

interface DailySummaryData {
  total_reviews: number;
  correct_reviews: number;
  percent_correct: number;
  problem_areas: Array<{
    concept: string;
    confidence_score: number;
  }>;
  streak_days: number;
  next_due_cards: number;
}

const DailySummary: React.FC = () => {
  const [summary, setSummary] = useState<DailySummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    const fetchDailySummary = async () => {
      try {
        // First get the user data to get the ID
        const userResponse = await axios.get(buildApiUrl('/auth/me'), {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        const userId = userResponse.data.id;
        
        // Then get the daily summary
        const summaryResponse = await axios.get(buildApiUrl(`/admin/daily-summary/${userId}`), {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (summaryResponse.data.success) {
          setSummary(summaryResponse.data.summary);
        } else {
          setError('Failed to load daily summary.');
        }
      } catch (err) {
        console.error('Failed to fetch daily summary:', err);
        setError('Failed to load daily summary.');
      } finally {
        setLoading(false);
      }
    };

    fetchDailySummary();
  }, [token]);

  if (error) return <div className="text-red-600">{error}</div>;
  if (loading) return <div>Loading daily summary...</div>;
  if (!summary) return <div>No daily summary available.</div>;

  const formatPercent = (num: number) => `${num.toFixed(1)}%`;

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700 mb-6">
      <h2 className="text-lg font-semibold mb-3 text-gray-800 dark:text-darktext">📅 Today's Summary</h2>
      
      {/* Main Stats Row */}
      <div className="flex flex-wrap gap-3 mb-4">
        <div className="flex-1 min-w-[120px] p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-xs text-blue-600 dark:text-blue-300">Reviews Today</p>
          <p className="text-xl font-bold text-blue-600 dark:text-blue-400">{summary.total_reviews}</p>
        </div>
        <div className="flex-1 min-w-[120px] p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <p className="text-xs text-green-600 dark:text-green-300">Correct</p>
          <p className="text-xl font-bold text-green-600 dark:text-green-400">{summary.correct_reviews}</p>
        </div>
        <div className="flex-1 min-w-[120px] p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
          <p className="text-xs text-purple-600 dark:text-purple-300">Accuracy</p>
          <p className="text-xl font-bold text-purple-600 dark:text-purple-400">{formatPercent(summary.percent_correct)}</p>
        </div>
        <div className="flex-1 min-w-[120px] p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
          <p className="text-xs text-orange-600 dark:text-orange-300">Streak</p>
          <p className="text-xl font-bold text-orange-600 dark:text-orange-400">{summary.streak_days} days</p>
        </div>
      </div>

      {/* Problem Areas */}
      {summary.problem_areas && summary.problem_areas.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🎯 Areas to Review</h3>
          <div className="space-y-2">
            {summary.problem_areas.slice(0, 3).map((area, index) => (
              <div key={index} className="flex justify-between items-center p-2 bg-red-50 dark:bg-red-900/20 rounded">
                <span className="text-sm text-gray-700 dark:text-gray-300">{area.concept}</span>
                <span className="text-xs text-red-600 dark:text-red-400">
                  {formatPercent(area.confidence_score)} confidence
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next Due Cards */}
      <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <span className="text-sm text-gray-600 dark:text-gray-300">Cards due tomorrow:</span>
        <span className="text-lg font-semibold text-gray-800 dark:text-gray-200">{summary.next_due_cards}</span>
      </div>
    </div>
  );
};

export default DailySummary;
