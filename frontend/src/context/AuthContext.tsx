import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { UserInfo, Token } from '../types';
import { login as apiLogin, getMe } from '../services/api';

interface AuthContextType {
  user: UserInfo | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('skylark_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userInfo = await getMe();
          setUser(userInfo);
        } catch (error) {
          console.error('Failed to authenticate token', error);
          localStorage.removeItem('skylark_token');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (username: string, password: string) => {
    const data: Token = await apiLogin(username, password);
    localStorage.setItem('skylark_token', data.access_token);
    setToken(data.access_token);
    const userInfo = await getMe();
    setUser(userInfo);
  };

  const logout = () => {
    localStorage.removeItem('skylark_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated: !!user,
        isLoading,
      }}
    >
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
