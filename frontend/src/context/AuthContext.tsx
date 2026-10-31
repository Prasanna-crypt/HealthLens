// Just a standard component, nothing fancy here.

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../lib/api';
import type { User } from '../lib/types';

// Defines what data our AuthContext will hold
interface AuthContextType {
  user: User | null; // The logged-in user, or null if logged out
  isAuthenticated: boolean; // True if user is logged in
  loading: boolean; // True while we are checking if the user is logged in
  login: (u: string, p: string) => Promise<void>; // Function to log in
  register: (e: string, p: string, f: string) => Promise<void>; // Function to register
  logout: () => void; // Function to log out
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// The Provider component that wraps our app
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check if the user is already logged in when the app loads
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('healthlens_token');
      if (token && token !== 'undefined' && token !== 'null' && token.trim() !== '') {
        try {
          // If we have a token, fetch the user's details
          const res = await authAPI.getMe();
          if (res?.data?.id || res?.data?.email) {
            setUser(res.data);
          } else {
            localStorage.removeItem('healthlens_token');
            setUser(null);
          }
        } catch (error) {
          // If token is invalid, remove it
          localStorage.removeItem('healthlens_token');
          setUser(null);
        }
      } else {
        localStorage.removeItem('healthlens_token');
        setUser(null);
      }
      setLoading(false); // Finished checking
    };
    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    // 1. Send credentials to server
    const res = await authAPI.login(username, password);
    if (!res?.data?.access_token) {
      throw new Error(res?.data?.detail || 'Invalid credentials or login response');
    }
    // 2. Save the token to local storage
    localStorage.setItem('healthlens_token', res.data.access_token);
    // 3. Fetch user details and update state
    const userRes = await authAPI.getMe();
    setUser(userRes.data);
  };

  const register = async (email: string, password: string, full_name: string) => {
    // Register the user on the server
    await authAPI.register(email, password, full_name);
    // Automatically log them in after registration
    await login(email, password);
  };

  const logout = () => {
    // Clear token and user state
    localStorage.removeItem('healthlens_token');
    setUser(null);
  };

  // Provide these values to all child components
  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to easily use the AuthContext in any component
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
