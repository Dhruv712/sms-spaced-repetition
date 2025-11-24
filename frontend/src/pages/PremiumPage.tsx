import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { buildApiUrl } from '../config';

const PremiumPage: React.FC = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [subscriptionStatus, setSubscriptionStatus] = useState<any>(null);

  useEffect(() => {
    if (user?.is_premium && token) {
      // Fetch subscription status for premium users
      const fetchStatus = async () => {
        try {
          const response = await axios.get(
            buildApiUrl('/subscription/status'),
            {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            }
          );
          setSubscriptionStatus(response.data);
        } catch (err) {
          console.error('Error fetching subscription status:', err);
        }
      };
      fetchStatus();
    }
  }, [user, token]);

  const handleUpgrade = async () => {
    if (!token) {
      navigate('/login');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        buildApiUrl('/subscription/create-checkout-session'),
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.data.success && response.data.url) {
        // Redirect to Stripe Checkout
        window.location.href = response.data.url;
      } else {
        setError('Failed to create checkout session. Please try again.');
      }
    } catch (err: any) {
      console.error('Error creating checkout session:', err);
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleManageSubscription = async () => {
    if (!token) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        buildApiUrl('/subscription/portal'),
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.data.success && response.data.url) {
        // Redirect to Stripe Customer Portal
        window.location.href = response.data.url;
      } else {
        setError('Failed to open customer portal. Please try again.');
      }
    } catch (err: any) {
      console.error('Error opening customer portal:', err);
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (user?.is_premium) {
    const formatDate = (dateString: string | null) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    };

    return (
      <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-secondary-900 dark:text-white mb-4">
              Premium Membership
            </h1>
            <p className="text-lg text-secondary-600 dark:text-secondary-400">
              Thank you for your support. Enjoy unlimited access to all features.
            </p>
          </div>

          {/* Subscription Status */}
          <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-6 mb-6">
            <h2 className="text-2xl font-semibold text-secondary-900 dark:text-white mb-4">
              Subscription Details
            </h2>
            {subscriptionStatus ? (
              <div className="space-y-3 text-secondary-700 dark:text-secondary-300">
                <div className="flex justify-between">
                  <span className="font-medium">Status:</span>
                  <span className={`font-semibold ${
                    subscriptionStatus.stripe_subscription_status === 'active' 
                      ? 'text-green-600 dark:text-green-400' 
                      : 'text-yellow-600 dark:text-yellow-400'
                  }`}>
                    {subscriptionStatus.stripe_subscription_status === 'active' ? 'Active' : subscriptionStatus.stripe_subscription_status}
                  </span>
                </div>
                {subscriptionStatus.subscription_end_date && (
                  <div className="flex justify-between">
                    <span className="font-medium">Next billing date:</span>
                    <span>{formatDate(subscriptionStatus.subscription_end_date)}</span>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-secondary-600 dark:text-secondary-400">Loading subscription details...</p>
            )}

            <div className="mt-6">
              <button
                onClick={handleManageSubscription}
                disabled={loading}
                className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {loading ? 'Loading...' : 'Manage Subscription'}
              </button>
              <p className="text-sm text-secondary-600 dark:text-secondary-400 mt-2">
                Manage your subscription, update payment method, or cancel from the Stripe customer portal.
              </p>
            </div>
          </div>

          {/* Premium Features */}
          <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-6">
            <h2 className="text-2xl font-semibold text-secondary-900 dark:text-white mb-4">
              Premium Features
            </h2>
            <ul className="space-y-3 text-secondary-700 dark:text-secondary-300">
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Unlimited SMS flashcard reviews per month
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Unlimited decks
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Unlimited flashcards per deck
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Create flashcards from PDF documents
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                All premium features unlocked
              </li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-secondary-900 dark:text-white mb-4">
            Upgrade to Premium
          </h1>
          <p className="text-lg text-secondary-600 dark:text-secondary-400">
            Unlock unlimited access to all features for just $8/month
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
            <p className="text-red-800 dark:text-red-300">{error}</p>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Free Plan */}
          <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-6">
            <h2 className="text-2xl font-semibold text-secondary-900 dark:text-white mb-4">
              Free Plan
            </h2>
            <div className="mb-6">
              <span className="text-4xl font-bold text-secondary-900 dark:text-white">$0</span>
              <span className="text-secondary-600 dark:text-secondary-400">/month</span>
            </div>
            <ul className="space-y-3 text-secondary-700 dark:text-secondary-300 mb-6">
              <li className="flex items-center">
                <span className="text-gray-400 mr-2">•</span>
                50 SMS reviews per month
              </li>
              <li className="flex items-center">
                <span className="text-gray-400 mr-2">•</span>
                Up to 3 decks
              </li>
              <li className="flex items-center">
                <span className="text-gray-400 mr-2">•</span>
                Up to 20 flashcards per deck
              </li>
            </ul>
          </div>

          {/* Premium Plan */}
          <div className="bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-lg shadow-soft p-6 border-2 border-primary-500">
            <div className="mb-4">
              <h2 className="text-2xl font-semibold text-secondary-900 dark:text-white">
                Premium
              </h2>
            </div>
            <div className="mb-6">
              <span className="text-4xl font-bold text-secondary-900 dark:text-white">$8</span>
              <span className="text-secondary-600 dark:text-secondary-400">/month</span>
            </div>
            <ul className="space-y-3 text-secondary-700 dark:text-secondary-300 mb-6">
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Unlimited SMS reviews per month
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Unlimited decks
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Unlimited flashcards per deck
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Create flashcards from PDF documents
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                All premium features unlocked
              </li>
            </ul>
            <button
              onClick={handleUpgrade}
              disabled={loading || !token}
              className="w-full px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 font-medium"
            >
              {loading ? 'Processing...' : 'Get Premium'}
            </button>
          </div>
        </div>

        <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-6">
          <h3 className="text-xl font-semibold text-secondary-900 dark:text-white mb-4">
            Frequently Asked Questions
          </h3>
          <div className="space-y-4 text-sm text-secondary-600 dark:text-secondary-400">
            <div>
              <h4 className="font-medium text-secondary-900 dark:text-white mb-1">
                What happens if I cancel?
              </h4>
              <p>You'll continue to have premium access until the end of your billing period. After that, you'll be moved to the free plan.</p>
            </div>
            <div>
              <h4 className="font-medium text-secondary-900 dark:text-white mb-1">
                Can I change my plan later?
              </h4>
              <p>Yes! You can manage your subscription at any time from your profile page.</p>
            </div>
            <div>
              <h4 className="font-medium text-secondary-900 dark:text-white mb-1">
                Is there a free trial?
              </h4>
              <p>No free trial, but you can cancel anytime. Your subscription will remain active until the end of the billing period.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PremiumPage;

