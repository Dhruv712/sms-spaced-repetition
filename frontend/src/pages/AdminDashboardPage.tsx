import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface AdminStats {
  total_users: number;
  premium_users: number;
  sms_opt_in_users: number;
  active_users: number;
  users_with_sms_conversation: number;
  new_users_7d: number;
  new_users_30d: number;
  total_flashcards: number;
  total_reviews: number;
  total_decks: number;
  reviews_last_7d: number;
  reviews_last_30d: number;
}

interface User {
  id: number;
  email: string;
  name: string | null;
  is_premium: boolean;
  is_admin: boolean;
  sms_opt_in: boolean;
  has_sms_conversation: boolean;
  phone_number: string | null;
  timezone: string;
  current_streak_days: number;
  longest_streak_days: number;
  flashcards_count: number;
  reviews_count: number;
  decks_count: number;
  last_review_date: string | null;
  created_at: string | null;
  subscription_status: string | null;
  subscription_end_date: string | null;
}

const AdminDashboardPage: React.FC = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPremium, setFilterPremium] = useState<boolean | null>(null);
  const [filterSms, setFilterSms] = useState<boolean | null>(null);

  useEffect(() => {
    if (!token || !user) {
      navigate('/login');
      return;
    }

    if (!user.is_admin) {
      setError('Access denied. Admin privileges required.');
      setLoading(false);
      return;
    }

    fetchDashboardData();
  }, [token, user, navigate]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(buildApiUrl('/admin/dashboard'), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.data.success) {
        setStats(response.data.stats);
        setUsers(response.data.users);
      } else {
        setError('Failed to load dashboard data');
      }
    } catch (err: any) {
      console.error('Error fetching admin dashboard:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (user.name && user.name.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesPremium = filterPremium === null || user.is_premium === filterPremium;
    const matchesSms = filterSms === null || user.sms_opt_in === filterSms;
    
    return matchesSearch && matchesPremium && matchesSms;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-darkbg flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white dark:bg-darkbg flex items-center justify-center">
        <div className="text-xl text-red-600 dark:text-red-400">{error}</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="min-h-screen bg-white dark:bg-darkbg flex items-center justify-center">
        <div className="text-xl text-gray-600 dark:text-gray-400">No data available</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-darkbg py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-light text-gray-900 dark:text-darktext mb-8">Admin Dashboard</h1>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Users</div>
            <div className="text-3xl font-light text-gray-900 dark:text-darktext">{stats.total_users}</div>
            <div className="text-xs text-gray-500 dark:text-gray-500 mt-2">
              {stats.new_users_7d} new (7d) • {stats.new_users_30d} new (30d)
            </div>
          </div>

          <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Premium Users</div>
            <div className="text-3xl font-light text-gray-900 dark:text-darktext">{stats.premium_users}</div>
            <div className="text-xs text-gray-500 dark:text-gray-500 mt-2">
              {((stats.premium_users / stats.total_users) * 100).toFixed(1)}% of total
            </div>
          </div>

          <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">SMS Opt-In</div>
            <div className="text-3xl font-light text-gray-900 dark:text-darktext">{stats.sms_opt_in_users}</div>
            <div className="text-xs text-gray-500 dark:text-gray-500 mt-2">
              {stats.users_with_sms_conversation} with active conversations
            </div>
          </div>

          <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Active Users (30d)</div>
            <div className="text-3xl font-light text-gray-900 dark:text-darktext">{stats.active_users}</div>
            <div className="text-xs text-gray-500 dark:text-gray-500 mt-2">
              Reviewed in last 30 days
            </div>
          </div>
        </div>

        {/* Content Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Flashcards</div>
            <div className="text-3xl font-light text-gray-900 dark:text-darktext">{stats.total_flashcards}</div>
          </div>

          <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Reviews</div>
            <div className="text-3xl font-light text-gray-900 dark:text-darktext">{stats.total_reviews}</div>
            <div className="text-xs text-gray-500 dark:text-gray-500 mt-2">
              {stats.reviews_last_7d} (7d) • {stats.reviews_last_30d} (30d)
            </div>
          </div>

          <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Decks</div>
            <div className="text-3xl font-light text-gray-900 dark:text-darktext">{stats.total_decks}</div>
          </div>
        </div>

        {/* User List */}
        <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
          <h2 className="text-xl font-light text-gray-900 dark:text-darktext mb-6">Users ({filteredUsers.length})</h2>

          {/* Filters */}
          <div className="mb-4 flex flex-wrap gap-4">
            <input
              type="text"
              placeholder="Search by email or name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 min-w-[200px] px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-darktext focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <select
              value={filterPremium === null ? 'all' : filterPremium.toString()}
              onChange={(e) => setFilterPremium(e.target.value === 'all' ? null : e.target.value === 'true')}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-darktext focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Premium Status</option>
              <option value="true">Premium Only</option>
              <option value="false">Free Only</option>
            </select>
            <select
              value={filterSms === null ? 'all' : filterSms.toString()}
              onChange={(e) => setFilterSms(e.target.value === 'all' ? null : e.target.value === 'true')}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-darktext focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All SMS Status</option>
              <option value="true">SMS Opt-In</option>
              <option value="false">No SMS</option>
            </select>
          </div>

          {/* User Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Email</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Name</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Premium</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">SMS</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Phone</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Cards</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Reviews</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Streak</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Last Review</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Joined</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="py-3 px-4 text-gray-900 dark:text-darktext">
                      {user.email}
                      {user.is_admin && (
                        <span className="ml-2 text-xs bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 px-2 py-0.5 rounded">Admin</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300">{user.name || '-'}</td>
                    <td className="py-3 px-4">
                      {user.is_premium ? (
                        <span className="text-green-600 dark:text-green-400 font-medium">✓</span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {user.sms_opt_in ? (
                        <span className="text-blue-600 dark:text-blue-400 font-medium">✓</span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                      {user.has_sms_conversation && (
                        <span className="ml-1 text-xs text-green-600 dark:text-green-400" title="Has active SMS conversation">💬</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300 text-xs">{user.phone_number || '-'}</td>
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300">{user.flashcards_count}</td>
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300">{user.reviews_count}</td>
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300">
                      {user.current_streak_days > 0 && (
                        <span>{user.current_streak_days} 🔥</span>
                      )}
                      {user.current_streak_days === 0 && '-'}
                    </td>
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300 text-xs">{formatDate(user.last_review_date)}</td>
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300 text-xs">{formatDate(user.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredUsers.length === 0 && (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              No users found matching your filters.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage;

