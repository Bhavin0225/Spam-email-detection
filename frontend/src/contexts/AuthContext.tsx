import React, { createContext, useState, useEffect, useContext } from 'react';
import { apiClient } from '../services/apiClient';

interface User {
  email: string;
  role: string;
  user_id?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper to safely parse JWT payload
function decodeJwt(token: string): any {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const initAuth = () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      const payload = decodeJwt(token);
      if (payload && payload.exp * 1000 > Date.now()) {
        setUser({
          email: payload.sub,
          role: payload.role,
        });
      } else {
        // Token expired on load, clear local storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
      }
    } else {
      setUser(null);
    }
    setLoading(false);
  };

  useEffect(() => {
    initAuth();
    
    // Listen for axios interceptor forced logouts (due to expired refresh tokens)
    const handleForcedLogout = () => {
      setUser(null);
    };
    window.addEventListener('auth_logout', handleForcedLogout);
    return () => {
      window.removeEventListener('auth_logout', handleForcedLogout);
    };
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // Backend auth expects urlencoded OAuth2 format
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const res = await apiClient.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      const { access_token, refresh_token } = res.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      const payload = decodeJwt(access_token);
      setUser({
        email: payload.sub,
        role: payload.role,
      });
    } catch (e) {
      setUser(null);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email: string, password: string, fullName: string) => {
    try {
      await apiClient.post('/auth/signup', {
        email,
        password,
        full_name: fullName,
      });
      
      // Auto login after signup (login manages its own loading state)
      await login(email, password);
    } catch (e) {
      setUser(null);
      setLoading(false);
      throw e;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
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
