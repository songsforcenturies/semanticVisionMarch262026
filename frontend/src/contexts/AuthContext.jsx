import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '@/lib/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check for existing token
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    const savedStudent = localStorage.getItem('student');

    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }

    if (savedStudent) {
      setStudent(JSON.parse(savedStudent));
    }

    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, user: userData } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      setUser(userData);
      setIsAuthenticated(true);

      return { success: true, user: userData };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (fullName, email, password, role = 'guardian') => {
    try {
      const response = await authAPI.register({
        full_name: fullName,
        email,
        password,
        role
      });

      // Auto-login after registration
      return await login(email, password);
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const studentLogin = async (studentCode, pin) => {
    try {
      const response = await authAPI.studentLogin(studentCode, pin);
      const { student: studentData } = response.data;

      localStorage.setItem('student', JSON.stringify(studentData));
      setStudent(studentData);

      return { success: true, student: studentData };
    } catch (error) {
      console.error('Student login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Invalid credentials' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('student');
    setUser(null);
    setStudent(null);
    setIsAuthenticated(false);
  };

  const studentLogout = () => {
    localStorage.removeItem('student');
    setStudent(null);
  };

  const value = {
    user,
    student,
    loading,
    isAuthenticated,
    login,
    register,
    studentLogin,
    logout,
    studentLogout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
