import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './components/Login';
import { Layout } from './components/Layout';
import { ChatInterface } from './components/ChatInterface';
import { DashboardCharts } from './components/DashboardCharts';
import { LeadershipReport } from './components/LeadershipReport';
import { DataQualityDashboard } from './components/DataQualityDashboard';
import { ProtectedRoute } from './components/ProtectedRoute';

// Route wrapper to redirect logged-in users away from login page
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  return isAuthenticated ? <Navigate to="/" replace /> : <>{children}</>;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } />
          
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<ChatInterface />} />
              <Route path="/dashboard" element={<DashboardCharts />} />
              <Route path="/leadership" element={<LeadershipReport />} />
              <Route path="/quality" element={<DataQualityDashboard />} />
            </Route>
          </Route>
          
          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
