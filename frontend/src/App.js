import "@/App.css";
import '@/i18n';
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { Toaster } from "sonner";

// Import pages (we'll create these next)
import LandingPage from "@/pages/LandingPage";
import GuardianLogin from "@/pages/GuardianLogin";
import GuardianRegister from "@/pages/GuardianRegister";
import StudentLogin from "@/pages/StudentLogin";
import GuardianPortal from "@/pages/GuardianPortal";
import StudentAcademy from "@/pages/StudentAcademy";
import TeacherLogin from "@/pages/TeacherLogin";
import TeacherRegister from "@/pages/TeacherRegister";
import TeacherPortal from "@/pages/TeacherPortal";
import AdminPortal from "@/pages/AdminPortal";
import DonatePage from "@/pages/DonatePage";
import BrandPortal from "@/pages/BrandPortal";

// Protected route component
const ProtectedRoute = ({ children, requireAuth = true }) => {
  const { isAuthenticated, loading } = useAuth();

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
          <Route path="/student-login" element={<StudentLogin />} />
          <Route path="/teacher-login" element={<TeacherLogin />} />
          <Route path="/teacher-register" element={<TeacherRegister />} />
          <Route path="/donate" element={<DonatePage />} />
          <Route path="/brand-portal" element={<BrandPortal />} />

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

          {/* Admin protected routes */}
          <Route
            path="/admin/*"
            element={
              <ProtectedRoute>
                <AdminPortal />
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
      <AppContent />
    </AuthProvider>
  );
}

export default App;
