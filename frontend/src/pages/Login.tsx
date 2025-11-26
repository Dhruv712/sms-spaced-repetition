import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import GoogleSignInButton from '../components/GoogleSignInButton';
import { buildApiUrl } from '../config';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [googleLoading, setGoogleLoading] = useState(false);
  const { login, loginWithGoogleToken, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  useEffect(() => {
    if (isAuthenticated) {
      console.log('User is authenticated, redirecting to:', from);
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  // Handle Google OAuth success callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const googleSuccess = urlParams.get('google_success');
    const googleError = urlParams.get('google_error');
    const token = urlParams.get('token');
    
    if (googleSuccess && token) {
      // Google OAuth was successful and we have a token
      console.log('Google OAuth successful, logging in with token');
      
      // Use the AuthContext method to properly set the token and fetch user profile
      loginWithGoogleToken(token);
      
      // Clear the URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (googleError) {
      setError(`Google sign-in failed: ${googleError}`);
    }
  }, [navigate, loginWithGoogleToken]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to login. Please check your credentials.');
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      setError('');
      setGoogleLoading(true);
      
      // First, check if the backend is reachable
      try {
        const healthCheck = await fetch(buildApiUrl('/auth/google/debug'), {
          method: 'GET',
          signal: AbortSignal.timeout(5000) // 5 second timeout
        });
        
        if (!healthCheck.ok) {
          throw new Error('Backend is not responding');
        }
      } catch (err) {
        console.error('Backend health check failed:', err);
        setError('Unable to connect to the server. Please check if the service is running.');
        setGoogleLoading(false);
        return;
      }
      
      // Redirect to backend Google OAuth endpoint
      window.location.href = buildApiUrl('/auth/google');
    } catch (err) {
      console.error('Google sign-in error:', err);
      setError('Failed to initiate Google sign-in. Please try again.');
      setGoogleLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-darkbg py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Welcome Section - Left Side */}
          <div className="bg-white dark:bg-darksurface p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-darktext mb-6">
              Welcome to Cue
            </h1>
            <div className="prose max-w-none text-gray-700 dark:text-gray-300">
              <p className="text-lg mb-4">
                The LLM-powered spaced repetition system that makes adding and reviewing your flashcards way easier. Here's what you need to know:
              </p>
              
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-bold">1</span>
                  <div>
                    <p>
                      If you provide your phone number, Cue will send you text messages every few hours with any flashcards due for review. You can simply reply with your answer, and Cue will grade your response using an LLM and automatically schedule the next review for that card.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-bold">2</span>
                  <div>
                    <p>
                      Active learning is best. By typing out your answers and having them graded by an LLM, you'll speed up your learning.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-bold">3</span>
                  <div>
                    <p>
                      To make a new card, you can text Cue "NEW" followed by instructions for that card, or a specific card title and definition. For example, if you text Cue "NEW card for the year of the declaration of independence", it will text you something back like:
                    </p>
                    <div className="mt-3 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg border-l-4 border-primary-500">
                      <p className="font-medium text-sm text-gray-800 dark:text-gray-200">Generated flashcard:</p>
                      <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">
                        <strong>Concept:</strong> Year of the Declaration of Independence<br/>
                        <strong>Definition:</strong> 1776
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                        Reply 'SAVE' to save or 'NO' to try again.
                      </p>
                    </div>
                    <p className="mt-3">
                      Text messages are the best way to review your cards while on the go. You can disable them at any time from the web app.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-bold">4</span>
                  <div>
                    <p>
                      You can also add, edit, delete, and review cards, create decks, and manage your settings from the web app.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Login Form - Right Side */}
          <div className="bg-white dark:bg-darksurface p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
            <div>
              <h2 className="text-center text-3xl font-extrabold text-gray-900 dark:text-darktext">
                Sign in to your account
              </h2>
            </div>
            <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
              {error && (
                <div className="rounded-md bg-red-100 dark:bg-red-900 p-4">
                  <div className="text-sm text-red-700 dark:text-red-200">{error}</div>
                </div>
              )}
              <div className="rounded-md shadow-sm -space-y-px">
                <div>
                  <label htmlFor="email-address" className="sr-only">
                    Email address
                  </label>
                  <input
                    id="email-address"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm dark:bg-gray-800 dark:text-darktext dark:border-gray-600 dark:placeholder-gray-400 transition-colors duration-200"
                    placeholder="Email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div>
                  <label htmlFor="password" className="sr-only">
                    Password
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm dark:bg-gray-800 dark:text-darktext dark:border-gray-600 dark:placeholder-gray-400 transition-colors duration-200"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
                >
                  Sign in
                </button>
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300 dark:border-gray-600" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white dark:bg-darksurface text-gray-500 dark:text-gray-400">Or continue with</span>
                </div>
              </div>

              <div>
                <GoogleSignInButton 
                  onClick={handleGoogleSignIn} 
                  disabled={googleLoading}
                  text={googleLoading ? "Connecting..." : "Sign in with Google"}
                />
              </div>

              <div className="text-sm text-center">
                <Link to="/register" className="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 transition-colors duration-200">
                  Don't have an account? Sign up
                </Link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}; 