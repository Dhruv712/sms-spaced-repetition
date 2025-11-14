import React from 'react';

interface ComparisonCardsProps {
  stats: any;
}

const ComparisonCards: React.FC<ComparisonCardsProps> = ({ stats }) => {
  const comparisons = stats?.comparisons || {};
  
  const thisWeek = comparisons.this_week || 0;
  const lastWeek = comparisons.last_week || 0;
  const thisMonth = comparisons.this_month || 0;
  const lastMonth = comparisons.last_month || 0;
  
  const weekChange = lastWeek > 0 ? ((thisWeek - lastWeek) / lastWeek * 100) : (thisWeek > 0 ? 100 : 0);
  const monthChange = lastMonth > 0 ? ((thisMonth - lastMonth) / lastMonth * 100) : (thisMonth > 0 ? 100 : 0);
  
  const weekTrend = thisWeek >= lastWeek ? 'up' : 'down';
  const monthTrend = thisMonth >= lastMonth ? 'up' : 'down';
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      {/* This Week vs Last Week */}
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h3 className="text-sm font-light text-gray-600 dark:text-gray-400 mb-4">This Week vs Last Week</h3>
        <div className="flex items-end justify-between">
          <div>
            <div className="text-3xl font-light text-gray-900 dark:text-darktext mb-1">
              {thisWeek}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">cards reviewed</div>
          </div>
          <div className="text-right">
            <div className={`text-lg font-light mb-1 ${weekTrend === 'up' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              {weekTrend === 'up' ? '↑' : '↓'} {Math.abs(weekChange).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              vs {lastWeek} last week
            </div>
          </div>
        </div>
      </div>
      
      {/* This Month vs Last Month */}
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h3 className="text-sm font-light text-gray-600 dark:text-gray-400 mb-4">This Month vs Last Month</h3>
        <div className="flex items-end justify-between">
          <div>
            <div className="text-3xl font-light text-gray-900 dark:text-darktext mb-1">
              {thisMonth}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">cards reviewed</div>
          </div>
          <div className="text-right">
            <div className={`text-lg font-light mb-1 ${monthTrend === 'up' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              {monthTrend === 'up' ? '↑' : '↓'} {Math.abs(monthChange).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              vs {lastMonth} last month
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonCards;

