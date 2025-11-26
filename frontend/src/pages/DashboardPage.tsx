import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import axios from 'axios';
import ActivityHeatmap from '../components/ActivityHeatmap';
import AccuracyGraph from '../components/AccuracyGraph';
import StreakVisualization from '../components/StreakVisualization';
import ComparisonCards from '../components/ComparisonCards';
import WeakestAreas from '../components/WeakestAreas';
import ReviewStats from '../components/ReviewStats';
import DailySummary from '../components/DailySummary';
import SmsSetupBanner from '../components/SmsSetupBanner';
import DifficultCards from '../components/DifficultCards';

const DashboardPage: React.FC = () => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);

  const fetchStats = useCallback(async () => {
    if (!token) return;
    
    try {
      const response = await axios.get(buildApiUrl('/dashboard/stats'), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-darkbg flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-darkbg py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-light text-gray-900 dark:text-darktext mb-8">Dashboard</h1>
        
        {/* SMS Setup Banner */}
        <SmsSetupBanner />
        
        {/* Comparison Cards */}
        <ComparisonCards stats={stats} />
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Streak Visualization */}
          <div className="lg:col-span-1">
            <StreakVisualization stats={stats} />
          </div>
          
          {/* Activity Heatmap */}
          <div className="lg:col-span-2">
            <ActivityHeatmap stats={stats} />
          </div>
        </div>

        {/* Review Stats and Today's Summary */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ReviewStats />
          <DailySummary />
        </div>

        {/* Accuracy Graph */}
        <div className="mb-8">
          <AccuracyGraph stats={stats} />
        </div>

        {/* Weakest Areas */}
        <div className="mb-8">
          <WeakestAreas stats={stats} />
        </div>

        {/* Most Difficult Cards */}
        <div className="mb-8">
          <DifficultCards />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;

