/**
 * Main App Component with Routing
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline, CircularProgress, Box } from '@mui/material';
import { AuthProvider, useAuth } from './context/AuthContext';
import theme from './theme/theme';
import LoginPage from './pages/Login';
import MADashboard from './pages/MADashboard';
import CreatorDashboard from './pages/CreatorDashboard';
import { UserRole } from './types';

// Protected Route Component
const ProtectedRoute: React.FC<{
  children: React.ReactElement;
  allowedRoles: UserRole[];
}> = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    // Redirect to appropriate dashboard based on role
    if (user.role === UserRole.MA) {
      return <Navigate to="/ma-dashboard" replace />;
    } else {
      return <Navigate to="/creator-dashboard" replace />;
    }
  }

  return children;
};

// App Routes Component
const AppRoutes: React.FC = () => {
  const { user, setUser, logout } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          user ? (
            <Navigate
              to={user.role === UserRole.MA ? '/ma-dashboard' : '/creator-dashboard'}
              replace
            />
          ) : (
            <LoginPage onLoginSuccess={setUser} />
          )
        }
      />

      <Route
        path="/ma-dashboard"
        element={
          <ProtectedRoute allowedRoles={[UserRole.MA]}>
            <MADashboard user={user!} onLogout={logout} />
          </ProtectedRoute>
        }
      />

      <Route
        path="/creator-dashboard"
        element={
          <ProtectedRoute allowedRoles={[UserRole.CREATOR]}>
            <CreatorDashboard user={user!} onLogout={logout} />
          </ProtectedRoute>
        }
      />

      <Route
        path="/"
        element={
          user ? (
            <Navigate
              to={user.role === UserRole.MA ? '/ma-dashboard' : '/creator-dashboard'}
              replace
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

// Main App Component
const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
