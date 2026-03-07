import "@/App.css";
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

  if (requireAuth && !isAuthenticated) {
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

          {/* Guardian protected routes */}
          <Route
            path="/portal/*"
            element={
              <ProtectedRoute>
                <GuardianPortal />
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
