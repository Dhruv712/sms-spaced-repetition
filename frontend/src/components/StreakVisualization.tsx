import React from 'react';

interface StreakVisualizationProps {
  stats: any;
}

const StreakVisualization: React.FC<StreakVisualizationProps> = ({ stats }) => {
  const currentStreak = stats?.streak?.current || 0;
  const longestStreak = stats?.streak?.longest || 0;
  const streakHistory = stats?.streak?.history || [];
  
  // Milestones
  const milestones = [7, 14, 30, 60, 100, 365];
  const nextMilestone = milestones.find(m => m > currentStreak) || null;
  const progressToNext = nextMilestone ? (currentStreak / nextMilestone * 100) : 100;
  
  // Show last 30 days of streak history
  const recentHistory = streakHistory.slice(-30);
  
  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-6">Streak Progress</h2>
      
      {/* Current Streak */}
      <div className="mb-6">
        <div className="flex items-baseline justify-between mb-2">
          <div className="text-sm text-gray-600 dark:text-gray-400">Current Streak</div>
          <div className="text-xs text-gray-500 dark:text-gray-500">Longest: {longestStreak} days</div>
        </div>
        <div className="text-5xl font-light text-primary-600 dark:text-primary-400 mb-2">
          {currentStreak}
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400">days</div>
      </div>
      
      {/* Progress to Next Milestone */}
      {nextMilestone && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <div className="text-xs text-gray-600 dark:text-gray-400">
              {nextMilestone - currentStreak} days until {nextMilestone} day milestone
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-500">
              {Math.round(progressToNext)}%
            </div>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-primary-500 dark:bg-primary-400 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(progressToNext, 100)}%` }}
            />
          </div>
        </div>
      )}
      
      {/* Recent Activity (30 days) */}
      <div className="mt-6">
        <div className="text-xs text-gray-600 dark:text-gray-400 mb-3">Last 30 Days</div>
        <div className="flex gap-1 flex-wrap">
          {recentHistory.map((day: any, index: number) => {
            const date = new Date(day.date);
            const isToday = date.toDateString() === new Date().toDateString();
            
            return (
              <div
                key={index}
                className={`w-2 h-2 rounded ${
                  day.reviewed
                    ? 'bg-primary-500 dark:bg-primary-400'
                    : 'bg-gray-200 dark:bg-gray-700'
                } ${isToday ? 'ring-2 ring-primary-400 dark:ring-primary-500' : ''}`}
                title={`${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}: ${day.reviewed ? 'Reviewed' : 'No reviews'}`}
              />
            );
          })}
        </div>
        <div className="flex items-center justify-between mt-3 text-xs text-gray-500 dark:text-gray-400">
          <span>30 days ago</span>
          <span>Today</span>
        </div>
      </div>
      
      {/* Milestones */}
      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-600 dark:text-gray-400 mb-3">Milestones</div>
        <div className="flex flex-wrap gap-2">
          {milestones.map((milestone) => {
            const achieved = currentStreak >= milestone;
            const isLongest = longestStreak >= milestone;
            
            return (
              <div
                key={milestone}
                className={`px-2 py-1 rounded text-xs ${
                  achieved
                    ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'
                }`}
              >
                {milestone} {achieved && isLongest ? '⭐' : achieved ? '✓' : ''}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default StreakVisualization;

