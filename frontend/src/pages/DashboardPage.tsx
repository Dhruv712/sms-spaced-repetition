import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { getOnboardingState, setOnboardingState, markOnboardingCompleted } from '../utils/onboarding';
import SmsSetupBanner from '../components/SmsSetupBanner';
import GamifiedDashboard from '../components/GamifiedDashboard';

const DashboardPage: React.FC = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [onboardingStep, setOnboardingStep] = useState<number>(0);
  const [showOnboarding, setShowOnboarding] = useState(false);

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

  // Onboarding: Step 1 (Dashboard)
  useEffect(() => {
    if (!user || !user.email) return;
    const state = getOnboardingState(user.email);
    if (state.completed) {
      setShowOnboarding(false);
      return;
    }
    if (!state.step || state.step < 1) {
      const initial = { step: 1, completed: false };
      setOnboardingState(user.email, initial);
      setOnboardingStep(1);
      setShowOnboarding(true);
    } else if (state.step === 1) {
      setOnboardingStep(1);
      setShowOnboarding(true);
    } else {
      setShowOnboarding(false);
    }
  }, [user]);

  const handleOnboardingSkip = () => {
    if (!user) return;
    markOnboardingCompleted(user.email);
    setShowOnboarding(false);
  };

  const handleOnboardingNextFromDashboard = () => {
    if (!user) return;
    setOnboardingState(user.email, { step: 2, completed: false }); // Step 2 is now Decks (was Step 3)
    setShowOnboarding(false);
    navigate('/decks');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-darkbg flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-darkbg py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-light text-gray-900 dark:text-darktext mb-8">Dashboard</h1>

        {showOnboarding && onboardingStep === 1 && (
          <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div>
                <p className="text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-wide mb-1">
                  Step 1 of 3
                </p>
                <h2 className="text-sm font-medium text-gray-900 dark:text-darktext mb-1">
                  Welcome to your dashboard
                </h2>
                <p className="text-xs text-gray-700 dark:text-gray-300">
                  This is your home base. You&apos;ll see your streak, today&apos;s stats, and how many cards are due for review.
                </p>
              </div>
              <div className="flex items-center gap-2 self-end md:self-auto">
                <button
                  type="button"
                  onClick={handleOnboardingSkip}
                  className="px-3 py-1.5 text-xs rounded border border-transparent text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100"
                >
                  Skip tour
                </button>
                <button
                  type="button"
                  onClick={handleOnboardingNextFromDashboard}
                  className="px-3 py-1.5 text-xs rounded bg-accent text-white hover:bg-accent/90 transition-colors duration-200"
                >
                  Next: Create flashcards
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* SMS Setup Banner */}
        <SmsSetupBanner />
        
        {/* Gamified Dashboard */}
        <GamifiedDashboard stats={stats} />
      </div>
    </div>
  );
};

export default DashboardPage;

