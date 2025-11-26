import React, { useState, useMemo } from 'react';
import {
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Line,
  ReferenceLine
} from 'recharts';

interface AccuracyGraphProps {
  stats: any;
}

// Beautiful, distinct color palette with better contrast
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
  
  // Calculate 7-day rolling average
  const calculateRollingAverage = (points: any[], windowDays: number = 7) => {
    if (points.length === 0) return [];
    
    // Sort points by date
    const sortedPoints = [...points].sort((a, b) => a.x - b.x);
    const result: any[] = [];
    
    for (let i = 0; i < sortedPoints.length; i++) {
      const currentDate = sortedPoints[i].x;
      const windowStart = currentDate - (windowDays * 24 * 60 * 60 * 1000); // 7 days in milliseconds
      
      // Find all points within the window
      const windowPoints = sortedPoints.filter(p => p.x >= windowStart && p.x <= currentDate);
      
      if (windowPoints.length > 0) {
        const avgAccuracy = windowPoints.reduce((sum, p) => sum + p.y, 0) / windowPoints.length;
        result.push({
          ...sortedPoints[i],
          rollingAverage: avgAccuracy
        });
      } else {
        result.push({
          ...sortedPoints[i],
          rollingAverage: sortedPoints[i].y
        });
      }
    }
    
    return result;
  };
  
  // Calculate linear regression for trend line
  const calculateTrend = (points: any[]) => {
    if (points.length === 0) return [];
    
    const n = points.length;
    const xValues = points.map((_, i) => i);
    const yValues = points.map((p: any) => p.rollingAverage ?? p.accuracy ?? p.y);
    
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
  
  // Prepare data - flatten all series into a single array for better tooltip handling
  const { chartData, seriesConfig } = useMemo(() => {
    if (viewMode === 'overall') {
      const points = overallData.map((point: any) => ({
        ...point,
        x: new Date(point.date).getTime(),
        y: point.accuracy,
        dateLabel: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }));
      const withRollingAvg = calculateRollingAverage(points, 7);
      const withTrend = calculateTrend(withRollingAvg);
      
      // Create a flat data structure where each date has all series data
      const flatData = withTrend.map((point: any) => ({
        date: point.date,
        dateLabel: point.dateLabel,
        x: point.x,
        'Overall Accuracy (7-day avg)': point.rollingAverage,
        'Overall Trend': point.trend,
      }));
      
      return {
        chartData: flatData,
        seriesConfig: [
          { key: 'Overall Accuracy (7-day avg)', type: 'line', color: DECK_COLORS[0], name: 'Overall Accuracy (7-day avg)' },
          { key: 'Overall Trend', type: 'line', color: DECK_COLORS[0], name: 'Overall Trend' }
        ]
      };
    } else {
      // For deck comparison, create a flat structure
      const allDates = new Set<number>();
      const deckPointsMap: Map<number, Map<number, any>> = new Map();
      
      selectedDecks.forEach((deckId, index) => {
        const deck = deckData.find((d: any) => d.deck_id === deckId);
        if (!deck) return;
        
        const points = deck.data_points.map((point: any) => ({
          ...point,
          x: new Date(point.date).getTime(),
          y: point.accuracy,
          dateLabel: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        }));
        
        const withRollingAvg = calculateRollingAverage(points, 7);
        const withTrend = calculateTrend(withRollingAvg);
        const pointsMap = new Map<number, any>();
        
        withTrend.forEach((point: any) => {
          allDates.add(point.x);
          pointsMap.set(point.x, {
            ...point,
            deckName: deck.deck_name,
            deckId: deck.deck_id,
            color: DECK_COLORS[index % DECK_COLORS.length]
          });
        });
        
        deckPointsMap.set(deckId, pointsMap);
      });
      
      // Create flat data structure
      const flatData: any[] = [];
      Array.from(allDates).sort().forEach(x => {
        const dateObj = new Date(x);
        const entry: any = {
          date: dateObj.toISOString(),
          dateLabel: dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          x: x
        };
        
        selectedDecks.forEach((deckId) => {
          const pointsMap = deckPointsMap.get(deckId);
          if (pointsMap && pointsMap.has(x)) {
            const point = pointsMap.get(x);
            entry[`${point.deckName} (7-day avg)`] = point.rollingAverage;
            entry[`${point.deckName} Trend`] = point.trend;
          }
        });
        
        flatData.push(entry);
      });
      
      const config: any[] = [];
      selectedDecks.forEach((deckId, index) => {
        const deck = deckData.find((d: any) => d.deck_id === deckId);
        if (!deck) return;
        const color = DECK_COLORS[index % DECK_COLORS.length];
        config.push(
          { key: `${deck.deck_name} (7-day avg)`, type: 'line', color, name: deck.deck_name },
          { key: `${deck.deck_name} Trend`, type: 'line', color, name: `${deck.deck_name} Trend` }
        );
      });
      
      return { chartData: flatData, seriesConfig: config };
    }
  }, [viewMode, overallData, deckData, selectedDecks]);
  
  // Custom tooltip that correctly handles multiple series
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || payload.length === 0) {
      return null;
    }
    
    // Get date label from the first payload
    const dateLabel = payload[0]?.payload?.dateLabel || label;
    
    // Filter out null/undefined values and group by series
    const seriesMap = new Map<string, { accuracy: number | null; trend: number | null; color: string }>();
    
    payload.forEach((entry: any) => {
      const name = entry.name || entry.dataKey;
      if (!name) return;
      
      // Determine if this is a trend or accuracy entry
      const isTrend = name.includes('Trend');
      const baseName = name.replace(' Trend', '').replace(' (7-day avg)', '').replace(' Accuracy', '');
      
      if (!seriesMap.has(baseName)) {
        seriesMap.set(baseName, { accuracy: null, trend: null, color: entry.color || DECK_COLORS[0] });
      }
      
      const series = seriesMap.get(baseName)!;
      const value = entry.value;
      
      if (isTrend) {
        series.trend = value;
      } else {
        series.accuracy = value;
      }
      series.color = entry.color || series.color;
    });
    
    return (
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl p-4 min-w-[200px]">
        <p className="font-semibold text-gray-900 dark:text-gray-100 mb-3 text-sm border-b border-gray-200 dark:border-gray-700 pb-2">
          {dateLabel}
        </p>
        <div className="space-y-2">
          {Array.from(seriesMap.entries()).map(([name, data]) => (
            <div key={name} className="space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: data.color }}
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{name}</span>
                </div>
              </div>
              {data.accuracy !== null && (
                <div className="ml-5 text-xs text-gray-600 dark:text-gray-400">
                  7-day avg: <span className="font-semibold text-gray-900 dark:text-gray-100">{data.accuracy.toFixed(1)}%</span>
                </div>
              )}
              {data.trend !== null && (
                <div className="ml-5 text-xs text-gray-500 dark:text-gray-500 italic">
                  Trend: {data.trend.toFixed(1)}%
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-light text-gray-900 dark:text-darktext">Accuracy Over Time</h2>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            7-day rolling average with trend line
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('overall')}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
              viewMode === 'overall'
                ? 'bg-primary-500 text-white dark:bg-primary-600 shadow-md'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            Overall
          </button>
          <button
            onClick={() => setViewMode('decks')}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
              viewMode === 'decks'
                ? 'bg-primary-500 text-white dark:bg-primary-600 shadow-md'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            By Deck
          </button>
        </div>
      </div>
      
      {viewMode === 'decks' && (
        <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Select decks to compare:</div>
          <div className="flex flex-wrap gap-2">
            {deckData.map((deck: any, index: number) => {
              const isSelected = selectedDecks.includes(deck.deck_id);
              const deckIndex = selectedDecks.indexOf(deck.deck_id);
              const color = isSelected ? DECK_COLORS[deckIndex % DECK_COLORS.length] : undefined;
              
              return (
                <button
                  key={deck.deck_id}
                  onClick={() => handleDeckToggle(deck.deck_id)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-200 ${
                    isSelected
                      ? 'text-white shadow-md'
                      : 'bg-white text-gray-700 border border-gray-300 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700 hover:border-primary-400 dark:hover:border-primary-500'
                  }`}
                  style={isSelected ? { backgroundColor: color } : {}}
                >
                  {deck.deck_name}
                </button>
              );
            })}
          </div>
          {selectedDecks.length === 0 && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 italic">
              Select at least one deck to view comparison
            </p>
          )}
        </div>
      )}
      
      {chartData.length > 0 && (viewMode === 'overall' || selectedDecks.length > 0) ? (
        <div>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart 
              data={chartData}
              margin={{ top: 20, right: 30, bottom: 20, left: 20 }}
            >
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="#e5e7eb" 
                strokeOpacity={0.5}
                vertical={false}
              />
              <XAxis
                type="number"
                dataKey="x"
                domain={['dataMin', 'dataMax']}
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                stroke="#6b7280"
                style={{ fontSize: '11px' }}
                tick={{ fill: '#6b7280' }}
              />
              <YAxis
                type="number"
                domain={[0, 100]}
                label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fontSize: '12px', fill: '#6b7280' } }}
                stroke="#6b7280"
                style={{ fontSize: '11px' }}
                tick={{ fill: '#6b7280' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="circle"
                formatter={(value) => value.replace(' Accuracy', '').replace(' Trend', '')}
              />
              
              {/* Reference line at 50% for context */}
              <ReferenceLine 
                y={50} 
                stroke="#9ca3af" 
                strokeDasharray="2 2" 
                strokeOpacity={0.5}
                label={{ value: '50%', position: 'right', fill: '#9ca3af', fontSize: '10px' }}
              />
              
              {/* Render rolling average lines (solid) */}
              {seriesConfig
                .filter(s => s.type === 'line' && !s.key.includes('Trend'))
                .map((series, index) => (
                  <Line
                    key={series.key}
                    type="monotone"
                    dataKey={series.key}
                    stroke={series.color}
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5, fill: series.color, strokeWidth: 2 }}
                    connectNulls
                    strokeOpacity={0.9}
                  />
                ))}
              
              {/* Render trend lines (dashed, behind rolling average) */}
              {seriesConfig
                .filter(s => s.type === 'line' && s.key.includes('Trend'))
                .map((series, index) => (
                  <Line
                    key={series.key}
                    type="linear"
                    dataKey={series.key}
                    stroke={series.color}
                    strokeWidth={2}
                    strokeDasharray="6 4"
                    dot={false}
                    activeDot={false}
                    connectNulls
                    strokeOpacity={0.6}
                  />
                ))}
            </ComposedChart>
          </ResponsiveContainer>
          
          {/* Summary stats */}
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            {viewMode === 'overall' && overallData.length > 0 && (
              <>
                <div className="text-center">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Average Accuracy</div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-darktext">
                    {(
                      overallData.reduce((sum: number, p: any) => sum + p.accuracy, 0) / overallData.length
                    ).toFixed(1)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Data Points</div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-darktext">
                    {overallData.length}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Highest</div>
                  <div className="text-lg font-semibold text-green-600 dark:text-green-400">
                    {Math.max(...overallData.map((p: any) => p.accuracy)).toFixed(1)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Lowest</div>
                  <div className="text-lg font-semibold text-red-600 dark:text-red-400">
                    {Math.min(...overallData.map((p: any) => p.accuracy)).toFixed(1)}%
                  </div>
                </div>
              </>
            )}
            {viewMode === 'decks' && selectedDecks.length > 0 && (
              <div className="col-span-2 md:col-span-4 text-center text-sm text-gray-600 dark:text-gray-400">
                Comparing {selectedDecks.length} deck{selectedDecks.length !== 1 ? 's' : ''}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <div className="text-sm mb-2">
            {viewMode === 'decks' && selectedDecks.length === 0
              ? 'Select at least one deck to view comparison'
              : 'No accuracy data yet. Start reviewing cards to see your progress!'}
          </div>
        </div>
      )}
    </div>
  );
};

export default AccuracyGraph;
