import React, { useMemo } from 'react';

interface ActivityHeatmapProps {
  stats: any;
}

const ActivityHeatmap: React.FC<ActivityHeatmapProps> = ({ stats }) => {
  const activityData = useMemo(() => {
    return stats?.activity_heatmap || {};
  }, [stats?.activity_heatmap]);
  
  // Generate calendar grid for the past year with date information
  const calendarData = useMemo(() => {
    const today = new Date();
    const oneYearAgo = new Date(today);
    oneYearAgo.setFullYear(today.getFullYear() - 1);
    
    const weeks: Array<Array<{ count: number; date: Date | null; dateStr: string }>> = [];
    let currentWeek: Array<{ count: number; date: Date | null; dateStr: string }> = [];
    const startDate = new Date(oneYearAgo);
    
    // Find the start of the week (Sunday)
    const dayOfWeek = startDate.getDay();
    startDate.setDate(startDate.getDate() - dayOfWeek);
    
    const endDate = new Date(today);
    const currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
      const dateStr = currentDate.toISOString().split('T')[0];
      const count = activityData[dateStr] || 0;
      currentWeek.push({
        count,
        date: new Date(currentDate),
        dateStr
      });
      
      if (currentWeek.length === 7) {
        weeks.push(currentWeek);
        currentWeek = [];
      }
      
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    if (currentWeek.length > 0) {
      while (currentWeek.length < 7) {
        currentWeek.push({ count: 0, date: null, dateStr: '' });
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
    // More contrast for dark mode - use lighter colors
    if (intensity < 0.25) return 'bg-primary-200 dark:bg-primary-600';
    if (intensity < 0.5) return 'bg-primary-300 dark:bg-primary-500';
    if (intensity < 0.75) return 'bg-primary-400 dark:bg-primary-400';
    return 'bg-primary-500 dark:bg-primary-300';
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
              <div key={weekIndex} className="flex flex-col gap-1 pb-4">
                {week.map((dayData, dayIndex) => {
                  const { count, date } = dayData;
                  const isFuture = date && date > new Date();
                  
                  // Format date for tooltip
                  let tooltipText = '';
                  if (date && !isFuture) {
                    const formattedDate = date.toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric',
                      year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
                    });
                    tooltipText = `${formattedDate}: ${count} ${count === 1 ? 'review' : 'reviews'}`;
                  } else if (isFuture) {
                    tooltipText = 'Future date';
                  } else {
                    tooltipText = `${count} ${count === 1 ? 'review' : 'reviews'}`;
                  }
                  
                  // Show date label on hover or for recent dates
                  const daysAgo = date ? Math.floor((new Date().getTime() - date.getTime()) / (1000 * 60 * 60 * 24)) : null;
                  const showDateLabel = date && daysAgo !== null && daysAgo <= 7; // Show date for last 7 days
                  
                  return (
                    <div
                      key={dayIndex}
                      className={`relative group ${date && !isFuture ? 'cursor-pointer' : ''}`}
                    >
                      <div
                        className={`w-3 h-3 rounded ${getColor(count)} transition-all duration-150 ${
                          date && !isFuture 
                            ? 'hover:scale-125 hover:ring-2 hover:ring-primary-400 dark:hover:ring-primary-500 hover:z-10' 
                            : ''
                        } ${isFuture ? 'opacity-30' : ''}`}
                        title={tooltipText}
                      />
                      {/* Custom tooltip */}
                      {date && !isFuture && (
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-20 transition-opacity duration-150">
                          {tooltipText}
                          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                            <div className="border-4 border-transparent border-t-gray-900 dark:border-t-gray-100"></div>
                          </div>
                        </div>
                      )}
                      {/* Date label for recent days */}
                      {showDateLabel && date && (
                        <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 text-[8px] text-gray-500 dark:text-gray-400 whitespace-nowrap">
                          {date.getDate()}
                        </div>
                      )}
                    </div>
                  );
                })}
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
          <div className="w-3 h-3 rounded bg-primary-200 dark:bg-primary-600" />
          <div className="w-3 h-3 rounded bg-primary-300 dark:bg-primary-500" />
          <div className="w-3 h-3 rounded bg-primary-400 dark:bg-primary-400" />
          <div className="w-3 h-3 rounded bg-primary-500 dark:bg-primary-300" />
        </div>
        <span>More</span>
      </div>
    </div>
  );
};

export default ActivityHeatmap;

