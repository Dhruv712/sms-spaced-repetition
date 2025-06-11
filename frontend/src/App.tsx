import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import FlashcardsPage from "./pages/FlashcardsPage";
import ProfilePage from './pages/ProfilePage';
import Navbar from './components/Navbar';
import ReviewHistoryPage from "./pages/ReviewHistoryPage";
import ManualReviewPage from "./pages/ManualReviewPage";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./contexts/AuthContext";

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <FlashcardsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <ReviewHistoryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/manual-review"
            element={
              <ProtectedRoute>
                <ManualReviewPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
};

export default App;
