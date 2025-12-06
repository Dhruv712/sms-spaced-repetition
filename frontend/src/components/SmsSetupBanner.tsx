import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const SmsSetupBanner: React.FC = () => {
  const { user, setShowPhoneModal } = useAuth();
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    // Check if banner has been dismissed in localStorage
    const dismissed = localStorage.getItem('sms_setup_banner_dismissed');
    if (dismissed === 'true') {
      setIsDismissed(true);
    }
  }, []);

  useEffect(() => {
    // Auto-hide if user starts SMS conversation
    if (user?.has_sms_conversation) {
      setIsDismissed(true);
    }
  }, [user?.has_sms_conversation]);

  const handleDismiss = () => {
    localStorage.setItem('sms_setup_banner_dismissed', 'true');
    setIsDismissed(true);
  };

  const handleAddPhone = () => {
    setShowPhoneModal(true);
  };

  // Don't show if:
  // - User doesn't exist
  // - User already has SMS conversation
  // - Banner has been dismissed
  if (
    !user ||
    user.has_sms_conversation ||
    isDismissed
  ) {
    return null;
  }

  // Case 1: User doesn't have a phone number
  if (!user.phone_number) {
    return (
      <div className="mb-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">📱</span>
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-blue-900 dark:text-blue-100 mb-2">
                  Add Your Phone Number to Get Started
                </h3>
                <p className="text-blue-700 dark:text-blue-300 mb-4">
                  Add your phone number to receive SMS flashcard reminders and use Cue's text-based features. Review cards on the go, right from your messages!
                </p>
                <button
                  onClick={handleAddPhone}
                  className="px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90 transition-colors duration-200 font-medium"
                >
                  Add Phone Number
                </button>
              </div>
              <button
                onClick={handleDismiss}
                className="ml-4 flex-shrink-0 px-4 py-2 text-sm font-medium text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-800/50 rounded-md hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors duration-200"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Case 2: User has phone number but hasn't started SMS conversation
  return (
    <div className="mb-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-bold">📱</span>
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-medium text-blue-900 dark:text-blue-100 mb-2">
                Get Started with SMS Flashcards!
              </h3>
              <p className="text-blue-700 dark:text-blue-300 mb-4">
                You have a phone number set up, but haven't started using SMS yet. Text "START" to this link to begin receiving flashcard reminders and create cards via text:
              </p>
              <div className="flex items-center gap-2 mb-3">
                <a
                  href="imessage://cue@a.imsg.co"
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 text-sm font-mono bg-white dark:bg-gray-800 px-3 py-2 rounded border border-blue-300 dark:border-blue-600 break-all"
                >
                  imessage://cue@a.imsg.co
                </a>
              </div>
              <p className="text-sm text-blue-600 dark:text-blue-400">
                💡 On mobile, tap the link above to open Messages and send "START"
              </p>
            </div>
            <button
              onClick={handleDismiss}
              className="ml-4 flex-shrink-0 px-4 py-2 text-sm font-medium text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-800/50 rounded-md hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors duration-200"
            >
              Got it!
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SmsSetupBanner;

