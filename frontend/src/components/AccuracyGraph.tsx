import React, { useState, useMemo } from 'react';
import {
  ComposedChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Line
} from 'recharts';

interface AccuracyGraphProps {
  stats: any;
}

// Better color palette - more distinct colors (moved outside component to avoid dependency issues)
const DECK_COLORS = [
  '#3b82f6', // Blue
  '#ef4444', // Red
  '#10b981', // Green
  '#f59e0b', // Amber
  '#8b5cf6', // Purple
  '#ec4899', // Pink
  '#06b6d4', // Cyan
  '#f97316', // Orange
];

const AccuracyGraph: React.FC<AccuracyGraphProps> = ({ stats }) => {
  const [viewMode, setViewMode] = useState<'overall' | 'decks'>('overall');
  const [selectedDecks, setSelectedDecks] = useState<number[]>([]);
  
  // Memoize data to avoid dependency issues
  const overallData = useMemo(() => stats?.accuracy_over_time || [], [stats?.accuracy_over_time]);
  const deckData = useMemo(() => stats?.deck_accuracy || [], [stats?.deck_accuracy]);
  
  const handleDeckToggle = (deckId: number) => {
    setSelectedDecks(prev => 
      prev.includes(deckId) 
        ? prev.filter(id => id !== deckId)
        : [...prev, deckId]
    );
  };
  
  // Calculate linear regression for trend line
  const calculateTrend = (points: any[]) => {
    if (points.length === 0) return [];
    
    const n = points.length;
    const xValues = points.map((_, i) => i);
    const yValues = points.map((p: any) => p.accuracy);
    
    const sumX = xValues.reduce((a, b) => a + b, 0);
    const sumY = yValues.reduce((a, b) => a + b, 0);
    const sumXY = xValues.reduce((sum, x, i) => sum + x * yValues[i], 0);
    const sumXX = xValues.reduce((sum, x) => sum + x * x, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    return points.map((_, i) => ({
      ...points[i],
      trend: slope * i + intercept
    }));
  };
  
  // Prepare scatter data with trend lines
  const { scatterData, trendData } = useMemo(() => {
    if (viewMode === 'overall') {
      const points = overallData.map((point: any) => ({
        ...point,
        x: new Date(point.date).getTime(),
        y: point.accuracy,
        dateLabel: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }));
      const withTrend = calculateTrend(points);
      return {
        scatterData: [{ name: 'Overall Accuracy', data: points }],
        trendData: [{ name: 'Overall Trend', data: withTrend }]
      };
    } else {
      const scatter: any[] = [];
      const trend: any[] = [];
      
      selectedDecks.forEach((deckId, index) => {
        const deck = deckData.find((d: any) => d.deck_id === deckId);
        if (!deck) return;
        
        const points = deck.data_points.map((point: any) => ({
          ...point,
          x: new Date(point.date).getTime(),
          y: point.accuracy,
          dateLabel: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        }));
        
        const withTrend = calculateTrend(points);
        scatter.push({
          name: deck.deck_name,
          data: points,
          color: DECK_COLORS[index % DECK_COLORS.length]
        });
        trend.push({
          name: `${deck.deck_name} Trend`,
          data: withTrend,
          color: DECK_COLORS[index % DECK_COLORS.length]
        });
      });
      
      return { scatterData: scatter, trendData: trend };
    }
  }, [viewMode, overallData, deckData, selectedDecks]);
  
  // Combine all data points for X-axis range
  const allDates = useMemo(() => {
    const dates: number[] = [];
    if (viewMode === 'overall') {
      overallData.forEach((point: any) => {
        dates.push(new Date(point.date).getTime());
      });
    } else {
      selectedDecks.forEach(deckId => {
        const deck = deckData.find((d: any) => d.deck_id === deckId);
        if (deck) {
          deck.data_points.forEach((point: any) => {
            dates.push(new Date(point.date).getTime());
          });
        }
      });
    }
    return dates.length > 0 ? { min: Math.min(...dates), max: Math.max(...dates) } : null;
  }, [viewMode, overallData, deckData, selectedDecks]);
  
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
            {deckData.map((deck: any, index: number) => (
              <button
                key={deck.deck_id}
                onClick={() => handleDeckToggle(deck.deck_id)}
                className={`px-3 py-1 text-xs rounded ${
                  selectedDecks.includes(deck.deck_id)
                    ? 'bg-primary-500 text-white dark:bg-primary-600'
                    : 'bg-white text-gray-700 border border-gray-300 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700'
                }`}
                style={selectedDecks.includes(deck.deck_id) ? {
                  backgroundColor: DECK_COLORS[selectedDecks.indexOf(deck.deck_id) % DECK_COLORS.length]
                } : {}}
              >
                {deck.deck_name}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {scatterData.length > 0 && scatterData[0].data.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              type="number"
              dataKey="x"
              domain={allDates ? ['dataMin', 'dataMax'] : undefined}
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              type="number"
              dataKey="y"
              domain={[0, 100]}
              label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft' }}
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: '4px',
              }}
              formatter={(value: any, name: string, props: any) => [
                `${value.toFixed(1)}%`,
                props.payload?.dateLabel || 'Accuracy'
              ]}
            />
            <Legend />
            {/* Trend lines first (so they're behind scatter points) */}
            {trendData.map((series, index) => (
              <Line
                key={series.name}
                type="linear"
                dataKey="trend"
                data={series.data}
                stroke={series.color || deckColors[index % deckColors.length]}
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name={series.name}
                connectNulls
              />
            ))}
            {/* Scatter points */}
            {scatterData.map((series, index) => (
              <Scatter
                key={series.name}
                name={series.name}
                data={series.data}
                fill={series.color || deckColors[index % deckColors.length]}
                fillOpacity={0.6}
              />
            ))}
          </ComposedChart>
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

