import React, { useState } from 'react';
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

interface AccuracyGraphProps {
  stats: any;
}

const AccuracyGraph: React.FC<AccuracyGraphProps> = ({ stats }) => {
  const [viewMode, setViewMode] = useState<'overall' | 'decks'>('overall');
  const [selectedDecks, setSelectedDecks] = useState<number[]>([]);
  
  const overallData = stats?.accuracy_over_time || [];
  const deckData = stats?.deck_accuracy || [];
  
  const handleDeckToggle = (deckId: number) => {
    setSelectedDecks(prev => 
      prev.includes(deckId) 
        ? prev.filter(id => id !== deckId)
        : [...prev, deckId]
    );
  };
  
  // Prepare chart data
  const chartData = viewMode === 'overall' 
    ? overallData.map((point: any) => ({
        ...point,
        date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }))
    : (() => {
        // Combine selected deck data
        const dateMap: any = {};
        selectedDecks.forEach(deckId => {
          const deck = deckData.find((d: any) => d.deck_id === deckId);
          if (deck) {
            deck.data_points.forEach((point: any) => {
              const dateKey = point.date;
              if (!dateMap[dateKey]) {
                dateMap[dateKey] = { date: new Date(dateKey).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) };
              }
              dateMap[dateKey][`deck_${deckId}`] = point.accuracy;
            });
          }
        });
        return Object.values(dateMap);
      })();
  
  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-light text-gray-900 dark:text-darktext">Accuracy Over Time</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('overall')}
            className={`px-3 py-1 text-sm rounded ${
              viewMode === 'overall'
                ? 'bg-primary-500 text-white dark:bg-primary-600'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
            }`}
          >
            Overall
          </button>
          <button
            onClick={() => setViewMode('decks')}
            className={`px-3 py-1 text-sm rounded ${
              viewMode === 'decks'
                ? 'bg-primary-500 text-white dark:bg-primary-600'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
            }`}
          >
            By Deck
          </button>
        </div>
      </div>
      
      {viewMode === 'decks' && (
        <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-900 rounded">
          <div className="text-sm text-gray-700 dark:text-gray-300 mb-2">Select decks to compare:</div>
          <div className="flex flex-wrap gap-2">
            {deckData.map((deck: any) => (
              <button
                key={deck.deck_id}
                onClick={() => handleDeckToggle(deck.deck_id)}
                className={`px-3 py-1 text-xs rounded ${
                  selectedDecks.includes(deck.deck_id)
                    ? 'bg-primary-500 text-white dark:bg-primary-600'
                    : 'bg-white text-gray-700 border border-gray-300 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700'
                }`}
              >
                {deck.deck_name}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              domain={[0, 100]}
              label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: '4px',
              }}
              formatter={(value: any) => [`${value.toFixed(1)}%`, 'Accuracy']}
            />
            <Legend />
            {viewMode === 'overall' ? (
              <Line
                type="monotone"
                dataKey="accuracy"
                stroke="#627d98"
                strokeWidth={2}
                name="Overall Accuracy"
                dot={false}
              />
            ) : (
              selectedDecks.map((deckId, index) => {
                const deck = deckData.find((d: any) => d.deck_id === deckId);
                const colors = ['#627d98', '#829ab1', '#9fb3c8', '#bcccdc'];
                return (
                  <Line
                    key={deckId}
                    type="monotone"
                    dataKey={`deck_${deckId}`}
                    stroke={colors[index % colors.length]}
                    strokeWidth={2}
                    name={deck?.deck_name || `Deck ${deckId}`}
                    dot={false}
                  />
                );
              })
            )}
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
          No accuracy data yet. Start reviewing cards to see your progress!
        </div>
      )}
    </div>
  );
};

export default AccuracyGraph;

