/**
 * AuthContext - Simple Email/Password Authentication
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService } from '../services/api';

// Types
interface User {
  id: string;
  email: string;
  full_name: string;
  user_type: 'patient' | 'doctor';
  profile_picture_url?: string;
  age?: number;
  gender?: string;
  date_of_birth?: string;
  license_number?: string;
  specialization?: string;
  hospital_affiliation?: string;
  phone?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Auth methods
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string, userType: 'patient' | 'doctor') => Promise<void>;
  logout: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// localStorage keys
const STORAGE_KEYS = {
  USER: 'medivault_user',
  TOKEN: 'medivault_token'
};

// Provider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  /**
   * Initialize - Check if user is already logged in
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem(STORAGE_KEYS.TOKEN);
        const storedUser = localStorage.getItem(STORAGE_KEYS.USER);

        if (storedToken && storedUser) {
          // Set token in API service
          apiService.setAuthToken(storedToken);

          try {
            // Verify token is still valid
            const response = await apiService.auth.getSession();

            if (response.success && response.user) {
              setUser(response.user);
            } else {
              // Token invalid, clear storage
              localStorage.removeItem(STORAGE_KEYS.TOKEN);
              localStorage.removeItem(STORAGE_KEYS.USER);
              apiService.setAuthToken(null);
            }
          } catch (error) {
            // Token invalid, clear storage
            localStorage.removeItem(STORAGE_KEYS.TOKEN);
            localStorage.removeItem(STORAGE_KEYS.USER);
            apiService.setAuthToken(null);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Login with email and password
   */
  const login = async (email: string, password: string) => {
    try {
      console.log('🔑 Logging in...', email);

      const response = await apiService.auth.login(email, password);

      if (response.success && response.user && response.token) {
        console.log('✅ Login successful!');

        // Set token
        apiService.setAuthToken(response.token);

        // Save user and token
        setUser(response.user);
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.user));
        localStorage.setItem(STORAGE_KEYS.TOKEN, response.token);
      } else {
        throw new Error('Login failed - invalid response');
      }
    } catch (error: any) {
      console.error('❌ Login error:', error);
      throw new Error(error.response?.data?.error || error.message || 'Login failed');
    }
  };

  /**
   * Signup new user
   */
  const signup = async (email: string, password: string, fullName: string, userType: 'patient' | 'doctor') => {
    try {
      console.log('📝 Signing up...', email, 'as', userType);

      let response;

      if (userType === 'patient') {
        response = await apiService.auth.signupPatient({
          email,
          password,
          full_name: fullName
        });
      } else {
        response = await apiService.auth.signupDoctor({
          email,
          password,
          full_name: fullName,
          license_number: 'PENDING',
          specialization: 'General'
        });
      }

      if (response.success && response.user && response.token) {
        console.log('✅ Signup successful!');

        // Set token
        apiService.setAuthToken(response.token);

        // Save user and token
        setUser(response.user);
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.user));
        localStorage.setItem(STORAGE_KEYS.TOKEN, response.token);
      } else {
        throw new Error('Signup failed - invalid response');
      }
    } catch (error: any) {
      console.error('❌ Signup error:', error);
      throw new Error(error.response?.data?.error || error.message || 'Signup failed');
    }
  };

  /**
   * Logout
   */
  const logout = async () => {
    try {
      // Clear local storage
      localStorage.removeItem(STORAGE_KEYS.USER);
      localStorage.removeItem(STORAGE_KEYS.TOKEN);

      // Clear API token
      apiService.setAuthToken(null);

      // Clear state
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,

    login,
    signup,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// ============================================================================
// HOOK
// ============================================================================

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
