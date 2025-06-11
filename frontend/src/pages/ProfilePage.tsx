import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface UserProfile {
  name: string;
  study_mode: string;
  preferred_start_hour: number;
  preferred_end_hour: number;
  timezone: string;
}

const USER_ID = 1; // 🔒 TODO: Replace with real auth logic eventually

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    axios.get(`http://localhost:8000/users/profile/${USER_ID}`)
      .then(res => setProfile(res.data))
      .catch(err => console.error("Failed to fetch profile", err));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    if (!profile) return;
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSave = () => {
    if (!profile) return;
    setIsSaving(true);
    axios.put(`http://localhost:8000/users/profile/${USER_ID}`, profile)
      .then(() => setMessage('Profile saved!'))
      .catch(() => setMessage('Failed to save profile.'))
      .finally(() => setIsSaving(false));
  };

  if (!profile) return <div>Loading...</div>;

  return (
    <div className="container">
      <h1 className="text-2xl font-bold mb-4">User Profile</h1>

      <div className="card">
        <div className="mb-4">
          <label>Name:</label>
          <input
            name="name"
            value={profile.name}
            onChange={handleChange}
            className="border p-1 ml-2"
          />
        </div>

        <div className="mb-4">
          <label>Study Mode:</label>
          <select
            name="study_mode"
            value={profile.study_mode}
            onChange={handleChange}
            className="border p-1 ml-2"
          >
            <option value="batch">Batch</option>
            <option value="distributed">Distributed</option>
          </select>
        </div>

        <div className="mb-4">
          <label>Start Hour:</label>
          <input
            type="number"
            name="preferred_start_hour"
            value={profile.preferred_start_hour}
            onChange={handleChange}
            className="border p-1 ml-2"
          />
        </div>

        <div className="mb-4">
          <label>End Hour:</label>
          <input
            type="number"
            name="preferred_end_hour"
            value={profile.preferred_end_hour}
            onChange={handleChange}
            className="border p-1 ml-2"
          />
        </div>

        <div className="mb-4">
          <label>Timezone:</label>
          <input
            name="timezone"
            value={profile.timezone}
            onChange={handleChange}
            className="border p-1 ml-2"
          />
        </div>

        <button onClick={handleSave} className="btn" disabled={isSaving}>
          {isSaving ? 'Saving...' : 'Save'}
        </button>

        {message && <p className="mt-2">{message}</p>}
      </div>
    </div>
  );
};

export default ProfilePage;
