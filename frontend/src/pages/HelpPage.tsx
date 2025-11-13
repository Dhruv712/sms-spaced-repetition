import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';

const HelpPage: React.FC = () => {
  const { token } = useAuth();
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<{ type: 'success' | 'error' | null; message: string }>({ type: null, message: '' });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!subject.trim() || !message.trim()) {
      setSubmitStatus({ type: 'error', message: 'Please fill in both subject and message fields.' });
      return;
    }

    if (!token) {
      setSubmitStatus({ type: 'error', message: 'You must be logged in to send a message.' });
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus({ type: null, message: '' });

    try {
      const response = await axios.post(
        buildApiUrl('/help/contact'),
        {
          subject: subject.trim(),
          message: message.trim()
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.data.success) {
        setSubmitStatus({ type: 'success', message: response.data.message || 'Your message has been sent successfully!' });
        setSubject('');
        setMessage('');
      } else {
        setSubmitStatus({ type: 'error', message: response.data.error || 'Failed to send message. Please try again.' });
      }
    } catch (err: any) {
      console.error('Error submitting contact form:', err);
      setSubmitStatus({
        type: 'error',
        message: err.response?.data?.detail || 'An error occurred. Please try again later.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-secondary-900 dark:text-white">
            Help & Support
          </h1>
          <p className="mt-2 text-secondary-600 dark:text-secondary-400">
            Have a question or need help? Send us a message and we'll get back to you soon.
          </p>
        </div>

        <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
                Subject
              </label>
              <input
                type="text"
                id="subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="block w-full rounded-md border-secondary-300 dark:border-secondary-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-secondary-700 dark:text-white sm:text-sm px-3 py-2"
                placeholder="What can we help you with?"
                required
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label htmlFor="message" className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
                Message
              </label>
              <textarea
                id="message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={8}
                className="block w-full rounded-md border-secondary-300 dark:border-secondary-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-secondary-700 dark:text-white sm:text-sm px-3 py-2"
                placeholder="Please describe your question or issue in detail..."
                required
                disabled={isSubmitting}
              />
            </div>

            {submitStatus.type && (
              <div
                className={`p-4 rounded-md ${
                  submitStatus.type === 'success'
                    ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300'
                    : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-300'
                }`}
              >
                {submitStatus.message}
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {isSubmitting ? 'Sending...' : 'Send Message'}
              </button>
            </div>
          </form>

          <div className="mt-8 pt-8 border-t border-secondary-200 dark:border-secondary-700">
            <h2 className="text-lg font-semibold text-secondary-900 dark:text-white mb-4">
              Frequently Asked Questions
            </h2>
            <div className="space-y-4 text-sm text-secondary-600 dark:text-secondary-400">
              <div>
                <h3 className="font-medium text-secondary-900 dark:text-white mb-1">
                  How do I create flashcards?
                </h3>
                <p>You can create flashcards by sending "NEW" followed by your flashcard description via SMS, or by using the web interface on the Flashcards page.</p>
              </div>
              <div>
                <h3 className="font-medium text-secondary-900 dark:text-white mb-1">
                  How does spaced repetition work?
                </h3>
                <p>Our algorithm uses the SM-2 spaced repetition system. Cards you answer correctly are scheduled further in the future, while cards you struggle with are shown more frequently.</p>
              </div>
              <div>
                <h3 className="font-medium text-secondary-900 dark:text-white mb-1">
                  Can I skip a flashcard?
                </h3>
                <p>Yes! Simply reply "skip" when you receive a flashcard. You'll be reminded of this option every 5 messages.</p>
              </div>
              <div>
                <h3 className="font-medium text-secondary-900 dark:text-white mb-1">
                  How do I organize my flashcards?
                </h3>
                <p>You can create decks on the Decks page to organize your flashcards by topic or subject. You can also enable or disable SMS notifications for specific decks.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpPage;

