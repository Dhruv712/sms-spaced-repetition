import React from 'react';
import ActivityHeatmap from './ActivityHeatmap';
import DifficultCards from './DifficultCards';

interface GamifiedDashboardProps {
  stats: any;
}

const GamifiedDashboard: React.FC<GamifiedDashboardProps> = ({ stats }) => {
  const hasReviewedToday = stats?.streak?.has_reviewed_today ?? false;
  const potentialStreak = stats?.streak?.potential || 0;
  const currentStreak = stats?.streak?.current || 0;
  const longestStreak = stats?.streak?.longest || 0;
  
  // Display the potential streak if they haven't reviewed today, otherwise show actual streak
  const displayStreak = hasReviewedToday ? currentStreak : potentialStreak;
  
  // Milestones
  const milestones = [7, 14, 30, 60, 100, 365];
  const nextMilestone = milestones.find(m => m > displayStreak) || null;
  const progressToNext = nextMilestone ? (displayStreak / nextMilestone * 100) : 100;
  
  // Celebratory messages based on streak
  const getStreakMessage = () => {
    if (displayStreak === 0) {
      return "Start your learning journey today! 🚀";
    } else if (displayStreak >= 365) {
      return "🔥 A FULL YEAR! You're absolutely incredible! 🔥";
    } else if (displayStreak >= 100) {
      return "🔥 100+ days! You're a learning legend! 🔥";
    } else if (displayStreak >= 60) {
      return "🔥 Amazing! 60+ days of consistent learning! 🔥";
    } else if (displayStreak >= 30) {
      return "🔥 Incredible! You've hit 30 days! 🔥";
    } else if (displayStreak >= 14) {
      return "🔥 Two weeks strong! Keep it going! 🔥";
    } else if (displayStreak >= 7) {
      return "🔥 One week streak! You're on fire! 🔥";
    } else if (displayStreak >= 3) {
      return "🔥 Great start! Your streak is building! 🔥";
    } else {
      return "🔥 You're building momentum! Keep it up! 🔥";
    }
  };

  // Get positive stat messages
  const getPositiveStats = () => {
    const totalReviews = stats?.comparisons?.this_week || 0;
    const lastWeekReviews = stats?.comparisons?.last_week || 0;
    const improvement = totalReviews - lastWeekReviews;
    
    const positiveStats = [];
    
    if (totalReviews > 0) {
      positiveStats.push({
        label: "Cards Reviewed This Week",
        value: totalReviews,
        emoji: "📚",
        positive: true
      });
    }
    
    if (improvement > 0) {
      positiveStats.push({
        label: "More Than Last Week",
        value: `+${improvement}`,
        emoji: "📈",
        positive: true
      });
    }
    
    return positiveStats;
  };

  const positiveStats = getPositiveStats();

  return (
    <div className="space-y-8">
      {/* Hero Streak Section - Prominent and Celebratory */}
      <div className="bg-gradient-to-br from-accent/10 via-accent/5 to-transparent dark:from-accent/20 dark:via-accent/10 dark:to-transparent rounded-2xl border-2 border-accent/20 dark:border-accent/30 p-8 md:p-12">
        <div className="text-center mb-6">
          <div className="text-6xl md:text-8xl font-bold text-accent mb-4">
            {displayStreak}
          </div>
          <div className="text-2xl md:text-3xl font-semibold text-gray-900 dark:text-darktext mb-2">
            Day{displayStreak !== 1 ? 's' : ''} Streak! 🔥
          </div>
          <div className="text-lg text-gray-700 dark:text-gray-300 mb-4">
            {getStreakMessage()}
          </div>
          {longestStreak > displayStreak && (
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Your longest streak: {longestStreak} days ⭐
            </div>
          )}
        </div>

        {/* Progress to Next Milestone */}
        {nextMilestone && (
          <div className="max-w-md mx-auto">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {nextMilestone - displayStreak} days until {nextMilestone}-day milestone! 🎯
              </div>
              <div className="text-sm font-medium text-accent">
                {Math.round(progressToNext)}%
              </div>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-accent to-accent/80 h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${Math.min(progressToNext, 100)}%` }}
              />
            </div>
          </div>
        )}

        {!hasReviewedToday && potentialStreak > 0 && (
          <div className="mt-6 text-center">
            <div className="inline-block px-6 py-3 bg-accent/20 dark:bg-accent/30 rounded-full border border-accent/40">
              <span className="text-accent font-semibold">
                💡 Review today to extend your streak to {potentialStreak} days!
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Positive Stats Cards */}
      {positiveStats.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {positiveStats.map((stat, index) => (
            <div
              key={index}
              className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-700 p-6 text-center"
            >
              <div className="text-3xl mb-2">{stat.emoji}</div>
              <div className="text-3xl font-bold text-gray-900 dark:text-darktext mb-1">
                {stat.value}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Activity Heatmap - Secondary Focus */}
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-darktext mb-4">
          Your Activity 📅
        </h2>
        <ActivityHeatmap stats={stats} />
      </div>

      {/* Most Challenging Cards - At Bottom */}
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-darktext mb-4">
          Cards to Focus On 💪
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          These are the cards you've found most challenging. Keep practicing and you'll master them!
        </p>
        <DifficultCards />
      </div>
    </div>
  );
};

export default GamifiedDashboard;

