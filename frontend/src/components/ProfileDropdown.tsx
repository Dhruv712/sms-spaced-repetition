import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { buildApiUrl } from '../config';

interface UserProfile {
  name: string;
  phone_number: string | null;
  study_mode: string;
  preferred_start_hour: number;
  preferred_end_hour: number;
  preferred_text_times: number[] | null;
  timezone: string;
  sms_opt_in: boolean;
  email: string;
}

const ProfileDropdown: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [countryCode, setCountryCode] = useState('+1');
  const [phoneNumber, setPhoneNumber] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { token } = useAuth();

  // Get user initials for avatar
  const getInitials = () => {
    if (!user?.name) return user?.email?.[0]?.toUpperCase() || '?';
    const names = user.name.split(' ');
    if (names.length >= 2) {
      return (names[0][0] + names[names.length - 1][0]).toUpperCase();
    }
    return user.name[0].toUpperCase();
  };

  // Fetch profile data
  useEffect(() => {
    if (!token || !showModal) return;

    axios.get(buildApiUrl('/users/profile'), {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
      .then((res) => {
        setProfile(res.data);
        // Parse phone number if it exists
        if (res.data.phone_number && res.data.phone_number !== null) {
          const phone = res.data.phone_number;
          if (phone.startsWith('+1')) {
            setCountryCode('+1');
            setPhoneNumber(phone.substring(2));
          } else {
            const match = phone.match(/^(\+\d{1,4})(.*)$/);
            if (match) {
              setCountryCode(match[1]);
              setPhoneNumber(match[2]);
            } else {
              setPhoneNumber(phone);
            }
          }
        }
      })
      .catch((err) => {
        console.error('Failed to fetch profile', err);
        setError('Failed to load profile. Please try again.');
      });
  }, [token, showModal]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setIsOpen(false);
  };

  const handleSave = async () => {
    if (!profile || !token) return;
    setIsSaving(true);
    setError('');
    setMessage('');

    try {
      const fullPhoneNumber = phoneNumber.trim() ? `${countryCode}${phoneNumber.replace(/\D/g, '')}` : '';

      const profileData = {
        ...profile,
        phone_number: fullPhoneNumber,
      };

      await axios.put(buildApiUrl('/users/profile'), profileData, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setMessage('Profile saved successfully!');
      setTimeout(() => {
        setMessage('');
        setShowModal(false);
      }, 1500);
    } catch (err) {
      console.error('Failed to save profile:', err);
      setError('Failed to save profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    if (!profile) return;
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  if (!user) return null;

  return (
    <>
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-accent/20 dark:bg-accent/30 hover:bg-accent/30 dark:hover:bg-accent/40 transition-colors border-2 border-accent/30 dark:border-accent/40"
          title={user.name || user.email}
        >
          <span className="text-accent font-semibold text-sm">
            {getInitials()}
          </span>
        </button>

        {isOpen && (
          <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-darksurface rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 py-1 z-50">
            <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
              <p className="text-sm font-medium text-gray-900 dark:text-darktext truncate">
                {user.name || 'User'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {user.email}
              </p>
            </div>
            <button
              onClick={() => {
                setShowModal(true);
                setIsOpen(false);
              }}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              Profile Settings
            </button>
            <button
              onClick={handleLogout}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              Logout
            </button>
          </div>
        )}
      </div>

      {/* Profile Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 dark:bg-opacity-70 overflow-y-auto">
          <div className="bg-white dark:bg-darksurface rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 my-8 border border-gray-200 dark:border-gray-700 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-darktext">Profile Settings</h2>
              <button
                onClick={() => {
                  setShowModal(false);
                  setError('');
                  setMessage('');
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200 rounded">
                {error}
              </div>
            )}

            {message && (
              <div className="mb-4 p-3 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200 rounded">
                {message}
              </div>
            )}

            {profile && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Name
                  </label>
                  <input
                    name="name"
                    value={profile.name}
                    onChange={handleChange}
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Phone Number
                  </label>
                  <div className="flex gap-2">
                    <select
                      value={countryCode}
                      onChange={(e) => setCountryCode(e.target.value)}
                      className="w-24 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600"
                    >
                      <option value="+1">🇺🇸 +1</option>
                      <option value="+44">🇬🇧 +44</option>
                      <option value="+33">🇫🇷 +33</option>
                      <option value="+49">🇩🇪 +49</option>
                      <option value="+81">🇯🇵 +81</option>
                      <option value="+91">🇮🇳 +91</option>
                      {/* Add more as needed */}
                    </select>
                    <input
                      type="tel"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="1234567890"
                      className="flex-1 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Study Mode
                  </label>
                  <select
                    name="study_mode"
                    value={profile.study_mode}
                    onChange={handleChange}
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600"
                  >
                    <option value="batch">Batch</option>
                    <option value="distributed">Distributed</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Timezone
                  </label>
                  <select
                    name="timezone"
                    value={profile.timezone}
                    onChange={handleChange}
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600"
                  >
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time (ET)</option>
                    <option value="America/Chicago">Central Time (CT)</option>
                    <option value="America/Denver">Mountain Time (MT)</option>
                    <option value="America/Los_Angeles">Pacific Time (PT)</option>
                    <option value="Europe/London">London (GMT/BST)</option>
                    <option value="Europe/Paris">Paris (CET/CEST)</option>
                    <option value="Asia/Tokyo">Tokyo (JST)</option>
                    <option value="Asia/Kolkata">Mumbai (IST)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Preferred Text Times (select all that apply)
                  </label>
                  <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2">
                    {Array.from({ length: 24 }, (_, i) => {
                      const hour = i;
                      const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
                      const amPm = hour < 12 ? 'AM' : 'PM';
                      const isSelected = profile.preferred_text_times?.includes(hour) || false;

                      return (
                        <label
                          key={hour}
                          className={`flex flex-col items-center justify-center p-2 border rounded-md cursor-pointer transition-colors ${
                            isSelected
                              ? 'bg-accent text-white border-accent'
                              : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-accent'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={(e) => {
                              const currentTimes = profile.preferred_text_times || [];
                              let newTimes: number[];
                              if (e.target.checked) {
                                newTimes = [...currentTimes, hour].sort((a, b) => a - b);
                              } else {
                                newTimes = currentTimes.filter((t) => t !== hour);
                              }
                              setProfile({ ...profile, preferred_text_times: newTimes.length > 0 ? newTimes : [12] });
                            }}
                            className="sr-only"
                          />
                          <span className="text-xs font-medium">{displayHour}</span>
                          <span className="text-[10px] opacity-75">{amPm}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    id="sms-opt-in"
                    name="sms_opt_in"
                    type="checkbox"
                    checked={profile.sms_opt_in}
                    onChange={(e) => setProfile({ ...profile, sms_opt_in: e.target.checked })}
                    className="h-4 w-4 text-accent focus:ring-accent border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600"
                  />
                  <label htmlFor="sms-opt-in" className="ml-2 block text-sm text-gray-900 dark:text-darktext">
                    <span className="font-medium">Receive SMS notifications</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Get daily flashcard reminders and spaced repetition notifications via text message.
                    </p>
                  </label>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      setError('');
                      setMessage('');
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="flex-1 px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90 disabled:opacity-50 transition-colors"
                  >
                    {isSaving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default ProfileDropdown;

