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
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import DecksPage from "./pages/DecksPage";
import DeckReviewPage from './pages/DeckReviewPage';
import MasteryGraph from './components/MasteryGraph';
import HelpPage from './pages/HelpPage';
import PremiumPage from './pages/PremiumPage';
import SubscriptionSuccessPage from './pages/SubscriptionSuccessPage';
import SubscriptionCancelPage from './pages/SubscriptionCancelPage';
import DashboardPage from './pages/DashboardPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import PhoneNumberModal from './components/PhoneNumberModal';

const AppContent: React.FC = () => {
  const { showPhoneModal, setShowPhoneModal, updatePhoneNumber } = useAuth();
  const [isSavingPhone, setIsSavingPhone] = React.useState(false);

  const handlePhoneSave = async (phoneNumber: string, smsOptIn: boolean) => {
    setIsSavingPhone(true);
    try {
      await updatePhoneNumber(phoneNumber, smsOptIn);
    } catch (error) {
      console.error('Failed to save phone number:', error);
    } finally {
      setIsSavingPhone(false);
    }
  };

  return (
    <>
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
            path="/flashcards/:deckId?"
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
            path="/review-due-cards"
            element={
              <ProtectedRoute>
                <ManualReviewPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/decks"
            element={
              <ProtectedRoute>
                <DecksPage />
              </ProtectedRoute>
            }
          />
          <Route path="/decks/:deck_id/review" element={<DeckReviewPage />} />
          <Route
            path="/decks/:deckId/mastery"
            element={
              <ProtectedRoute>
                <MasteryGraph />
              </ProtectedRoute>
            }
          />
          <Route
            path="/help"
            element={<HelpPage />}
          />
          <Route
            path="/premium"
            element={
              <ProtectedRoute>
                <PremiumPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription/success"
            element={
              <ProtectedRoute>
                <SubscriptionSuccessPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription/cancel"
            element={
              <ProtectedRoute>
                <SubscriptionCancelPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <AdminDashboardPage />
              </ProtectedRoute>
            }
          />
        </Routes>
        <PhoneNumberModal
          isOpen={showPhoneModal}
          onClose={() => setShowPhoneModal(false)}
          onSave={handlePhoneSave}
          isSaving={isSavingPhone}
        />
      </>
    );
  };

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
};

export default App;
