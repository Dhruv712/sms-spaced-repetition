import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { buildApiUrl } from '../config';

interface User {
  email: string;
  name: string;
  phone_number: string;
  study_mode?: string;
  preferred_start_hour?: number;
  preferred_end_hour?: number;
  timezone?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, phone_number: string, name: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
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
        setUser(userData);
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
        navigate('/');
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

  const register = async (email: string, password: string, phone_number: string, name: string) => {
    try {
      console.log('Attempting registration for:', email);
      const response = await fetch(buildApiUrl('/users/register'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, phone_number, name }),
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
        navigate('/');
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

  const isAuthenticated = !!token && !!user;

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
      register,
      logout,
      isAuthenticated,
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