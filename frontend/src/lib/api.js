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
      // Only clear auth if not on a login-related request
      const url = error.config?.url || '';
      if (!url.includes('/auth/login') && !url.includes('/auth/register')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
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
  forgotPassword: (email) => apiClient.post('/auth/forgot-password', { email }),
  resetPassword: (data) => apiClient.post('/auth/reset-password', data),
  sendVerification: () => apiClient.post('/auth/send-verification'),
  verifyEmail: (code) => apiClient.post('/auth/verify-email', { code }),
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
  delete: (id) => apiClient.delete(`/word-banks/${id}`),
  purchase: (guardianId, bankId) => apiClient.post('/word-banks/purchase', { guardian_id: guardianId, bank_id: bankId }),
  assignToStudent: (studentId, bankIds) => apiClient.post('/students/assign-banks', { student_id: studentId, bank_ids: bankIds }),
  canParentCreate: () => apiClient.get('/feature-flags/parent-wordbank'),
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
  getStats: () => apiClient.get('/admin/stats'),
  getUsers: () => apiClient.get('/admin/users'),
  delegateAdmin: (data) => apiClient.post('/admin/delegate', data),
  getCoupons: () => apiClient.get('/admin/coupons'),
  createCoupon: (data) => apiClient.post('/admin/coupons', data),
  deleteCoupon: (id) => apiClient.delete(`/admin/coupons/${id}`),
  getPlans: () => apiClient.get('/admin/plans'),
  createPlan: (data) => apiClient.post('/admin/plans', data),
  deletePlan: (id) => apiClient.delete(`/admin/plans/${id}`),
  createWordBank: (data) => apiClient.post('/admin/word-banks', data),
  getBillingConfig: () => apiClient.get('/admin/billing-config'),
  updateBillingConfig: (data) => apiClient.post('/admin/billing-config', data),
  getFeatureFlags: () => apiClient.get('/admin/feature-flags'),
  updateFeatureFlags: (data) => apiClient.post('/admin/feature-flags', data),
  getBrands: () => apiClient.get('/admin/brands'),
  createBrand: (data) => apiClient.post('/admin/brands', data),
  updateBrand: (id, data) => apiClient.put(`/admin/brands/${id}`, data),
  deleteBrand: (id) => apiClient.delete(`/admin/brands/${id}`),
  getBrandAnalytics: () => apiClient.get('/admin/brand-analytics'),
  getClassroomSponsorships: () => apiClient.get('/admin/classroom-sponsorships'),
  createClassroomSponsorship: (data) => apiClient.post('/admin/classroom-sponsorships', data),
  deleteClassroomSponsorship: (id) => apiClient.delete(`/admin/classroom-sponsorships/${id}`),
  // User Management
  createUser: (data) => apiClient.post('/admin/users', data),
  updateUser: (id, data) => apiClient.put(`/admin/users/${id}`, data),
  resetPassword: (id) => apiClient.post(`/admin/users/${id}/reset-password`),
  deactivateUser: (id) => apiClient.post(`/admin/users/${id}/deactivate`),
  deleteUser: (id) => apiClient.delete(`/admin/users/${id}`),
  addCredits: (id, data) => apiClient.post(`/admin/users/${id}/add-credits`, data),
};

// ==================== WALLET API ====================

export const walletAPI = {
  getBalance: () => apiClient.get('/wallet/balance'),
  getTransactions: () => apiClient.get('/wallet/transactions'),
  getPackages: () => apiClient.get('/wallet/packages'),
  topup: (data) => apiClient.post('/wallet/topup', data),
  purchaseBank: (data) => apiClient.post('/wallet/purchase-bank', data),
  getPaymentStatus: (sessionId) => apiClient.get(`/payments/status/${sessionId}`),
};

// ==================== COUPON API ====================

export const couponAPI = {
  redeem: (code) => apiClient.post('/coupons/redeem', { code }),
};

// ==================== REFERRAL API ====================

export const referralAPI = {
  getMyCode: () => apiClient.get('/referrals/my-code'),
  getMyReferrals: () => apiClient.get('/referrals/my-referrals'),
};

// ==================== WORD DEFINITION API ====================

export const wordAPI = {
  define: (word, context) => apiClient.post('/words/define', { word, context }),
};

// ==================== DONATION API ====================

export const donationAPI = {
  create: (data) => apiClient.post('/donations/create', data),
  getStatus: (sessionId) => apiClient.get(`/donations/status/${sessionId}`),
  getStats: () => apiClient.get('/donations/stats'),
};

// ==================== STUDENT AD PREFERENCES API ====================

export const adPreferencesAPI = {
  get: (studentId) => apiClient.get(`/students/${studentId}/ad-preferences`),
  update: (studentId, data) => apiClient.post(`/students/${studentId}/ad-preferences`, data),
};

// ==================== BRAND PORTAL API ====================

export const brandPortalAPI = {
  getProfile: () => apiClient.get('/brand-portal/profile'),
  getDashboard: () => apiClient.get('/brand-portal/dashboard'),
  updateProfile: (data) => apiClient.put('/brand-portal/profile', data),
  uploadLogo: (formData) => apiClient.post('/brand-portal/logo-upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getProducts: () => apiClient.get('/brand-portal/products'),
  addProduct: (data) => apiClient.post('/brand-portal/products', data),
  updateProduct: (id, data) => apiClient.put(`/brand-portal/products/${id}`, data),
  deleteProduct: (id) => apiClient.delete(`/brand-portal/products/${id}`),
  getCampaigns: () => apiClient.get('/brand-portal/campaigns'),
  createCampaign: (data) => apiClient.post('/brand-portal/campaigns', data),
  updateCampaign: (id, data) => apiClient.put(`/brand-portal/campaigns/${id}`, data),
  deleteCampaign: (id) => apiClient.delete(`/brand-portal/campaigns/${id}`),
  topup: (data) => apiClient.post('/brand-portal/topup', data),
  getTopupStatus: (sessionId) => apiClient.get(`/brand-portal/topup-status/${sessionId}`),
  getStoryPreview: () => apiClient.get('/brand-portal/story-preview'),
  generateStoryPreview: () => apiClient.post('/brand-portal/story-preview'),
  getAnalytics: () => apiClient.get('/brand-portal/analytics'),
  getCoupons: () => apiClient.get('/brand-portal/coupons'),
  createCoupon: (data) => apiClient.post('/brand-portal/coupons', data),
  deleteCoupon: (id) => apiClient.delete(`/brand-portal/coupons/${id}`),
};

export default apiClient;
