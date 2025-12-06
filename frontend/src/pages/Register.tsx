import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import GoogleSignInButton from '../components/GoogleSignInButton';
import { buildApiUrl } from '../config';

export const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [smsOptIn, setSmsOptIn] = useState(false);
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(email, password, phoneNumber, name, smsOptIn);
      navigate('/dashboard');
    } catch (err) {
      setError('Failed to create an account. Please try again.');
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      setError('');
      // Redirect to backend Google OAuth endpoint
      window.location.href = buildApiUrl('/auth/google');
    } catch (err) {
      console.error('Google sign-in error:', err);
      setError('Failed to initiate Google sign-in. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-darkbg py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        {/* Registration Form */}
        <div className="bg-white dark:bg-darksurface p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-darktext">
            Create your account
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
              <label htmlFor="name" className="sr-only">
                Full Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-accent focus:border-accent focus:z-10 sm:text-sm dark:bg-gray-800 dark:text-darktext dark:border-gray-600 dark:placeholder-gray-400 transition-colors duration-200"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
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
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-accent focus:border-accent focus:z-10 sm:text-sm dark:bg-gray-800 dark:text-darktext dark:border-gray-600 dark:placeholder-gray-400 transition-colors duration-200"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="phone-number" className="sr-only">
                Phone Number
              </label>
              <input
                id="phone-number"
                name="phone"
                type="tel"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-accent focus:border-accent focus:z-10 sm:text-sm dark:bg-gray-800 dark:text-darktext dark:border-gray-600 dark:placeholder-gray-400 transition-colors duration-200"
                placeholder="Phone Number (e.g., +1234567890)"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
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
                autoComplete="new-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm dark:bg-gray-800 dark:text-darktext dark:border-gray-600 dark:placeholder-gray-400 transition-colors duration-200"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center">
            <input
              id="sms-opt-in"
              name="sms-opt-in"
              type="checkbox"
              checked={smsOptIn}
              onChange={(e) => setSmsOptIn(e.target.checked)}
              className="h-4 w-4 text-accent focus:ring-accent border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600 dark:checked:bg-accent dark:checked:border-accent"
            />
            <label htmlFor="sms-opt-in" className="ml-2 block text-sm text-gray-900 dark:text-darktext">
              <span className="font-medium">Receive SMS notifications</span>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Get daily flashcard reminders and spaced repetition notifications via text message. 
                You can change this preference anytime in your profile.
              </p>
            </label>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-accent hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-accent transition-colors duration-200"
            >
              Sign up
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
            <GoogleSignInButton onClick={handleGoogleSignIn} text="Sign up with Google" />
          </div>

          <div className="text-sm text-center">
            <Link to="/login" className="font-medium text-accent hover:text-accent/80 dark:text-accent dark:hover:text-accent/80 transition-colors duration-200">
              Already have an account? Sign in
            </Link>
          </div>
        </form>
        </div>
      </div>
    </div>
  );
}; 