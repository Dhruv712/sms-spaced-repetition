import React from 'react';

interface StreakDisplayProps {
  user: any;
  stats: any;
}

const StreakDisplay: React.FC<StreakDisplayProps> = ({ user, stats }) => {
  const currentStreak = stats?.streak?.current || user?.current_streak_days || 0;
  const longestStreak = stats?.streak?.longest || user?.longest_streak_days || 0;

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Streak</h2>
      <div className="space-y-4">
        <div>
          <div className="text-4xl font-light text-primary-600 dark:text-primary-400 mb-1">
            {currentStreak}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">days current</div>
        </div>
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-lg font-light text-gray-700 dark:text-gray-300">
            {longestStreak}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-500">longest streak</div>
        </div>
      </div>
    </div>
  );
};

export default StreakDisplay;

