import axios from 'axios';
import { AnalyticsDashboard, ChatMessage, ChatResponse, Token, UserInfo } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api`
  : 'http://localhost:8000/api';


const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('skylark_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('skylark_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const login = async (username: string, password: string): Promise<Token> => {
  // Backend expects JSON body (LoginRequest Pydantic model)
  const response = await api.post<Token>('/auth/login', { username, password });
  return response.data;
};

export const getMe = async (): Promise<UserInfo> => {
  const response = await api.get<UserInfo>('/auth/me');
  return response.data;
};

export const getDashboard = async (): Promise<AnalyticsDashboard> => {
  const response = await api.get<AnalyticsDashboard>('/analytics/dashboard');
  return response.data;
};

export const chat = async (message: string, history: ChatMessage[]): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>('/agent/chat', { message, history });
  return response.data;
};

export const getHealth = async (): Promise<{ status: string }> => {
  const response = await api.get<{ status: string }>('/health');
  return response.data;
};

export default api;
