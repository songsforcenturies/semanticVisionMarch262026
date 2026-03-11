import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { authAPI, sessionAPI } from '@/lib/api';

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
  const heartbeatRef = useRef(null);
  const sessionIdRef = useRef(null);
  const studentIdRef = useRef(null);

  const stopSessionTracking = useCallback(() => {
    if (heartbeatRef.current) {
      clearInterval(heartbeatRef.current);
      heartbeatRef.current = null;
    }
    // Try to end the session
    if (sessionIdRef.current && studentIdRef.current) {
      sessionAPI.end(studentIdRef.current, sessionIdRef.current).catch(() => {});
    }
    sessionIdRef.current = null;
    studentIdRef.current = null;
  }, []);

  const startSessionTracking = useCallback(async (studentData) => {
    // Stop any existing tracking
    stopSessionTracking();
    try {
      const res = await sessionAPI.start(studentData.id);
      const sid = res.data.session_id;
      sessionIdRef.current = sid;
      studentIdRef.current = studentData.id;
      // Store in localStorage for beforeunload
      localStorage.setItem('active_session_id', sid);
      localStorage.setItem('active_student_id', studentData.id);
      // Heartbeat every 60 seconds
      heartbeatRef.current = setInterval(() => {
        if (sessionIdRef.current && studentIdRef.current) {
          sessionAPI.heartbeat(studentIdRef.current, sessionIdRef.current).catch(() => {});
        }
      }, 60000);
    } catch (e) {
      console.error('Failed to start session tracking:', e);
    }
  }, [stopSessionTracking]);

  // Handle tab close / page unload
  useEffect(() => {
    const handleBeforeUnload = () => {
      const sid = localStorage.getItem('active_session_id');
      const stId = localStorage.getItem('active_student_id');
      if (sid && stId) {
        const url = `${process.env.REACT_APP_BACKEND_URL}/api/sessions/end`;
        navigator.sendBeacon(url, JSON.stringify({ student_id: stId, session_id: sid }));
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

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
      const parsedStudent = JSON.parse(savedStudent);
      setStudent(parsedStudent);
      // Resume session tracking for returning student
      startSessionTracking(parsedStudent);
    }

    setLoading(false);
  }, [startSessionTracking]);

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

  const register = async (fullName, email, password, referralCode = null, role = 'guardian') => {
    try {
      const payload = {
        full_name: fullName,
        email,
        password,
        role
      };
      if (referralCode) payload.referral_code = referralCode;
      
      const response = await authAPI.register(payload);

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

      // Start session tracking
      startSessionTracking(studentData);

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
    stopSessionTracking();
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('student');
    localStorage.removeItem('active_session_id');
    localStorage.removeItem('active_student_id');
    setUser(null);
    setStudent(null);
    setIsAuthenticated(false);
  };

  const studentLogout = () => {
    stopSessionTracking();
    localStorage.removeItem('student');
    localStorage.removeItem('active_session_id');
    localStorage.removeItem('active_student_id');
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
