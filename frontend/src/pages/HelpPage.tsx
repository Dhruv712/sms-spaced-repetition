import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { buildApiUrl } from '../config';

const HelpPage: React.FC = () => {
  const { token, user } = useAuth();
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [userEmail, setUserEmail] = useState<string | null>(null);

  // Fetch user email if logged in
  useEffect(() => {
    const fetchUserEmail = async () => {
      // First try to use email from user object
      if (user?.email) {
        setUserEmail(user.email);
        return;
      }
      
      // If not available, fetch from profile endpoint
      if (token) {
        try {
          const response = await axios.get(buildApiUrl('/users/profile'), {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          if (response.data?.email) {
            setUserEmail(response.data.email);
          }
        } catch (err) {
          console.error('Error fetching user email:', err);
        }
      }
    };

    fetchUserEmail();
  }, [token, user]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!subject.trim() || !message.trim()) {
      return;
    }

    // Determine the email to use
    const fromEmail = userEmail || email.trim();
    if (!fromEmail) {
      return;
    }

    // Create mailto link
    const recipientEmail = 'dhruv.sumathi@gmail.com';
    const mailtoSubject = encodeURIComponent(subject.trim());
    const mailtoBody = encodeURIComponent(
      `From: ${fromEmail}\n\n${message.trim()}`
    );
    
    const mailtoLink = `mailto:${recipientEmail}?subject=${mailtoSubject}&body=${mailtoBody}`;
    
    // Open default email client
    window.location.href = mailtoLink;
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
            {!token && !userEmail && (
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
                  Your Email
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full rounded-md border-secondary-300 dark:border-secondary-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-secondary-700 dark:text-white sm:text-sm px-3 py-2"
                  placeholder="your.email@example.com"
                  required={!token && !userEmail}
                />
                <p className="mt-1 text-xs text-secondary-500 dark:text-secondary-400">
                  We'll use this to respond to your message
                </p>
              </div>
            )}
            
            {token && userEmail && (
              <div className="bg-secondary-50 dark:bg-secondary-900 rounded-md p-3 text-sm text-secondary-600 dark:text-secondary-400">
                Sending as: <span className="font-medium text-secondary-900 dark:text-white">{userEmail}</span>
              </div>
            )}
            
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
              />
            </div>

            <div>
              <button
                type="submit"
                className="w-full px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
              >
                Open Email Client
              </button>
              <p className="mt-2 text-xs text-secondary-500 dark:text-secondary-400 text-center">
                This will open your default email client with the message pre-filled
              </p>
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

