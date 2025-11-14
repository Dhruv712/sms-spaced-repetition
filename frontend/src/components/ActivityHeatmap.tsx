import React, { useMemo } from 'react';

interface ActivityHeatmapProps {
  stats: any;
}

const ActivityHeatmap: React.FC<ActivityHeatmapProps> = ({ stats }) => {
  const activityData = useMemo(() => {
    return stats?.activity_heatmap || {};
  }, [stats?.activity_heatmap]);
  
  // Generate calendar grid for the past year
  const calendarData = useMemo(() => {
    const today = new Date();
    const oneYearAgo = new Date(today);
    oneYearAgo.setFullYear(today.getFullYear() - 1);
    
    const weeks: number[][] = [];
    let currentWeek: number[] = [];
    const startDate = new Date(oneYearAgo);
    
    // Find the start of the week (Sunday)
    const dayOfWeek = startDate.getDay();
    startDate.setDate(startDate.getDate() - dayOfWeek);
    
    const endDate = new Date(today);
    const currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
      const dateStr = currentDate.toISOString().split('T')[0];
      const count = activityData[dateStr] || 0;
      currentWeek.push(count);
      
      if (currentWeek.length === 7) {
        weeks.push(currentWeek);
        currentWeek = [];
      }
      
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    if (currentWeek.length > 0) {
      while (currentWeek.length < 7) {
        currentWeek.push(0);
      }
      weeks.push(currentWeek);
    }
    
    return weeks;
  }, [activityData]);
  
  // Get max count for color scaling
  const maxCount = useMemo(() => {
    return Math.max(...Object.values(activityData) as number[], 1);
  }, [activityData]);
  
  const getColor = (count: number) => {
    if (count === 0) return 'bg-gray-100 dark:bg-gray-800';
    const intensity = Math.min(count / maxCount, 1);
    if (intensity < 0.25) return 'bg-primary-200 dark:bg-primary-900';
    if (intensity < 0.5) return 'bg-primary-300 dark:bg-primary-800';
    if (intensity < 0.75) return 'bg-primary-400 dark:bg-primary-700';
    return 'bg-primary-500 dark:bg-primary-600';
  };
  
  const weekDays = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
  
  // Generate month labels for horizontal scale
  const monthLabels = useMemo(() => {
    const today = new Date();
    const oneYearAgo = new Date(today);
    oneYearAgo.setFullYear(today.getFullYear() - 1);
    
    const labels: { weekIndex: number; label: string }[] = [];
    const startDate = new Date(oneYearAgo);
    const dayOfWeek = startDate.getDay();
    startDate.setDate(startDate.getDate() - dayOfWeek);
    
    let currentDate = new Date(startDate);
    let lastMonth = -1;
    let weekIndex = 0;
    
    while (currentDate <= today) {
      const month = currentDate.getMonth();
      if (month !== lastMonth && currentDate.getDate() <= 7) {
        labels.push({
          weekIndex,
          label: currentDate.toLocaleDateString('en-US', { month: 'short' })
        });
        lastMonth = month;
      }
      
      if (currentDate.getDay() === 6) { // End of week
        weekIndex++;
      }
      
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return labels;
  }, []);
  
  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Activity</h2>
      <div className="overflow-x-auto">
        <div className="flex gap-1">
          {/* Day labels - show all days */}
          <div className="flex flex-col gap-1 mr-2">
            {weekDays.map((day, i) => (
              <div key={i} className="h-3 text-xs text-gray-500 dark:text-gray-400" style={{ lineHeight: '12px' }}>
                {day}
              </div>
            ))}
          </div>
          
          {/* Calendar grid */}
          <div className="flex gap-1 relative">
            {calendarData.map((week, weekIndex) => (
              <div key={weekIndex} className="flex flex-col gap-1">
                {week.map((count, dayIndex) => (
                  <div
                    key={dayIndex}
                    className={`w-3 h-3 rounded ${getColor(count)}`}
                    title={`${count} reviews`}
                  />
                ))}
                {/* Month labels at bottom */}
                {monthLabels.some(m => m.weekIndex === weekIndex) && (
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1" style={{ fontSize: '10px' }}>
                    {monthLabels.find(m => m.weekIndex === weekIndex)?.label}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>Less</span>
        <div className="flex gap-1">
          <div className="w-3 h-3 rounded bg-gray-100 dark:bg-gray-800" />
          <div className="w-3 h-3 rounded bg-primary-200 dark:bg-primary-900" />
          <div className="w-3 h-3 rounded bg-primary-300 dark:bg-primary-800" />
          <div className="w-3 h-3 rounded bg-primary-400 dark:bg-primary-700" />
          <div className="w-3 h-3 rounded bg-primary-500 dark:bg-primary-600" />
        </div>
        <span>More</span>
      </div>
    </div>
  );
};

export default ActivityHeatmap;

