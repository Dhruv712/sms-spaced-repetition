import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface UserProfile {
  name: string;
  study_mode: string;
  preferred_start_hour: number;
  preferred_end_hour: number;
  timezone: string;
}

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    axios.get('http://localhost:8000/users/profile', {
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
      await axios.put('http://localhost:8000/users/profile', profile, {
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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">User Profile</h1>

      <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl">
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded">
            {error}
          </div>
        )}
        {message && (
          <div className="mb-4 p-3 bg-green-50 text-green-700 rounded">
            {message}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              name="name"
              value={profile.name}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Study Mode</label>
            <select
              name="study_mode"
              value={profile.study_mode}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="batch">Batch</option>
              <option value="distributed">Distributed</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Hour (24-hour format)</label>
            <input
              type="number"
              name="preferred_start_hour"
              value={profile.preferred_start_hour}
              onChange={handleChange}
              min="0"
              max="23"
              className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Hour (24-hour format)</label>
            <input
              type="number"
              name="preferred_end_hour"
              value={profile.preferred_end_hour}
              onChange={handleChange}
              min="0"
              max="23"
              className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Timezone</label>
            <input
              name="timezone"
              value={profile.timezone}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <button
            onClick={handleSave}
            disabled={isSaving}
            className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
