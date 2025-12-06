import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';

const SubscriptionSuccessPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPremium, setIsPremium] = useState(false);

  useEffect(() => {
    const verifySubscription = async () => {
      const sessionId = searchParams.get('session_id');
      
      // Wait a moment for webhook to process
      setTimeout(async () => {
        try {
          // Refresh user profile to get updated premium status
          const response = await fetch(buildApiUrl('/users/profile'), {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          
          if (response.ok) {
            const userData = await response.json();
            const userIsPremium = userData.is_premium || false;
            setIsPremium(userIsPremium);
            
            // If user is premium, show success (even without session_id)
            if (userIsPremium) {
              // Don't reload - just show success message
              // The AuthContext will update on next navigation
              setError(null);
            } else if (!sessionId) {
              // No session ID and not premium - show error
              setError('No session ID found. If your subscription was activated, please refresh the page.');
            } else {
              // Has session ID but not premium yet - wait a bit more
              setError('Subscription may still be processing. Please wait a moment and refresh the page.');
            }
          }
        } catch (err) {
          console.error('Error verifying subscription:', err);
          // Check if user is already premium (from AuthContext)
          if (user?.is_premium) {
            setIsPremium(true);
          } else {
            setError('Subscription may have been activated. Please refresh the page.');
          }
        } finally {
          setLoading(false);
        }
      }, 2000);
    };

    if (token) {
      verifySubscription();
    } else {
      setLoading(false);
    }
  }, [searchParams, token, user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
          <p className="text-secondary-600 dark:text-secondary-400">Processing your subscription...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-8 text-center">
          {error && !isPremium ? (
            <>
              <div className="text-6xl mb-4">⚠️</div>
              <h1 className="text-3xl font-bold text-secondary-900 dark:text-white mb-4">
                Verification Issue
              </h1>
              <p className="text-secondary-600 dark:text-secondary-400 mb-6">{error}</p>
              <button
                onClick={() => navigate('/premium')}
                className="px-6 py-3 bg-accent text-white rounded-md hover:bg-accent/90 transition-colors duration-200"
              >
                Go to Premium Page
              </button>
            </>
          ) : (
            <>
              <div className="text-6xl mb-4">🎉</div>
              <h1 className="text-3xl font-bold text-secondary-900 dark:text-white mb-4">
                Welcome to Premium!
              </h1>
              <p className="text-lg text-secondary-600 dark:text-secondary-400 mb-6">
                Your subscription has been activated. You now have unlimited access to all premium features!
              </p>
              <button
                onClick={() => {
                  // Navigate to dashboard
                  navigate('/dashboard');
                }}
                className="px-6 py-3 bg-accent text-white rounded-md hover:bg-accent/90 transition-colors duration-200"
              >
                Get Started
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SubscriptionSuccessPage;

