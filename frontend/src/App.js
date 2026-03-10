import "@/App.css";
import '@/i18n';
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { CurrencyProvider } from "@/contexts/CurrencyContext";
import { Toaster } from "sonner";

// Import pages (we'll create these next)
import LandingPage from "@/pages/LandingPage";
import GuardianLogin from "@/pages/GuardianLogin";
import GuardianRegister from "@/pages/GuardianRegister";
import ForgotPassword from "@/pages/ForgotPassword";
import GuardianPortal from "@/pages/GuardianPortal";
import StudentAcademy from "@/pages/StudentAcademy";
import TeacherPortal from "@/pages/TeacherPortal";
import AdminPortal from "@/pages/AdminPortal";
import DonatePage from "@/pages/DonatePage";
import BrandPortal from "@/pages/BrandPortal";
import AffiliateSignup from "@/pages/AffiliateSignup";

// Protected route component
const ProtectedRoute = ({ children, requireAuth = true, allowedRoles = null }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl font-bold">Loading...</div>
      </div>
    );
  }

  // Check both context state and localStorage (handles race condition after login)
  const hasToken = !!localStorage.getItem('token') && !!localStorage.getItem('user');
  if (requireAuth && !isAuthenticated && !hasToken) {
    return <Navigate to="/login" replace />;
  }

  // Role-based access control
  if (allowedRoles) {
    const savedUser = user || JSON.parse(localStorage.getItem('user') || '{}');
    if (!allowedRoles.includes(savedUser?.role)) {
      return <Navigate to="/portal" replace />;
    }
  }

  return children;
};

// Student protected route
const StudentRoute = ({ children }) => {
  const { student } = useAuth();

  if (!student) {
    return <Navigate to="/student-login" replace />;
  }

  return children;
};

function AppContent() {
  return (
    <BrowserRouter>
      <div className="App min-h-screen bg-gray-50">
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<GuardianLogin />} />
          <Route path="/register" element={<GuardianRegister />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/student-login" element={<Navigate to="/login?type=student" replace />} />
          <Route path="/teacher-login" element={<Navigate to="/login?type=teacher" replace />} />
          <Route path="/teacher-register" element={<Navigate to="/register?role=teacher" replace />} />
          <Route path="/donate" element={<DonatePage />} />
          <Route path="/affiliate" element={<AffiliateSignup />} />

          {/* Guardian protected routes */}
          <Route
            path="/portal/*"
            element={
              <ProtectedRoute>
                <GuardianPortal />
              </ProtectedRoute>
            }
          />

          {/* Teacher protected routes */}
          <Route
            path="/teacher-portal/*"
            element={
              <ProtectedRoute>
                <TeacherPortal />
              </ProtectedRoute>
            }
          />

          {/* Admin protected routes - ADMIN ONLY */}
          <Route
            path="/admin/*"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminPortal />
              </ProtectedRoute>
            }
          />

          {/* Brand Portal protected routes */}
          <Route
            path="/brand-portal"
            element={
              <ProtectedRoute allowedRoles={['brand_partner', 'admin']}>
                <BrandPortal />
              </ProtectedRoute>
            }
          />

          {/* Student protected routes */}
          <Route
            path="/academy/*"
            element={
              <StudentRoute>
                <StudentAcademy />
              </StudentRoute>
            }
          />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster position="top-right" richColors />
      </div>
    </BrowserRouter>
  );
}

function App() {
  return (
    <AuthProvider>
      <CurrencyProvider>
        <AppContent />
      </CurrencyProvider>
    </AuthProvider>
  );
}

export default App;
