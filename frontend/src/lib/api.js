import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==================== AUTH API ====================

export const authAPI = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (data) => apiClient.post('/auth/login', data),
  studentLogin: (studentCode, pin) => apiClient.post('/auth/student-login', { student_code: studentCode, pin }),
  getMe: () => apiClient.get('/auth/me'),
};

// ==================== STUDENT API ====================

export const studentAPI = {
  create: (data) => apiClient.post('/students', data),
  getAll: (guardianId) => apiClient.get('/students', { params: { guardian_id: guardianId } }),
  getById: (id) => apiClient.get(`/students/${id}`),
  update: (id, data) => apiClient.patch(`/students/${id}`, data),
  delete: (id) => apiClient.delete(`/students/${id}`),
  resetPin: (id) => apiClient.post(`/students/${id}/reset-pin`),
  getProgress: (id) => apiClient.get(`/students/${id}/progress`),
  getExportUrl: (id, format) => `${API}/students/${id}/export?format=${format}`,
  toggleSpellcheck: (id) => apiClient.post(`/students/${id}/spellcheck`),
  toggleSpellingMode: (id) => apiClient.post(`/students/${id}/spelling-mode`),
  getSpellingLogs: (id) => apiClient.get(`/students/${id}/spelling-logs`),
};

// ==================== SUBSCRIPTION API ====================

export const subscriptionAPI = {
  get: (guardianId) => apiClient.get(`/subscriptions/${guardianId}`),
};

// ==================== WORD BANK API ====================

export const wordBankAPI = {
  create: (data) => apiClient.post('/word-banks', data),
  getAll: (params) => apiClient.get('/word-banks', { params }),
  getById: (id) => apiClient.get(`/word-banks/${id}`),
  purchase: (guardianId, bankId) => apiClient.post('/word-banks/purchase', { guardian_id: guardianId, bank_id: bankId }),
  assignToStudent: (studentId, bankIds) => apiClient.post('/students/assign-banks', { student_id: studentId, bank_ids: bankIds }),
};

// ==================== NARRATIVE API ====================

export const narrativeAPI = {
  create: (data) => apiClient.post('/narratives', data),
  getAll: (studentId) => apiClient.get('/narratives', { params: { student_id: studentId } }),
  getById: (id) => apiClient.get(`/narratives/${id}`),
  delete: (id) => apiClient.delete(`/narratives/${id}`),
};

// ==================== READ LOG API ====================

export const readLogAPI = {
  create: (data) => apiClient.post('/read-logs', data),
  getAll: (studentId) => apiClient.get('/read-logs', { params: { student_id: studentId } }),
};

// ==================== ASSESSMENT API ====================

export const assessmentAPI = {
  create: (data) => apiClient.post('/assessments', data),
  getAll: (params) => apiClient.get('/assessments', { params }),
  getById: (id) => apiClient.get(`/assessments/${id}`),
  evaluate: (id, answers) => apiClient.post(`/assessments/${id}/evaluate`, answers),
  evaluateWritten: (data) => apiClient.post('/assessments/evaluate-written', data),
};

// ==================== GIFT API ====================

export const giftAPI = {
  create: (data) => apiClient.post('/gifts', data),
  redeem: (token) => apiClient.post('/gifts/redeem', { token }),
};

// ==================== CLASSROOM API ====================

export const classroomAPI = {
  create: (data) => apiClient.post('/classroom-sessions', data),
  getAll: () => apiClient.get('/classroom-sessions'),
  getById: (id) => apiClient.get(`/classroom-sessions/${id}`),
  start: (id) => apiClient.post(`/classroom-sessions/${id}/start`),
  end: (id) => apiClient.post(`/classroom-sessions/${id}/end`),
  join: (code, studentId) => apiClient.post('/classroom-sessions/join', { session_code: code, student_id: studentId }),
  analytics: (id) => apiClient.get(`/classroom-sessions/${id}/analytics`),
};

// ==================== ADMIN API ====================

export const adminAPI = {
  getCosts: () => apiClient.get('/admin/costs'),
  getModels: () => apiClient.get('/admin/models'),
  updateModels: (data) => apiClient.post('/admin/models', data),
  getSettings: () => apiClient.get('/admin/settings'),
  updateSettings: (data) => apiClient.post('/admin/settings', data),
};

export default apiClient;
