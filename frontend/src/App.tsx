import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import FlashcardsPage from "./pages/FlashcardsPage";
import ProfilePage from './pages/ProfilePage';
import Navbar from './components/Navbar';
import ReviewHistoryPage from "./pages/ReviewHistoryPage";
import ManualReviewPage from "./pages/ManualReviewPage";


const App: React.FC = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<FlashcardsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/history" element={<ReviewHistoryPage />} />
        <Route path="/manual-review" element={<ManualReviewPage />} />
      </Routes>
    </Router>
  );
};

export default App;
