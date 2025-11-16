import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface DataPoint {
  date: string;
  accuracy: number;
  average_confidence: number;
  total_reviews: number;
  correct_reviews: number;
}

interface MasteryData {
  deck_id: number;
  deck_name: string;
  data_points: DataPoint[];
  current_streak: number;
  longest_streak: number;
}

const MasteryGraph: React.FC = () => {
  const { deckId } = useParams<{ deckId: string }>();
  const navigate = useNavigate();
  const { token } = useAuth();
  const [masteryData, setMasteryData] = useState<MasteryData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token || !deckId) {
      setError('Missing authentication or deck ID');
      setIsLoading(false);
      return;
    }

    const fetchMasteryData = async () => {
      try {
        const response = await axios.get(
          buildApiUrl(`/decks/${deckId}/mastery`),
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );
        setMasteryData(response.data);
      } catch (err: any) {
        console.error('Error fetching mastery data:', err);
        setError(err.response?.data?.detail || 'Failed to load mastery data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchMasteryData();
  }, [token, deckId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 flex items-center justify-center">
        <div className="text-xl text-red-600 dark:text-red-400">{error}</div>
      </div>
    );
  }

  if (!masteryData) {
    return (
      <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 flex items-center justify-center">
        <div className="text-xl text-secondary-600 dark:text-secondary-400">No data available</div>
      </div>
    );
  }

  // Format dates for display
  const formattedData = masteryData.data_points.map(point => ({
    ...point,
    date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }));

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <button
            onClick={() => navigate('/decks')}
            className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 mb-4"
          >
            ← Back to Decks
          </button>
          <h1 className="text-3xl font-bold text-secondary-900 dark:text-white">
            Mastery Graph: {masteryData.deck_name}
          </h1>
        </div>

        {formattedData.length === 0 ? (
          <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-8 text-center">
            <p className="text-secondary-600 dark:text-secondary-400">
              No review data yet. Start reviewing cards to see your progress!
            </p>
          </div>
        ) : (
          <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-6">
            <h2 className="text-xl font-semibold text-secondary-900 dark:text-white mb-4">
              Performance Over Time
            </h2>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={formattedData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="date"
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                />
                <YAxis
                  yAxisId="left"
                  stroke="#3b82f6"
                  style={{ fontSize: '12px' }}
                  domain={[0, 100]}
                  label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft' }}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  stroke="#10b981"
                  style={{ fontSize: '12px' }}
                  label={{ value: 'Cards Reviewed', angle: 90, position: 'insideRight' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                  }}
                  formatter={(value: any, name: string) => {
                    if (name === 'accuracy') return [`${value}%`, 'Accuracy'];
                    if (name === 'cards_reviewed') return [value, 'Cards Reviewed'];
                    return [value, name];
                  }}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="accuracy"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="Accuracy (%)"
                  dot={{ r: 4 }}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="cards_reviewed"
                  stroke="#10b981"
                  strokeWidth={2}
                  name="Cards Reviewed"
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-secondary-50 dark:bg-secondary-900 rounded-lg p-4">
                <div className="text-sm text-secondary-600 dark:text-secondary-400">Total Reviews</div>
                <div className="text-2xl font-bold text-secondary-900 dark:text-white">
                  {formattedData.reduce((sum, point) => sum + point.total_reviews, 0)}
                </div>
              </div>
              <div className="bg-secondary-50 dark:bg-secondary-900 rounded-lg p-4">
                <div className="text-sm text-secondary-600 dark:text-secondary-400">Average Accuracy</div>
                <div className="text-2xl font-bold text-secondary-900 dark:text-white">
                  {formattedData.length > 0
                    ? `${(
                        formattedData.reduce((sum, point) => sum + point.accuracy, 0) /
                        formattedData.length
                      ).toFixed(1)}%`
                    : '0%'}
                </div>
              </div>
              <div className="bg-secondary-50 dark:bg-secondary-900 rounded-lg p-4">
                <div className="text-sm text-secondary-600 dark:text-secondary-400">Days Studied</div>
                <div className="text-2xl font-bold text-secondary-900 dark:text-white">
                  {formattedData.length}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MasteryGraph;

