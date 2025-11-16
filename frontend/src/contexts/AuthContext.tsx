import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { buildApiUrl } from '../config';

interface User {
  email: string;
  name: string;
  phone_number: string | null;
  google_id: string | null;
  study_mode?: string;
  preferred_start_hour?: number;
  preferred_end_hour?: number;
  timezone?: string;
  sms_opt_in?: boolean;
  has_sms_conversation?: boolean;
  is_premium?: boolean;
  is_admin?: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, phone_number: string, name: string, sms_opt_in?: boolean) => Promise<void>;
  loginWithGoogleToken: (token: string) => void;
  updatePhoneNumber: (phoneNumber: string, smsOptIn: boolean) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  showPhoneModal: boolean;
  setShowPhoneModal: (show: boolean) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [showPhoneModal, setShowPhoneModal] = useState(false);
  const navigate = useNavigate();

  const logout = useCallback(() => {
    console.log('Logging out...');
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    navigate('/login');
  }, [navigate]);

  const fetchUserProfile = useCallback(async () => {
    try {
      console.log('Attempting to fetch user profile...');
      const response = await fetch(buildApiUrl('/users/profile'), {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const userData = await response.json();
        console.log('User profile fetched successfully:', userData);
        console.log('Google ID:', userData.google_id);
        console.log('Phone number:', userData.phone_number);
        setUser(userData);
        
        // Show phone modal for Google users without phone numbers
        if (userData.google_id && (!userData.phone_number || userData.phone_number === null)) {
          console.log('Google user without phone number, showing phone modal');
          setShowPhoneModal(true);
        } else {
          console.log('Not showing phone modal. Google ID exists:', !!userData.google_id, 'Phone number exists:', !!userData.phone_number);
        }
      } else {
        console.log('Failed to fetch user profile:', response.status);
        // If the token is invalid, clear it
        logout();
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
      logout();
    }
  }, [token, logout]);

  useEffect(() => {
    console.log('Auth state changed:', { token, user });
  }, [token, user]);

  useEffect(() => {
    // If we have a token, try to get the user profile
    if (token) {
      console.log('Fetching user profile with token:', token);
      fetchUserProfile();
    } else {
      // If no token, clear user
      setUser(null);
    }
  }, [token, fetchUserProfile]);

  const login = async (email: string, password: string) => {
    try {
      console.log('Attempting login for:', email);
      const response = await fetch(buildApiUrl('/users/login'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      console.log('Login successful, received token');
      const newToken = data.access_token;
      setToken(newToken);
      localStorage.setItem('token', newToken);
      
      // Fetch user profile immediately after login
      const profileResponse = await fetch(buildApiUrl('/users/profile'), {
        headers: {
          'Authorization': `Bearer ${newToken}`
        }
      });
      
      if (profileResponse.ok) {
        const userData = await profileResponse.json();
        setUser(userData);
        navigate('/dashboard');
      } else {
        throw new Error('Failed to fetch user profile after login');
      }
    } catch (error) {
      console.error('Login error:', error);
      // Clear any partial state
      setToken(null);
      setUser(null);
      localStorage.removeItem('token');
      throw error;
    }
  };

  const register = async (email: string, password: string, phone_number: string, name: string, sms_opt_in: boolean = false) => {
    try {
      console.log('Attempting registration for:', email);
      const response = await fetch(buildApiUrl('/users/register'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, phone_number, name, sms_opt_in }),
      });

      if (!response.ok) {
        throw new Error('Registration failed');
      }

      const data = await response.json();
      console.log('Registration successful, received token');
      const newToken = data.access_token;
      setToken(newToken);
      localStorage.setItem('token', newToken);
      
      // Fetch user profile immediately after registration
      const profileResponse = await fetch(buildApiUrl('/users/profile'), {
        headers: {
          'Authorization': `Bearer ${newToken}`
        }
      });
      
      if (profileResponse.ok) {
        const userData = await profileResponse.json();
        setUser(userData);
        navigate('/dashboard');
      } else {
        throw new Error('Failed to fetch user profile after registration');
      }
    } catch (error) {
      console.error('Registration error:', error);
      // Clear any partial state
      setToken(null);
      setUser(null);
      localStorage.removeItem('token');
      throw error;
    }
  };

  const loginWithGoogleToken = useCallback((googleToken: string) => {
    console.log('Logging in with Google token');
    setToken(googleToken);
    localStorage.setItem('token', googleToken);
    // The useEffect will automatically fetch the user profile when token changes
  }, []);

  const updatePhoneNumber = useCallback(async (phoneNumber: string, smsOptIn: boolean) => {
    if (!token || !user) return;
    
    try {
      // Send the complete user profile with updated phone number
      const profileData = {
        name: user.name,
        phone_number: phoneNumber,
        google_id: user.google_id,
        study_mode: user.study_mode || 'batch',
        preferred_start_hour: user.preferred_start_hour || 9,
        preferred_end_hour: user.preferred_end_hour || 21,
        timezone: user.timezone || 'UTC',
        sms_opt_in: smsOptIn,
        has_sms_conversation: user.has_sms_conversation || false
      };
      
      console.log('Sending profile data:', profileData);
      
      const response = await fetch(buildApiUrl('/users/profile'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUser(updatedUser);
        setShowPhoneModal(false);
        console.log('Phone number updated successfully');
      } else {
        const errorData = await response.json();
        console.error('Failed to update phone number:', response.status, errorData);
        throw new Error('Failed to update phone number');
      }
    } catch (error) {
      console.error('Error updating phone number:', error);
      throw error;
    }
  }, [token, user]);

  const isAuthenticated = !!token && !!user;

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
      register,
      loginWithGoogleToken,
      updatePhoneNumber,
      logout,
      isAuthenticated,
      showPhoneModal,
      setShowPhoneModal,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 