/**
 * Login Page
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import api from '../services/api';
import { LoginRequest, User } from '../types';

interface LoginPageProps {
  onLoginSuccess: (user: User) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleLogin = async (credentials: LoginRequest) => {
    setError(null);
    try {
      const response = await api.post('/api/v1/auth/login', credentials);
      onLoginSuccess(response.data.user);

      // Navigate based on user role
      if (response.data.user.role === 'MA') {
        navigate('/ma-dashboard');
      } else {
        navigate('/creator-dashboard');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Login failed. Please try again.';
      setError(errorMessage);
      throw err;
    }
  };

  return <LoginForm onSubmit={handleLogin} error={error || undefined} />;
};

export default LoginPage;
