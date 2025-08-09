import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { buildApiUrl } from '../config';

interface UserProfile {
  name: string;
  study_mode: string;
  preferred_start_hour: number;
  preferred_end_hour: number;
  timezone: string;
  sms_opt_in: boolean;
}

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    axios.get(buildApiUrl('/users/profile'), {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => setProfile(res.data))
      .catch(err => {
        console.error("Failed to fetch profile", err);
        setError('Failed to load profile. Please try again.');
      });
  }, [token]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    if (!profile) return;
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    if (!profile || !token) return;
    setIsSaving(true);
    setError('');
    setMessage('');

    try {
      await axios.put(buildApiUrl('/users/profile'), profile, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setMessage('Profile saved successfully!');
    } catch (err) {
      console.error('Failed to save profile:', err);
      setError('Failed to save profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-darkbg">
        <div className="text-xl text-gray-600 dark:text-gray-300">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 bg-gray-50 dark:bg-darkbg min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-darktext">User Profile</h1>

      <div className="bg-white dark:bg-darksurface rounded-lg shadow-xl p-8 max-w-2xl mx-auto border border-gray-200 dark:border-gray-700">
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200 rounded-md">
            {error}
          </div>
        )}
        {message && (
          <div className="mb-4 p-3 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200 rounded-md">
            {message}
          </div>
        )}

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
            <input
              name="name"
              value={profile.name}
              onChange={handleChange}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Study Mode</label>
            <select
              name="study_mode"
              value={profile.study_mode}
              onChange={handleChange}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 appearance-none pr-8 transition-colors duration-200"
            >
              <option value="batch">Batch</option>
              <option value="distributed">Distributed</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start Hour (24-hour format)</label>
            <input
              type="number"
              name="preferred_start_hour"
              value={profile.preferred_start_hour}
              onChange={handleChange}
              min="0"
              max="23"
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">End Hour (24-hour format)</label>
            <input
              type="number"
              name="preferred_end_hour"
              value={profile.preferred_end_hour}
              onChange={handleChange}
              min="0"
              max="23"
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Timezone</label>
            <input
              name="timezone"
              value={profile.timezone}
              onChange={handleChange}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
            />
          </div>

          <div className="flex items-center">
            <input
              id="sms-opt-in"
              name="sms_opt_in"
              type="checkbox"
              checked={profile.sms_opt_in}
              onChange={(e) => setProfile({ ...profile, sms_opt_in: e.target.checked })}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600 dark:checked:bg-primary-600 dark:checked:border-primary-600"
            />
            <label htmlFor="sms-opt-in" className="ml-2 block text-sm text-gray-900 dark:text-darktext">
              <span className="font-medium">Receive SMS notifications</span>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Get daily flashcard reminders and spaced repetition notifications via text message.
              </p>
            </label>
          </div>

          <button
            onClick={handleSave}
            disabled={isSaving}
            className="w-full px-4 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
