import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const FloatingHelpButton: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Don't show on landing, login, or register pages
  if (location.pathname === '/' || location.pathname === '/login' || location.pathname === '/register') {
    return null;
  }

  const handleClick = () => {
    navigate('/help');
  };

  return (
    <button
      onClick={handleClick}
      className="fixed bottom-6 left-6 z-40 w-14 h-14 bg-accent hover:bg-accent/90 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center group"
      title="Help"
      aria-label="Help"
    >
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    </button>
  );
};

export default FloatingHelpButton;

