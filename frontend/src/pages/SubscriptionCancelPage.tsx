import React from 'react';
import { useNavigate } from 'react-router-dom';

const SubscriptionCancelPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-8 text-center">
          <div className="text-6xl mb-4">😔</div>
          <h1 className="text-3xl font-bold text-secondary-900 dark:text-white mb-4">
            Subscription Cancelled
          </h1>
          <p className="text-lg text-secondary-600 dark:text-secondary-400 mb-6">
            You cancelled the subscription process. No charges were made.
          </p>
          <div className="space-x-4">
            <button
              onClick={() => navigate('/premium')}
              className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors duration-200"
            >
              Try Again
            </button>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200"
            >
              Go Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionCancelPage;

