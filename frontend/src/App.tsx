import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import FlashcardsPage from "./pages/FlashcardsPage";

function App() {
  return (
    <Router>
      <div className="p-4">
        <nav className="mb-4">
          <Link to="/" className="text-blue-600 underline">Flashcards</Link>
        </nav>
        <Routes>
          <Route path="/" element={<FlashcardsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
